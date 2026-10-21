from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.core.config import get_settings
from app.core.cache import SQLiteCache
from app.api.routes import router
from app.models.schemas import ModelProvider, ModelType


@asynccontextmanager
async def lifespan(app: FastAPI):
    settings = get_settings()
    print("Starting AI Web Scraper Showcase...")
    cache = SQLiteCache(db_path=settings.cache_db_path)
    deleted = cache.cleanup_expired()
    if deleted:
        print(f"Cache cleanup: removed {deleted} expired entries")
    yield
    # Graceful shutdown: close persistent browser
    from app.services.scraper_service import browser_pool
    await browser_pool.close()
    print("Shutting down AI Web Scraper Showcase...")


def create_app() -> FastAPI:
    settings = get_settings()

    # Counted from the catalog, so the docs cannot drift from what the API
    # actually serves.
    app = FastAPI(
        title=settings.app_name,
        description=f"""
AI Web Scraper API v3.0 - Multi-Provider LLM Extraction

**Features**:
- {len(ModelProvider)} AI providers: Groq, OpenAI, DeepSeek, Gemini, Anthropic, xAI Grok
- {len(ModelType)} models with optional cost-tier routing
- HTML to Markdown conversion (fewer tokens sent to the model)
- Headless Chromium with a realistic desktop browser profile
- Page actions (click, scroll, wait, type)
- Output checked against a schema when you send one (validation_passed is null otherwise)
- Per-key caching
        """,
        version="3.0.0",
        lifespan=lifespan,
        docs_url="/docs" if settings.debug else None,
        redoc_url="/redoc" if settings.debug else None,
        openapi_url="/openapi.json" if settings.debug else None,
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["GET", "POST", "DELETE", "OPTIONS"],
        allow_headers=["Content-Type", "X-Session-Id"],
    )

    app.include_router(router, prefix="/api/v1", tags=["scraper"])

    @app.get("/")
    async def root():
        return {
            "message": "AI Web Scraper Showcase API",
            "health": "/api/v1/health"
        }

    return app


app = create_app()


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
