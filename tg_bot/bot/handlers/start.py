"""Welcome / start handlers."""
import logging

from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from bot.database import has_filled_request, upsert_lead_on_start
from bot.db_utils import run_sync
from bot.i18n import t
from bot.keyboards import existing_kb, start_kb

logger = logging.getLogger(__name__)

router = Router()


@router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext) -> None:
    """Greet the user and immediately register their tg_id as a 'visitor' lead.

    Then check whether the user already has a filled request in the DB:
      * no record, or status == 'visitor' -> welcome + 'Fill in the request'
      * any other status                  -> 'View request' button instead
    """
    tg_id = message.from_user.id
    try:
        await run_sync(upsert_lead_on_start, tg_id)
        already_filled = await run_sync(has_filled_request, tg_id)
    except Exception:  # noqa: BLE001
        logger.exception("Failed to upsert lead on /start")
        already_filled = False

    await state.clear()
    if already_filled:
        await message.answer(t("welcome_existing"), reply_markup=existing_kb())
    else:
        await message.answer(t("welcome"), reply_markup=start_kb())
