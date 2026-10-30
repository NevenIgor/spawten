"""Менеджерский веб-интерфейс обработки заявок (Django subsystem).

URLs:
    /manager/            — главная страница со «стеной» карточек (после логина)
    /manager/lead/<pk>/  — подробная карточка лида + live-чат через бота
    /manager/login/      — вход по учётным данным Django
    /manager/logout/     — выход
"""
import json
from datetime import date

from django.contrib.auth import login as auth_login
from django.contrib.auth import logout as auth_logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.paginator import Paginator
from django.db.models import Q
from django.http import HttpResponseBadRequest, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
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
    "admin.site_header",
]


def _tmap() -> dict:
    return {key: translate(key) for key in _T_KEYS}


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
    return render(request, "manager/login.html", {"error": error, "t": _tmap()})


# ---------------------------------------------------------------- dashboard

@manager_required
def dashboard(request):
    """Main window: colour-coded cards of everyone who used the bot."""
    qs = Lead.objects.select_related("status").order_by("-created")

    q = request.GET.get("q", "").strip()
    if q:
        qs = qs.filter(
            Q(full_name__icontains=q)
            | Q(relative_full_name__icontains=q)
            | Q(contact_phone__icontains=q)
            | Q(workplace__icontains=q)
            | Q(tg_id__icontains=q if q.lstrip("-").isdigit() else "")
        )
    status_filter = request.GET.get("status", "").strip()
    if status_filter:
        qs = qs.filter(status__name=status_filter)

    paginator = Paginator(qs, 24)
    page_obj = paginator.get_page(request.GET.get("page"))

    statuses = list(LeadStatus.objects.all())
    legend = [
        {"name": s.name, "label": status_display(s.name), "color": s.color}
        for s in statuses
    ]

    context = {
        "page_obj": page_obj,
        "total_leads": paginator.count,
        "statuses": statuses,
        "legend": legend,
        "q": q,
        "status_filter": status_filter,
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

    context = {
        "lead": lead,
        "tg_info": tg_info,
        "chat_history_json": json.dumps(history, ensure_ascii=False),
        "statuses": list(LeadStatus.objects.all()),
        "photo_url": lead.photo.url if lead.photo else "",
        "media_url": lead.additional_media.url if lead.additional_media else "",
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
