"""REST API for the web chat interface (leads, chats, operator replies)."""
import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_GET, require_POST

from core.bridge import INCOMING_CHANNEL, encode_message, get_redis_url, outgoing_channel
from core.models import ChatMessage, Lead

MAX_BODY_SIZE = 10 * 1024 * 1024  # 10 MB


def _json_error(message: str, status: int = 400) -> JsonResponse:
    return JsonResponse({"error": message}, status=status)


def _parse_body(request):
    if request.content_length and request.content_length > MAX_BODY_SIZE:
        return None, _json_error("Request body is too large", 413)
    try:
        body = json.loads(request.body or b"{}")
    except (ValueError, TypeError):
        return None, _json_error("Invalid JSON body", 400)
    if not isinstance(body, dict):
        return None, _json_error("JSON body must be an object", 400)
    return body, None


@require_GET
def lead_list(request):
    """GET /api/leads/ — all leads with their latest message info."""
    leads = (
        Lead.objects.select_related("status")
        .prefetch_related("chat_messages")
        .order_by("-created")[:500]
    )
    data = [
        {
            "id": str(lead.id),
            "tg_id": lead.tg_id,
            "full_name": lead.full_name,
            "contact_phone": lead.contact_phone,
            "status": lead.status.name if lead.status else None,
            "created": lead.created.isoformat(),
            "unread": lead.chat_messages.filter(
                direction=ChatMessage.DIRECTION_INCOMING, is_read=False
            ).count(),
            "last_message": (
                lead.chat_messages.order_by("-created")
                .values_list("text", flat=True)
                .first()
                or ""
            )[:80],
        }
        for lead in leads
    ]
    return JsonResponse({"results": data}, json_dumps_params={"ensure_ascii": False})


@require_GET
def chat_detail(request, tg_id: int):
    """GET /api/chats/<tg_id>/ — full message history of one user."""
    lead = Lead.objects.filter(tg_id=tg_id).first()
    messages = ChatMessage.objects.filter(tg_id=tg_id).order_by("created")
    data = [
        {
            "id": str(m.id),
            "direction": m.direction,
            "text": m.text,
            "media_url": f"/media/{m.media_path}" if m.media_path else "",
            "created": m.created.isoformat(),
        }
        for m in messages
    ]
    return JsonResponse(
        {
            "tg_id": tg_id,
            "lead": {
                "id": str(lead.id),
                "full_name": lead.full_name,
                "status": lead.status.name if lead.status else None,
            }
            if lead
            else None,
            "messages": data,
        },
        json_dumps_params={"ensure_ascii": False},
    )


@csrf_exempt
@require_POST
def chat_send(request, tg_id: int):
    """POST /api/chats/<tg_id>/send/ {"text": "..."} — operator reply.

    Persists the message and publishes it to the bot over Redis pub/sub;
    the bot delivers it to the user on Telegram.
    """
    body, error = _parse_body(request)
    if error:
        return error

    text = (body.get("text") or "").strip()
    if not text:
        return _json_error("'text' is required")

    lead = Lead.objects.filter(tg_id=tg_id).first()
    message = ChatMessage.objects.create(
        lead=lead,
        tg_id=tg_id,
        direction=ChatMessage.DIRECTION_OUTGOING,
        text=text,
    )

    try:
        _publish(outgoing_channel(tg_id), encode_message(tg_id=tg_id, text=text))
    except Exception as exc:  # noqa: BLE001 - surface delivery problems to the UI
        return JsonResponse(
            {"error": f"Message saved but could not be published to the bot: {exc}",
             "id": str(message.id)},
            status=502,
        )

    return JsonResponse({"id": str(message.id), "sent": True}, status=201)


@csrf_exempt
@require_POST
def chat_inject(request, tg_id: int):
    """POST /api/chats/<tg_id>/inject/ — simulate an incoming user message.

    Intended for local testing of the bridge without a real Telegram account:
    stores the message and pushes it into the live feed channel, exactly like
    the bot does.
    """
    body, error = _parse_body(request)
    if error:
        return error

    text = (body.get("text") or "").strip()
    media_path = (body.get("media_path") or "").strip()
    if not text and not media_path:
        return _json_error("'text' or 'media_path' is required")

    lead = Lead.objects.filter(tg_id=tg_id).first()
    message = ChatMessage.objects.create(
        lead=lead,
        tg_id=tg_id,
        direction=ChatMessage.DIRECTION_INCOMING,
        text=text,
        media_path=media_path,
    )
    payload = encode_message(tg_id=tg_id, text=text, media_path=media_path)
    _publish(INCOMING_CHANNEL, payload)
    return JsonResponse({"id": str(message.id)}, status=201)


def _publish(channel: str, payload: str) -> None:
    import redis

    client = redis.Redis.from_url(get_redis_url())
    try:
        client.publish(channel, payload)
    finally:
        try:
            client.close()
        except Exception:  # pragma: no cover
            pass
