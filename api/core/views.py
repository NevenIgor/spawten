"""Server-rendered web chat interface (operator inbox)."""
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render

from core.bridge import encode_message, outgoing_channel
from core.models import ChatMessage, Lead


def _publish_async(channel: str, payload: str) -> None:
    """Publish to Redis without blocking the request thread on a bad connection."""
    import redis

    from core.bridge import get_redis_url

    client = redis.Redis.from_url(get_redis_url())
    try:
        client.publish(channel, payload)
    finally:
        try:
            client.close()
        except Exception:  # pragma: no cover
            pass


@login_required
def inbox(request):
    leads = (
        Lead.objects.select_related("status")
        .filter(tg_id__isnull=False)
        .order_by("-created")[:200]
    )
    unread_counts = {}
    for lead in leads:
        unread_counts[lead.tg_id] = ChatMessage.objects.filter(
            tg_id=lead.tg_id, direction=ChatMessage.DIRECTION_INCOMING, is_read=False
        ).count()
    return render(
        request,
        "core/inbox.html",
        {"leads": leads, "unread_counts": unread_counts},
    )


@login_required
def chat_room(request, pk):
    lead = get_object_or_404(Lead, pk=pk)
    messages = ChatMessage.objects.filter(tg_id=lead.tg_id).order_by("created")
    if request.method == "POST":
        text = (request.POST.get("text") or "").strip()
        if text and lead.tg_id is not None:
            ChatMessage.objects.create(
                lead=lead,
                tg_id=lead.tg_id,
                direction=ChatMessage.DIRECTION_OUTGOING,
                text=text,
            )
            try:
                _publish_async(
                    outgoing_channel(lead.tg_id),
                    encode_message(tg_id=lead.tg_id, text=text),
                )
            except Exception as exc:  # noqa: BLE001
                messages = ChatMessage.objects.filter(tg_id=lead.tg_id).order_by("created")
                return render(
                    request,
                    "core/chat.html",
                    {"lead": lead, "messages": messages,
                     "error": f"Message saved but the bot is unreachable: {exc}"},
                )
        return redirect("core:chat", pk=lead.pk)

    ChatMessage.objects.filter(
        tg_id=lead.tg_id, direction=ChatMessage.DIRECTION_INCOMING, is_read=False
    ).update(is_read=True)

    return render(request, "core/chat.html", {"lead": lead, "messages": messages})



