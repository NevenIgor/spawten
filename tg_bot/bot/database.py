"""Database access layer for the bot (direct PostgreSQL via Django ORM).

The bot configures a minimal Django instance that points to the shared
PostgreSQL database and loads the API project's ``core`` app by path,
so no code is duplicated between containers.
"""
import os
import sys
from pathlib import Path

import django

_configured = False


def configure_django() -> None:
    """Configure a bare Django setup reusing the api project's core models."""
    global _configured
    if _configured:
        return

    # Locate the Django project (core app): env override or compose mount /app/api
    candidates = [os.getenv("DJANGO_API_DIR", ""), "/app/api",
                  str(Path(__file__).resolve().parents[2] / "api")]
    for cand in candidates:
        if cand and (Path(cand) / "core" / "models.py").exists():
            if cand not in sys.path:
                sys.path.insert(0, cand)
            break

    from django.conf import settings

    if not settings.configured:
        settings.configure(
            DEBUG=False,
            INSTALLED_APPS=[
                "django.contrib.contenttypes",
                "django.contrib.auth",
                "core",
            ],
            DATABASES={
                "default": {
                    "ENGINE": "django.db.backends.postgresql",
                    "NAME": os.getenv("POSTGRES_DB", "app"),
                    "USER": os.getenv("POSTGRES_USER", "app"),
                    "PASSWORD": os.getenv("POSTGRES_PASSWORD", "change_me"),
                    "HOST": os.getenv("POSTGRES_HOST", "postgres"),
                    "PORT": os.getenv("POSTGRES_PORT", "5432"),
                }
            },
            USE_TZ=True,
            DEFAULT_AUTO_FIELD="django.db.models.BigAutoField",
        )
    django.setup()

    # The bot shares the api project's database but must not depend on the
    # ``api`` service having run its startup migrations: if the tables are
    # missing (fresh/empty Postgres volume, or api failed to migrate), apply
    # the core migrations here once so ORM writes (e.g. save_lead_from_form)
    # don't fail with "relation \"core_lead\" does not exist".
    _ensure_schema()
    _configured = True


def _ensure_schema() -> None:
    """Apply pending migrations if the core tables are missing."""
    import logging

    from django.core.exceptions import ImproperlyConfigured
    from django.db import connection
    from django.db.migrations.executor import MigrationExecutor

    log = logging.getLogger(__name__)
    try:
        # Backend-agnostic check whether the core tables already exist.
        with connection.cursor() as cursor:
            names = connection.introspection.table_names(cursor)
        if "core_lead" in names:
            return
        executor = MigrationExecutor(connection)
        # Migrate only the shared `core` app (plus its dependencies) — never
        # unrelated apps that may exist in the same database.
        targets = [
            node for node in executor.loader.graph.leaf_nodes()
            if node[0] == "core"
        ]
        plan = executor.migration_plan(targets)
        if plan:
            log.info("Bot: core tables missing — applying %d migration(s)", len(plan))
            executor.migrate(targets)
            log.info("Bot: migrations applied successfully")
    except ImproperlyConfigured:
        raise
    except Exception:  # pragma: no cover - network/db issues must not crash the bot
        log.exception(
            "Bot: automatic migration failed; run "
            "'docker compose exec api python manage.py migrate' manually"
        )


configure_django()

from core.models import ChatMessage, Lead, LeadStatus, TelegramProfile  # noqa: E402

VISITOR_STATUS_NAME = "visitor"
ORDER_STATUS_NAME = "order"


def get_status(name: str) -> LeadStatus | None:
    """Return a LeadStatus by name, creating it on the fly if it is missing."""
    status, _created = LeadStatus.objects.get_or_create(
        name=name, defaults={"color": "gray"}
    )
    return status


def get_visitor_status() -> LeadStatus | None:
    return get_status(VISITOR_STATUS_NAME)


def get_order_status() -> LeadStatus | None:
    return get_status(ORDER_STATUS_NAME)


# ---------------------------------------------------------- telegram profile

def upsert_telegram_profile(user, *, phone: str = "", location: str = "",
                            source: str = "bot /start") -> None:
    """Store/refresh the data we can extract from a Telegram user object.

    ``user`` is an aiogram ``User``; optional ``phone`` (shared contact) and
    ``location`` (shared geolocation) are merged in when provided.
    """
    if user is None or not getattr(user, "id", None):
        return
    profile, _ = TelegramProfile.objects.get_or_create(tg_id=user.id)
    changed = False
    for field, value in (
        ("username", user.username or ""),
        ("first_name", user.first_name or ""),
        ("last_name", user.last_name or ""),
        ("language_code", user.language_code or ""),
        ("is_premium", bool(user.is_premium)),
    ):
        current = getattr(profile, field)
        if value != "" and current != value:
            setattr(profile, field, value)
            changed = True
        elif field == "is_premium" and current != value:
            setattr(profile, field, value)
            changed = True
    if phone and profile.phone_number != phone:
        profile.phone_number = phone
        changed = True
    if location and profile.location != location:
        profile.location = location
        changed = True
    if source and profile.source != source:
        profile.source = source
        changed = True
    if profile.registered_at is None:
        estimated = TelegramProfile.estimated_registration(user.id)
        if estimated is not None:
            profile.registered_at = estimated
            changed = True
    if changed:
        profile.save()


