"""Менеджерский веб-интерфейс обработки заявок (Django subsystem).

URLs:
    /manager/            — главная страница со «стеной» карточек (после логина)
    /manager/lead/<pk>/  — подробная карточка лида + live-чат через бота
    /manager/login/      — вход по учётным данным Django
    /manager/logout/     — выход
"""
import json
from datetime import date, timedelta

from django.contrib.auth import login as auth_login
from django.contrib.auth import logout as auth_logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.paginator import Paginator
from django.db.models import Count, Q
from django.db.models.functions import TruncDate
from django.http import HttpResponseBadRequest, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views.decorators.http import require_POST

from core.models import ChatMessage, Lead, LeadStatus, TelegramProfile
from core.translations import status_display, translate


def tr(key: str) -> str:
    """Перевод строки веб-интерфейса менеджера (см. core/translations.py)."""
    return translate(key)


def _is_manager(user) -> bool:
    """Any staff member or superuser may work with leads."""
    return user.is_authenticated and (user.is_staff or user.is_superuser)


manager_required = user_passes_test(_is_manager, login_url="/manager/login/")


#: keys of the manager UI section in core/translations.py exposed to templates
_T_KEYS = [
    "mgr.login_title", "mgr.username", "mgr.password", "mgr.sign_in", "mgr.logout",
    "mgr.dashboard_title", "mgr.search_placeholder", "mgr.search_btn", "mgr.reset_btn",
    "mgr.no_leads", "mgr.new_cards", "mgr.card_created", "mgr.card_user", "mgr.card_phone",
    "mgr.legend", "mgr.filter_all", "mgr.lead_details", "mgr.back_to_list",
    "mgr.section_lead", "mgr.section_relative", "mgr.section_tg", "mgr.section_service",
    "mgr.change_status", "mgr.save", "mgr.saved", "mgr.chat_title", "mgr.chat_hint",
    "mgr.chat_input_placeholder", "mgr.chat_send", "mgr.chat_empty",
    "mgr.chat_connected", "mgr.chat_disconnected", "mgr.not_found",
    "mgr.you", "mgr.bot", "mgr.user", "mgr.tg_link", "mgr.tg_none", "mgr.tg_estimate_note",
    "mgr.not_filled", "mgr.attachment", "mgr.premium_yes", "mgr.premium_no",
    # --- navigation / filters ---
    "mgr.nav_leads", "mgr.nav_stats",
    "mgr.filter_status", "mgr.filter_date_from", "mgr.filter_date_to",
    "mgr.sort_label", "mgr.sort_new", "mgr.sort_old", "mgr.sort_name",
    "mgr.sort_rname", "mgr.sort_status",
    "mgr.per_page", "mgr.active_filters", "mgr.clear_filters",
    "mgr.filled_label", "mgr.filled_any", "mgr.filled_yes", "mgr.filled_no",
    "mgr.show_filters",
    "mgr.results_count", "mgr.no_results",
    # --- statistics page ---
    "mgr.stats_title", "mgr.stats_total", "mgr.stats_week", "mgr.stats_month",
    "mgr.stats_conversion", "mgr.stats_chats", "mgr.stats_profiles",
    "mgr.by_status", "mgr.dynamics", "mgr.top_managers", "mgr.recent_activity",
    "mgr.lead", "mgr.leads", "mgr.messages", "mgr.none_data",
    "admin.site_header",
]


#: additional model-field labels used directly by the manager templates
_EXTRA_KEYS = [
    "lead.full_name", "lead.contact_phone", "lead.workplace", "lead.tg_id",
    "lead.first_contact_date", "lead.note", "lead.relative_full_name",
    "lead.relative_birth_date", "lead.relationship", "lead.relative_workplace",
    "lead.relative_location", "lead.additional_info",
    "tgsnapshot.username", "tgsnapshot.phone_number", "tgsnapshot.registered_at",
    "tgsnapshot.location", "tgsnapshot.language_code", "tgsnapshot.is_premium",
]


def _tmap() -> dict:
    """Flat dotted-key map (JSON payload for JS) ..."""
    m = {key: translate(key) for key in _T_KEYS}
    for key in _EXTRA_KEYS:
        m[key] = translate(key)
    return m


def _tnested() -> dict:
    """... and the nested variant used by Django templates: ``t.mgr.dashboard_title``."""
    tree: dict = {}
    for key, value in _tmap().items():
        parts = key.split(".")
        node = tree
        for part in parts[:-1]:
            node = node.setdefault(part, {})
        node[parts[-1]] = value
    return tree


# ---------------------------------------------------------------- helpers

def _fmt_date(value) -> str:
    if isinstance(value, date):
        return value.strftime("%d.%m.%Y")
    return ""


