import typing

from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Application settings."""

    APP_NAME: str = "FastAPI Auth Examples"
    DEBUG: bool = False
    API_USERNAME: str = "admin"
    API_PASSWORD: str = "password"
    MAX_COOKIE_AGE_DEFAULT: int = 30 * 60
    MAX_COOKIE_AGE_REMEMBER: int = 7 * 24 * 60 * 60
    COOKIE_HTTPONLY: bool = False
    COOKIE_SECURE: bool = False
    COOKIE_DOMAIN: str | None = None
    COOKIE_SAMESITE: typing.Literal["lax", "strict", "none"] | None = "lax"

    class Config:
        env_file = ".env"


settings = Settings()
