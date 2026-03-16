"""
AI Web Scraper Service - v4.0.0

Features:
- Multi-provider LLM support (OpenAI, DeepSeek, Gemini, Anthropic, Grok, Groq)
- HTML to Markdown conversion (67% token reduction)
- Enhanced Playwright stealth mode (59 flags, resource blocking)
- Smart model routing by cost tier
- Persistent SQLite cache (survives restarts)
- SSRF protection via URL validation
- Content truncation per model context limits
- LLM retry with exponential backoff
- Structured output validation
- Page actions (click, scroll, wait, type)
"""

import asyncio
import json
import re
import time
from typing import Any
from datetime import datetime, timezone

from bs4 import BeautifulSoup
from markdownify import markdownify as md
from playwright.async_api import async_playwright

# AI Providers
import openai
import anthropic
import google.generativeai as genai

from app.models.schemas import (
    ScrapeRequest,
    ScrapeResponse,
    ModelType,
    ModelProvider,
    CostTier,
    PageAction,
    ActionType,
    OutputField,
    MODEL_PROVIDER_MAP,
    MODEL_PRICING,
    MODEL_CONTEXT_LIMITS,
)
from app.core.config import get_settings
from app.core.cache import SQLiteCache
from app.core.url_validator import validate_url
from app.core.constants import (
    BLOCKED_RESOURCE_TYPES,
    STEALTH_ARGS,
    DEFAULT_ARGS,
    HARMFUL_ARGS,
    get_random_user_agent,
    generate_convincing_referer,
)


class HTMLToMarkdown:
    """Converts HTML to clean Markdown for LLM consumption."""

    REMOVE_TAGS = [
        'script', 'style', 'nav', 'footer', 'header', 'aside',
        'noscript', 'iframe', 'svg', 'canvas', 'video', 'audio',
        'form', 'input', 'button', 'select', 'textarea'
    ]

    @staticmethod
    def convert(html: str) -> tuple[str, float]:
        """
        Convert HTML to Markdown.
        Returns (markdown, reduction_percentage)
        """
        original_length = len(html)

        soup = BeautifulSoup(html, 'html.parser')

        for tag in HTMLToMarkdown.REMOVE_TAGS:
            for element in soup.find_all(tag):
                element.decompose()

        for comment in soup.find_all(string=lambda text: isinstance(text, str) and text.strip().startswith('<!--')):
            comment.extract()

        markdown = md(
            str(soup),
            heading_style="ATX",
            bullets="-",
            strip=['a'],
        )

        markdown = re.sub(r'\n{3,}', '\n\n', markdown)
        markdown = re.sub(r' {2,}', ' ', markdown)
        markdown = markdown.strip()

        new_length = len(markdown)
        reduction = ((original_length - new_length) / original_length * 100) if original_length > 0 else 0

        return markdown, round(reduction, 1)


class SmartRouter:
    """Routes requests to the optimal model based on cost tier."""

    TIER_MODELS = {
        CostTier.FREE: [
            ModelType.LLAMA_3_3_70B,
            ModelType.LLAMA_3_1_8B,
        ],
        CostTier.BUDGET: [
            ModelType.DEEPSEEK_CHAT,
            ModelType.GEMINI_FLASH_LITE,
            ModelType.GPT_5_NANO,
            ModelType.GPT_4O_MINI,
            ModelType.GROK_FAST,
        ],
        CostTier.STANDARD: [
            ModelType.GEMINI_FLASH,
            ModelType.GPT_5_MINI,
            ModelType.CLAUDE_HAIKU,
        ],
        CostTier.PREMIUM: [
            ModelType.GPT_5,
            ModelType.CLAUDE_SONNET,
            ModelType.GEMINI_PRO,
            ModelType.GROK_4,
        ],
    }

    @staticmethod
    def select_model(cost_tier: CostTier, preferred_provider: ModelProvider | None = None) -> ModelType:
        models = SmartRouter.TIER_MODELS.get(cost_tier, SmartRouter.TIER_MODELS[CostTier.STANDARD])

        if preferred_provider:
            for model in models:
                if MODEL_PROVIDER_MAP.get(model) == preferred_provider:
                    return model

        return models[0]


