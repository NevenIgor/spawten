"""Welcome / start handlers."""
import logging

from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from bot.database import upsert_lead_on_start
from bot.db_utils import run_sync
from bot.keyboards import start_kb
from bot.texts import WELCOME

logger = logging.getLogger(__name__)

router = Router()


@router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext) -> None:
    """Greet the user and immediately register their tg_id as a 'visitor' lead."""
    try:
        await run_sync(upsert_lead_on_start, message.from_user.id)
    except Exception:  # noqa: BLE001
        logger.exception("Failed to upsert lead on /start")

    await state.clear()
    await message.answer(
        WELCOME,
        reply_markup=start_kb(),
    )
