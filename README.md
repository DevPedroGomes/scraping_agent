# AI Web Scraper v3.0

A full-stack web scraping application powered by multiple LLM providers. Users provide a URL and describe what data they want to extract in natural language. The system uses AI to understand the page structure and return structured data.

## What's New in v3.0

- **5 AI Providers**: OpenAI, DeepSeek, Gemini, Anthropic, Grok
- **15+ Models**: From budget ($0.05/1M tokens) to premium ($25/1M tokens)
- **67% Token Reduction**: HTML to Markdown conversion saves costs
- **Stealth Mode**: Anti-bot detection bypass with Playwright
- **Smart Routing**: Auto-select models by cost tier (budget/standard/premium)
- **Real-time Cost Tracking**: See tokens used and estimated cost per request

## Features

| Feature | Description |
|---------|-------------|
| **Multi-Provider AI** | Choose from OpenAI, DeepSeek, Gemini, Anthropic, or Grok |
| **Intelligent Extraction** | Natural language prompts to extract any data |
| **Stealth Mode** | Bypass bot detection with browser fingerprint evasion |
| **Markdown Conversion** | Reduce tokens by 67% with HTML to Markdown |
| **Smart Routing** | Auto-select cheapest model for your quality tier |
| **Structured Output** | Define expected schema for validated results |
| **Page Actions** | Execute clicks, scrolls, waits before scraping |
| **Smart Caching** | Reduce costs by caching page content |
| **Cost Tracking** | Real-time token usage and cost estimates |

## Supported Models & Pricing

### Budget Tier (Cheapest)
| Model | Provider | Input/Output per 1M tokens |
|-------|----------|---------------------------|
| GPT-5 Nano | OpenAI | $0.05 / $0.40 |
| Gemini Flash Lite | Google | $0.10 / $0.40 |
| DeepSeek Chat | DeepSeek | $0.14 / $0.28 |
| Grok 4 Fast | xAI | $0.20 / $0.50 |
| DeepSeek V3 | DeepSeek | $0.27 / $1.10 |

### Standard Tier (Balanced)
| Model | Provider | Input/Output per 1M tokens |
|-------|----------|---------------------------|
| GPT-5 Mini | OpenAI | $0.25 / $2.00 |
| Gemini 2.5 Flash | Google | $0.30 / $2.50 |
| Claude Haiku 4.5 | Anthropic | $1.00 / $5.00 |

### Premium Tier (Best Quality)
| Model | Provider | Input/Output per 1M tokens |
|-------|----------|---------------------------|
| GPT-5 | OpenAI | $1.25 / $10.00 |
| Gemini 2.5 Pro | Google | $1.25 / $2.50 |
| Claude Sonnet 4.5 | Anthropic | $3.00 / $15.00 |
| Grok 4 | xAI | $3.00 / $15.00 |
| Claude Opus 4.5 | Anthropic | $5.00 / $25.00 |

## Architecture

```
ai-web-scraper/
├── backend/                 # FastAPI REST API
│   └── app/
│       ├── api/routes.py    # HTTP endpoints
│       ├── core/
│       │   ├── config.py    # Environment configuration
│       │   └── session_manager.py  # Session and rate limiting
│       ├── models/schemas.py       # Pydantic models (15+ AI models)
│       └── services/
│           └── scraper_service.py  # Multi-provider scraping logic
│               ├── HTMLToMarkdown      # 67% token reduction
│               ├── SmartRouter         # Cost-tier model selection
│               ├── PageCache           # TTL-based caching
│               ├── OutputValidator     # Schema validation
│               ├── PageActionExecutor  # Playwright stealth mode
│               └── LLMProviders        # OpenAI, DeepSeek, Gemini, Anthropic, Grok
│
└── frontend/                # Next.js 16 client
    └── src/
        ├── app/             # Pages
        ├── components/      # React components (shadcn/ui)
        │   └── scraper/
        │       ├── scraper-form.tsx    # Multi-provider model selector
        │       ├── scraper-result.tsx  # Cost & token display
        │       └── status-bar.tsx      # API health status
        ├── hooks/           # Custom React hooks
        ├── lib/api.ts       # API client
        └── types/           # TypeScript definitions (15+ models)
```

