"""Router registration for the bot."""
from aiogram import Dispatcher

from bot.handlers.form import router as form_router
from bot.handlers.start import router as start_router


def register_routers(dp: Dispatcher) -> None:
    # form first: it owns all FSM states; start handles /start in no-state
    dp.include_router(form_router)
    dp.include_router(start_router)
