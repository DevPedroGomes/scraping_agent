import asyncio
from datetime import datetime, timedelta, timezone
from typing import Dict
from uuid import uuid4
from cachetools import TTLCache
from app.core.config import get_settings


class SessionManager:
    def __init__(self):
        settings = get_settings()
        self._sessions: TTLCache = TTLCache(
            maxsize=settings.max_concurrent_sessions,
            ttl=settings.session_timeout_minutes * 60
        )
        self._locks: Dict[str, asyncio.Lock] = {}
        self._request_counts: Dict[str, int] = {}
        self._last_requests: Dict[str, datetime] = {}

    @property
    def active_sessions_count(self) -> int:
        return len(self._sessions)

    @property
    def max_sessions(self) -> int:
        return get_settings().max_concurrent_sessions

    def create_session(self) -> str:
        if len(self._sessions) >= self.max_sessions:
            self._cleanup_oldest_session()

        session_id = str(uuid4())
        now = datetime.now(timezone.utc)
        self._sessions[session_id] = {
            "created_at": now,
            "last_activity": now,
            "requests_count": 0
        }
        self._locks[session_id] = asyncio.Lock()
        self._request_counts[session_id] = 0
        self._last_requests[session_id] = now

        return session_id

    def get_session(self, session_id: str) -> dict | None:
        return self._sessions.get(session_id)

    def update_session_activity(self, session_id: str) -> bool:
        if session_id in self._sessions:
            self._sessions[session_id]["last_activity"] = datetime.now(timezone.utc)
            self._sessions[session_id]["requests_count"] += 1
            return True
        return False

    def delete_session(self, session_id: str) -> bool:
        if session_id in self._sessions:
            del self._sessions[session_id]
            if session_id in self._locks:
                del self._locks[session_id]
            if session_id in self._request_counts:
                del self._request_counts[session_id]
            if session_id in self._last_requests:
                del self._last_requests[session_id]
            return True
        return False

    def can_make_request(self, session_id: str) -> bool:
        settings = get_settings()
        now = datetime.now(timezone.utc)

        if session_id not in self._last_requests:
            return True

        last_request = self._last_requests[session_id]
        time_diff = (now - last_request).total_seconds()

        if time_diff < 60:
            if self._request_counts.get(session_id, 0) >= settings.max_requests_per_minute:
                return False

        if time_diff >= 60:
            self._request_counts[session_id] = 0

        return True

    def record_request(self, session_id: str):
        now = datetime.now(timezone.utc)
        last_request = self._last_requests.get(session_id)

        if last_request and (now - last_request).total_seconds() >= 60:
            self._request_counts[session_id] = 0

        self._request_counts[session_id] = self._request_counts.get(session_id, 0) + 1
        self._last_requests[session_id] = now

    def get_lock(self, session_id: str) -> asyncio.Lock:
        if session_id not in self._locks:
            self._locks[session_id] = asyncio.Lock()
        return self._locks[session_id]

    def _cleanup_oldest_session(self):
        if not self._sessions:
            return

        oldest_session = min(
            self._sessions.items(),
            key=lambda x: x[1]["last_activity"]
        )[0]
        self.delete_session(oldest_session)

    def get_all_sessions_info(self) -> list[dict]:
        return [
            {
                "session_id": sid,
                "created_at": data["created_at"],
                "last_activity": data["last_activity"],
                "requests_count": data["requests_count"]
            }
            for sid, data in self._sessions.items()
        ]


session_manager = SessionManager()