## How It Works

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         AI WEB SCRAPER v3.0 FLOW                            │
└─────────────────────────────────────────────────────────────────────────────┘

┌──────────┐     ┌──────────┐     ┌──────────┐     ┌──────────────────────┐
│  USER    │     │ FRONTEND │     │ BACKEND  │     │    AI PROVIDERS      │
│          │     │ (Next.js)│     │ (FastAPI)│     │ OpenAI/DeepSeek/     │
│          │     │          │     │          │     │ Gemini/Anthropic/Grok│
└────┬─────┘     └────┬─────┘     └────┬─────┘     └──────────┬───────────┘
     │                │                │                      │
     │  1. Enter:     │                │                      │
     │   - URL        │                │                      │
     │   - Prompt     │                │                      │
     │   - Provider   │                │                      │
     │   - API Key    │                │                      │
     │   - Options    │                │                      │
     │───────────────>│                │                      │
     │                │                │                      │
     │                │  2. POST       │                      │
     │                │     /scrape    │                      │
     │                │───────────────>│                      │
     │                │                │                      │
     │                │                │  3. Check cache      │
     │                │                │─────┐                │
     │                │                │     │ HIT: skip      │
     │                │                │<────┘ fetch          │
     │                │                │                      │
     │                │                │  4. Stealth Mode     │
     │                │                │     Playwright       │
     │                │                │─────┐                │
     │                │                │     │ Execute        │
     │                │                │<────┘ actions        │
     │                │                │                      │
     │                │                │  5. HTML → Markdown  │
     │                │                │     (67% reduction)  │
     │                │                │─────┐                │
     │                │                │<────┘                │
     │                │                │                      │
     │                │                │  6. Route to         │
     │                │                │     provider         │
     │                │                │─────────────────────>│
     │                │                │                      │
     │                │                │  7. Structured       │
     │                │                │     JSON response    │
     │                │                │<─────────────────────│
     │                │                │                      │
     │                │                │  8. Validate &       │
     │                │                │     calculate cost   │
     │                │                │─────┐                │
     │                │                │<────┘                │
     │                │                │                      │
     │                │  9. Result +   │                      │
     │                │     metadata   │                      │
     │                │<───────────────│                      │
     │                │                │                      │
     │  10. Display   │                │                      │
     │   - Data       │                │                      │
     │   - Tokens     │                │                      │
     │   - Cost       │                │                      │
     │<───────────────│                │                      │
```

## Tech Stack

### Backend

| Technology | Purpose |
|------------|---------|
| FastAPI | REST API framework with async support |
| Playwright | Headless browser with stealth mode |
| OpenAI SDK | GPT-5, GPT-4o models |
| Anthropic SDK | Claude Haiku, Sonnet, Opus |
| Google GenAI | Gemini Flash, Pro models |
| Markdownify | HTML to Markdown (67% token reduction) |
| BeautifulSoup | HTML parsing and cleaning |
| Pydantic | Request/response validation |
| cachetools | TTL-based page content caching |

### Frontend

| Technology | Purpose |
|------------|---------|
| Next.js 16 | React framework with App Router |
| React 19 | UI library |
| TypeScript | Type safety |
| Tailwind CSS 4 | Utility-first styling |
| shadcn/ui | Component library |
| Sonner | Toast notifications |

## API Reference

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/health` | Server status, version, features |
| POST | `/api/v1/session` | Create new session |
| GET | `/api/v1/session/{id}` | Get session info |
| DELETE | `/api/v1/session/{id}` | End session |
| POST | `/api/v1/scrape` | Execute scraping |
| GET | `/api/v1/models` | List all 15+ models with pricing |

### Scrape Request