def _card_payload(lead: Lead) -> dict:
    """Brief card data for the dashboard wall."""
    profile = lead.telegram_profile if hasattr(lead, "telegram_profile") else None
    if profile is None:
        profile = TelegramProfile.objects.filter(tg_id=lead.tg_id).first() if lead.tg_id else None
    return {
        "id": str(lead.pk),
        "color": lead.status_color,
        "status_name": lead.status.name if lead.status else "",
        "status_label": status_display(lead.status.name if lead.status else ""),
        "relative_full_name": lead.relative_full_name,
        "relative_birth_date": _fmt_date(lead.relative_birth_date),
        "relative_workplace": lead.relative_workplace,
        "relative_location": lead.relative_location,
        "full_name": lead.full_name,
        "contact_phone": lead.contact_phone,
        "tg_id": lead.tg_id or "",
        "tg_username": (profile.username if profile else "") or "",
        "tg_phone": (profile.phone_number if profile else "") or "",
        "created": lead.created.strftime("%d.%m.%Y %H:%M"),
    }


#: allowed sort options for the dashboard (querystring value -> queryset order_by)
_SORTS = {
    "new": "-created",
    "old": "created",
    "name": "full_name",
    "rname": "relative_full_name",
    "status": "status__sort_order",
}


def _lead_filters(request):
    """Build a filtered lead queryset from GET parameters.

    Supported params: q, status (multi), date_from, date_to, filled, sort.
    Returns (queryset, filters_dict) where filters_dict is used by the template.
    """
    qs = Lead.objects.select_related("status").order_by("-created")

    q = request.GET.get("q", "").strip()
    if q:
        search_q = (
            Q(full_name__icontains=q)
            | Q(relative_full_name__icontains=q)
            | Q(contact_phone__icontains=q)
            | Q(workplace__icontains=q)
            | Q(note__icontains=q)
        )
        if q.lstrip("-").isdigit():
            search_q |= Q(tg_id__icontains=q)
        # username lives on TelegramProfile (no FK from Lead) — resolve via tg_id
        tg_user_ids = list(
            TelegramProfile.objects.filter(username__icontains=q).values_list("tg_id", flat=True)[:500]
        )
        if tg_user_ids:
            search_q |= Q(tg_id__in=tg_user_ids)
        qs = qs.filter(search_q)

    # multi-status filter: ?status=visitor&status=order  or  ?status=visitor,order
    status_names: list[str] = []
    for raw in request.GET.getlist("status"):
        status_names.extend(n for n in raw.split(",") if n)
    if status_names:
        qs = qs.filter(status__name__in=status_names)

    date_from = request.GET.get("date_from", "").strip()
    date_to = request.GET.get("date_to", "").strip()
    if date_from:
        try:
            qs = qs.filter(created__date__gte=date.fromisoformat(date_from))
        except ValueError:
            date_from = ""
    if date_to:
        try:
            qs = qs.filter(created__date__lte=date.fromisoformat(date_to))
        except ValueError:
            date_to = ""

    filled = request.GET.get("filled", "").strip()
    if filled == "yes":
        qs = qs.exclude(relative_full_name="")
    elif filled == "no":
        qs = qs.filter(relative_full_name="")

    sort = request.GET.get("sort", "new").strip()
    qs = qs.order_by(_SORTS.get(sort, "-created"))

    filters = {
        "q": q,
        "statuses": status_names,
        "date_from": date_from,
        "date_to": date_to,
        "filled": filled,
        "sort": sort if sort in _SORTS else "new",
    }
    return qs, filters


def _has_active_filters(filters: dict) -> bool:
    return any([
        filters["q"], filters["statuses"], filters["date_from"],
        filters["date_to"], filters["filled"],
        filters["sort"] != "new",
    ])


# ---------------------------------------------------------------- login

@login_required(login_url="/manager/login/")
def logout_view(request):
    auth_logout(request)
    return redirect("/manager/login/")


def login_view(request):
    """Manager sign-in page (username/password from the Django auth system)."""
    error = ""
    if request.method == "POST":
        from django.contrib.auth import authenticate

        username = request.POST.get("username", "").strip()
        password = request.POST.get("password", "")
        user = authenticate(request, username=username, password=password)
        if user is not None and _is_manager(user):
            auth_login(request, user)
            nxt = request.GET.get("next") or "/manager/"
            return redirect(nxt)
        error = translate("mgr.login_failed")

    if request.user.is_authenticated and _is_manager(request.user):
        return redirect("/manager/")
    return render(request, "manager/login.html", {"error": error, "t": _tnested()})


# ---------------------------------------------------------------- dashboard

