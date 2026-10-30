"""Real-time bridge between the bot and the manager web UI chat.

* ``publish_incoming`` — вызывается из хендлеров бота: каждое сообщение
  пользователя сохраняется в БД (``ChatMessage``) и публикуется в Redis-канал
  ``chat_<tg_id>``, куда подписан WebSocket менеджера (channels).
* ``OutgoingListener`` — asyncio-задача, слушающая канал ``bot_outgoing``:
  сообщения, написанные менеджером в веб-интерфейсе, отправляются
  пользователю от лица бота через Telegram Bot API.

Redis-сообщения имеют тот же формат payload, что и events channels
``RedisChannelLayer``: ``{"type": "web", "channel": <name>, "data": {...}}``.
Имя канала подчиняется правилу channels: ``group.<md5(name)>``.
"""
import asyncio
import hashlib
import json
import logging
from urllib.parse import urlparse

logger = logging.getLogger(__name__)

BOT_OUTGOING_CHANNEL = "bot_outgoing"


def _decode_channel_name(name: str) -> str:
    """channels RedisChannelLayer: 'group.' + md5hex(group_or_channel_key)."""
    return f"group.{hashlib.md5(name.encode('utf-8')).hexdigest()}"


class ChatBridge:
    def __init__(self, redis_url: str):
        parsed = urlparse(redis_url)
        self._redis_kwargs = {
            "host": parsed.hostname or "redis",
            "port": parsed.port or 6379,
            "db": int((parsed.path or "/0").lstrip("/") or 0),
        }
        if parsed.password:
            self._redis_kwargs["password"] = parsed.password
        self._client = None

    async def _get_client(self):
        if self._client is None:
            import redis.asyncio as aioredis

            self._client = aioredis.Redis(**self._redis_kwargs)
        return self._client

    # ------------------------------------------------------------- incoming
    async def publish_incoming(self, tg_id: int, *, text: str, time_str: str,
                               attachment_kind: str = "", attachment_url: str = "") -> None:
        """Notify all manager tabs watching this lead about a new user message."""
        try:
            client = await self._get_client()
            event = {
                "type": "message",
                "direction": "incoming",
                "text": text,
                "time": time_str,
                "attachment_kind": attachment_kind,
                "attachment_url": attachment_url,
            }
            await client.publish(
                _decode_channel_name(f"chat_{tg_id}"),
                json.dumps({"type": "web", "channel": "this", "data": event}, ensure_ascii=False),
            )
        except Exception:  # noqa: BLE001 - chat bridge must never break the bot
            logger.exception("Failed to publish incoming chat message for tg_id=%s", tg_id)

    # ------------------------------------------------------------- outgoing
    async def listen_outgoing(self, bot, stop: asyncio.Event) -> None:
        """Send messages typed by the manager (via the web UI) through the bot."""
        try:
            client = await self._get_client()
            pubsub = client.pubsub()
            await pubsub.subscribe(_decode_channel_name(BOT_OUTGOING_CHANNEL))
            logger.info("Bot outgoing-chat listener subscribed.")
            while not stop.is_set():
                msg = await pubsub.get_message(ignore_subscribe_messages=True, timeout=1.0)
                if msg is None or msg.get("type") != "message":
                    continue
                try:
                    raw = msg["data"]
                    if isinstance(raw, bytes):
                        raw = raw.decode("utf-8")
                    payload = json.loads(raw)
                    data = payload.get("data", {})
                except (json.JSONDecodeError, TypeError):
                    continue
                if data.get("type") != "bot.send":
                    continue
                tg_id = data.get("tg_id")
                text = data.get("text") or ""
                if not tg_id or not text:
                    continue
                try:
                    await bot.send_message(chat_id=int(tg_id), text=text)
                except Exception:  # noqa: BLE001
                    logger.exception("Failed to forward manager message to tg_id=%s", tg_id)
        except asyncio.CancelledError:
            raise
        except Exception:  # noqa: BLE001
            logger.exception("Outgoing chat listener crashed; will not retry automatically.")


_bridge: ChatBridge | None = None


def get_bridge(redis_url: str) -> ChatBridge:
    global _bridge
    if _bridge is None:
        _bridge = ChatBridge(redis_url)
    return _bridge
