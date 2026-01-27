# AI Web Scraper

A full-stack web scraping application powered by LLMs. Users provide a URL and describe what data they want to extract in natural language. The system uses AI to understand the page structure and return structured data.

## Features

- **Intelligent Extraction**: Natural language prompts to extract any data
- **Structured Output**: Define expected schema for validated, consistent results
- **Page Actions**: Execute clicks, scrolls, and waits before scraping
- **Smart Caching**: Reduce costs by caching page content
- **Multiple Models**: Support for GPT-4o, GPT-4, GPT-3.5-turbo

## Architecture

```
showcase/
├── backend/                 # FastAPI REST API
│   └── app/
│       ├── api/routes.py    # HTTP endpoints
│       ├── core/
│       │   ├── config.py    # Environment configuration
│       │   └── session_manager.py  # Session and rate limiting
│       ├── models/schemas.py       # Pydantic models
│       └── services/scraper_service.py  # Scraping logic
│
└── frontend/                # Next.js client
    └── src/
        ├── app/             # Pages
        ├── components/      # React components (shadcn/ui)
        ├── hooks/           # Custom React hooks
        ├── lib/api.ts       # API client
        └── types/           # TypeScript definitions
```

## How It Works

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                              APPLICATION FLOW                               │
└─────────────────────────────────────────────────────────────────────────────┘

┌──────────┐      ┌──────────┐      ┌──────────┐      ┌──────────┐
│  USER    │      │ FRONTEND │      │ BACKEND  │      │  OPENAI  │
│          │      │ (Next.js)│      │ (FastAPI)│      │   API    │
└────┬─────┘      └────┬─────┘      └────┬─────┘      └────┬─────┘
     │                 │                 │                 │
     │  1. Enter URL   │                 │                 │
     │     + prompt    │                 │                 │
     │     + API key   │                 │                 │
     │     + actions   │                 │                 │
     │     + schema    │                 │                 │
     │────────────────>│                 │                 │
     │                 │                 │                 │
     │                 │  2. POST /scrape│                 │
     │                 │────────────────>│                 │
     │                 │                 │                 │
     │                 │                 │  3. Check cache │
     │                 │                 │────┐            │
     │                 │                 │    │ HIT: skip  │
     │                 │                 │<───┘ fetch      │
     │                 │                 │                 │
     │                 │                 │  4. Execute     │
     │                 │                 │     actions     │
     │                 │                 │     (Playwright)│
     │                 │                 │────┐            │
     │                 │                 │    │            │
     │                 │                 │<───┘            │
     │                 │                 │                 │
     │                 │                 │  5. Send HTML   │
     │                 │                 │     + prompt    │
     │                 │                 │     + schema    │
     │                 │                 │────────────────>│
     │                 │                 │                 │
     │                 │                 │  6. Structured  │
     │                 │                 │     response    │
     │                 │                 │<────────────────│
     │                 │                 │                 │
     │                 │                 │  7. Validate    │
     │                 │                 │     output      │
     │                 │                 │────┐            │
     │                 │                 │    │            │
     │                 │                 │<───┘            │
     │                 │                 │                 │
     │                 │  8. JSON result │                 │
     │                 │     + metadata  │                 │
     │                 │<────────────────│                 │
     │                 │                 │                 │
     │  9. Display     │                 │                 │
     │     result      │                 │                 │
     │<────────────────│                 │                 │
```

### Step-by-step

1. User enters URL, prompt, API key, optional actions, and optional output schema
2. Frontend sends request to backend with session ID
3. Backend checks cache for previously fetched page content
4. If not cached: execute page actions (click, scroll, wait, type) using Playwright
5. Page content and prompt (with schema instructions) are sent to OpenAI
6. LLM returns structured data based on the prompt
7. Backend validates output against schema if provided
8. Response includes data, cache status, validation status, actions executed
9. Frontend displays result with metadata badges

## Tech Stack

### Backend

| Technology | Purpose |
|------------|---------|
| FastAPI | REST API framework with async support |
| ScrapeGraphAI | AI-powered web scraping library |
| Playwright | Headless browser for JavaScript rendering and page actions |
| Pydantic | Request/response validation and serialization |
| cachetools | TTL-based page content caching |

### Frontend

| Technology | Purpose |
|------------|---------|
| Next.js 16 | React framework with App Router |
| React 19 | UI library |
| TypeScript | Type safety |
| Tailwind CSS | Utility-first styling |
| shadcn/ui | Component library |
| Sonner | Toast notifications |

## API Reference

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/health` | Server status and session count |
| POST | `/api/v1/session` | Create new session |
| GET | `/api/v1/session/{id}` | Get session info |
| DELETE | `/api/v1/session/{id}` | End session |
| POST | `/api/v1/scrape` | Execute scraping |
| GET | `/api/v1/models` | List available LLM models |

