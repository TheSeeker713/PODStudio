"""
Application Configuration
Uses pydantic-settings for type-safe config from .env

TODO (Step 2+): Define Settings class with all env vars
"""

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from .env"""

    app_env: str = "development"
    app_debug: bool = True
    db_path: str = "./podstudio.db"

    class Config:
        env_file = ".env"
        case_sensitive = False


# Singleton instance
settings = Settings()
