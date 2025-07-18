from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings."""

    APP_NAME: str = "FastAPI Basic Auth Example"
    API_PREFIX: str = "/api"
    DEBUG: bool = False
    API_USERNAME: str = "admin"
    API_PASSWORD: str = "admin"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