@manager_required
def dashboard(request):
    """Main window: colour-coded cards of everyone who used the bot.

    Supports search (q), multi-status filter, date range, "filled" flag,
    sorting and page size — all via GET parameters.
    """
    qs, filters = _lead_filters(request)

    # per-page size selector (24/48/96)
    try:
        per_page = int(request.GET.get("per_page", "24"))
    except ValueError:
        per_page = 24
    if per_page not in (24, 48, 96):
        per_page = 24

    paginator = Paginator(qs, per_page)
    page_obj = paginator.get_page(request.GET.get("page"))

    statuses = list(LeadStatus.objects.all())
    status_counts = dict(
        Lead.objects.values_list("status__name").annotate(c=Count("id"))
    )
    legend = [
        {
            "name": s.name,
            "label": status_display(s.name),
            "color": s.color,
            "count": status_counts.get(s.name, 0),
            "checked": (not filters["statuses"]) or (s.name in filters["statuses"]),
        }
        for s in statuses
    ]

    # base url without the "page" param so filter links keep their state
    get_params = request.GET.copy()
    get_params.pop("page", None)
    base_query = get_params.urlencode()

    t = _tnested()
    context = {
        "page_obj": page_obj,
        "cards": [_card_payload(lead) for lead in page_obj],
        "total_leads": paginator.count,
        "all_leads": Lead.objects.count(),
        "statuses": statuses,
        "legend": legend,
        "filters": filters,
        "q": filters["q"],
        "status_filter": ",".join(filters["statuses"]),
        "has_filters": _has_active_filters(filters),
        "base_query": base_query,
        "per_page": per_page,
        "per_page_options": [24, 48, 96],
        "t": t,
        "t_json": json.dumps(_tmap(), ensure_ascii=False),
    }
    return render(request, "manager/dashboard.html", context)


@manager_required
def new_cards(request):
    """Polling endpoint: cards created after ``?after=<iso>`` as JSON."""
    after = request.GET.get("after", "")
    qs = Lead.objects.select_related("status").order_by("created")
    if after:
        try:
            from datetime import datetime

            ts = datetime.fromisoformat(after)
            qs = qs.filter(created__gt=ts)
        except ValueError:
            return HttpResponseBadRequest("bad 'after' parameter")
    return JsonResponse({"cards": [_card_payload(l) for l in qs[:200]]})


# ---------------------------------------------------------------- statistics

@manager_required
def stats_view(request):
    """Statistics page with several dashboards about leads and chats."""
    now = timezone.now()
    week_ago = now - timedelta(days=7)
    month_ago = now - timedelta(days=30)

    total = Lead.objects.count()
    new_week = Lead.objects.filter(created__gte=week_ago).count()
    new_month = Lead.objects.filter(created__gte=month_ago).count()
    active_week = Lead.objects.exclude(status__name="visitor").filter(
        modified__gte=week_ago
    ).count()

    # --- distribution by status (bar chart) ---
    counts = dict(
        Lead.objects.values_list("status__name").annotate(c=Count("id"))
    )
    by_status = []
    max_count = max(counts.values()) if counts else 0
    for s in LeadStatus.objects.all():
        c = counts.get(s.name, 0)
        pct = round(c * 100 / total, 1) if total else 0
        bar = round(c * 100 / max_count, 1) if max_count else 0
        by_status.append({
            "name": s.name,
            "label": status_display(s.name),
            "color": s.color,
            "count": c,
            "percent": pct,
            "bar": bar,
        })

    # --- conversion funnel visitor -> order -> work -> lead ---
    v = counts.get("visitor", 0) + counts.get("order", 0) + \
        counts.get("work", 0) + counts.get("lead", 0)
    def _pct(name):
        return round(counts.get(name, 0) * 100 / v, 1) if v else 0
    funnel = [
        {"label": status_display("visitor"), "percent": 100 if v else 0,
         "count": v},
        {"label": status_display("order"), "percent": _pct("order") + _pct("work") + _pct("lead"),
         "count": counts.get("order", 0) + counts.get("work", 0) + counts.get("lead", 0)},
        {"label": status_display("work"), "percent": _pct("work") + _pct("lead"),
         "count": counts.get("work", 0) + counts.get("lead", 0)},
        {"label": status_display("lead"), "percent": _pct("lead"),
         "count": counts.get("lead", 0)},
    ]

    # --- dynamics over the last 14 days (column chart) ---
    dyn_start = (now - timedelta(days=13)).date()
    daily_qs = (
        Lead.objects.filter(created__date__gte=dyn_start)
        .annotate(day=TruncDate("created"))
        .values("day").annotate(c=Count("id")).order_by("day")
    )
    daily_map = {row["day"]: row["c"] for row in daily_qs}
    daily_max = max(daily_map.values()) if daily_map else 0
    dynamics = []
    for i in range(14):
        d = dyn_start + timedelta(days=i)
        c = daily_map.get(d, 0)
        dynamics.append({
            "date": d.strftime("%d.%m"),
            "count": c,
            "height": round(c * 100 / daily_max) if daily_max else 0,
        })

    # --- top managers by handled messages ---
    top_managers = (
        ChatMessage.objects.filter(direction="outgoing", sent_by__gt="")
        .values("sent_by")
        .annotate(msgs=Count("id"), leads=Count("tg_id", distinct=True))
        .order_by("-msgs")[:10]
    )

    chat_stats = {
        "incoming": ChatMessage.objects.filter(direction="incoming").count(),
        "outgoing": ChatMessage.objects.filter(direction="outgoing").count(),
        "week": ChatMessage.objects.filter(created__gte=week_ago).count(),
    }
    profiles_total = TelegramProfile.objects.count()
    profiles_phone = TelegramProfile.objects.exclude(phone_number="").count()
    profiles_location = TelegramProfile.objects.exclude(location="").count()

    # --- recent activity feed ---
    recent = [
        {
            "lead_id": str(l.pk),
            "title": l.full_name or l.relative_full_name or f"tg:{l.tg_id}",
            "color": l.status_color,
            "status_label": status_display(l.status.name if l.status else ""),
            "time": l.created.strftime("%d.%m.%Y %H:%M"),
        }
        for l in Lead.objects.select_related("status").order_by("-created")[:10]
    ]

    t = _tnested()
    context = {
        "kpi": {
            "total": total,
            "new_week": new_week,
            "new_month": new_month,
            "active_week": active_week,
            "chats": chat_stats["incoming"] + chat_stats["outgoing"],
            "profiles": profiles_total,
        },
        "by_status": by_status,
        "funnel": funnel,
        "dynamics": dynamics,
        "top_managers": list(top_managers),
        "chat_stats": chat_stats,
        "profiles": {
            "total": profiles_total,
            "phone": profiles_phone,
            "location": profiles_location,
        },
        "recent": recent,
        "t": t,
    }
    return render(request, "manager/stats.html", context)


