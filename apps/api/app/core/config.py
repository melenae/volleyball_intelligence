from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Environment-backed settings.

    Domain models are intentionally absent in Phase 1. Database URL is used
    only to check that PostgreSQL accepts a connection.
    """

    app_env: str = "development"
    database_url: str = "postgresql+psycopg://vi:vi@localhost:5433/volleyball_intelligence"
    cors_origins: str = "http://localhost:3000"

    model_config = SettingsConfigDict(
        env_file=(".env", "../../.env"),
        env_file_encoding="utf-8",
        extra="ignore",
    )

    @property
    def cors_origin_list(self) -> list[str]:
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()
