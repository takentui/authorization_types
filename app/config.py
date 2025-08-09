import secrets

import uvicorn
from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Application settings."""

    APP_NAME: str = "FastAPI Auth Examples"
    DEBUG: bool = False
    API_USERNAME: str = "admin"
    API_PASSWORD: str = "password"
    JWT_SECRET_KEY: str = secrets.token_urlsafe(32)
    ACCESS_EXPIRE_MINUTES: int = 15
    REFRESH_EXPIRE_REMEMBER_DAYS: int = 30
    REFRESH_EXPIRE_DEFAULT_DAYS: int = 7
    ROTATE_REFRESH: bool = False

    class Config:
        env_file = ".env"


settings = Settings()

LOGGING_CONFIG = {
    "version": 1,
    "formatters": {
        "standard": {"format": "%(asctime)s [%(levelname)s] %(name)s: %(message)s"},
    },
    "handlers": {
        "default": {
            "level": "DEBUG",
            "formatter": "standard",
            "class": "logging.StreamHandler",
            "stream": "ext://sys.stdout",  # Default is stderr
        },
    },
    "loggers": {
        "root": {  # root logger
            "handlers": ["default"],
            "level": "DEBUG",
            "propagate": True,
        },
        "": {  # root logger
            "handlers": ["default"],
            "level": "DEBUG",
            "propagate": True,
        },
        "uvicorn": {"handlers": ["default"], "level": "INFO", "propagate": False},
        "uvicorn.error": {"level": "INFO"},
    },
}
