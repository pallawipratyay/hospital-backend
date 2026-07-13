from __future__ import annotations

from typing import List

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict





class Settings(BaseSettings):
    app_name: str = "Hospital Management API"
    debug: bool = False
    environment: str = "development"

    # Can be either:
    # - path to service account JSON file
    # - inline JSON string starting with '{'
    firebase_credentials_path: str = Field(
        default="",
        validation_alias="FIREBASE_CREDENTIALS_PATH",
    )



    cors_origins: List[str] = Field(default_factory=lambda: ["*"], env="CORS_ORIGINS")

    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore",
    )

    @property
    def firebase_credentials_path(self) -> str:  # type: ignore[override]
        val = self.__dict__.get("firebase_credentials_path", "")
        return "" if val == "{" else val







settings = Settings()


