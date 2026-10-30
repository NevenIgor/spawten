from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.types import Message

router = Router()


@router.message(CommandStart())
async def cmd_start(message: Message) -> None:
    await message.answer(f"Привет, {message.from_user.full_name}! Я работаю 🤖")


@router.message()
async def echo(message: Message) -> None:
    if message.text:
        await message.answer(f"Вы написали: {message.text}")
