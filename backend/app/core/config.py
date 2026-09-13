"""Lumina V3 core configuration — loaded from environment variables."""

from __future__ import annotations

from functools import lru_cache
from typing import Any

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from .env / environment."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # -- App --
    app_env: str = "development"
    app_debug: bool = False
    app_secret_key: str = "change-me-to-random-64-chars"
    app_host: str = "0.0.0.0"
    app_port: int = 8000
    app_log_level: str = "INFO"
    app_cors_origins: list[str] = ["http://localhost:5173"]

    # -- Database --
    database_url: str = "postgresql+asyncpg://lumina:lumina@localhost:5432/lumina"
    database_echo: bool = False
    database_pool_size: int = 20
    database_max_overflow: int = 10

    # -- Redis --
    redis_url: str = "redis://localhost:6379/0"

    # -- Telegram --
    telegram_bot_token: str = ""
    telegram_webhook_secret: str = ""
    telegram_webhook_url: str = ""
    telegram_mini_app_url: str = ""

    # -- Auth --
    auth_token_expire_minutes: int = 1440  # 24h
    auth_init_data_expire_seconds: int = 300  # 5min

    # -- AI (optional — graceful degradation) --
    openai_api_key: str = ""
    openai_model: str = "gpt-4o-mini"
    whisper_model: str = "whisper-1"

    # -- File storage --
    file_storage_path: str = "./storage/files"
    file_max_size_mb: int = 50

    # -- Workers --
    worker_concurrency: int = 10

    @field_validator("app_cors_origins", mode="before")
    @classmethod
    def parse_cors(cls, v: Any) -> list[str]:
        if isinstance(v, str):
            import json

            try:
                return json.loads(v)
            except json.JSONDecodeError:
                return [s.strip() for s in v.split(",")]
        return v

    @property
    def is_production(self) -> bool:
        return self.app_env == "production"

    @property
    def sync_database_url(self) -> str:
        return self.database_url.replace("+asyncpg", "+psycopg2")


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()
