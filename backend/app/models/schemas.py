from pydantic import BaseModel, Field, ConfigDict
from typing import Any
from datetime import datetime, timezone
from enum import Enum


class ModelProvider(str, Enum):
    """AI Provider for LLM inference."""
    GROQ = "groq"  # FREE - Open source models
    OPENAI = "openai"
    DEEPSEEK = "deepseek"
    GEMINI = "gemini"
    ANTHROPIC = "anthropic"
    GROK = "grok"


class ModelType(str, Enum):
    """Available models across all providers."""
    # Groq (FREE - Open Source Models)
    LLAMA_3_3_70B = "llama-3.3-70b-versatile"    # FREE - Best open source
    LLAMA_3_1_8B = "llama-3.1-8b-instant"        # FREE - Fast
    MIXTRAL_8X7B = "mixtral-8x7b-32768"          # FREE - Good quality
    GEMMA_2_9B = "gemma2-9b-it"                  # FREE - Google open source

    # DeepSeek (CHEAPEST - Best value)
    DEEPSEEK_CHAT = "deepseek-chat"          # $0.14/$0.28 per 1M tokens
    DEEPSEEK_V3 = "deepseek-v3"              # $0.27/$1.10 per 1M tokens

    # Gemini (CHEAP + Large context)
    GEMINI_FLASH_LITE = "gemini-2.5-flash-lite"  # $0.10/$0.40 per 1M tokens
    GEMINI_FLASH = "gemini-2.5-flash"            # $0.30/$2.50 per 1M tokens
    GEMINI_PRO = "gemini-2.5-pro"                # $1.25/$2.50 per 1M tokens

    # OpenAI GPT-5 (PREMIUM)
    GPT_5_NANO = "gpt-5-nano"                # $0.05/$0.40 per 1M tokens
    GPT_5_MINI = "gpt-5-mini"                # $0.25/$2.00 per 1M tokens
    GPT_5 = "gpt-5"                          # $1.25/$10.00 per 1M tokens

    # OpenAI Legacy (for compatibility)
    GPT_4O_MINI = "gpt-4o-mini"              # Legacy
    GPT_4O = "gpt-4o"                        # Legacy

    # Anthropic Claude (Excellent structured output)
    CLAUDE_HAIKU = "claude-haiku-4.5"        # $1.00/$5.00 per 1M tokens
    CLAUDE_SONNET = "claude-sonnet-4.5"      # $3.00/$15.00 per 1M tokens
    CLAUDE_OPUS = "claude-opus-4.5"          # $5.00/$25.00 per 1M tokens

    # xAI Grok (2M context window)
    GROK_FAST = "grok-4-fast"                # $0.20/$0.50 per 1M tokens
    GROK_4 = "grok-4"                        # $3.00/$15.00 per 1M tokens


# Model to Provider mapping
MODEL_PROVIDER_MAP = {
    # Groq (FREE)
    ModelType.LLAMA_3_3_70B: ModelProvider.GROQ,
    ModelType.LLAMA_3_1_8B: ModelProvider.GROQ,
    ModelType.MIXTRAL_8X7B: ModelProvider.GROQ,
    ModelType.GEMMA_2_9B: ModelProvider.GROQ,
    # DeepSeek
    ModelType.DEEPSEEK_CHAT: ModelProvider.DEEPSEEK,
    ModelType.DEEPSEEK_V3: ModelProvider.DEEPSEEK,
    # Gemini
    ModelType.GEMINI_FLASH_LITE: ModelProvider.GEMINI,
    ModelType.GEMINI_FLASH: ModelProvider.GEMINI,
    ModelType.GEMINI_PRO: ModelProvider.GEMINI,
    # OpenAI
    ModelType.GPT_5_NANO: ModelProvider.OPENAI,
    ModelType.GPT_5_MINI: ModelProvider.OPENAI,
    ModelType.GPT_5: ModelProvider.OPENAI,
    ModelType.GPT_4O_MINI: ModelProvider.OPENAI,
    ModelType.GPT_4O: ModelProvider.OPENAI,
    # Anthropic
    ModelType.CLAUDE_HAIKU: ModelProvider.ANTHROPIC,
    ModelType.CLAUDE_SONNET: ModelProvider.ANTHROPIC,
    ModelType.CLAUDE_OPUS: ModelProvider.ANTHROPIC,
    # Grok
    ModelType.GROK_FAST: ModelProvider.GROK,
    ModelType.GROK_4: ModelProvider.GROK,
}

