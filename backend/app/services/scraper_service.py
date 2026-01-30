"""
AI Web Scraper Service - v3.0.0

Features:
- Multi-provider LLM support (OpenAI, DeepSeek, Gemini, Anthropic, Grok)
- HTML to Markdown conversion (67% token reduction)
- Playwright stealth mode (anti-bot detection)
- Smart model routing by cost tier
- Page caching with TTL
- Structured output validation
- Page actions (click, scroll, wait, type)
"""

import asyncio
import hashlib
import time
import json
import re
from typing import Any
from datetime import datetime, timezone
from cachetools import TTLCache
from bs4 import BeautifulSoup
from markdownify import markdownify as md

# Browser automation
from playwright.async_api import async_playwright

# AI Providers
import openai
import anthropic
import google.generativeai as genai
import httpx

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
)
from app.core.config import get_settings


class HTMLToMarkdown:
    """Converts HTML to clean Markdown for LLM consumption."""

    # Tags to remove completely
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

        # Parse HTML
        soup = BeautifulSoup(html, 'html.parser')

        # Remove unwanted tags
        for tag in HTMLToMarkdown.REMOVE_TAGS:
            for element in soup.find_all(tag):
                element.decompose()

        # Remove comments
        for comment in soup.find_all(string=lambda text: isinstance(text, str) and text.strip().startswith('<!--')):
            comment.extract()

        # Convert to markdown
        markdown = md(
            str(soup),
            heading_style="ATX",
            bullets="-",
            strip=['a'],  # Remove links but keep text
        )

        # Clean up excessive whitespace
        markdown = re.sub(r'\n{3,}', '\n\n', markdown)
        markdown = re.sub(r' {2,}', ' ', markdown)
        markdown = markdown.strip()

        new_length = len(markdown)
        reduction = ((original_length - new_length) / original_length * 100) if original_length > 0 else 0

        return markdown, round(reduction, 1)


