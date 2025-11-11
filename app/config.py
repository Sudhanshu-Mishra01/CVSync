from pydantic_settings import BaseSettings
from functools import lru_cache

class Settings(BaseSettings):
    groq_api_key: str
    secret_key: str
    database_url: str = "sqlite:///./recruitment.db"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 60

    class Config:
        env_file = ".env"

@lru_cache
def get_settings() -> Settings:
    return Settings()