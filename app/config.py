"""
Application Configuration using Pydantic Settings.

This module defines the Settings class and a cached function to get
a single instance of the settings.
"""
import os
from functools import lru_cache
from pydantic import ConfigDict
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    """
    Manages application settings and environment variables.
    """
    APP_ENV: str = "prod"
    API_SPECS_PATH: str = os.path.join(os.getcwd(), 'azure-rest-api-specs', 'specification')

    # Security settings
    MOCK_AUTH_TOKEN: str = "mock-token"

    # Database settings loaded from .env file
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_DB: str
    DATABASE_HOST: str
    DATABASE_PORT: int = 5432

    @property
    def DATABASE_URL(self) -> str:
        """
        Constructs the database connection URL from individual settings.
        """
        return f"postgresql://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.DATABASE_HOST}:{self.DATABASE_PORT}/{self.POSTGRES_DB}"

    model_config = ConfigDict(
        env_file=".env",
        env_file_encoding='utf-8',
        case_sensitive=False,
    )

@lru_cache()
def get_settings() -> Settings:
    """
    Returns a cached instance of the Settings object.

    If the APP_ENV environment variable is set to "test", it will return
    a test-specific configuration with dummy values, bypassing .env loading.
    Otherwise, it loads the production settings.
    """
    if os.getenv("APP_ENV") == "test":
        return Settings(
            POSTGRES_USER="test",
            POSTGRES_PASSWORD="test",
            POSTGRES_DB="testdb",
            DATABASE_HOST="localhost",
            MOCK_AUTH_TOKEN="test-token"
        )
    return Settings()
