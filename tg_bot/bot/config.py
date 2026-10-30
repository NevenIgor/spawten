"""Bot configuration (environment variables from docker-compose)."""
import os

from bot.translations import set_language


class Config:
    def __init__(self, bot_token: str, redis_url: str, language: str):
        self.bot_token = bot_token
        self.redis_url = redis_url
        self.language = language

    @classmethod
    def from_env(cls) -> "Config":
        language = os.getenv("BOT_LANGUAGE", "ru")
        set_language(language)  # apply translations before anything else
        return cls(
            bot_token=os.getenv("TELEGRAM_BOT_TOKEN", ""),
            redis_url=os.getenv("REDIS_URL", "redis://redis:6379/0"),
            language=language,
        )