class SmartRouter:
    """Routes requests to the optimal model based on cost tier."""

    # Default models per tier
    TIER_MODELS = {
        CostTier.FREE: [
            ModelType.LLAMA_3_3_70B,
            ModelType.MIXTRAL_8X7B,
            ModelType.LLAMA_3_1_8B,
            ModelType.GEMMA_2_9B,
        ],
        CostTier.BUDGET: [
            ModelType.DEEPSEEK_CHAT,
            ModelType.GEMINI_FLASH_LITE,
            ModelType.GPT_5_NANO,
            ModelType.GROK_FAST,
        ],
        CostTier.STANDARD: [
            ModelType.DEEPSEEK_V3,
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
        """Select the best model for a given cost tier."""
        models = SmartRouter.TIER_MODELS.get(cost_tier, SmartRouter.TIER_MODELS[CostTier.STANDARD])

        if preferred_provider:
            # Try to find a model from the preferred provider
            for model in models:
                if MODEL_PROVIDER_MAP.get(model) == preferred_provider:
                    return model

        # Return first (cheapest) model in tier
        return models[0]


class PageCache:
    """In-memory cache for page content."""

    def __init__(self, max_size: int = 100, default_ttl: int = 3600):
        self._cache: TTLCache = TTLCache(maxsize=max_size, ttl=default_ttl)
        self._metadata: dict[str, dict] = {}

    def _get_key(self, url: str, actions: list[PageAction] | None) -> str:
        """Generate cache key from URL and actions."""
        actions_str = json.dumps([a.model_dump() for a in actions]) if actions else ""
        key_data = f"{url}:{actions_str}"
        return hashlib.md5(key_data.encode()).hexdigest()

    def get(self, url: str, actions: list[PageAction] | None = None) -> tuple[str | None, bool]:
        """Get cached page content. Returns (content, cache_hit)."""
        key = self._get_key(url, actions)
        content = self._cache.get(key)
        return content, content is not None

    def set(self, url: str, content: str, actions: list[PageAction] | None = None, ttl: int | None = None):
        """Cache page content."""
        key = self._get_key(url, actions)
        self._cache[key] = content
        self._metadata[key] = {
            "url": url,
            "cached_at": datetime.now(timezone.utc),
            "ttl": ttl or 3600
        }

    def clear(self):
        """Clear all cache."""
        self._cache.clear()
        self._metadata.clear()


class OutputValidator:
    """Validates LLM output against schema."""

    @staticmethod
    def build_schema_prompt(fields: list[OutputField]) -> str:
        """Build prompt addition for structured output."""
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
        """Validate data against schema. Returns (is_valid, errors)."""
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
        """Check if value matches expected type."""
        type_map = {
            "string": str,
            "number": (int, float),
            "boolean": bool,
            "array": list,
            "object": dict
        }
        expected = type_map.get(expected_type, str)
        return isinstance(value, expected)


class PageActionExecutor:
    """Executes actions on page using Playwright with stealth mode."""

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
            # Launch browser
            browser = await p.chromium.launch(headless=True)

            # Create context with stealth settings
            context_options = {
                "viewport": {"width": 1920, "height": 1080},
                "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
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
                # Add stealth scripts
                await page.add_init_script("""
                    // Override webdriver property
                    Object.defineProperty(navigator, 'webdriver', {
                        get: () => undefined
                    });

                    // Override plugins
                    Object.defineProperty(navigator, 'plugins', {
                        get: () => [1, 2, 3, 4, 5]
                    });

                    // Override languages
                    Object.defineProperty(navigator, 'languages', {
                        get: () => ['en-US', 'en']
                    });

                    // Override chrome
                    window.chrome = {
                        runtime: {}
                    };

                    // Override permissions
                    const originalQuery = window.navigator.permissions.query;
                    window.navigator.permissions.query = (parameters) => (
                        parameters.name === 'notifications' ?
                            Promise.resolve({ state: Notification.permission }) :
                            originalQuery(parameters)
                    );
                """)

            try:
                await page.goto(url, wait_until="networkidle", timeout=30000)

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
        """Simple page fetch with optional stealth mode."""
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)

            context_options = {
                "viewport": {"width": 1920, "height": 1080},
                "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
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
                await page.add_init_script("""
                    Object.defineProperty(navigator, 'webdriver', { get: () => undefined });
                    Object.defineProperty(navigator, 'plugins', { get: () => [1, 2, 3, 4, 5] });
                    window.chrome = { runtime: {} };
                """)

            try:
                await page.goto(url, wait_until="networkidle", timeout=30000)
                content = await page.content()
            finally:
                await browser.close()

        return content


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
        """
        Extract data using the specified model.
        Returns (extracted_data, tokens_used)
        """
        provider = MODEL_PROVIDER_MAP.get(model)

        if provider == ModelProvider.GROQ:
            return await self._extract_groq(content, prompt, model, api_key)
        elif provider == ModelProvider.OPENAI:
            return await self._extract_openai(content, prompt, model, api_key)
        elif provider == ModelProvider.DEEPSEEK:
            return await self._extract_deepseek(content, prompt, model, api_key)
        elif provider == ModelProvider.GEMINI:
            return await self._extract_gemini(content, prompt, model, api_key)
        elif provider == ModelProvider.ANTHROPIC:
            return await self._extract_anthropic(content, prompt, model, api_key)
        elif provider == ModelProvider.GROK:
            return await self._extract_grok(content, prompt, model, api_key)
        else:
            raise ValueError(f"Unsupported provider for model: {model}")

    async def _extract_openai(
        self,
        content: str,
        prompt: str,
        model: ModelType,
        api_key: str
    ) -> tuple[Any, int]:
        """Extract using OpenAI models."""
        client = openai.AsyncOpenAI(api_key=api_key)

        messages = [
            {"role": "system", "content": "You are a data extraction assistant. Extract the requested information and return it as JSON."},
            {"role": "user", "content": f"{prompt}\n\nContent:\n{content}"}
        ]

        response = await client.chat.completions.create(
            model=model.value,
            messages=messages,
            response_format={"type": "json_object"},
            temperature=0.1,
        )

        result_text = response.choices[0].message.content
        tokens_used = response.usage.total_tokens if response.usage else 0

        try:
            return json.loads(result_text), tokens_used
        except json.JSONDecodeError:
            return {"raw_text": result_text}, tokens_used

    async def _extract_deepseek(
        self,
        content: str,
        prompt: str,
        model: ModelType,
        api_key: str
    ) -> tuple[Any, int]:
        """Extract using DeepSeek models (OpenAI-compatible API)."""
        client = openai.AsyncOpenAI(
            api_key=api_key,
            base_url="https://api.deepseek.com/v1"
        )

        messages = [
            {"role": "system", "content": "You are a data extraction assistant. Extract the requested information and return it as JSON."},
            {"role": "user", "content": f"{prompt}\n\nContent:\n{content}"}
        ]

        response = await client.chat.completions.create(
            model=model.value,
            messages=messages,
            response_format={"type": "json_object"},
            temperature=0.1,
        )

        result_text = response.choices[0].message.content
        tokens_used = response.usage.total_tokens if response.usage else 0

        try:
            return json.loads(result_text), tokens_used
        except json.JSONDecodeError:
            return {"raw_text": result_text}, tokens_used

    async def _extract_gemini(
        self,
        content: str,
        prompt: str,
        model: ModelType,
        api_key: str
    ) -> tuple[Any, int]:
        """Extract using Google Gemini models."""
        genai.configure(api_key=api_key)

        gemini_model = genai.GenerativeModel(model.value)

        full_prompt = f"""You are a data extraction assistant. Extract the requested information and return it as valid JSON only.

{prompt}

Content:
{content}

Return only valid JSON, no markdown formatting."""

        response = await asyncio.get_event_loop().run_in_executor(
            None,
            lambda: gemini_model.generate_content(full_prompt)
        )

        result_text = response.text
        # Estimate tokens (Gemini doesn't always return token count)
        tokens_used = len(content.split()) + len(result_text.split())

        # Clean up response (remove markdown if present)
        if result_text.startswith("```"):
            result_text = re.sub(r'^```(?:json)?\n?', '', result_text)
            result_text = re.sub(r'\n?```$', '', result_text)

        try:
            return json.loads(result_text), tokens_used
        except json.JSONDecodeError:
            return {"raw_text": result_text}, tokens_used

    async def _extract_anthropic(
        self,
        content: str,
        prompt: str,
        model: ModelType,
        api_key: str
    ) -> tuple[Any, int]:
        """Extract using Anthropic Claude models."""
        client = anthropic.AsyncAnthropic(api_key=api_key)

        message = await client.messages.create(
            model=model.value,
            max_tokens=4096,
            messages=[
                {
                    "role": "user",
                    "content": f"""You are a data extraction assistant. Extract the requested information and return it as valid JSON only.

{prompt}

Content:
{content}

Return only valid JSON, no explanation or markdown formatting."""
                }
            ]
        )

        result_text = message.content[0].text
        tokens_used = message.usage.input_tokens + message.usage.output_tokens

        # Clean up response
        if result_text.startswith("```"):
            result_text = re.sub(r'^```(?:json)?\n?', '', result_text)
            result_text = re.sub(r'\n?```$', '', result_text)

        try:
            return json.loads(result_text), tokens_used
        except json.JSONDecodeError:
            return {"raw_text": result_text}, tokens_used

    async def _extract_grok(
        self,
        content: str,
        prompt: str,
        model: ModelType,
        api_key: str
    ) -> tuple[Any, int]:
        """Extract using xAI Grok models (OpenAI-compatible API)."""
        client = openai.AsyncOpenAI(
            api_key=api_key,
            base_url="https://api.x.ai/v1"
        )

        messages = [
            {"role": "system", "content": "You are a data extraction assistant. Extract the requested information and return it as JSON."},
            {"role": "user", "content": f"{prompt}\n\nContent:\n{content}"}
        ]

        response = await client.chat.completions.create(
            model=model.value,
            messages=messages,
            response_format={"type": "json_object"},
            temperature=0.1,
        )

        result_text = response.choices[0].message.content
        tokens_used = response.usage.total_tokens if response.usage else 0

        try:
            return json.loads(result_text), tokens_used
        except json.JSONDecodeError:
            return {"raw_text": result_text}, tokens_used

    async def _extract_groq(
        self,
        content: str,
        prompt: str,
        model: ModelType,
        api_key: str
    ) -> tuple[Any, int]:
        """Extract using Groq with open source models (FREE - OpenAI-compatible API)."""
        client = openai.AsyncOpenAI(
            api_key=api_key,
            base_url="https://api.groq.com/openai/v1"
        )

        messages = [
            {"role": "system", "content": "You are a data extraction assistant. Extract the requested information and return it as valid JSON only, no markdown formatting."},
            {"role": "user", "content": f"{prompt}\n\nContent:\n{content}"}
        ]

        response = await client.chat.completions.create(
            model=model.value,
            messages=messages,
            temperature=0.1,
        )

        result_text = response.choices[0].message.content
        tokens_used = response.usage.total_tokens if response.usage else 0

        # Clean up response (remove markdown if present)
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
        self.page_cache = PageCache(max_size=100, default_ttl=3600)
        self.validator = OutputValidator()
        self.action_executor = PageActionExecutor()
        self.html_converter = HTMLToMarkdown()
        self.llm_providers = LLMProviders()
        self.smart_router = SmartRouter()

    def _estimate_cost(self, model: ModelType, tokens: int) -> float:
        """Estimate cost based on model and token usage."""
        pricing = MODEL_PRICING.get(model, {"input": 0, "output": 0})
        # Assume 70% input, 30% output
        input_tokens = int(tokens * 0.7)
        output_tokens = int(tokens * 0.3)
        cost = (input_tokens * pricing["input"] + output_tokens * pricing["output"]) / 1_000_000
        return round(cost, 6)

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

        # Determine model to use
        model = request.model
        if request.cost_tier:
            model = self.smart_router.select_model(request.cost_tier)

        provider = MODEL_PROVIDER_MAP.get(model)

        # Get API key
        api_key = request.api_key
        if not api_key:
            # Check for default keys based on provider
            if provider == ModelProvider.OPENAI:
                api_key = self.settings.default_openai_api_key
            # Add other default keys as needed

        if not api_key:
            return ScrapeResponse(
                success=False,
                error=f"API key is required for {provider.value if provider else 'unknown'} provider.",
                execution_time=time.time() - start_time,
                model_used=model.value,
                provider_used=provider.value if provider else None
            )

        try:
            # Check cache first
            page_content = None
            if request.use_cache:
                page_content, cache_hit = self.page_cache.get(request.url, request.actions)

            # Fetch page if not cached
            if not page_content:
                if request.actions:
                    page_content, actions_executed = await self.action_executor.execute_actions(
                        request.url,
                        request.actions,
                        request.stealth_mode
                    )
                else:
                    page_content = await self.action_executor.fetch_page(
                        request.url,
                        request.stealth_mode
                    )

                # Cache the content
                if request.use_cache:
                    self.page_cache.set(
                        request.url,
                        page_content,
                        request.actions,
                        request.cache_ttl_minutes * 60
                    )

            # Convert to Markdown if requested
            content_for_llm = page_content
            if request.use_markdown:
                content_for_llm, token_reduction = self.html_converter.convert(page_content)
                markdown_used = True

            # Build prompt with schema if provided
            prompt = request.prompt
            if request.output_schema:
                prompt += self.validator.build_schema_prompt(request.output_schema)

            # Extract data using LLM
            result, tokens_used = await self.llm_providers.extract(
                content_for_llm,
                prompt,
                model,
                api_key
            )

            # Estimate cost
            if tokens_used:
                estimated_cost = self._estimate_cost(model, tokens_used)

            # Validate output if schema provided
            if request.output_schema and result:
                validation_passed, validation_errors = self.validator.validate(
                    result,
                    request.output_schema
                )

            return ScrapeResponse(
                success=True,
                data=result,
                execution_time=time.time() - start_time,
                model_used=model.value,
                provider_used=provider.value if provider else None,
                tokens_used=tokens_used,
                estimated_cost=estimated_cost,
                cache_hit=cache_hit,
                markdown_used=markdown_used,
                token_reduction=token_reduction,
                actions_executed=actions_executed,
                validation_passed=validation_passed,
                validation_errors=validation_errors if validation_errors else None
            )

        except Exception as e:
            error_message = str(e)

            # Friendly error messages
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
                actions_executed=actions_executed
            )


# Singleton instance
scraper_service = ScraperService()
