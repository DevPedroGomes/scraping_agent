import asyncio
import hashlib
import time
import json
from typing import Any
from datetime import datetime, timedelta
from cachetools import TTLCache
from scrapegraphai.graphs import SmartScraperGraph
from playwright.async_api import async_playwright
from app.models.schemas import (
    ScrapeRequest,
    ScrapeResponse,
    ModelType,
    PageAction,
    ActionType,
    OutputField
)
from app.core.config import get_settings


class PageCache:
    """In-memory cache for page content"""

    def __init__(self, max_size: int = 100, default_ttl: int = 3600):
        self._cache: TTLCache = TTLCache(maxsize=max_size, ttl=default_ttl)
        self._metadata: dict[str, dict] = {}

    def _get_key(self, url: str, actions: list[PageAction] | None) -> str:
        """Generate cache key from URL and actions"""
        actions_str = json.dumps([a.model_dump() for a in actions]) if actions else ""
        key_data = f"{url}:{actions_str}"
        return hashlib.md5(key_data.encode()).hexdigest()

    def get(self, url: str, actions: list[PageAction] | None = None) -> tuple[str | None, bool]:
        """Get cached page content. Returns (content, cache_hit)"""
        key = self._get_key(url, actions)
        content = self._cache.get(key)
        return content, content is not None

    def set(self, url: str, content: str, actions: list[PageAction] | None = None, ttl: int | None = None):
        """Cache page content"""
        key = self._get_key(url, actions)
        self._cache[key] = content
        self._metadata[key] = {
            "url": url,
            "cached_at": datetime.utcnow(),
            "ttl": ttl or 3600
        }

    def clear(self):
        """Clear all cache"""
        self._cache.clear()
        self._metadata.clear()


class OutputValidator:
    """Validates LLM output against schema"""

    @staticmethod
    def build_schema_prompt(fields: list[OutputField]) -> str:
        """Build prompt addition for structured output"""
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
        """Validate data against schema. Returns (is_valid, errors)"""
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
        """Check if value matches expected type"""
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
    """Executes actions on page using Playwright"""

    @staticmethod
    async def execute_actions(url: str, actions: list[PageAction]) -> tuple[str, int]:
        """
        Execute actions on page and return final HTML content.
        Returns (html_content, actions_executed)
        """
        actions_executed = 0

        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page()

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
    async def fetch_page(url: str) -> str:
        """Simple page fetch without actions"""
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page()

            try:
                await page.goto(url, wait_until="networkidle", timeout=30000)
                content = await page.content()
            finally:
                await browser.close()

        return content


class ScraperService:
    def __init__(self):
        self.settings = get_settings()
        self.page_cache = PageCache(max_size=100, default_ttl=3600)
        self.validator = OutputValidator()
        self.action_executor = PageActionExecutor()

    def _get_graph_config(self, api_key: str, model: ModelType) -> dict:
        return {
            "llm": {
                "api_key": api_key,
                "model": model.value,
            },
        }

    async def scrape(self, request: ScrapeRequest) -> ScrapeResponse:
        start_time = time.time()
        cache_hit = False
        actions_executed = 0
        validation_passed = None
        validation_errors = None

        api_key = request.api_key or self.settings.default_openai_api_key
        if not api_key:
            return ScrapeResponse(
                success=False,
                error="API key is required. Provide an OpenAI API key.",
                execution_time=time.time() - start_time
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
                        request.actions
                    )
                else:
                    page_content = await self.action_executor.fetch_page(request.url)

                # Cache the content
                if request.use_cache:
                    self.page_cache.set(
                        request.url,
                        page_content,
                        request.actions,
                        request.cache_ttl_minutes * 60
                    )

            # Build prompt with schema if provided
            prompt = request.prompt
            if request.output_schema:
                prompt += self.validator.build_schema_prompt(request.output_schema)

            # Run scraper with page content
            config = self._get_graph_config(api_key, request.model)
            result = await asyncio.get_event_loop().run_in_executor(
                None,
                self._run_scraper_with_content,
                page_content,
                prompt,
                config
            )

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
                cache_hit=cache_hit,
                actions_executed=actions_executed,
                validation_passed=validation_passed,
                validation_errors=validation_errors if validation_errors else None
            )

        except Exception as e:
            error_message = str(e)

            if "api_key" in error_message.lower() or "authentication" in error_message.lower():
                error_message = "Authentication error. Check your API key."
            elif "rate limit" in error_message.lower():
                error_message = "Rate limit exceeded. Wait a moment."
            elif "timeout" in error_message.lower():
                error_message = "Timeout accessing the site. Try again."

            return ScrapeResponse(
                success=False,
                error=error_message,
                execution_time=time.time() - start_time,
                cache_hit=cache_hit,
                actions_executed=actions_executed
            )

    def _run_scraper_with_content(self, content: str, prompt: str, config: dict) -> Any:
        """Run scraper with pre-fetched HTML content"""
        scraper = SmartScraperGraph(
            prompt=prompt,
            source=content,
            config=config
        )
        return scraper.run()

    def _run_scraper(self, url: str, prompt: str, config: dict) -> Any:
        """Legacy method for direct URL scraping"""
        scraper = SmartScraperGraph(
            prompt=prompt,
            source=url,
            config=config
        )
        return scraper.run()


scraper_service = ScraperService()
