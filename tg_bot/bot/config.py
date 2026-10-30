"""Bot configuration (environment variables from docker-compose)."""
import os


class Config:
    def __init__(self, bot_token: str, redis_url: str):
        self.bot_token = bot_token
        self.redis_url = redis_url

    @classmethod
    def from_env(cls) -> "Config":
        return cls(
            bot_token=os.getenv("TELEGRAM_BOT_TOKEN", ""),
            redis_url=os.getenv("REDIS_URL", "redis://redis:6379/0"),
        )
