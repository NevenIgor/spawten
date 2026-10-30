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
    _configured = True


configure_django()

from core.models import Lead, Status  # noqa: E402

VISITOR_STATUS_NAME = "visitor"
ORDER_STATUS_NAME = "order"


def get_status(name: str) -> Status | None:
    """Return a Status by name, creating it on the fly if it is missing."""
    status, _created = Status.objects.get_or_create(name=name)
    return status


def get_visitor_status() -> Status | None:
    return get_status(VISITOR_STATUS_NAME)


def get_order_status() -> Status | None:
    return get_status(ORDER_STATUS_NAME)


def upsert_lead_on_start(tg_id: int) -> bool:
    """Create a lead with status 'visitor' for a new tg user.

    Returns True if a new lead was created, False if it already existed.
    """
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