# ---------------------------------------------------------------- lead detail

@manager_required
def lead_detail_view(request, pk: str):
    lead = get_object_or_404(Lead.objects.select_related("status"), pk=pk)
    profile = TelegramProfile.objects.filter(tg_id=lead.tg_id).first() if lead.tg_id else None

    tg_info = None
    if lead.tg_id:
        estimated = TelegramProfile.estimated_registration(lead.tg_id)
        registered_at = (profile.registered_at if profile and profile.registered_at else estimated)
        tg_info = {
            "tg_id": lead.tg_id,
            "username": profile.username if profile else "",
            "first_name": profile.first_name if profile else "",
            "last_name": profile.last_name if profile else "",
            "phone": profile.phone_number if profile else "",
            "registered_at": registered_at.strftime("%d.%m.%Y") if registered_at else "",
            "registered_estimated": bool(
                estimated and (not profile or not profile.registered_at)
            ),
            "location": profile.location if profile else "",
            "language": profile.language_code if profile else "",
            "premium": bool(profile.is_premium) if profile else False,
            "link": (f"https://t.me/{profile.username}" if profile and profile.username
                     else f"tg://user?id={lead.tg_id}"),
        }

    history = []
    if lead.tg_id:
        for msg in ChatMessage.objects.filter(tg_id=lead.tg_id).order_by("created")[:500]:
            history.append({
                "id": str(msg.pk),
                "direction": msg.direction,
                "text": msg.text,
                "time": msg.created.strftime("%d.%m.%Y %H:%M:%S"),
                "sent_by": msg.sent_by,
                "attachment_kind": msg.attachment_kind,
                "attachment_url": msg.attachment_url,
            })

    t = _tnested()
    context = {
        "lead": lead,
        "tg_info": tg_info,
        "chat_history_json": json.dumps(history, ensure_ascii=False),
        "statuses": list(LeadStatus.objects.all()),
        "photo_url": lead.photo.url if lead.photo else "",
        "media_url": lead.additional_media.url if lead.additional_media else "",
        "fmt_date": _fmt_date,
        "t": t,
        "t_json": json.dumps(_tmap(), ensure_ascii=False),
    }
    return render(request, "manager/lead_detail.html", context)


@manager_required
@require_POST
def lead_set_status(request, pk: str):
    lead = get_object_or_404(Lead, pk=pk)
    status_name = request.POST.get("status", "")
    st = get_object_or_404(LeadStatus, name=status_name)
    lead.status = st
    lead.save(update_fields=["status", "modified"])
    if request.headers.get("X-Requested-With") == "fetch":
        return JsonResponse({"ok": True, "color": st.color,
                             "label": status_display(st.name)})
    return redirect("manager_lead_detail", pk=lead.pk)
