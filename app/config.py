"""

config.py

---------

Central configuration using Pydantic Settings.

Reads all values from your .env file automatically.
 
Usage anywhere in the app:

    from app.config import settings

    print(settings.GROQ_API_KEY)

"""
 
from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache
 
 
class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file = ".env",
        extra    = "ignore"
    )
 
    DATABASE_URL     : str
    GROQ_API_KEY     : str
    SLACK_WEBHOOK_URL: str
    ENVIRONMENT      : str = "development"
 
 
@lru_cache()
def get_settings() -> Settings:
    return Settings()
 
 
settings = get_settings()