### Scrape Request

```json
{
  "url": "https://example.com",
  "prompt": "Extract all product names and prices",
  "model": "gpt-4o-mini",
  "api_key": "sk-...",
  "use_cache": true,
  "cache_ttl_minutes": 60,
  "actions": [
    {"action": "scroll", "value": "down", "wait_ms": 1000},
    {"action": "click", "selector": ".load-more", "wait_ms": 2000}
  ],
  "output_schema": [
    {"name": "products", "type": "array", "required": true},
    {"name": "total_count", "type": "number", "required": true}
  ]
}
```

### Scrape Response

```json
{
  "success": true,
  "data": {
    "products": ["Product A", "Product B"],
    "total_count": 2
  },
  "execution_time": 3.45,
  "timestamp": "2024-01-20T10:30:00Z",
  "cache_hit": false,
  "actions_executed": 2,
  "validation_passed": true,
  "validation_errors": null
}
```

## Page Actions

Execute actions before scraping to handle dynamic content:

| Action | Parameters | Description |
|--------|------------|-------------|
| `click` | `selector` | Click on element |
| `scroll` | `value` (up/down) | Scroll the page |
| `wait` | `wait_ms` | Wait for specified time |
| `type` | `selector`, `value` | Type text into input |

## Output Schema

Define expected fields for validated output:

| Property | Values | Description |
|----------|--------|-------------|
| `name` | string | Field name in output |
| `type` | string, number, boolean, array, object | Expected type |
| `description` | string | Hint for the LLM |
| `required` | boolean | Whether field is mandatory |

## Rate Limiting and Cost Control

| Control | Value | Purpose |
|---------|-------|---------|
| Max requests/minute | 10 | Prevent rapid-fire requests |
| Max concurrent sessions | 35 | Limit server load |
| Session timeout | 30 min | Auto-cleanup inactive sessions |
| Page caching | 60 min default | Reduce redundant fetches |
| User-provided API key | Required | User pays for their own inference |

## Setup

### Backend

```bash
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
playwright install chromium
uvicorn app.main:app --reload --port 8000
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

Access at:
- Frontend: http://localhost:3000
- API Docs: http://localhost:8000/docs

### Environment Variables

Backend (`.env`):
```
DEBUG=false
MAX_CONCURRENT_SESSIONS=35
MAX_REQUESTS_PER_MINUTE=10
SESSION_TIMEOUT_MINUTES=30
CORS_ORIGINS=["http://localhost:3000"]
```

Frontend (`.env.local`):
```
NEXT_PUBLIC_API_URL=http://localhost:8000
```

## Deployment

### Backend (Docker)

```dockerfile
FROM python:3.11-slim
WORKDIR /app
RUN apt-get update && apt-get install -y wget gnupg
COPY requirements.txt .
RUN pip install -r requirements.txt
RUN playwright install chromium --with-deps
COPY . .
EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Frontend (Vercel)

Deploy directly to Vercel. Set `NEXT_PUBLIC_API_URL` to your backend URL.

## Supported Models

- gpt-4o-mini (default, fast and economical)
- gpt-4o (multimodal, high accuracy)
- gpt-4-turbo (high performance)
- gpt-4 (robust)
- gpt-3.5-turbo (economical)

## Version History

- **v2.0.0**: Added structured output, page caching, and page actions
- **v1.0.0**: Initial release with basic scraping

## License

MIT