# Model context limits in characters (~4 chars per token)
MODEL_CONTEXT_LIMITS: dict[ModelType, int] = {
    # Groq
    ModelType.LLAMA_3_3_70B: 128_000 * 4,
    ModelType.LLAMA_3_1_8B: 128_000 * 4,
    ModelType.MIXTRAL_8X7B: 32_768 * 4,
    ModelType.GEMMA_2_9B: 8_192 * 4,
    # DeepSeek
    ModelType.DEEPSEEK_CHAT: 64_000 * 4,
    ModelType.DEEPSEEK_V3: 64_000 * 4,
    # Gemini
    ModelType.GEMINI_FLASH_LITE: 1_000_000 * 4,
    ModelType.GEMINI_FLASH: 1_000_000 * 4,
    ModelType.GEMINI_PRO: 1_000_000 * 4,
    # OpenAI
    ModelType.GPT_5_NANO: 128_000 * 4,
    ModelType.GPT_5_MINI: 128_000 * 4,
    ModelType.GPT_5: 128_000 * 4,
    ModelType.GPT_4O_MINI: 128_000 * 4,
    ModelType.GPT_4O: 128_000 * 4,
    # Anthropic
    ModelType.CLAUDE_HAIKU: 200_000 * 4,
    ModelType.CLAUDE_SONNET: 200_000 * 4,
    ModelType.CLAUDE_OPUS: 200_000 * 4,
    # Grok
    ModelType.GROK_FAST: 2_000_000 * 4,
    ModelType.GROK_4: 2_000_000 * 4,
}

# Model pricing info (input/output per 1M tokens)
MODEL_PRICING = {
    # Groq (FREE)
    ModelType.LLAMA_3_3_70B: {"input": 0.00, "output": 0.00, "tier": "free"},
    ModelType.LLAMA_3_1_8B: {"input": 0.00, "output": 0.00, "tier": "free"},
    ModelType.MIXTRAL_8X7B: {"input": 0.00, "output": 0.00, "tier": "free"},
    ModelType.GEMMA_2_9B: {"input": 0.00, "output": 0.00, "tier": "free"},
    # DeepSeek
    ModelType.DEEPSEEK_CHAT: {"input": 0.14, "output": 0.28, "tier": "budget"},
    ModelType.DEEPSEEK_V3: {"input": 0.27, "output": 1.10, "tier": "budget"},
    ModelType.GEMINI_FLASH_LITE: {"input": 0.10, "output": 0.40, "tier": "budget"},
    ModelType.GEMINI_FLASH: {"input": 0.30, "output": 2.50, "tier": "standard"},
    ModelType.GEMINI_PRO: {"input": 1.25, "output": 2.50, "tier": "premium"},
    ModelType.GPT_5_NANO: {"input": 0.05, "output": 0.40, "tier": "budget"},
    ModelType.GPT_5_MINI: {"input": 0.25, "output": 2.00, "tier": "standard"},
    ModelType.GPT_5: {"input": 1.25, "output": 10.00, "tier": "premium"},
    ModelType.GPT_4O_MINI: {"input": 0.15, "output": 0.60, "tier": "budget"},
    ModelType.GPT_4O: {"input": 2.50, "output": 10.00, "tier": "premium"},
    ModelType.CLAUDE_HAIKU: {"input": 1.00, "output": 5.00, "tier": "standard"},
    ModelType.CLAUDE_SONNET: {"input": 3.00, "output": 15.00, "tier": "premium"},
    ModelType.CLAUDE_OPUS: {"input": 5.00, "output": 25.00, "tier": "premium"},
    ModelType.GROK_FAST: {"input": 0.20, "output": 0.50, "tier": "budget"},
    ModelType.GROK_4: {"input": 3.00, "output": 15.00, "tier": "premium"},
}


class ActionType(str, Enum):
    """Types of page actions that can be performed before scraping."""
    CLICK = "click"
    SCROLL = "scroll"
    WAIT = "wait"
    TYPE = "type"


