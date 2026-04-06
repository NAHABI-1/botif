from __future__ import annotations

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    database_url: str = Field(
        default="postgresql+psycopg://localhost:5432/mt5_platform",
        validation_alias="MT5_DB_URL",
    )
    database_schema: str = Field(default="trading", validation_alias="MT5_DB_SCHEMA")
    database_echo: bool = Field(default=False, validation_alias="MT5_DB_ECHO")


settings = Settings()
