"""Application configuration loaded from environment variables / .env."""
from __future__ import annotations

from functools import lru_cache

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Strongly-typed settings sourced from environment variables."""

    # Telegram
    bot_token: str
    admin_ids: list[int] = []

    # PostgreSQL
    postgres_host: str = "db"
    postgres_port: int = 5432
    postgres_user: str = "store"
    postgres_password: str = "store_password"
    postgres_db: str = "store_bot"

    # Store settings
    currency: str = "₽"
    low_stock_threshold: int = 5
    referral_bonus: int = 50

    # Misc
    log_level: str = "INFO"
    seed_demo_data: bool = True

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=False,
    )

    @field_validator("admin_ids", mode="before")
    @classmethod
    def _parse_admin_ids(cls, value: object) -> object:
        """Allow ADMIN_IDS to be given as \"1,2 3\" or a JSON-style list."""
        if value is None or value == "":
            return []
        if isinstance(value, str):
            cleaned = value.replace(",", " ").replace(";", " ")
            return [int(part) for part in cleaned.split() if part.strip()]
        return value

    @property
    def database_url(self) -> str:
        """Async SQLAlchemy URL (asyncpg driver)."""
        return (
            f"postgresql+asyncpg://{self.postgres_user}:{self.postgres_password}"
            f"@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"
        )

    def is_admin(self, telegram_id: int) -> bool:
        return telegram_id in self.admin_ids


@lru_cache
def get_settings() -> Settings:
    return Settings()  # type: ignore[call-arg]


settings = get_settings()
