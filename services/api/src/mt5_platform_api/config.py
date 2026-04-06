from __future__ import annotations

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class ApiSettings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")
    app_name: str = "MT5 Platform API"
    app_version: str = "0.1.0"
    api_prefix: str = "/api/v1"
    expose_openapi: bool = True
    log_level: str = "INFO"
    auth_session_ttl_minutes: int = Field(default=720, ge=5)


settings = ApiSettings()
