from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings."""
    APP_NAME: str = "FastAPI Basic Auth Example"
    API_PREFIX: str = "/api"
    DEBUG: bool = False

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"


settings = Settings()
