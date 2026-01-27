from fastapi import APIRouter, HTTPException, Header, Depends
from typing import Annotated
from app.models.schemas import (
    ScrapeRequest,
    ScrapeResponse,
    SessionInfo,
    HealthResponse,
    ErrorResponse,
    ModelsResponse,
    DeleteSessionResponse
)
from app.core.session_manager import session_manager
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
    """
    Create a new session.

    - **Rate limit**: 10 requests per minute per session
    - **Timeout**: 30 minutes of inactivity
    - **Max sessions**: 35 concurrent sessions
    """
    if session_manager.active_sessions_count >= session_manager.max_sessions:
        raise HTTPException(
            status_code=503,
            detail="Maximum number of sessions reached. Please try again later."
        )

    session_id = session_manager.create_session()
    session_data = session_manager.get_session(session_id)

    return SessionInfo(
        session_id=session_id,
        created_at=session_data["created_at"],
        last_activity=session_data["last_activity"],
        requests_count=session_data["requests_count"]
    )


@router.get(
    "/session/{session_id}",
    response_model=SessionInfo,
    summary="Get Session",
    description="Retrieve information about an existing session.",
    responses={
        404: {
            "description": "Session not found",
            "content": {
                "application/json": {
                    "example": {"detail": "Session not found"}
                }
            }
        }
    }
)
async def get_session(session_id: str):
    """Get session details by ID."""
    session_data = session_manager.get_session(session_id)
    if not session_data:
        raise HTTPException(status_code=404, detail="Session not found")

    return SessionInfo(
        session_id=session_id,
        created_at=session_data["created_at"],
        last_activity=session_data["last_activity"],
        requests_count=session_data["requests_count"]
    )


@router.delete(
    "/session/{session_id}",
    response_model=DeleteSessionResponse,
    summary="Delete Session",
    description="Close and delete an existing session.",
    responses={
        404: {
            "description": "Session not found",
            "content": {
                "application/json": {
                    "example": {"detail": "Session not found"}
                }
            }
        }
    }
)
async def delete_session(session_id: str):
    """Delete a session by ID."""
    if not session_manager.delete_session(session_id):
        raise HTTPException(status_code=404, detail="Session not found")

    return DeleteSessionResponse(message="Session closed successfully")


@router.post(
    "/scrape",
    response_model=ScrapeResponse,
    summary="Scrape Website",
    description="""
Extract structured data from any website using AI.

**Rate Limit**: 10 requests per minute per session.

**Features**:
- AI-powered data extraction using OpenAI models
- Page actions (click, scroll, wait, type) before scraping
- Structured output with schema validation
- Page content caching to reduce costs

**Required**: OpenAI API key (passed in request body)
    """,
    responses={
        429: {
            "description": "Rate limit exceeded",
            "content": {
                "application/json": {
                    "example": {"detail": "Request limit exceeded. Please wait a moment."}
                }
            }
        },
        422: {
            "description": "Validation error",
            "content": {
                "application/json": {
                    "example": {"detail": [{"loc": ["body", "url"], "msg": "field required", "type": "value_error.missing"}]}
                }
            }
        }
    }
)
async def scrape_website(
    request: ScrapeRequest,
    session_id: str = Depends(get_session_id)
):
    """
    Scrape a website and extract data using AI.

    - **url**: Target website URL
    - **prompt**: What data to extract (natural language)
    - **model**: OpenAI model to use
    - **api_key**: Your OpenAI API key
    - **actions**: Optional page actions before scraping
    - **output_schema**: Optional schema for structured output
    - **use_cache**: Use cached page content (default: true)
    """
    if not session_manager.can_make_request(session_id):
        raise HTTPException(
            status_code=429,
            detail="Request limit exceeded. Please wait a moment."
        )

    lock = session_manager.get_lock(session_id)
    async with lock:
        session_manager.record_request(session_id)
        session_manager.update_session_activity(session_id)

        result = await scraper_service.scrape(request)
        return result


@router.get(
    "/models",
    response_model=ModelsResponse,
    summary="List Models",
    description="Get list of available OpenAI models for scraping."
)
async def get_available_models():
    """Returns all available OpenAI models."""
    return ModelsResponse(
        models=[
            {"id": "gpt-4o-mini", "name": "GPT-4o Mini", "description": "Fast and economical"},
            {"id": "gpt-4o", "name": "GPT-4o", "description": "More accurate, multimodal"},
            {"id": "gpt-4-turbo", "name": "GPT-4 Turbo", "description": "High performance"},
            {"id": "gpt-4", "name": "GPT-4", "description": "Robust model"},
            {"id": "gpt-3.5-turbo", "name": "GPT-3.5 Turbo", "description": "Economical"},
        ]
    )
