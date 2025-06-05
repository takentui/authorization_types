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

    # GitHub OAuth Settings
    GITHUB_CLIENT_ID: Optional[str] = None
    GITHUB_CLIENT_SECRET: Optional[str] = None
    GITHUB_REDIRECT_URI: str = "http://localhost:8000/auth/github/callback"
    GITHUB_SCOPE: str = "user:email"

    # OAuth URLs
    GITHUB_AUTH_URL: str = "https://github.com/login/oauth/authorize"
    GITHUB_TOKEN_URL: str = "https://github.com/login/oauth/access_token"
    GITHUB_USER_URL: str = "https://api.github.com/user"

    class Config:
        env_file = ".env"


settings = Settings()
