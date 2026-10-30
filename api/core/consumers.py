"""Real-time chat between the manager (via the bot) and a Telegram user.

Поток данных:

* входящее сообщение пользователя -> бот пишет его в БД (``ChatMessage``) и в
  group_channel ``chat_<tg_id>`` через Redis-публ/саб (channels InMemory/Redis);
* браузер менеджера подписан на этот канал по WebSocket — сообщения
  появляются мгновенно;
* исходящее сообщение менеджера приходит по WS на consumer, сохраняется в БД
  и публикуется в channel ``bot_outgoing`` — бот забирает его оттуда и
  отправляет пользователю через Telegram Bot API.
"""
import json
import logging

from channels.exceptions import DenyConnection
from channels.generic.websocket import AsyncWebsocketConsumer

logger = logging.getLogger(__name__)

CHAT_GROUP_PREFIX = "chat_"      # + tg_id  -> messages for one lead
BOT_OUTGOING_GROUP = "bot_outgoing"  # consumed by the telegram bot process


class ManagerChatConsumer(AsyncWebsocketConsumer):
    """WS endpoint: /ws/manager/chat/<tg_id>/"""

    async def connect(self):
        self.tg_id = self.scope["url_route"]["kwargs"]["tg_id"]
        try:
            self.tg_id = int(self.tg_id)
        except (TypeError, ValueError):
            raise DenyConnection("bad tg_id") from None

        user = self.scope.get("user")
        if user is None or not user.is_authenticated or not (user.is_staff or user.is_superuser):
            raise DenyConnection("not a manager")

        self.group = f"{CHAT_GROUP_PREFIX}{self.tg_id}"
        await self.channel_layer.group_add(self.group, self.channel_name)
        await self.accept()
        logger.info("manager chat WS opened for tg_id=%s", self.tg_id)

    async def disconnect(self, code):
        group = getattr(self, "group", None)
        if group:
            await self.channel_layer.group_discard(group, self.channel_name)

    # --- browser -> server ---------------------------------------------------
    async def receive(self, text_data=None, bytes_data=None):
        try:
            payload = json.loads(text_data or "{}")
        except json.JSONDecodeError:
            return

        kind = payload.get("type")
        if kind == "typing":
            await self._notify_user_typing()
            return
        if kind != "message":
            return

        text = (payload.get("text") or "").strip()
        if not text:
            return

        from core.models import ChatMessage  # ORM import kept lazy for tests

        sent_by = getattr(self.scope.get("user"), "get_full_name", lambda: "")() \
            or getattr(self.scope.get("user"), "username", "")

        msg = await self._db_save(ChatMessage, tg_id=self.tg_id,
                                  direction=ChatMessage.Direction.OUTGOING,
                                  text=text, sent_by=sent_by)

        out = {
            "type": "message",
            "id": str(msg.pk),
            "direction": "outgoing",
            "text": text,
            "time": msg.created.strftime("%d.%m.%Y %H:%M:%S"),
            "sent_by": sent_by,
        }
        # 1) всем вкладкам менеджеров этого лида
        await self.channel_layer.group_send(self.group, {"type": "chat.event", "event": out})
        # 2) боту — отправить в Telegram
        await self.channel_layer.group_send(
            BOT_OUTGOING_GROUP,
            {"type": "bot.send", "tg_id": self.tg_id, "text": text, "msg_id": str(msg.pk)},
        )

    async def _notify_user_typing(self):
        await self.channel_layer.group_send(
            BOT_OUTGOING_GROUP, {"type": "bot.typing", "tg_id": self.tg_id}
        )

    # --- server -> browser ----------------------------------------------------
    async def chat_event(self, event):
        """Deliver an internal message to the websocket client."""
        await self.send(text_data=json.dumps(event["event"], ensure_ascii=False))

    # --- helpers ---------------------------------------------------------------
    @staticmethod
    async def _db_save(model, **fields):
        import asgiref.sync

        return await asgiref.sync.sync_to_async(model.objects.create, thread_sensitive=False)(**fields)
