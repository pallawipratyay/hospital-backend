from __future__ import annotations

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Hospital Management API"
    debug: bool = False
    environment: str = "development"

    firebase_credentials_path: str = Field(..., env="FIREBASE_CREDENTIALS_PATH")
    cors_origins: list[str] = ["*"]

    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore",
        case_sensitive=True,
    )


settings = Settings()

