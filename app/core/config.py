from __future__ import annotations

from typing import List

from pydantic import BaseSettings, Field


class Settings(BaseSettings):
    app_name: str = "Hospital Management API"
    debug: bool = False
    environment: str = "development"

    firebase_credentials_path: str = Field("", env="FIREBASE_CREDENTIALS_PATH")
    cors_origins: List[str] = Field(default_factory=lambda: ["*"], env="CORS_ORIGINS")

    class Config:
        env_file = ".env"
        case_sensitive = True
        extra = "ignore"


settings = Settings()
