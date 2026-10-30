import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.redis import RedisStorage

from bot.config import Config
from bot.handlers import register_routers

logger = logging.getLogger(__name__)


async def main() -> None:
    logging.basicConfig(level=logging.INFO)

    config = Config.from_env()  # also applies BOT_LANGUAGE translations
    if not config.bot_token or config.bot_token == "put-your-bot-token-here":
        logger.error("TELEGRAM_BOT_TOKEN is not set. Put the token into .env")
        raise SystemExit(1)

    bot = Bot(token=config.bot_token, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    storage = RedisStorage(redis=config.redis_url)
    dp = Dispatcher(storage=storage)
    register_routers(dp)

    logger.info("Starting polling...")
    try:
        await dp.start_polling(bot)
    finally:
        await bot.session.close()


if __name__ == "__main__":
    asyncio.run(main())
