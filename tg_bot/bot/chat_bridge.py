"""Redis pub/sub bridge: Telegram user <-> web operator chat.

Two flows, both keyed by the user's tg_id:

* incoming  — every message from a user is stored in the DB (ChatMessage)
  and published to the ``bot:incoming`` channel for the live web feed;
* outgoing  — the listener below subscribes to ``bot:outgoing:<tg_id>``
  channels (pattern subscription), receives operator replies published by the
  Django web UI and sends them to the user on Telegram.

Reliability notes
-----------------
* The subscriber blocks with a short timeout and treats a timeout as "idle",
  never as an error — previously an idle ``Timeout reading from redis`` was
  caught as a fatal listener error and caused an endless resubscribe loop.
* Reconnects use capped exponential backoff instead of a tight 1 s loop.
* Because pub/sub messages are lost while the bot is offline, periodically
  (and after each reconnect) the bot catches up on undelivered operator
  replies directly from PostgreSQL ("last delivered" timestamp kept in Redis).
"""
import asyncio
import json
import logging
import os
from datetime import datetime, timezone

import redis.asyncio as aioredis
from aiogram import BaseMiddleware, Bot
from aiogram.types import Message

logger = logging.getLogger(__name__)

BRIDGE_DB_URL = os.getenv("BRIDGE_REDIS_URL", "redis://redis:6379/2")
OUTGOING_PATTERN = "bot:outgoing:*"
INCOMING_CHANNEL = "bot:incoming"
LAST_DELIVERED_KEY = "bot:last_delivered:{tg_id}"

PUBSUB_TIMEOUT = 5.0        # seconds per get_message() block (idle check period)
RECONNECT_DELAY_MAX = 30.0