class CostTier(str, Enum):
    """Cost tier for smart routing."""
    FREE = "free"          # Free models (Groq)
    BUDGET = "budget"      # Cheapest paid models
    STANDARD = "standard"  # Balanced cost/performance
    PREMIUM = "premium"    # Best performance


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
        default=ModelType.DEEPSEEK_V3,
        description="LLM model to use for extraction (default: DeepSeek V3 - best value)"
    )

    # API Keys per provider (user provides their own)
    api_key: str | None = Field(
        default=None,
        description="API Key for the selected model's provider",
        json_schema_extra={"example": "sk-..."}
    )

    # Smart routing
    cost_tier: CostTier | None = Field(
        default=None,
        description="Cost tier for automatic model selection (overrides model if set)"
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

    # Stealth mode
    stealth_mode: bool = Field(
        default=True,
        description="Use stealth mode to avoid bot detection"
    )

    # Markdown conversion
    use_markdown: bool = Field(
        default=True,
        description="Convert HTML to Markdown before LLM (reduces tokens by ~67%)"
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "url": "https://example.com",
                "prompt": "Extract the main heading text",
                "model": "deepseek-v3",
                "api_key": "sk-...",
                "use_cache": True,
                "stealth_mode": True,
                "use_markdown": True
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

    # Model info
    model_used: str | None = Field(default=None, description="Actual model used for extraction")
    provider_used: str | None = Field(default=None, description="Provider used")

    # Token usage
    tokens_used: int | None = Field(default=None, description="Approximate tokens used")
    estimated_cost: float | None = Field(default=None, description="Estimated cost in USD")

    # Cache info
    cache_hit: bool = Field(
        default=False,
        description="Whether page content was served from cache"
    )

    # Markdown conversion
    markdown_used: bool = Field(
        default=False,
        description="Whether HTML was converted to Markdown"
    )
    token_reduction: float | None = Field(
        default=None,
        description="Token reduction percentage from Markdown conversion"
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

    # Content truncation
    content_truncated: bool = Field(
        default=False,
        description="Whether content was truncated to fit model context window"
    )

    # Intermediate content
    markdown_content: str | None = Field(
        default=None,
        description="Processed markdown content (limited to 5KB for display)"
    )

    # Timing breakdown
    fetch_time: float | None = Field(default=None, description="Time to fetch page in seconds")
    parse_time: float | None = Field(default=None, description="Time to parse/convert content in seconds")
    llm_time: float | None = Field(default=None, description="Time for LLM extraction in seconds")

    # Cost control
    scrapes_remaining: int | None = Field(
        default=None,
        description="Number of scrapes remaining in this session"
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "success": True,
                "data": {"heading": "Example Domain"},
                "error": None,
                "execution_time": 2.35,
                "timestamp": "2024-01-27T15:30:00Z",
                "model_used": "deepseek-v3",
                "provider_used": "deepseek",
                "tokens_used": 1500,
                "estimated_cost": 0.002,
                "cache_hit": False,
                "markdown_used": True,
                "token_reduction": 67.5,
                "validation_passed": None,
                "validation_errors": None,
                "actions_executed": 0,
                "content_truncated": False,
                "fetch_time": 1.5,
                "parse_time": 0.3,
                "llm_time": 0.55
            }
        }
    )


class SessionInfo(BaseModel):
    """Session information."""
    session_id: str = Field(..., description="Unique session identifier")
    created_at: datetime = Field(..., description="Session creation timestamp")
    last_activity: datetime = Field(..., description="Last activity timestamp")
    requests_count: int = Field(..., description="Number of requests made in this session")
    scrape_count: int = Field(default=0, description="Number of scrapes performed")
    max_scrapes: int = Field(default=5, description="Maximum scrapes allowed per session")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "session_id": "550e8400-e29b-41d4-a716-446655440000",
                "created_at": "2024-01-27T15:00:00Z",
                "last_activity": "2024-01-27T15:30:00Z",
                "requests_count": 5,
                "scrape_count": 2,
                "max_scrapes": 5
            }
        }
    )


class HealthResponse(BaseModel):
    """API health status response."""
    status: str = Field(..., description="Health status", json_schema_extra={"example": "healthy"})
    active_sessions: int = Field(..., description="Number of active sessions")
    max_sessions: int = Field(..., description="Maximum allowed sessions")
    version: str = Field(default="3.0.0", description="API version")
    features: list[str] = Field(
        default=["multi-provider", "smart-routing", "stealth-mode", "markdown-conversion"],
        description="Enabled features"
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "status": "healthy",
                "active_sessions": 5,
                "max_sessions": 35,
                "version": "3.0.0",
                "features": ["multi-provider", "smart-routing", "stealth-mode", "markdown-conversion"]
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
    provider: str = Field(..., description="Provider name")
    description: str = Field(..., description="Model description")
    tier: str = Field(..., description="Cost tier: budget, standard, premium")
    input_price: float = Field(..., description="Price per 1M input tokens")
    output_price: float = Field(..., description="Price per 1M output tokens")


class ModelsResponse(BaseModel):
    """Response listing available models."""
    models: list[ModelInfo] = Field(..., description="List of available models")
    default_model: str = Field(default="deepseek-v3", description="Default recommended model")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "models": [
                    {
                        "id": "deepseek-v3",
                        "name": "DeepSeek V3",
                        "provider": "deepseek",
                        "description": "Best value - 95% GPT-4 quality at 5% cost",
                        "tier": "budget",
                        "input_price": 0.27,
                        "output_price": 1.10
                    }
                ],
                "default_model": "deepseek-v3"
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
