from fastapi import APIRouter, HTTPException, Header, Depends
from typing import Annotated
from app.models.schemas import (
    ScrapeRequest,
    ScrapeResponse,
    SessionInfo,
    HealthResponse,
    ErrorResponse,
    ModelsResponse,
    ModelInfo,
    DeleteSessionResponse,
    ModelType,
    ModelProvider,
    MODEL_PROVIDER_MAP,
    MODEL_PRICING,
)
from app.core.session_manager import session_manager
from app.core.examples import get_examples_list, get_example_by_match
from app.services.scraper_service import scraper_service

router = APIRouter()


async def get_session_id(x_session_id: Annotated[str | None, Header()] = None) -> str:
    """
    Get or create session ID from header.
    If no session ID provided or session expired, creates a new one.
    """
    if not x_session_id:
        return session_manager.create_session()

    session = session_manager.get_session(x_session_id)
    if not session:
        return session_manager.create_session()

    return x_session_id


def _build_session_info(session_id: str) -> SessionInfo:
    """Build SessionInfo from session data."""
    session_data = session_manager.get_session(session_id)
    if not session_data:
        raise HTTPException(status_code=404, detail="Session not found")

    scrape_count, max_scrapes = session_manager.get_scrape_info(session_id)
    return SessionInfo(
        session_id=session_id,
        created_at=session_data["created_at"],
        last_activity=session_data["last_activity"],
        requests_count=session_data["requests_count"],
        scrape_count=scrape_count,
        max_scrapes=max_scrapes,
    )


@router.get(
    "/health",
    response_model=HealthResponse,
    summary="Health Check",
    description="Check API health status, active sessions count, and version."
)
async def health_check():
    """Returns the current health status of the API."""
    return HealthResponse(
        status="healthy",
        active_sessions=session_manager.active_sessions_count,
        max_sessions=session_manager.max_sessions
    )


@router.post(
    "/session",
    response_model=SessionInfo,
    summary="Create Session",
    description="Create a new session for rate limiting. Sessions expire after 30 minutes of inactivity.",
    responses={
        503: {
            "description": "Maximum sessions reached",
            "content": {
                "application/json": {
                    "example": {"detail": "Maximum number of sessions reached. Please try again later."}
                }
            }
        }
    }
)
async def create_session():
    """Create a new session."""
    if session_manager.active_sessions_count >= session_manager.max_sessions:
        raise HTTPException(
            status_code=503,
            detail="Maximum number of sessions reached. Please try again later."
        )

    session_id = session_manager.create_session()
    return _build_session_info(session_id)


@router.get(
    "/session/{session_id}",
    response_model=SessionInfo,
    summary="Get Session",
    description="Retrieve information about an existing session.",
    responses={404: {"description": "Session not found"}}
)
async def get_session(session_id: str):
    """Get session details by ID."""
    return _build_session_info(session_id)


@router.delete(
    "/session/{session_id}",
    response_model=DeleteSessionResponse,
    summary="Delete Session",
    description="Close and delete an existing session.",
    responses={404: {"description": "Session not found"}}
)
async def delete_session(session_id: str):
    """Delete a session by ID."""
    if not session_manager.delete_session(session_id):
        raise HTTPException(status_code=404, detail="Session not found")

    return DeleteSessionResponse(message="Session closed successfully")


@router.get(
    "/examples",
    summary="List Examples",
    description="Get list of pre-cached example scrapes for showcase mode."
)
async def list_examples():
    """Returns available example scrapes."""
    return {"examples": get_examples_list()}


