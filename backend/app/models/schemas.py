from pydantic import BaseModel, Field, HttpUrl
from typing import Any
from datetime import datetime, timezone
from enum import Enum


class ModelType(str, Enum):
    GPT_35_TURBO = "gpt-3.5-turbo"
    GPT_4 = "gpt-4"
    GPT_4_TURBO = "gpt-4-turbo"
    GPT_4O = "gpt-4o"
    GPT_4O_MINI = "gpt-4o-mini"


class ActionType(str, Enum):
    CLICK = "click"
    SCROLL = "scroll"
    WAIT = "wait"
    TYPE = "type"


class PageAction(BaseModel):
    """Action to perform on the page before scraping"""
    action: ActionType
    selector: str | None = Field(default=None, description="CSS selector for click/type actions")
    value: str | None = Field(default=None, description="Value for type action or direction for scroll (up/down)")
    wait_ms: int = Field(default=1000, description="Wait time in milliseconds")


class OutputField(BaseModel):
    """Field definition for structured output"""
    name: str = Field(..., description="Field name")
    type: str = Field(default="string", description="Field type: string, number, boolean, array, object")
    description: str | None = Field(default=None, description="Field description for the LLM")
    required: bool = Field(default=True, description="Whether this field is required")


class ScrapeRequest(BaseModel):
    url: str = Field(..., description="URL of the website to scrape")
    prompt: str = Field(..., description="What you want to extract from the website")
    model: ModelType = Field(default=ModelType.GPT_4O_MINI, description="LLM model to use")
    api_key: str | None = Field(default=None, description="OpenAI API Key (optional if configured on server)")

    # Structured Output
    output_schema: list[OutputField] | None = Field(
        default=None,
        description="Schema for structured output validation"
    )

    # Page Actions (Tool Use)
    actions: list[PageAction] | None = Field(
        default=None,
        description="Actions to perform before scraping (click, scroll, wait, type)"
    )

    # Caching
    use_cache: bool = Field(default=True, description="Use cached page content if available")
    cache_ttl_minutes: int = Field(default=60, description="Cache TTL in minutes")


class ScrapeResponse(BaseModel):
    success: bool
    data: Any | None = None
    error: str | None = None
    execution_time: float
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    # Cache info
    cache_hit: bool = Field(default=False, description="Whether page content was served from cache")

    # Validation info
    validation_passed: bool | None = Field(default=None, description="Whether output matched the schema")
    validation_errors: list[str] | None = Field(default=None, description="Validation error messages")

    # Actions info
    actions_executed: int = Field(default=0, description="Number of page actions executed")


class SessionInfo(BaseModel):
    session_id: str
    created_at: datetime
    last_activity: datetime
    requests_count: int


class HealthResponse(BaseModel):
    status: str
    active_sessions: int
    max_sessions: int
    version: str = "2.0.0"


class ErrorResponse(BaseModel):
    detail: str
    error_code: str | None = None
