from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    app_name: str = "AI Web Scraper Showcase"
    debug: bool = False

    # Registro de sessoes em memoria. NAO e o teto de carga da VPS: o frontend
    # abre uma sessao a cada carregamento de pagina, entao um numero baixo aqui
    # recusa visitante que nem chegou a pedir um scrape. Quem protege a maquina
    # e MAX_CONCURRENT_PAGES (semaforo no BrowserManager), porque a demo usa um
    # unico Chromium com um contexto por request, nao um navegador por sessao.
    max_concurrent_sessions: int = 200
    max_concurrent_pages: int = 3
    max_requests_per_minute: int = 10
    session_timeout_minutes: int = 30

    # CORS - Frontend URL (set in production)
    frontend_url: str = "http://localhost:3000"

    # Optional default API keys (for "free showcase" mode — user doesn't bring
    # their own key). When set, the backend uses these as fallback on providers
    # where they apply. Per-IP rate limit applies stricter than BYOK.
    default_openai_api_key: str | None = None
    default_groq_api_key: str | None = None
    default_openrouter_api_key: str | None = None

    # Cache
    cache_db_path: str = "scrape_cache.db"

    # Cost control
    max_scrapes_per_session: int = 5

    # Teto diario global de chamadas pagas com a NOSSA chave compartilhada.
    # Os limites por sessao e por IP protegem contra um visitante; nenhum dos
    # dois protege contra todos eles juntos, nem contra alguem trocando de IP.
    # Quem traz a propria chave (BYOK) nao consome deste teto: nao custa nada.
    daily_shared_key_scrapes: int = 200

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
