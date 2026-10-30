"""Real-time bridge between the bot and the manager web UI chat.

* ``publish_incoming`` — вызывается из хендлеров бота: каждое сообщение
  пользователя сохраняется в БД (``ChatMessage``) и публикуется в Redis-группу
  ``chat_<tg_id>``, куда подписан WebSocket менеджера (channels).
* ``listen_outgoing`` — asyncio-задача, слушающая группу ``bot_outgoing``:
  сообщения, написанные менеджером в веб-интерфейсе, отправляются
  пользователю от лица бота через Telegram Bot API.

Ранее мост ходил «в обход» channels: публиковал JSON в сырой pub/sub-канал
``group.<md5(...)>`` и слушал его же. Это не работало по двум причинам:

1. ``RedisChannelLayer.group_send`` вообще не использует Redis pub/sub — он
   кладёт сериализованное (msgpack по умолчанию) сообщение в sorted-set
   ``asgi:<имя канала>`` каждого участника группы, а consumer забирает его
   через ``BRPOP``. Сырой ``PUBLISH`` в ``group.<md5>`` никто не читал, а
   JSON-payload не совпадал с msgpack-форматом channels.
2. Подписка шла на имя ``group.<md5>("bot_outgoing")``, тогда как channels
   вычисляет ключ группы как MD5 от строки ``"group:group:bot_outgoing"`` —
   даже при pub/sub имена никогда не совпадали.

Теперь бот использует сам ``channels_redis.core.RedisChannelLayer`` — формат,
ключи и сериализация гарантированно совпадают с серверной частью (daphne).
"""
import asyncio
import logging
from urllib.parse import urlparse

logger = logging.getLogger(__name__)

BOT_OUTGOING_CHANNEL = "bot_outgoing"


def _layer_kwargs(redis_url: str) -> dict:
    """Параметры RedisChannelLayer из REDIS_URL (в т.ч. номер db, который
    channels-redis сам по URL не разбирает)."""
    parsed = urlparse(redis_url)
    kwargs = {
        "host": parsed.hostname or "redis",
        "port": parsed.port or 6379,
        "db": int((parsed.path or "/0").lstrip("/") or 0),
    }
    if parsed.password:
        kwargs["password"] = parsed.password
    return {"hosts": [kwargs]}


class ChatBridge:
    def __init__(self, redis_url: str):
        self._redis_kwargs = _layer_kwargs(redis_url)
        self._layer = None
        self._recv_layer = None

    async def _get_layer(self):
        """RedisChannelLayer для редких исходящих публикаций (долгоживущий).

        Долгоживущий singleton переживает кратковременные сбои/перезапуски
        Redis, после чего его пул соединений остаётся «мёртвым» и
        ``group_send`` молча падал в исключение — сообщения пользователя
        переставали долетать до веб-чата. Поэтому перед публикацией
        выполняем дешёвый PING: если он не прошёл — пересоздаём слой.
        """
        from channels_redis.core import RedisChannelLayer

        if self._layer is None:
            self._layer = RedisChannelLayer(**self._redis_kwargs)
            return self._layer
        try:
            conn = self._layer.to_redis[0]
            await asyncio.wait_for(conn.ping(), timeout=2)
        except Exception:  # noqa: BLE001 - dead pool after a Redis outage
            old = self._layer
            self._layer = RedisChannelLayer(**self._redis_kwargs)
            try:
                await old.close()
            except Exception:  # noqa: BLE001 - best effort cleanup
                pass
        return self._layer

    async def _get_recv_layer(self):
        """Долгоживущий слой для слушателя ``listen_outgoing``.

        Его нельзя пересоздавать на каждый цикл: подписка группы
        ``bot_outgoing`` привязана к каналу конкретного слоя, и новый слой
        терял бы накопленные в Redis сообщения между reconnect'ами.
        Но после сбоя Redis пул «умирает» — поэтому перед (пере)подпиской
        проверяем соединение дешёвым PING и при неудаче заменяем слой
        свежим, закрывая старый.
        """
        from channels_redis.core import RedisChannelLayer

        if self._recv_layer is not None:
            try:
                conn = self._recv_layer.to_redis[0]
                await asyncio.wait_for(conn.ping(), timeout=2)
                return self._recv_layer
            except Exception:  # noqa: BLE001 - dead pool after a Redis outage
                old = self._recv_layer
        else:
            old = None
        self._recv_layer = RedisChannelLayer(**self._redis_kwargs)
        if old is not None:
            try:
                await old.close()
            except Exception:  # noqa: BLE001 - best effort cleanup
                pass
        return self._recv_layer

    # ------------------------------------------------------------- incoming
    async def publish_incoming(self, tg_id: int, *, msg_id: str = "", text: str,
                               time_str: str, attachment_kind: str = "",
                               attachment_url: str = "") -> None:
        """Notify all manager tabs watching this lead about a new user message."""
        try:
            layer = await self._get_layer()
            event = {
                "type": "message",
                "direction": "incoming",
                "text": text,
                "time": time_str,
                "sent_by": "",
                "attachment_kind": attachment_kind,
                "attachment_url": attachment_url,
            }
            if msg_id:
                event["id"] = msg_id
            await layer.group_send(
                f"chat_{tg_id}", {"type": "chat.event", "event": event}
            )
        except Exception:  # noqa: BLE001 - chat bridge must never break the bot
            logger.exception("Failed to publish incoming chat message for tg_id=%s", tg_id)

    # ------------------------------------------------------------- outgoing
    async def listen_outgoing(self, bot, stop: asyncio.Event) -> None:
        """Send messages typed by the manager (via the web UI) through the bot.

        Читает собственным каналом channels-слоя (``receive``): consumer'ы
        менеджеров и бот — независимые получатели одной группы bot_outgoing.
        Цикл устойчив к ошибкам Redis (reconnect с экспоненциальной паузой).
        """
        backoff = 1.0
        while not stop.is_set():
            try:
                layer = await self._get_layer()
                channel = await layer.new_channel(BOT_OUTGOING_CHANNEL)
                await layer.group_add(BOT_OUTGOING_CHANNEL, channel)
                logger.info("Bot outgoing-chat listener subscribed (%s).", channel)
                backoff = 1.0
                while not stop.is_set():
                    payload = await layer.receive(channel)
                    if payload is None:
                        continue
                    if payload.get("type") != "bot.send":
                        continue  # e.g. "bot.typing" — пока не используем
                    tg_id = payload.get("tg_id")
                    text = payload.get("text") or ""
                    if not tg_id or not text:
                        continue
                    try:
                        await bot.send_message(chat_id=int(tg_id), text=text)
                    except Exception:  # noqa: BLE001
                        logger.exception("Failed to forward manager message to tg_id=%s", tg_id)
                await layer.group_discard(BOT_OUTGOING_CHANNEL, channel)
            except asyncio.CancelledError:
                raise
            except Exception as exc:  # noqa: BLE001 - Redis hiccup: reconnect
                logger.warning("Outgoing chat listener error (%s); retrying in %.0fs.",
                               exc, backoff)
                try:
                    await asyncio.wait_for(stop.wait(), timeout=backoff)
                except asyncio.TimeoutError:
                    pass
                backoff = min(backoff * 2, 30.0)


_bridge: ChatBridge | None = None


def get_bridge(redis_url: str) -> ChatBridge:
    global _bridge
    if _bridge is None:
        _bridge = ChatBridge(redis_url)
    return _bridge