class ChatBridge:
    """Owns the Redis connection, subscriptions and Telegram delivery."""

    def __init__(self, bot: Bot):
        self.bot = bot
        self._redis: aioredis.Redis | None = None
        self._task: asyncio.Task | None = None
        self._stop = asyncio.Event()

    # ------------------------------------------------------------ lifecycle

    async def start(self) -> None:
        self._redis = aioredis.from_url(
            BRIDGE_DB_URL, decode_responses=True, socket_keepalive=True
        )
        self._task = asyncio.create_task(self._listen_outgoing(), name="bridge-outgoing")
        logger.info("Chat bridge started (pattern '%s').", OUTGOING_PATTERN)

    async def stop(self) -> None:
        self._stop.set()
        if self._task is not None:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass
            self._task = None
        if self._redis is not None:
            await self._redis.aclose()
            self._redis = None

    # ------------------------------------------------------------ outgoing

    async def _listen_outgoing(self) -> None:
        """Subscribe with reconnect/backoff; catch up from DB when idle/offline."""
        delay = 1.0
        while not self._stop.is_set():
            pubsub = None
            try:
                pubsub = self._redis.pubsub(ignore_subscribe_messages=True)
                await pubsub.psubscribe(OUTGOING_PATTERN)
                logger.info("Outgoing-chat listener subscribed (pattern '%s').", OUTGOING_PATTERN)
                delay = 1.0  # reset backoff after a successful subscribe
                await self._pump(pubsub)
            except asyncio.CancelledError:
                raise
            except Exception as exc:  # noqa: BLE001
                logger.warning("Outgoing chat listener error (%s); retrying in %.0fs.", exc, delay)
                try:
                    await asyncio.wait_for(self._stop.wait(), timeout=delay)
                    break  # stopped while waiting
                except (asyncio.TimeoutError, TimeoutError):
                    pass
                delay = min(delay * 2, RECONNECT_DELAY_MAX)
            finally:
                if pubsub is not None:
                    try:
                        await pubsub.unsubscribe(OUTGOING_PATTERN)
                        await pubsub.aclose()
                    except Exception:  # noqa: BLE001
                        pass

    async def _pump(self, pubsub) -> None:
        """Read pub/sub messages; a read timeout just means 'idle', not an error."""
        while not self._stop.is_set():
            msg = await pubsub.get_message(timeout=PUBSUB_TIMEOUT)
            if msg is None:
                # Idle window (this is where the old code raised/logged a bogus
                # "Timeout reading from redis"). Do a cheap DB catch-up instead.
                await self._catch_up()
                continue
            if msg.get("type") not in ("pmessage", "message"):
                continue
            payload = self._decode(msg.get("data"))
            if payload is None:  # malformed / heartbeat — ignore silently
                continue
            await self._deliver(payload)

    @staticmethod
    def _decode(raw):
        if isinstance(raw, bytes):
            raw = raw.decode("utf-8", "replace")
        try:
            payload = json.loads(raw)
        except (TypeError, ValueError):
            return None
        if not isinstance(payload, dict) or payload.get("type") != "message":
            return None
        return payload

    async def _deliver(self, payload: dict) -> None:
        tg_id = int(payload["tg_id"])
        text = payload.get("text") or ""
        media_path = payload.get("media_path") or ""
        if not text and not media_path:
            return
        try:
            if media_path:
                await self._send_media(tg_id, media_path, text)
            else:
                await self.bot.send_message(tg_id, text)
            logger.info("Delivered operator message to tg_id=%s", tg_id)
            # Remember where this user's queue ended (for post-restart catch-up).
            now_iso = datetime.now(timezone.utc).isoformat()
            await self._redis.set(LAST_DELIVERED_KEY.format(tg_id=tg_id), now_iso)
        except Exception:  # noqa: BLE001
            logger.exception("Failed to deliver operator message to tg_id=%s", tg_id)

    async def _send_media(self, tg_id: int, rel_path: str, caption: str) -> None:
        from pathlib import Path

        media_dir = os.getenv("BOT_MEDIA_DIR", "/media")
        path = Path(media_dir) / rel_path
        if not path.exists():
            await self.bot.send_message(tg_id, f"📎 {rel_path}\n{caption}".strip())
            return
        suffix = path.suffix.lower()
        if suffix in (".jpg", ".jpeg", ".png", ".webp", ".gif"):
            await self.bot.send_photo(tg_id, str(path), caption=caption or None)
        elif suffix in (".mp4", ".mov"):
            await self.bot.send_video(tg_id, str(path), caption=caption or None)
        else:
            await self.bot.send_document(tg_id, str(path), caption=caption or None)

    # ------------------------------------------------------------- incoming

    async def publish_incoming(self, *, tg_id: int, text: str = "", media_path: str = "") -> None:
        """Push a user message into the live web-feed channel (best effort)."""
        if self._redis is None:
            return
        payload = json.dumps(
            {"type": "message", "tg_id": tg_id, "text": text, "media_path": media_path},
            ensure_ascii=False,
        )
        try:
            await self._redis.publish(INCOMING_CHANNEL, payload)
        except Exception:  # noqa: BLE001 - DB is the source of truth, feed is optional
            logger.exception("Failed to publish incoming message to the web feed")

    # ------------------------------------------------------------ catch-up

    async def _catch_up(self) -> None:
        """Safety net: fetch operator replies that arrived while disconnected."""
        from bot.database import get_outgoing_messages
        from bot.db_utils import run_sync

        pattern = LAST_DELIVERED_KEY.format(tg_id="")
        try:
            tg_ids = []
            async for key in self._redis.scan_iter(match=pattern + "*", count=200):
                try:
                    tg_ids.append(int(str(key).removeprefix(pattern)))
                except ValueError:
                    continue
        except Exception:  # noqa: BLE001
            return
        for tg_id in tg_ids:
            last = await self._redis.get(LAST_DELIVERED_KEY.format(tg_id=tg_id))
            try:
                rows = await run_sync(get_outgoing_messages, tg_id, last, 20)
            except Exception:  # noqa: BLE001
                logger.exception("Catch-up query failed for tg_id=%s", tg_id)
                continue
            for row in rows:
                await self._deliver({"type": "message", "tg_id": tg_id,
                                     "text": row["text"], "media_path": row["media_path"]})


# ------------------------------------------------------------------ dispatcher glue

_bridge: ChatBridge | None = None  # set via bind_bridge() from __main__


def bind_bridge(bridge: ChatBridge) -> None:
    global _bridge
    _bridge = bridge


def register_chat_saving(dispatcher) -> None:
    """Record every incoming Telegram message in the DB + live feed."""

    class _ChatSaver(BaseMiddleware):
        async def __call__(self, handler, event: dict, data: dict):
            update = event.get("update")
            message = getattr(update, "message", None) or getattr(update, "edited_message", None)
            if message is not None and getattr(message, "from_user", None) is not None:
                await _save_incoming(message)
            return await handler(event, data)

    dispatcher.update.outer_middleware.register(_ChatSaver())


async def _save_incoming(message: Message) -> None:
    from bot.database import save_incoming_message
    from bot.db_utils import run_sync

    text = message.text or message.caption or ""
    try:
        await run_sync(save_incoming_message, tg_id=message.from_user.id, text=text)
    except Exception:  # noqa: BLE001
        logger.exception("Failed to store incoming chat message")
    if _bridge is not None:
        await _bridge.publish_incoming(tg_id=message.from_user.id, text=text)

