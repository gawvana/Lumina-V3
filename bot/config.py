from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    BOT_TOKEN: str
    API_BASE_URL: str
    REDIS_URL: str
    WEBHOOK_URL: str | None = None
    WEBHOOK_SECRET: str | None = None
    MINI_APP_URL: str

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

config = Settings()
