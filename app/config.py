import secrets

from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Application settings."""

    APP_NAME: str = "FastAPI Auth Examples"
    DEBUG: bool = False
    API_USERNAME: str = "admin"
    API_PASSWORD: str = "password"
    JWT_SECRET_KEY: str = secrets.token_urlsafe(32)
    ACCESS_EXPIRE_MINUTES: int = 30
    REFRESH_EXPIRE_DAYS: int = 7

    class Config:
        env_file = ".env"


settings = Settings()
