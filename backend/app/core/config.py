"""
Central application configuration.

All settings are loaded from environment variables (or a .env file locally).
Never hardcode secrets — this file only defines shape + safe defaults for
non-sensitive values.
"""
from functools import lru_cache
from typing import List

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    # App
    APP_NAME: str = "AI Analytics Copilot"
    ENVIRONMENT: str = "development"  # development | staging | production
    API_V1_PREFIX: str = "/api/v1"

    # Security
    JWT_SECRET_KEY: str
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 24h
    REFRESH_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7d

    # Database
    DATABASE_URL: str  # postgresql+psycopg://user:pass@host/db

    # CORS
    CORS_ORIGINS: List[str] = ["http://localhost:3000"]

    # File storage
    UPLOAD_DIR: str = "storage/uploads"
    MAX_UPLOAD_SIZE_MB: int = 50

    # LLM provider
    LLM_PROVIDER: str = "gemini"  # gemini | openai (pluggable)
    GEMINI_API_KEY: str = ""
    GEMINI_MODEL: str = "gemini-2.0-flash"

    @property
    def is_production(self) -> bool:
        return self.ENVIRONMENT == "production"


@lru_cache
def get_settings() -> Settings:
    """Cached settings instance — avoids re-parsing env on every import."""
    return Settings()


settings = get_settings()