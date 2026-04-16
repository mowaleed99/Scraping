from __future__ import annotations

from functools import lru_cache
from typing import Literal

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # ── Environment ──────────────────────────────────────────────────────────
    environment: Literal["development", "production"] = "development"
    log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR"] = "INFO"
    api_secret_key: str = "change-me-in-production"

    # ── Database ─────────────────────────────────────────────────────────────
    # Runtime (pooled — lower latency for app queries)
    database_pool_url: str = Field(..., alias="DATABASE_POOL_URL")
    # Migrations (direct — Alembic needs a non-pooled connection)
    database_url: str = Field(..., alias="DATABASE_URL")

    # SQLAlchemy pool settings (tuned for Neon serverless)
    db_pool_size: int = 5
    db_max_overflow: int = 10
    db_pool_timeout: int = 30
    db_pool_recycle: int = 1800  # recycle connections every 30 min

    # ── API Keys & Models ────────────────────────────────────────────────────
    gemini_api_key: str = Field(..., alias="GEMINI_API_KEY")
    groq_api_key: str = Field(..., alias="GROQ_API_KEY")
    llm_model: str = "llama-3.1-8b-instant"
    llm_embed_model: str = "gemini-embedding-exp-03-07"
    llm_max_tokens: int = 1024
    llm_temperature: float = 0.0

    # ── Scraping ─────────────────────────────────────────────────────────────
    apify_api_token: str = Field(..., alias="APIFY_API_TOKEN")
    brightdata_api_key: str = ""
    scrape_overlap_hours: int = 1

    # ── Processing ───────────────────────────────────────────────────────────
    batch_size: int = 20
    max_retries: int = 3

    # ── Derived helpers ──────────────────────────────────────────────────────
    @property
    def is_production(self) -> bool:
        return self.environment == "production"

    @field_validator("llm_temperature")
    @classmethod
    def clamp_temperature(cls, v: float) -> float:
        return max(0.0, min(1.0, v))


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Return a cached singleton Settings instance."""
    return Settings()  # type: ignore[call-arg]
