"""
Application configuration using Pydantic Settings.
Reads from environment variables and .env file.
"""

from pydantic_settings import BaseSettings
from pydantic import AnyHttpUrl, validator
from typing import List, Optional, Union
import os
import json


class Settings(BaseSettings):
    # ─── App ──────────────────────────────────────────────────────────────────
    APP_NAME: str = "Task Manager API"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    ENVIRONMENT: str = "development"

    # ─── Security ─────────────────────────────────────────────────────────────
    SECRET_KEY: str = "change-this-secret-key-in-production-must-be-32-chars-min"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # ─── Database ─────────────────────────────────────────────────────────────
    DATABASE_URL: str = "sqlite:///./taskmanager.db"

    # ─── CORS ─────────────────────────────────────────────────────────────────
    CORS_ORIGINS: Union[List[str], str] = [
        "http://localhost:3000",
        "http://localhost:8080",
        "http://127.0.0.1:5500",
        "http://localhost:5500",
        "http://127.0.0.1:8080",
    ]

    @validator("CORS_ORIGINS", pre=True)
    def parse_cors_origins(cls, v):
        if isinstance(v, str):
            try:
                return json.loads(v)
            except Exception:
                return [origin.strip() for origin in v.split(",")]
        return v

    # ─── Rate Limiting ────────────────────────────────────────────────────────
    RATE_LIMIT_PER_MINUTE: int = 60

    # ─── File Upload ──────────────────────────────────────────────────────────
    MAX_FILE_SIZE_MB: int = 5
    UPLOAD_DIR: str = "uploads"

    # ─── Admin Seed ───────────────────────────────────────────────────────────
    FIRST_ADMIN_EMAIL: str = "admin@taskmanager.com"
    FIRST_ADMIN_PASSWORD: str = "Admin@123456"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True


settings = Settings()

# Ensure upload directory exists
os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
