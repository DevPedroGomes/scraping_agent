"""Tests for SQLite persistent cache."""

import os
import time
import tempfile
import pytest
from app.core.cache import SQLiteCache


@pytest.fixture
def cache():
    """Create a temporary cache for testing."""
    fd, path = tempfile.mkstemp(suffix=".db")
    os.close(fd)
    c = SQLiteCache(db_path=path, default_ttl=3600)
    yield c
    c.clear()
    try:
        os.unlink(path)
    except OSError:
        pass


class TestSQLiteCache:
    def test_set_and_get(self, cache: SQLiteCache):
        cache.set("https://example.com", None, "extract titles", "gpt-5",
                   {"success": True, "data": {"title": "Hello"}})
        result, hit = cache.get("https://example.com", None, "extract titles", "gpt-5")
        assert hit is True
        assert result["success"] is True
        assert result["data"]["title"] == "Hello"

    def test_miss_returns_none(self, cache: SQLiteCache):
        result, hit = cache.get("https://nonexistent.com", None, "prompt", "model")
        assert hit is False
        assert result is None

    def test_different_prompts_different_keys(self, cache: SQLiteCache):
        cache.set("https://example.com", None, "prompt1", "gpt-5",
                   {"data": "result1"})
        cache.set("https://example.com", None, "prompt2", "gpt-5",
                   {"data": "result2"})

        r1, _ = cache.get("https://example.com", None, "prompt1", "gpt-5")
        r2, _ = cache.get("https://example.com", None, "prompt2", "gpt-5")
        assert r1["data"] == "result1"
        assert r2["data"] == "result2"

    def test_different_models_different_keys(self, cache: SQLiteCache):
        cache.set("https://example.com", None, "prompt", "gpt-5",
                   {"data": "gpt5"})
        cache.set("https://example.com", None, "prompt", "llama-70b",
                   {"data": "llama"})

        r1, _ = cache.get("https://example.com", None, "prompt", "gpt-5")
        r2, _ = cache.get("https://example.com", None, "prompt", "llama-70b")
        assert r1["data"] == "gpt5"
        assert r2["data"] == "llama"

    def test_ttl_expiry(self, cache: SQLiteCache):
        cache.set("https://example.com", None, "prompt", "model",
                   {"data": "value"}, ttl=1)
        time.sleep(1.1)
        result, hit = cache.get("https://example.com", None, "prompt", "model")
        assert hit is False
        assert result is None

    def test_cleanup_expired(self, cache: SQLiteCache):
        cache.set("https://example.com", None, "prompt", "model",
                   {"data": "value"}, ttl=1)
        time.sleep(1.1)
        deleted = cache.cleanup_expired()
        assert deleted >= 1

    def test_stats(self, cache: SQLiteCache):
        cache.set("https://a.com", None, "p", "m", {"data": 1})
        cache.set("https://b.com", None, "p", "m", {"data": 2})
        # Trigger hits
        cache.get("https://a.com", None, "p", "m")
        cache.get("https://a.com", None, "p", "m")

        stats = cache.stats()
        assert stats["total_entries"] == 2
        assert stats["total_hits"] == 2

    def test_clear(self, cache: SQLiteCache):
        cache.set("https://a.com", None, "p", "m", {"data": 1})
        cache.clear()
        stats = cache.stats()
        assert stats["total_entries"] == 0

    def test_actions_in_key(self, cache: SQLiteCache):
        actions = [{"action": "click", "selector": "#btn"}]
        cache.set("https://example.com", actions, "prompt", "model",
                   {"data": "with_actions"})

        # Without actions = miss
        r1, h1 = cache.get("https://example.com", None, "prompt", "model")
        assert h1 is False

        # With actions = hit
        r2, h2 = cache.get("https://example.com", actions, "prompt", "model")
        assert h2 is True
        assert r2["data"] == "with_actions"
