"""Redis pub/sub bridge between the Telegram bot and the web interface.

Shared by both containers (tg_bot mounts /app/api on PYTHONPATH), so the
channel names and payload format are defined in exactly one place.

Channels
--------
bot:outgoing:<tg_id>   operator reply from the web UI -> bot sends it to Telegram
bot:incoming           any message from a Telegram user -> web UI live feed

Payload is JSON with a "type" field ("message" or "ping"). The periodic
"ping" keeps the subscriber's read timeout from firing while idle — without
it aiogram-style listeners wake up every ``timeout`` seconds and log spurious
"Timeout reading from redis" warnings.
"""
import json
import os

OUTGOING_CHANNEL_PREFIX = "bot:outgoing:"
INCOMING_CHANNEL = "bot:incoming"


def outgoing_channel(tg_id: int | str) -> str:
    return f"{OUTGOING_CHANNEL_PREFIX}{tg_id}"


def get_redis_url() -> str:
    """Redis connection string (db 2 is reserved for the chat bridge)."""
    return os.getenv("BRIDGE_REDIS_URL", "redis://redis:6379/2")


def encode_message(*, tg_id: int, text: str = "", media_path: str = "") -> str:
    return json.dumps(
        {"type": "message", "tg_id": int(tg_id), "text": text, "media_path": media_path},
        ensure_ascii=False,
    )


def decode_message(raw) -> dict | None:
    """Return the parsed payload dict, or None for pings / malformed data."""
    if isinstance(raw, bytes):
        raw = raw.decode("utf-8", "replace")
    try:
        payload = json.loads(raw)
    except (TypeError, ValueError):
        return None
    if not isinstance(payload, dict) or payload.get("type") != "message":
        return None
    return payload