@router.post(
    "/scrape",
    response_model=ScrapeResponse,
    summary="Scrape Website",
    description="""
Extract structured data from any website using AI.

**Rate Limit**: 10 requests per minute per session.
**Scrape Limit**: 5 scrapes per session (examples don't count).

**Providers**: Groq (FREE), OpenAI, DeepSeek, Gemini, Anthropic, Grok
    """,
    responses={
        429: {
            "description": "Rate limit or scrape limit exceeded",
            "content": {
                "application/json": {
                    "example": {"detail": "Request limit exceeded. Please wait a moment."}
                }
            }
        },
    }
)
async def scrape_website(
    request: ScrapeRequest,
    session_id: str = Depends(get_session_id)
):
    """Scrape a website and extract data using AI."""
    if not session_manager.can_make_request(session_id):
        raise HTTPException(
            status_code=429,
            detail="Request limit exceeded. Please wait a moment."
        )

    # Check if this matches a pre-cached example (doesn't count toward limits)
    example = get_example_by_match(request.url, request.prompt)
    if example:
        from datetime import datetime, timezone
        cached = example["cached_response"].copy()
        cached["timestamp"] = datetime.now(timezone.utc).isoformat()
        scrape_count, max_scrapes = session_manager.get_scrape_info(session_id)
        cached["scrapes_remaining"] = max_scrapes - scrape_count
        return ScrapeResponse(**cached)

    # Check scrape limit
    if not session_manager.can_scrape(session_id):
        raise HTTPException(
            status_code=429,
            detail="Scrape limit reached for this session. Examples are still available."
        )

    lock = session_manager.get_lock(session_id)
    async with lock:
        session_manager.record_request(session_id)
        session_manager.update_session_activity(session_id)

        result = await scraper_service.scrape(request)

        # Record scrape on success
        if result.success:
            session_manager.record_scrape(session_id)

        # Add remaining scrapes info
        scrape_count, max_scrapes = session_manager.get_scrape_info(session_id)
        result.scrapes_remaining = max_scrapes - scrape_count

        return result


@router.get(
    "/models",
    response_model=ModelsResponse,
    summary="List Models",
    description="Get list of all available AI models for scraping across all providers."
)
async def get_available_models():
    """Returns all available AI models across all providers."""
    models = []

    model_info = {
        # Groq (FREE - Open Source Models)
        ModelType.LLAMA_3_3_70B: ("Llama 3.3 70B", "FREE - Best open source model, rivals GPT-4"),
        ModelType.LLAMA_3_1_8B: ("Llama 3.1 8B", "FREE - Fast and efficient for simple tasks"),
        ModelType.MIXTRAL_8X7B: ("Mixtral 8x7B", "FREE - High quality MoE model with 32K context"),
        ModelType.GEMMA_2_9B: ("Gemma 2 9B", "FREE - Google's open source model"),
        # DeepSeek
        ModelType.DEEPSEEK_CHAT: ("DeepSeek Chat", "Cheapest paid - Great for simple extractions"),
        ModelType.DEEPSEEK_V3: ("DeepSeek V3", "Best value - 95% GPT-4 quality at 5% cost"),
        # Gemini
        ModelType.GEMINI_FLASH_LITE: ("Gemini Flash Lite", "Ultra-fast and cheap - Good for large pages"),
        ModelType.GEMINI_FLASH: ("Gemini 2.5 Flash", "Fast with 1M context window"),
        ModelType.GEMINI_PRO: ("Gemini 2.5 Pro", "Most capable Gemini model"),
        # OpenAI GPT-5
        ModelType.GPT_5_NANO: ("GPT-5 Nano", "Fastest OpenAI model - Great for simple tasks"),
        ModelType.GPT_5_MINI: ("GPT-5 Mini", "Balanced speed and intelligence"),
        ModelType.GPT_5: ("GPT-5", "Most intelligent OpenAI model"),
        # OpenAI Legacy
        ModelType.GPT_4O_MINI: ("GPT-4o Mini (Legacy)", "Fast and economical - Previous gen"),
        ModelType.GPT_4O: ("GPT-4o (Legacy)", "Multimodal - Previous gen"),
        # Anthropic
        ModelType.CLAUDE_HAIKU: ("Claude Haiku 4.5", "Fastest Claude - Great for structured output"),
        ModelType.CLAUDE_SONNET: ("Claude Sonnet 4.5", "Balanced Claude model"),
        ModelType.CLAUDE_OPUS: ("Claude Opus 4.5", "Most capable Claude model"),
        # Grok
        ModelType.GROK_FAST: ("Grok 4 Fast", "Fast with 2M context window"),
        ModelType.GROK_4: ("Grok 4", "Most capable xAI model - 2M context"),
    }

    for model_type in ModelType:
        provider = MODEL_PROVIDER_MAP.get(model_type)
        pricing = MODEL_PRICING.get(model_type, {"input": 0, "output": 0, "tier": "standard"})
        name, description = model_info.get(model_type, (model_type.value, "AI model"))

        models.append(ModelInfo(
            id=model_type.value,
            name=name,
            provider=provider.value if provider else "unknown",
            description=description,
            tier=pricing["tier"],
            input_price=pricing["input"],
            output_price=pricing["output"]
        ))

    return ModelsResponse(models=models, default_model="llama-3.3-70b-versatile")