class OutputValidator:
    """Validates LLM output against schema."""

    @staticmethod
    def build_schema_prompt(fields: list[OutputField]) -> str:
        schema_desc = "\n\nYou MUST return a JSON object with exactly these fields:\n"
        for field in fields:
            type_hint = field.type
            req = "required" if field.required else "optional"
            desc = f" - {field.description}" if field.description else ""
            schema_desc += f"- {field.name} ({type_hint}, {req}){desc}\n"
        schema_desc += "\nReturn ONLY valid JSON, no markdown or extra text."
        return schema_desc

    @staticmethod
    def validate(data: Any, fields: list[OutputField]) -> tuple[bool, list[str]]:
        errors = []

        if not isinstance(data, dict):
            return False, ["Output is not a JSON object"]

        for field in fields:
            if field.required and field.name not in data:
                errors.append(f"Missing required field: {field.name}")
                continue

            if field.name in data:
                value = data[field.name]
                type_valid = OutputValidator._check_type(value, field.type)
                if not type_valid:
                    errors.append(f"Field '{field.name}' has wrong type. Expected {field.type}")

        return len(errors) == 0, errors

    @staticmethod
    def _check_type(value: Any, expected_type: str) -> bool:
        type_map = {
            "string": str,
            "number": (int, float),
            "boolean": bool,
            "array": list,
            "object": dict
        }
        expected = type_map.get(expected_type, str)
        return isinstance(value, expected)


async def _intercept_route(route):
    """Block unnecessary resource types for performance."""
    if route.request.resource_type in BLOCKED_RESOURCE_TYPES:
        await route.abort()
    else:
        await route.continue_()


