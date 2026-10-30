"""Конфигурация бота (переменные окружения из docker-compose)."""
from pydantic_settings import BaseSettings


class Config(BaseSettings):
    bot_token: str = "put-your-bot-token-here"
    redis_url: str = "redis://redis:6379/0"

    class ConfigDictMeta:
        env_prefix = ""

    @classmethod
    def from_env(cls) -> "Config":
        import os

        return cls(
            bot_token=os.getenv("TELEGRAM_BOT_TOKEN", cls.model_fields["bot_token"].default),
            redis_url=os.getenv("REDIS_URL", cls.model_fields["redis_url"].default),
        )
