"""Application configuration loaded from environment variables."""

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # ── Database ──────────────────────────────────────────────
    DATABASE_URL: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/restapi_db"

    # ── JWT ───────────────────────────────────────────────────
    SECRET_KEY: str = "change-me-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 15
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # ── CORS ──────────────────────────────────────────────────
    CORS_ORIGINS: list[str] = ["http://localhost:3000", "http://localhost:8000"]

    # ── App ───────────────────────────────────────────────────
    APP_NAME: str = "REST API"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False

    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "case_sensitive": True,
    }


settings = Settings()
