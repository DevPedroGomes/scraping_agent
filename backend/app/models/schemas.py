from pydantic import BaseModel, Field, HttpUrl, ConfigDict
from typing import Any
from datetime import datetime, timezone
from enum import Enum


class ModelType(str, Enum):
    """Available OpenAI models for scraping."""
    GPT_35_TURBO = "gpt-3.5-turbo"
    GPT_4 = "gpt-4"
    GPT_4_TURBO = "gpt-4-turbo"
    GPT_4O = "gpt-4o"
    GPT_4O_MINI = "gpt-4o-mini"


class ActionType(str, Enum):
    """Types of page actions that can be performed before scraping."""
    CLICK = "click"
    SCROLL = "scroll"
    WAIT = "wait"
    TYPE = "type"


class PageAction(BaseModel):
    """Action to perform on the page before scraping."""
    action: ActionType = Field(..., description="Type of action to perform")
    selector: str | None = Field(
        default=None,
        description="CSS selector for click/type actions",
        json_schema_extra={"example": "#submit-button"}
    )
    value: str | None = Field(
        default=None,
        description="Value for type action or direction for scroll (up/down)",
        json_schema_extra={"example": "down"}
    )
    wait_ms: int = Field(
        default=1000,
        description="Wait time in milliseconds after action",
        ge=0,
        le=30000
    )

    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {"action": "click", "selector": "#load-more", "wait_ms": 2000},
                {"action": "scroll", "value": "down", "wait_ms": 1000},
                {"action": "type", "selector": "#search", "value": "python", "wait_ms": 500}
            ]
        }
    )


class OutputField(BaseModel):
    """Field definition for structured output validation."""
    name: str = Field(..., description="Field name in the output", json_schema_extra={"example": "title"})
    type: str = Field(
        default="string",
        description="Field type: string, number, boolean, array, object",
        json_schema_extra={"example": "string"}
    )
    description: str | None = Field(
        default=None,
        description="Field description to help the LLM",
        json_schema_extra={"example": "The main title of the article"}
    )
    required: bool = Field(default=True, description="Whether this field is required")


class ScrapeRequest(BaseModel):
    """Request body for the scrape endpoint."""
    url: str = Field(
        ...,
        description="URL of the website to scrape",
        json_schema_extra={"example": "https://example.com"}
    )
    prompt: str = Field(
        ...,
        description="What you want to extract from the website",
        json_schema_extra={"example": "Extract the main heading and all paragraph texts"}
    )
    model: ModelType = Field(
        default=ModelType.GPT_4O_MINI,
        description="LLM model to use for extraction"
    )
    api_key: str | None = Field(
        default=None,
        description="OpenAI API Key (required unless server has default key)",
        json_schema_extra={"example": "sk-..."}
    )

    # Structured Output
    output_schema: list[OutputField] | None = Field(
        default=None,
        description="Optional schema for structured output validation"
    )

    # Page Actions (Tool Use)
    actions: list[PageAction] | None = Field(
        default=None,
        description="Optional actions to perform before scraping (click, scroll, wait, type)"
    )

    # Caching
    use_cache: bool = Field(
        default=True,
        description="Use cached page content if available (reduces costs)"
    )
    cache_ttl_minutes: int = Field(
        default=60,
        description="Cache TTL in minutes",
        ge=1,
        le=1440
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "url": "https://example.com",
                "prompt": "Extract the main heading text",
                "model": "gpt-4o-mini",
                "api_key": "sk-...",
                "use_cache": True
            }
        }
    )


class ScrapeResponse(BaseModel):
    """Response from the scrape endpoint."""
    success: bool = Field(..., description="Whether the scraping was successful")
    data: Any | None = Field(default=None, description="Extracted data from the website")
    error: str | None = Field(default=None, description="Error message if scraping failed")
    execution_time: float = Field(..., description="Time taken in seconds")
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    # Cache info
    cache_hit: bool = Field(
        default=False,
        description="Whether page content was served from cache"
    )

    # Validation info
    validation_passed: bool | None = Field(
        default=None,
        description="Whether output matched the schema (null if no schema provided)"
    )
    validation_errors: list[str] | None = Field(
        default=None,
        description="Validation error messages if schema validation failed"
    )

    # Actions info
    actions_executed: int = Field(
        default=0,
        description="Number of page actions successfully executed"
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "success": True,
                "data": {"heading": "Example Domain"},
                "error": None,
                "execution_time": 2.35,
                "timestamp": "2024-01-27T15:30:00Z",
                "cache_hit": False,
                "validation_passed": None,
                "validation_errors": None,
                "actions_executed": 0
            }
        }
    )


class SessionInfo(BaseModel):
    """Session information."""
    session_id: str = Field(..., description="Unique session identifier")
    created_at: datetime = Field(..., description="Session creation timestamp")
    last_activity: datetime = Field(..., description="Last activity timestamp")
    requests_count: int = Field(..., description="Number of requests made in this session")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "session_id": "550e8400-e29b-41d4-a716-446655440000",
                "created_at": "2024-01-27T15:00:00Z",
                "last_activity": "2024-01-27T15:30:00Z",
                "requests_count": 5
            }
        }
    )


class HealthResponse(BaseModel):
    """API health status response."""
    status: str = Field(..., description="Health status", json_schema_extra={"example": "healthy"})
    active_sessions: int = Field(..., description="Number of active sessions")
    max_sessions: int = Field(..., description="Maximum allowed sessions")
    version: str = Field(default="2.0.0", description="API version")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "status": "healthy",
                "active_sessions": 5,
                "max_sessions": 35,
                "version": "2.0.0"
            }
        }
    )


class ErrorResponse(BaseModel):
    """Error response format."""
    detail: str = Field(..., description="Error message")
    error_code: str | None = Field(default=None, description="Optional error code")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "detail": "Session not found",
                "error_code": "SESSION_NOT_FOUND"
            }
        }
    )


class ModelInfo(BaseModel):
    """Information about an available model."""
    id: str = Field(..., description="Model identifier")
    name: str = Field(..., description="Display name")
    description: str = Field(..., description="Model description")


class ModelsResponse(BaseModel):
    """Response listing available models."""
    models: list[ModelInfo] = Field(..., description="List of available models")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "models": [
                    {"id": "gpt-4o-mini", "name": "GPT-4o Mini", "description": "Fast and economical"},
                    {"id": "gpt-4o", "name": "GPT-4o", "description": "More accurate, multimodal"}
                ]
            }
        }
    )


class DeleteSessionResponse(BaseModel):
    """Response for session deletion."""
    message: str = Field(..., description="Success message")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "message": "Session closed successfully"
            }
        }
    )
