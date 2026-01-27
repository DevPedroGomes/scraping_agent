from fastapi import APIRouter, HTTPException, Header, Depends
from typing import Annotated
from app.models.schemas import (
    ScrapeRequest,
    ScrapeResponse,
    SessionInfo,
    HealthResponse,
    ErrorResponse
)
from app.core.session_manager import session_manager
from app.services.scraper_service import scraper_service

router = APIRouter()


async def get_session_id(x_session_id: Annotated[str | None, Header()] = None) -> str:
    if not x_session_id:
        return session_manager.create_session()

    session = session_manager.get_session(x_session_id)
    if not session:
        return session_manager.create_session()

    return x_session_id


@router.get("/health", response_model=HealthResponse)
async def health_check():
    return HealthResponse(
        status="healthy",
        active_sessions=session_manager.active_sessions_count,
        max_sessions=session_manager.max_sessions
    )


@router.post("/session", response_model=SessionInfo)
async def create_session():
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


@router.get("/session/{session_id}", response_model=SessionInfo)
async def get_session(session_id: str):
    session_data = session_manager.get_session(session_id)
    if not session_data:
        raise HTTPException(status_code=404, detail="Session not found")

    return SessionInfo(
        session_id=session_id,
        created_at=session_data["created_at"],
        last_activity=session_data["last_activity"],
        requests_count=session_data["requests_count"]
    )


@router.delete("/session/{session_id}")
async def delete_session(session_id: str):
    if not session_manager.delete_session(session_id):
        raise HTTPException(status_code=404, detail="Session not found")

    return {"message": "Session closed successfully"}


@router.post("/scrape", response_model=ScrapeResponse)
async def scrape_website(
    request: ScrapeRequest,
    session_id: str = Depends(get_session_id)
):
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


@router.get("/models")
async def get_available_models():
    return {
        "models": [
            {"id": "gpt-4o-mini", "name": "GPT-4o Mini", "description": "Fast and economical"},
            {"id": "gpt-4o", "name": "GPT-4o", "description": "More accurate, multimodal"},
            {"id": "gpt-4-turbo", "name": "GPT-4 Turbo", "description": "High performance"},
            {"id": "gpt-4", "name": "GPT-4", "description": "Robust model"},
            {"id": "gpt-3.5-turbo", "name": "GPT-3.5 Turbo", "description": "Economical"},
        ]
    }
