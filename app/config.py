from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Application settings."""

    APP_NAME: str = "FastAPI Auth Examples"
    DEBUG: bool = False
    API_USERNAME: str = "admin"
    API_PASSWORD: str = "password"
    JWT_SECRET_KEY: str
    JWT_EXPIRATION_DEFAULT_MINUTES: int = 1
    JWT_EXPIRATION_REMEMBER_MINUTES: int = 7 * 24 * 60

    class Config:
        env_file = ".env"


settings = Settings()
