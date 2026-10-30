import asyncio
import json
import logging

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.fsm.storage.redis import RedisStorage
from redis.asyncio import Redis

from bot.chat_bridge import get_bridge
from bot.config import Config
from bot.handlers import register_routers

logger = logging.getLogger(__name__)


def _fsm_dumps(obj):
    """JSON encoder for FSM data: datetime.date/time are not JSON serializable."""
    return json.dumps(obj, default=str)


async def main() -> None:
    logging.basicConfig(level=logging.INFO)

    config = Config.from_env()
    if not config.bot_token or config.bot_token == "put-your-bot-token-here":
        logger.error("TELEGRAM_BOT_TOKEN is not set. Put the token into .env")
        raise SystemExit(1)

    bot = Bot(token=config.bot_token, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    # RedisStorage requires an actual Redis client instance — passing the URL
    # string breaks at first update ("'str' object has no attribute 'get'").
    redis_client: Redis | None = None
    try:
        redis_client = Redis.from_url(config.redis_url)
        await redis_client.ping()
        storage: MemoryStorage | RedisStorage = RedisStorage(
            redis=redis_client, json_dumps=_fsm_dumps
        )
        logger.info("FSM storage: Redis (%s)", config.redis_url)
    except Exception as exc:  # noqa: BLE001
        if redis_client is not None:
            await redis_client.aclose()
            redis_client = None
        storage = MemoryStorage()
        logger.warning("Redis unavailable (%s); falling back to in-memory FSM storage.", exc)
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
