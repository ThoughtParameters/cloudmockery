"""
Application Configuration using Pydantic Settings.

This module defines the Settings class for managing application configuration
and environment variables.
"""
import os
from pydantic import ConfigDict
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    """
    Manages application settings and environment variables.

    Attributes:
        API_SPECS_PATH (str): The path to the Azure REST API specifications directory.
                              Defaults to 'azure-rest-api-specs/specification' in the
                              current working directory. Can be overridden by an
                              environment variable of the same name.
    """
    API_SPECS_PATH: str = os.path.join(os.getcwd(), 'azure-rest-api-specs', 'specification')

    model_config = ConfigDict(
        env_file=".env",
        env_file_encoding='utf-8',
        case_sensitive=False,
    )

# A single, reusable instance of the settings.
# Other modules can import this instance to access application settings.
settings = Settings()
