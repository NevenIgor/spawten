"""Welcome / start handlers."""
import logging

from aiogram import F, Router
from aiogram.filters import CommandStart, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from bot.chat_bridge import get_bridge
from bot.config import Config
from bot.database import (has_filled_request, save_incoming_message,
                          upsert_lead_on_start, upsert_telegram_profile)
from bot.db_utils import run_sync
from bot.keyboards import existing_kb, start_kb
from bot.texts import WELCOME, WELCOME_EXISTING, text

logger = logging.getLogger(__name__)

router = Router()


async def publish_to_manager_chat(message: Message, *, body: str | None = None,
                                  attachment_kind: str = "",
                                  attachment_url: str = "") -> None:
    """Persist the user's message as a chat log entry and push it to the
    manager web UI in real time (Redis channel consumed by the WS client)."""
    if message.from_user is None:
        return
    tg_id = message.from_user.id
    text_body = message.text or "" if body is None else body
    try:
        msg = await run_sync(
            save_incoming_message, tg_id, text_body,
            attachment_kind=attachment_kind, attachment_url=attachment_url,
            tg_message_id=message.message_id,
        )
        await get_bridge(Config.from_env().redis_url).publish_incoming(
            tg_id,
            msg_id=str(msg.pk),
            text=text_body,
            time_str=msg.created.strftime("%d.%m.%Y %H:%M:%S"),
            attachment_kind=attachment_kind,
            attachment_url=attachment_url,
        )
    except Exception:  # noqa: BLE001 - chat mirroring must never break handling
        logger.exception("Failed to mirror message into manager chat")


@router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext) -> None:
    """Greet the user and immediately register their tg_id as a 'visitor' lead.

    Then check whether the user already has a filled request in the DB:
      * no record, or status == 'visitor' -> welcome + 'Fill in the request'
      * any other status                  -> 'View request' button instead
    """
    tg_id = message.from_user.id
    try:
        await run_sync(upsert_lead_on_start, tg_id, message.from_user)
        already_filled = await run_sync(has_filled_request, tg_id)
    except Exception:  # noqa: BLE001
        logger.exception("Failed to upsert lead on /start")
        already_filled = False

    await state.clear()
    if already_filled:
        await message.answer(text(WELCOME_EXISTING), reply_markup=existing_kb())
    else:
        await message.answer(text(WELCOME), reply_markup=start_kb())


# ------------------------------------------------------------------ chat mirroring
# Any message outside the form FSM (state=None) is mirrored into the live chat
# of the manager web UI. The form router runs first and owns all FSM states,
# so form answers never end up duplicated here.

@router.message(StateFilter(None), F.text & ~F.text.startswith("/"))
async def mirror_plain_text(message: Message) -> None:
    await publish_to_manager_chat(message)


@router.message(F.contact)
async def mirror_contact(message: Message) -> None:
    """Shared contact: store the phone behind the account + mirror to chat."""
    if message.from_user is not None and message.contact:
        try:
            await run_sync(upsert_telegram_profile, message.from_user,
                           phone=message.contact.phone_number or "")
        except Exception:  # noqa: BLE001
            logger.exception("Failed to store shared contact phone")
    await publish_to_manager_chat(
        message,
        body=(f"📞 {message.contact.phone_number}" if message.contact else ""),
        attachment_kind="contact",
        attachment_url=(message.contact.phone_number if message.contact else ""),
    )


@router.message(F.location)
async def mirror_location(message: Message) -> None:
    """Shared geolocation: store it in the Telegram profile + mirror to chat."""
    loc = ""
    if message.location is not None:
        loc = f"{message.location.latitude:.5f}, {message.location.longitude:.5f}"
        if message.from_user is not None:
            try:
                await run_sync(upsert_telegram_profile, message.from_user, location=loc)
            except Exception:  # noqa: BLE001
                logger.exception("Failed to store shared location")
    await publish_to_manager_chat(
        message, body=f"📍 {loc}", attachment_kind="location", attachment_url=loc
    )