```json
{
  "url": "https://example.com",
  "prompt": "Extract all product names and prices",
  "model": "deepseek-v3",
  "api_key": "your-provider-api-key",
  "cost_tier": "budget",
  "stealth_mode": true,
  "use_markdown": true,
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
  "timestamp": "2026-01-29T10:30:00Z",
  "model_used": "deepseek-v3",
  "provider_used": "deepseek",
  "tokens_used": 1523,
  "estimated_cost": 0.0018,
  "cache_hit": false,
  "markdown_used": true,
  "token_reduction": 67.5,
  "actions_executed": 2,
  "validation_passed": true,
  "validation_errors": null
}
```

## New Features in v3.0

### Stealth Mode
Bypass bot detection with browser fingerprint evasion:
- Hides `navigator.webdriver` property
- Spoofs plugins and languages
- Emulates real Chrome browser
- Bypasses CSP restrictions

### HTML to Markdown Conversion
Reduce token costs by ~67%:
- Removes scripts, styles, navigation
- Converts to clean Markdown
- Preserves semantic structure
- Shows reduction percentage in response

### Smart Routing
Auto-select the best model for your budget:

| Cost Tier | Default Model | Use Case |
|-----------|---------------|----------|
| `budget` | DeepSeek Chat | Simple extractions |
| `standard` | DeepSeek V3 | Balanced quality |
| `premium` | GPT-5 | Complex extractions |

### Multi-Provider Support
Use your preferred AI provider:

| Provider | API Key Format | Models |
|----------|----------------|--------|
| OpenAI | `sk-...` | GPT-5, GPT-4o |
| DeepSeek | `sk-...` | DeepSeek V3, Chat |
| Google | `AI...` | Gemini Flash, Pro |
| Anthropic | `sk-ant-...` | Claude Haiku, Sonnet, Opus |
| xAI | `xai-...` | Grok 4, Grok 4 Fast |

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

## Rate Limiting

| Control | Value | Purpose |
|---------|-------|---------|
| Max requests/minute | 10 | Prevent rapid-fire requests |
| Max concurrent sessions | 35 | Limit server load |
| Session timeout | 30 min | Auto-cleanup inactive sessions |
| Page caching | 60 min default | Reduce redundant fetches |

## Setup

### Backend

```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
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

## Environment Variables

### Backend (`.env`)
```bash
# Server
DEBUG=false

# Rate Limiting
MAX_CONCURRENT_SESSIONS=35
MAX_REQUESTS_PER_MINUTE=10
SESSION_TIMEOUT_MINUTES=30

# CORS - Set to your frontend URL in production
FRONTEND_URL=http://localhost:3000

# Optional: Default API key for demo
# DEFAULT_OPENAI_API_KEY=sk-...
```

### Frontend (`.env.local`)
```bash
# Backend API URL - Set to your backend URL in production
NEXT_PUBLIC_API_URL=http://localhost:8000
```

## Deployment

### Railway (Recommended)

Both frontend and backend have `railway.json` configured for one-click deploy.

1. Connect your GitHub repo to Railway
2. Create two services: `backend` and `frontend`
3. Set root directories: `backend` and `frontend`
4. Add environment variables
5. Generate domains and update `FRONTEND_URL` / `NEXT_PUBLIC_API_URL`

### Docker (Backend)

```dockerfile
FROM python:3.11-slim
WORKDIR /app

RUN apt-get update && apt-get install -y \
    wget gnupg ca-certificates \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
RUN playwright install chromium --with-deps

COPY . .

EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Vercel (Frontend)

Deploy directly to Vercel. Set `NEXT_PUBLIC_API_URL` to your backend URL.

## Version History

- **v3.0.0**: Multi-provider support (5 providers, 15+ models), stealth mode, HTML to Markdown conversion, smart routing, cost tracking
- **v2.0.0**: Added structured output, page caching, and page actions
- **v1.0.0**: Initial release with basic scraping

## Cost Optimization Tips

1. **Use Markdown Conversion**: Reduces tokens by ~67%
2. **Enable Caching**: Avoid re-fetching same pages
3. **Choose Budget Tier**: DeepSeek V3 offers 95% of GPT-4 quality at 5% cost
4. **Use Smart Routing**: Let the system pick the cheapest model for your tier
5. **Define Output Schema**: More precise prompts = fewer tokens

## License

MIT
