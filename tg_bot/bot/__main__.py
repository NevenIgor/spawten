import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.redis import RedisStorage

from bot.chat_bridge import get_bridge
from bot.config import Config
from bot.handlers import register_routers

logger = logging.getLogger(__name__)


async def main() -> None:
    logging.basicConfig(level=logging.INFO)

    config = Config.from_env()
    if not config.bot_token or config.bot_token == "put-your-bot-token-here":
        logger.error("TELEGRAM_BOT_TOKEN is not set. Put the token into .env")
        raise SystemExit(1)

    bot = Bot(token=config.bot_token, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    storage = RedisStorage(redis=config.redis_url)
    dp = Dispatcher(storage=storage)
    register_routers(dp)

    # live chat bridge: manager messages typed in the web UI -> Telegram user
    stop = asyncio.Event()
    listener = asyncio.create_task(get_bridge(config.redis_url).listen_outgoing(bot, stop))

    logger.info("Starting polling...")
    try:
        await dp.start_polling(bot)
    finally:
        stop.set()
        listener.cancel()
        await bot.session.close()


if __name__ == "__main__":
    asyncio.run(main())
