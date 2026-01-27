from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    app_name: str = "AI Web Scraper Showcase"
    debug: bool = False

    # Rate limiting
    max_concurrent_sessions: int = 35
    max_requests_per_minute: int = 10
    session_timeout_minutes: int = 30

    # CORS - Frontend URL (set in production)
    frontend_url: str = "http://localhost:3000"

    # Optional default API key (for demo purposes)
    default_openai_api_key: str | None = None

    @property
    def cors_origins(self) -> list[str]:
        """Generate CORS origins from frontend URL"""
        origins = [self.frontend_url]
        # Add localhost variants for development
        if "localhost" in self.frontend_url or "127.0.0.1" in self.frontend_url:
            origins.extend([
                "http://localhost:3000",
                "http://127.0.0.1:3000"
            ])
        return list(set(origins))

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


@lru_cache()
def get_settings() -> Settings:
    return Settings()
