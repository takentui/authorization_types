import secrets

from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Application settings."""

    APP_NAME: str = "FastAPI Keycloak Auth Example"
    DEBUG: bool = False
    API_USERNAME: str = "admin"
    API_PASSWORD: str = "password"

    # Keycloak configuration
    KEYCLOAK_SERVER_URL: str = "http://localhost:8080"
    KEYCLOAK_REALM: str = "master"
    KEYCLOAK_CLIENT_ID: str = "fastapi-app"
    KEYCLOAK_CLIENT_SECRET: str = "your-client-secret"

    class Config:
        env_file = ".env"


settings = Settings()
