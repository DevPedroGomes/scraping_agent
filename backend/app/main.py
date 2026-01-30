from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.core.config import get_settings
from app.api.routes import router


@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Starting AI Web Scraper Showcase...")
    yield
    print("Shutting down AI Web Scraper Showcase...")


def create_app() -> FastAPI:
    settings = get_settings()

    app = FastAPI(
        title=settings.app_name,
        description="""
AI Web Scraper API v3.0 - Multi-Provider LLM Extraction

**Features**:
- 5 AI Providers: OpenAI, DeepSeek, Gemini, Anthropic, Grok
- 15+ AI Models with smart cost-tier routing
- HTML to Markdown conversion (67% token reduction)
- Playwright stealth mode (anti-bot detection)
- Page actions (click, scroll, wait, type)
- Structured output validation
- Intelligent caching
        """,
        version="3.0.0",
        lifespan=lifespan,
        docs_url="/docs",
        redoc_url="/redoc"
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(router, prefix="/api/v1", tags=["scraper"])

    @app.get("/")
    async def root():
        return {
            "message": "AI Web Scraper Showcase API",
            "docs": "/docs",
            "health": "/api/v1/health"
        }

    return app


app = create_app()


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
