# app/config.py
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    openrouter_api_key: str
    openrouter_base_url: str = "https://openrouter.ai/api/v1"
    database_file: str = "recipe_ai.db" 

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
    )