class PageActionExecutor:
    """Executes actions on page using Playwright with enhanced stealth mode."""

    @staticmethod
    async def execute_actions(
        url: str,
        actions: list[PageAction],
        stealth_mode: bool = True
    ) -> tuple[str, int]:
        """
        Execute actions on page and return final HTML content.
        Returns (html_content, actions_executed)
        """
        actions_executed = 0

        async with async_playwright() as p:
            launch_args = {
                "headless": True,
            }
            if stealth_mode:
                launch_args["args"] = list(DEFAULT_ARGS + STEALTH_ARGS)
                launch_args["ignore_default_args"] = list(HARMFUL_ARGS)

            browser = await p.chromium.launch(**launch_args)

            user_agent = get_random_user_agent() if stealth_mode else (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
            )

            context_options = {
                "viewport": {"width": 1920, "height": 1080},
                "screen": {"width": 1920, "height": 1080},
                "user_agent": user_agent,
                "color_scheme": "dark",
                "device_scale_factor": 2,
            }

            if stealth_mode:
                context_options.update({
                    "java_script_enabled": True,
                    "bypass_csp": True,
                    "ignore_https_errors": True,
                })

            context = await browser.new_context(**context_options)
            page = await context.new_page()

            # Block unnecessary resources
            if stealth_mode:
                await page.route("**/*", _intercept_route)

            if stealth_mode:
                await page.add_init_script("""
                    Object.defineProperty(navigator, 'webdriver', { get: () => undefined });
                    Object.defineProperty(navigator, 'plugins', {
                        get: () => [1, 2, 3, 4, 5]
                    });
                    Object.defineProperty(navigator, 'languages', {
                        get: () => ['en-US', 'en']
                    });
                    window.chrome = { runtime: {} };
                    const originalQuery = window.navigator.permissions.query;
                    window.navigator.permissions.query = (parameters) => (
                        parameters.name === 'notifications' ?
                            Promise.resolve({ state: Notification.permission }) :
                            originalQuery(parameters)
                    );
                """)

            try:
                referer = generate_convincing_referer(url) if stealth_mode else None
                goto_opts = {"wait_until": "networkidle", "timeout": 30000}
                if referer:
                    goto_opts["referer"] = referer

                await page.goto(url, **goto_opts)

                for action in actions:
                    try:
                        if action.action == ActionType.CLICK:
                            if action.selector:
                                await page.click(action.selector, timeout=5000)
                                await page.wait_for_timeout(action.wait_ms)
                                actions_executed += 1

                        elif action.action == ActionType.SCROLL:
                            direction = action.value or "down"
                            distance = 500 if direction == "down" else -500
                            await page.evaluate(f"window.scrollBy(0, {distance})")
                            await page.wait_for_timeout(action.wait_ms)
                            actions_executed += 1

                        elif action.action == ActionType.WAIT:
                            await page.wait_for_timeout(action.wait_ms)
                            actions_executed += 1

                        elif action.action == ActionType.TYPE:
                            if action.selector and action.value:
                                await page.fill(action.selector, action.value, timeout=5000)
                                await page.wait_for_timeout(action.wait_ms)
                                actions_executed += 1

                    except Exception as e:
                        print(f"Action {action.action} failed: {e}")
                        continue

                content = await page.content()

            finally:
                await browser.close()

        return content, actions_executed

    @staticmethod
    async def fetch_page(url: str, stealth_mode: bool = True) -> str:
        """Simple page fetch with enhanced stealth mode."""
        async with async_playwright() as p:
            launch_args = {"headless": True}
            if stealth_mode:
                launch_args["args"] = list(DEFAULT_ARGS + STEALTH_ARGS)
                launch_args["ignore_default_args"] = list(HARMFUL_ARGS)

            browser = await p.chromium.launch(**launch_args)

            user_agent = get_random_user_agent() if stealth_mode else (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
            )

            context_options = {
                "viewport": {"width": 1920, "height": 1080},
                "screen": {"width": 1920, "height": 1080},
                "user_agent": user_agent,
                "color_scheme": "dark",
                "device_scale_factor": 2,
            }

            if stealth_mode:
                context_options.update({
                    "java_script_enabled": True,
                    "bypass_csp": True,
                    "ignore_https_errors": True,
                })

            context = await browser.new_context(**context_options)
            page = await context.new_page()

            if stealth_mode:
                await page.route("**/*", _intercept_route)
                await page.add_init_script("""
                    Object.defineProperty(navigator, 'webdriver', { get: () => undefined });
                    Object.defineProperty(navigator, 'plugins', { get: () => [1, 2, 3, 4, 5] });
                    window.chrome = { runtime: {} };
                """)

            try:
                referer = generate_convincing_referer(url) if stealth_mode else None
                goto_opts = {"wait_until": "networkidle", "timeout": 30000}
                if referer:
                    goto_opts["referer"] = referer

                await page.goto(url, **goto_opts)
                content = await page.content()
            finally:
                await browser.close()

        return content


async def _retry_with_backoff(func, max_retries: int = 3, base_delay: float = 1.0):
    """Retry an async function with exponential backoff.

    Does NOT retry on auth errors (api_key, authentication, invalid key).
    """
    last_error = None
    for attempt in range(max_retries):
        try:
            return await func()
        except Exception as e:
            last_error = e
            error_msg = str(e).lower()
            # Don't retry auth errors
            if any(kw in error_msg for kw in ("api_key", "authentication", "invalid", "unauthorized", "forbidden")):
                raise
            if attempt < max_retries - 1:
                delay = base_delay * (2 ** attempt)
                await asyncio.sleep(delay)
    raise last_error


