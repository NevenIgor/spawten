"""Welcome / start handlers.

On /start the bot checks whether a lead with this tg_id exists in the DB:
  - no record, or status 'visitor' -> welcome text + "Fill in the data" button;
  - any other status               -> "View request" button instead.
"""
import logging

from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from bot.database import VISITOR_STATUS_NAME, get_lead_status_name, upsert_lead_on_start
from bot.db_utils import run_sync
from bot.keyboards import start_kb, view_request_kb
from bot.texts import WELCOME, WELCOME_SEEN

logger = logging.getLogger(__name__)

router = Router()


@router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext) -> None:
    """Greet the user and offer either to fill in the form or view the request."""
    status_name: str | None = None
    try:
        status_name = await run_sync(get_lead_status_name, message.from_user.id)
        # New users are registered immediately as 'visitor'.
        if status_name is None:
            await run_sync(upsert_lead_on_start, message.from_user.id)
            status_name = VISITOR_STATUS_NAME
    except Exception:  # noqa: BLE001
        logger.exception("Failed to check/create lead on /start")

    await state.clear()

    if status_name is not None and status_name != VISITOR_STATUS_NAME:
        await message.answer(WELCOME_SEEN, reply_markup=view_request_kb())
    else:
        await message.answer(WELCOME, reply_markup=start_kb())