def upsert_lead_on_start(tg_id: int, user=None) -> bool:
    """Create a lead with status 'visitor' for a new tg user.

    Returns True if a new lead was created, False if it already existed.
    ``user`` (aiogram User), when given, is also stored as TelegramProfile.
    """
    if user is not None:
        try:
            upsert_telegram_profile(user)
        except Exception:  # noqa: BLE001 - profile storage must never break /start
            pass
    lead, created = Lead.objects.get_or_create(
        tg_id=tg_id,
        defaults={
            "full_name": "",
            "status": get_visitor_status(),
            "first_contact_date": _today(),
        },
    )
    if not created and lead.status_id is None:
        lead.status = get_visitor_status()
        if lead.first_contact_date is None:
            lead.first_contact_date = _today()
        lead.save(update_fields=["status", "first_contact_date", "modified"])
    return created


def has_filled_request(tg_id: int) -> bool:
    """Return True if the user has a record that is NOT missing/`visitor`.

    Used on /start to decide which button to show:
      * no record or status == 'visitor'  -> 'Fill in the request'
      * any other status                  -> 'View request'
    """
    lead = Lead.objects.filter(tg_id=tg_id).first()
    if lead is None:
        return False
    visitor = get_visitor_status()
    if lead.status_id is None:
        return False
    if visitor is not None and lead.status_id == visitor.id:
        return False
    return lead.status.name != VISITOR_STATUS_NAME


def get_lead_snapshot(tg_id: int) -> dict | None:
    """Return a plain dict of the stored lead data (for the 'View request')."""
    lead = Lead.objects.filter(tg_id=tg_id).first()
    if lead is None:
        return None
    return {
        "relative_full_name": lead.relative_full_name,
        "relative_birth_date": lead.relative_birth_date,
        "relative_workplace": lead.relative_workplace,
        "relative_location": lead.relative_location,
        "photo": lead.photo.name if lead.photo else "",
        "additional_info": lead.additional_info,
        "additional_media": lead.additional_media.name if lead.additional_media else "",
        "relationship": lead.relationship,
        "full_name": lead.full_name,
        "workplace": lead.workplace,
        "contact_phone": lead.contact_phone,
        "status": lead.status.name if lead.status else "",
    }


def _today():
    from datetime import date

    return date.today()


def save_lead_from_form(
    *,
    tg_id: int,
    relative_full_name: str,
    relative_birth_date,
    relative_workplace: str,
    relative_location: str,
    photo_path: str | None,
    additional_info: str,
    additional_media_path: str | None,
    relationship: str,
    full_name: str,
    workplace: str,
    contact_phone: str,
) -> Lead:
    """Write the finished form into the existing (or newly created) lead."""
    lead = Lead.objects.filter(tg_id=tg_id).first()
    if lead is None:
        lead = Lead(tg_id=tg_id)

    lead.relative_full_name = relative_full_name
    lead.relative_birth_date = relative_birth_date
    lead.relative_workplace = relative_workplace
    lead.relative_location = relative_location
    if photo_path:
        lead.photo.name = photo_path
    lead.additional_info = additional_info
    if additional_media_path:
        lead.additional_media.name = additional_media_path
    lead.relationship = relationship
    lead.full_name = full_name or lead.full_name
    lead.workplace = workplace
    lead.contact_phone = contact_phone
    # Submitted request: move the status from 'visitor' to 'order'.
    lead.status = get_order_status()
    if lead.first_contact_date is None:
        lead.first_contact_date = _today()
    lead.save()
    return lead


# ------------------------------------------------------------- chat messages

def save_incoming_message(tg_id: int, text: str, *, attachment_kind: str = "",
                          attachment_url: str = "", tg_message_id: int | None = None) -> ChatMessage:
    """Persist a message the user sent to the bot (direction: incoming)."""
    return ChatMessage.objects.create(
        tg_id=tg_id,
        direction=ChatMessage.Direction.INCOMING,
        text=text or "",
        attachment_kind=attachment_kind,
        attachment_url=attachment_url,
        tg_message_id=tg_message_id,
    )


def get_lead_status_name(tg_id: int) -> str:
    lead = Lead.objects.filter(tg_id=tg_id).select_related("status").first()
    return lead.status.name if lead and lead.status else ""


def set_lead_status(tg_id: int, status_name: str) -> bool:
    """Move a lead to another canonical status (work / lead / ...)."""
    lead = Lead.objects.filter(tg_id=tg_id).first()
    if lead is None:
        return False
    lead.status = get_status(status_name)
    lead.save(update_fields=["status", "modified"])
    return True
