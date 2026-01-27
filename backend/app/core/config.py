from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    app_name: str = "AI Web Scraper Showcase"
    debug: bool = False

    # Rate limiting
    max_concurrent_sessions: int = 35
    max_requests_per_minute: int = 10
    session_timeout_minutes: int = 30

    # CORS
    cors_origins: list[str] = ["http://localhost:3000", "http://127.0.0.1:3000"]

    # Optional default API key (for demo purposes)
    default_openai_api_key: str | None = None

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


@lru_cache()
def get_settings() -> Settings:
    return Settings()