class LLMProviders:
    """Multi-provider LLM interface."""

    def __init__(self):
        self.settings = get_settings()

    async def extract(
        self,
        content: str,
        prompt: str,
        model: ModelType,
        api_key: str
    ) -> tuple[Any, int]:
        """Extract data using the specified model with retry."""
        provider = MODEL_PROVIDER_MAP.get(model)

        extract_map = {
            ModelProvider.GROQ: self._extract_groq,
            ModelProvider.OPENAI: self._extract_openai,
            ModelProvider.DEEPSEEK: self._extract_deepseek,
            ModelProvider.GEMINI: self._extract_gemini,
            ModelProvider.ANTHROPIC: self._extract_anthropic,
            ModelProvider.GROK: self._extract_grok,
        }

        extract_fn = extract_map.get(provider)
        if not extract_fn:
            raise ValueError(f"Unsupported provider for model: {model}")

        return await _retry_with_backoff(
            lambda: extract_fn(content, prompt, model, api_key)
        )

    async def _extract_openai(
        self, content: str, prompt: str, model: ModelType, api_key: str
    ) -> tuple[Any, int]:
        client = openai.AsyncOpenAI(api_key=api_key)
        messages = [
            {"role": "system", "content": "You are a data extraction assistant. Extract the requested information and return it as JSON."},
            {"role": "user", "content": f"{prompt}\n\nContent:\n{content}"}
        ]
        response = await client.chat.completions.create(
            model=model.value, messages=messages,
            response_format={"type": "json_object"}, temperature=0.1,
        )
        result_text = response.choices[0].message.content
        tokens_used = response.usage.total_tokens if response.usage else 0
        try:
            return json.loads(result_text), tokens_used
        except json.JSONDecodeError:
            return {"raw_text": result_text}, tokens_used

    async def _extract_deepseek(
        self, content: str, prompt: str, model: ModelType, api_key: str
    ) -> tuple[Any, int]:
        client = openai.AsyncOpenAI(api_key=api_key, base_url="https://api.deepseek.com/v1")
        messages = [
            {"role": "system", "content": "You are a data extraction assistant. Extract the requested information and return it as JSON."},
            {"role": "user", "content": f"{prompt}\n\nContent:\n{content}"}
        ]
        response = await client.chat.completions.create(
            model=model.value, messages=messages,
            response_format={"type": "json_object"}, temperature=0.1,
        )
        result_text = response.choices[0].message.content
        tokens_used = response.usage.total_tokens if response.usage else 0
        try:
            return json.loads(result_text), tokens_used
        except json.JSONDecodeError:
            return {"raw_text": result_text}, tokens_used

    async def _extract_gemini(
        self, content: str, prompt: str, model: ModelType, api_key: str
    ) -> tuple[Any, int]:
        genai.configure(api_key=api_key)
        gemini_model = genai.GenerativeModel(model.value)
        full_prompt = f"""You are a data extraction assistant. Extract the requested information and return it as valid JSON only.

{prompt}

Content:
{content}

Return only valid JSON, no markdown formatting."""

        response = await asyncio.get_event_loop().run_in_executor(
            None, lambda: gemini_model.generate_content(full_prompt)
        )
        result_text = response.text
        tokens_used = len(content.split()) + len(result_text.split())
        if result_text.startswith("```"):
            result_text = re.sub(r'^```(?:json)?\n?', '', result_text)
            result_text = re.sub(r'\n?```$', '', result_text)
        try:
            return json.loads(result_text), tokens_used
        except json.JSONDecodeError:
            return {"raw_text": result_text}, tokens_used

    async def _extract_anthropic(
        self, content: str, prompt: str, model: ModelType, api_key: str
    ) -> tuple[Any, int]:
        client = anthropic.AsyncAnthropic(api_key=api_key)
        message = await client.messages.create(
            model=model.value, max_tokens=4096,
            messages=[{
                "role": "user",
                "content": f"""You are a data extraction assistant. Extract the requested information and return it as valid JSON only.

{prompt}

Content:
{content}

Return only valid JSON, no explanation or markdown formatting."""
            }]
        )
        result_text = message.content[0].text
        tokens_used = message.usage.input_tokens + message.usage.output_tokens
        if result_text.startswith("```"):
            result_text = re.sub(r'^```(?:json)?\n?', '', result_text)
            result_text = re.sub(r'\n?```$', '', result_text)
        try:
            return json.loads(result_text), tokens_used
        except json.JSONDecodeError:
            return {"raw_text": result_text}, tokens_used

    async def _extract_grok(
        self, content: str, prompt: str, model: ModelType, api_key: str
    ) -> tuple[Any, int]:
        client = openai.AsyncOpenAI(api_key=api_key, base_url="https://api.x.ai/v1")
        messages = [
            {"role": "system", "content": "You are a data extraction assistant. Extract the requested information and return it as JSON."},
            {"role": "user", "content": f"{prompt}\n\nContent:\n{content}"}
        ]
        response = await client.chat.completions.create(
            model=model.value, messages=messages,
            response_format={"type": "json_object"}, temperature=0.1,
        )
        result_text = response.choices[0].message.content
        tokens_used = response.usage.total_tokens if response.usage else 0
        try:
            return json.loads(result_text), tokens_used
        except json.JSONDecodeError:
            return {"raw_text": result_text}, tokens_used

    async def _extract_groq(
        self, content: str, prompt: str, model: ModelType, api_key: str
    ) -> tuple[Any, int]:
        client = openai.AsyncOpenAI(api_key=api_key, base_url="https://api.groq.com/openai/v1")
        messages = [
            {"role": "system", "content": "You are a data extraction assistant. Extract the requested information and return it as valid JSON only, no markdown formatting."},
            {"role": "user", "content": f"{prompt}\n\nContent:\n{content}"}
        ]
        response = await client.chat.completions.create(
            model=model.value, messages=messages, temperature=0.1,
        )
        result_text = response.choices[0].message.content
        tokens_used = response.usage.total_tokens if response.usage else 0
        if result_text.startswith("```"):
            result_text = re.sub(r'^```(?:json)?\n?', '', result_text)
            result_text = re.sub(r'\n?```$', '', result_text)
        try:
            return json.loads(result_text), tokens_used
        except json.JSONDecodeError:
            return {"raw_text": result_text}, tokens_used


