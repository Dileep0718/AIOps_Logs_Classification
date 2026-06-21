"""

config.py

---------

Central configuration using Pydantic Settings.

Reads all values from your .env file automatically.
 
Usage anywhere in the app:

    from app.config import settings

    print(settings.GROQ_API_KEY)

"""
 
from pydantic_settings import BaseSettings

from functools import lru_cache
 
 
class Settings(BaseSettings):

    # database

    DATABASE_URL       : str
 
    # LLM

    GROQ_API_KEY       : str
 
    # alerting

    SLACK_WEBHOOK_URL  : str
 
    # app

    ENVIRONMENT        : str = "development"
 
    class Config:

        # tells Pydantic where to find the .env file

        env_file = ".env"

        # allows extra fields in .env without crashing

        extra    = "ignore"
 
 
@lru_cache()

def get_settings() -> Settings:

    """

    lru_cache means Settings() is only created once

    and reused for every call — not re-read from disk each time

    """

    return Settings()
 
 
# single instance used across the entire app

settings = get_settings()
 