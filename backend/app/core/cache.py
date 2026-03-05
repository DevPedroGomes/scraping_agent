"""
Persistent SQLite cache with WAL mode (inspired by Scrapling storage.py).

Thread-safe, survives restarts, auto-evicts expired entries.
"""

import hashlib
import json
import sqlite3
import threading
import time
from typing import Any


class SQLiteCache:
    """Persistent cache backed by SQLite with WAL mode."""

    def __init__(self, db_path: str = "scrape_cache.db", default_ttl: int = 3600):
        self.db_path = db_path
        self.default_ttl = default_ttl
        self._lock = threading.RLock()
        self._init_db()

    def _init_db(self):
        with self._lock:
            conn = self._connect()
            conn.execute("""
                CREATE TABLE IF NOT EXISTS cache (
                    cache_key TEXT PRIMARY KEY,
                    url TEXT NOT NULL,
                    response_data TEXT NOT NULL,
                    created_at REAL NOT NULL,
                    ttl INTEGER NOT NULL,
                    hit_count INTEGER DEFAULT 0
                )
            """)
            conn.execute("CREATE INDEX IF NOT EXISTS idx_cache_url ON cache(url)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_cache_expiry ON cache(created_at, ttl)")
            conn.commit()
            conn.close()

    def _connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path, check_same_thread=False)
        conn.execute("PRAGMA journal_mode=WAL")
        conn.execute("PRAGMA busy_timeout=5000")
        conn.row_factory = sqlite3.Row
        return conn

    @staticmethod
    def _generate_key(url: str, actions: list | None, prompt: str, model: str) -> str:
        """Generate cache key from URL + actions + prompt + model."""
        actions_str = json.dumps(actions, sort_keys=True) if actions else ""
        key_data = f"{url}:{actions_str}:{prompt}:{model}"
        return hashlib.md5(key_data.encode()).hexdigest()

    def get(self, url: str, actions: list | None, prompt: str, model: str) -> tuple[dict | None, bool]:
        """
        Get cached response.

        Returns:
            (response_dict, True) on hit
            (None, False) on miss or expired
        """
        key = self._generate_key(url, actions, prompt, model)
        with self._lock:
            conn = self._connect()
            try:
                row = conn.execute(
                    "SELECT response_data, created_at, ttl FROM cache WHERE cache_key = ?",
                    (key,)
                ).fetchone()

                if row is None:
                    return None, False

                # Check expiry
                if time.time() - row["created_at"] > row["ttl"]:
                    conn.execute("DELETE FROM cache WHERE cache_key = ?", (key,))
                    conn.commit()
                    return None, False

                # Update hit count
                conn.execute(
                    "UPDATE cache SET hit_count = hit_count + 1 WHERE cache_key = ?",
                    (key,)
                )
                conn.commit()

                return json.loads(row["response_data"]), True
            finally:
                conn.close()

    def set(
        self,
        url: str,
        actions: list | None,
        prompt: str,
        model: str,
        response_data: dict[str, Any],
        ttl: int | None = None,
    ):
        """Cache a complete response."""
        key = self._generate_key(url, actions, prompt, model)
        ttl = ttl or self.default_ttl
        with self._lock:
            conn = self._connect()
            try:
                conn.execute(
                    """INSERT OR REPLACE INTO cache
                       (cache_key, url, response_data, created_at, ttl, hit_count)
                       VALUES (?, ?, ?, ?, ?, 0)""",
                    (key, url, json.dumps(response_data), time.time(), ttl)
                )
                conn.commit()
            finally:
                conn.close()

    def cleanup_expired(self) -> int:
        """Delete all expired entries. Returns number deleted."""
        with self._lock:
            conn = self._connect()
            try:
                now = time.time()
                cursor = conn.execute(
                    "DELETE FROM cache WHERE (? - created_at) > ttl",
                    (now,)
                )
                conn.commit()
                return cursor.rowcount
            finally:
                conn.close()

    def stats(self) -> dict[str, int]:
        """Return cache statistics."""
        with self._lock:
            conn = self._connect()
            try:
                row = conn.execute(
                    "SELECT COUNT(*) as total, COALESCE(SUM(hit_count), 0) as total_hits FROM cache"
                ).fetchone()
                return {"total_entries": row["total"], "total_hits": row["total_hits"]}
            finally:
                conn.close()

    def clear(self):
        """Clear all cache entries."""
        with self._lock:
            conn = self._connect()
            try:
                conn.execute("DELETE FROM cache")
                conn.commit()
            finally:
                conn.close()