class ScraperService:
    """Main scraper service orchestrating all components."""

    def __init__(self):
        self.settings = get_settings()
        self.cache = SQLiteCache(
            db_path=self.settings.cache_db_path,
            default_ttl=3600,
        )
        self.validator = OutputValidator()
        self.action_executor = PageActionExecutor()
        self.html_converter = HTMLToMarkdown()
        self.llm_providers = LLMProviders()
        self.smart_router = SmartRouter()

    def _estimate_cost(self, model: ModelType, tokens: int) -> float:
        pricing = MODEL_PRICING.get(model, {"input": 0, "output": 0})
        input_tokens = int(tokens * 0.7)
        output_tokens = int(tokens * 0.3)
        cost = (input_tokens * pricing["input"] + output_tokens * pricing["output"]) / 1_000_000
        return round(cost, 6)

    @staticmethod
    def _truncate_content(content: str, model: ModelType, prompt: str) -> tuple[str, bool]:
        """Truncate content to fit model context window.

        Reserves 20% of context for prompt + output.
        Returns (content, was_truncated).
        """
        limit = MODEL_CONTEXT_LIMITS.get(model, 128_000 * 4)
        # Reserve 20% for prompt + output
        available = int(limit * 0.8) - len(prompt)
        if available <= 0:
            available = 1000

        if len(content) <= available:
            return content, False

        # Truncate at a clean boundary
        truncated = content[:available]
        last_newline = truncated.rfind('\n')
        if last_newline > available * 0.8:
            truncated = truncated[:last_newline]

        truncated += "\n\n[Content truncated to fit model context window]"
        return truncated, True

    async def scrape(self, request: ScrapeRequest) -> ScrapeResponse:
        """Main scrape method with all features."""
        start_time = time.time()
        cache_hit = False
        actions_executed = 0
        validation_passed = None
        validation_errors = None
        markdown_used = False
        token_reduction = None
        tokens_used = None
        estimated_cost = None
        content_truncated = False
        markdown_content = None
        fetch_time = None
        parse_time = None
        llm_time = None

        # Determine model to use
        model = request.model
        if request.cost_tier:
            model = self.smart_router.select_model(request.cost_tier)

        provider = MODEL_PROVIDER_MAP.get(model)

        # SSRF protection - validate URL before anything
        url_valid, url_error = validate_url(request.url)
        if not url_valid:
            return ScrapeResponse(
                success=False,
                error=url_error,
                execution_time=time.time() - start_time,
                model_used=model.value,
                provider_used=provider.value if provider else None,
            )

        # Resolve API key: user > env (per provider) > friendly error
        api_key = request.api_key
        if not api_key:
            if provider == ModelProvider.GROQ:
                api_key = self.settings.default_groq_api_key
            elif provider == ModelProvider.OPENAI:
                api_key = self.settings.default_openai_api_key

        if not api_key:
            suggestion = ""
            if provider != ModelProvider.GROQ:
                suggestion = " Try selecting a Groq model (FREE tier) which may not require an API key."
            return ScrapeResponse(
                success=False,
                error=f"API key is required for {provider.value if provider else 'unknown'} provider.{suggestion}",
                execution_time=time.time() - start_time,
                model_used=model.value,
                provider_used=provider.value if provider else None,
            )

        try:
            # Serialize actions for cache key
            actions_data = [a.model_dump() for a in request.actions] if request.actions else None

            # Check cache (now covers full response including LLM result)
            if request.use_cache:
                cached_response, cache_hit = self.cache.get(
                    request.url, actions_data, request.prompt, model.value
                )
                if cache_hit and cached_response:
                    cached_response["cache_hit"] = True
                    cached_response["execution_time"] = time.time() - start_time
                    return ScrapeResponse(**cached_response)

            # --- FETCH ---
            fetch_start = time.time()
            if request.actions:
                page_content, actions_executed = await self.action_executor.execute_actions(
                    request.url, request.actions, request.stealth_mode
                )
            else:
                page_content = await self.action_executor.fetch_page(
                    request.url, request.stealth_mode
                )
            fetch_time = round(time.time() - fetch_start, 3)

            # --- PARSE ---
            parse_start = time.time()
            content_for_llm = page_content
            if request.use_markdown:
                content_for_llm, token_reduction = self.html_converter.convert(page_content)
                markdown_used = True
                # Keep first 5KB for display
                markdown_content = content_for_llm[:5120] if content_for_llm else None

            # Build prompt with schema if provided
            prompt = request.prompt
            if request.output_schema:
                prompt += self.validator.build_schema_prompt(request.output_schema)

            # Truncate content to fit model context
            content_for_llm, content_truncated = self._truncate_content(
                content_for_llm, model, prompt
            )
            parse_time = round(time.time() - parse_start, 3)

            # --- LLM ---
            llm_start = time.time()
            result, tokens_used = await self.llm_providers.extract(
                content_for_llm, prompt, model, api_key
            )
            llm_time = round(time.time() - llm_start, 3)

            # Estimate cost
            if tokens_used:
                estimated_cost = self._estimate_cost(model, tokens_used)

            # Validate output if schema provided
            if request.output_schema and result:
                validation_passed, validation_errors = self.validator.validate(
                    result, request.output_schema
                )

            response_data = {
                "success": True,
                "data": result,
                "execution_time": time.time() - start_time,
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "model_used": model.value,
                "provider_used": provider.value if provider else None,
                "tokens_used": tokens_used,
                "estimated_cost": estimated_cost,
                "cache_hit": False,
                "markdown_used": markdown_used,
                "token_reduction": token_reduction,
                "actions_executed": actions_executed,
                "validation_passed": validation_passed,
                "validation_errors": validation_errors if validation_errors else None,
                "content_truncated": content_truncated,
                "markdown_content": markdown_content,
                "fetch_time": fetch_time,
                "parse_time": parse_time,
                "llm_time": llm_time,
            }

            # Cache complete response
            if request.use_cache:
                self.cache.set(
                    request.url, actions_data, request.prompt, model.value,
                    response_data, request.cache_ttl_minutes * 60
                )

            return ScrapeResponse(**response_data)

        except Exception as e:
            error_message = str(e)

            if "api_key" in error_message.lower() or "authentication" in error_message.lower():
                error_message = "Authentication error. Check your API key."
            elif "rate limit" in error_message.lower():
                error_message = "Rate limit exceeded. Wait a moment or try a different model."
            elif "timeout" in error_message.lower():
                error_message = "Timeout accessing the site. Try again."
            elif "quota" in error_message.lower():
                error_message = "API quota exceeded. Check your account limits."

            return ScrapeResponse(
                success=False,
                error=error_message,
                execution_time=time.time() - start_time,
                model_used=model.value,
                provider_used=provider.value if provider else None,
                cache_hit=cache_hit,
                markdown_used=markdown_used,
                actions_executed=actions_executed,
                fetch_time=fetch_time,
                parse_time=parse_time,
                llm_time=llm_time,
            )


# Singleton instance
scraper_service = ScraperService()
