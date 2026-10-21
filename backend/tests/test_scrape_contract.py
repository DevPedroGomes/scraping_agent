"""Contract of POST /api/v1/scrape: HTTP status, error body and honesty rules.

Two regressions this pins down:

1. A failed scrape used to come back as HTTP 200 with ``success: false``. Any
   client that trusts the status code (curl, fetch without a body check,
   monitoring) read a refused SSRF probe or a dead provider key as a success.
   Failures now carry a 4xx/5xx status, while the body keeps the
   ScrapeResponse shape plus a ``detail`` string, so both the current UI and a
   generic FastAPI-style client still find the message.

2. Without an output schema the response says ``validation_passed: null`` but
   the page promised "validated JSON", and the model filled a field the page
   did not state (a registration year it inferred from a launch date). The
   extraction prompt now tells the model to return null instead of guessing,
   and a required field that comes back null is reported as not found.

Nothing here touches the network: DNS, the browser and the provider are
replaced with fakes.
"""

import uuid

import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.models.schemas import OutputField
from app.services import scraper_service as svc_module
from app.services.scraper_service import (
    OutputValidator,
    _INJECTION_SYSTEM_PROMPT,
    scraper_service,
)

PUBLIC_IP = "93.184.216.34"


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture(autouse=True)
def isolated_budget(tmp_path, monkeypatch):
    monkeypatch.setenv("DAILY_BUDGET_PATH", str(tmp_path / "daily_budget.json"))
    monkeypatch.delenv("DEMO_KILL_SWITCH", raising=False)


@pytest.fixture
def session_headers(client):
    # Unique x-real-ip per test: the per-IP session limiter would otherwise
    # start refusing once the suite has opened a handful of sessions.
    ip = f"test-{uuid.uuid4().hex}"
    resp = client.post("/api/v1/session", headers={"x-real-ip": ip})
    assert resp.status_code == 200, resp.text
    return {"X-Session-Id": resp.json()["session_id"], "x-real-ip": ip}


@pytest.fixture
def public_dns(monkeypatch):
    """validate_url resolves DNS; tests stay offline by faking a public answer."""
    monkeypatch.setattr(
        svc_module, "validate_url", lambda url: (True, None, {PUBLIC_IP})
    )


def _payload(**overrides):
    body = {
        "url": "https://example.org/page",
        "prompt": "Extract the title",
        "model": "openai/gpt-oss-120b",
        "api_key": "user-supplied-key",
        "use_cache": False,
    }
    body.update(overrides)
    return body


def _assert_error_body(resp, status: int, code: str):
    assert resp.status_code == status, resp.text
    body = resp.json()
    assert body["success"] is False
    assert body["error_code"] == code
    assert isinstance(body["error"], str) and body["error"]
    # Generic clients read FastAPI's `detail`; it must carry the same message.
    assert body["detail"] == body["error"]
    return body


# --- HTTP status on failure ---------------------------------------------------


class TestFailureStatus:
    def test_private_address_is_403(self, client, session_headers):
        resp = client.post(
            "/api/v1/scrape",
            json=_payload(url="http://127.0.0.1/"),
            headers=session_headers,
        )
        _assert_error_body(resp, 403, "blocked_url")

    def test_bad_scheme_is_400(self, client, session_headers):
        resp = client.post(
            "/api/v1/scrape",
            json=_payload(url="ftp://example.org/file"),
            headers=session_headers,
        )
        _assert_error_body(resp, 400, "invalid_url")

    def test_paid_model_without_key_is_400(self, client, session_headers, public_dns):
        resp = client.post(
            "/api/v1/scrape",
            json=_payload(model="gpt-5-mini", api_key=None),
            headers=session_headers,
        )
        _assert_error_body(resp, 400, "api_key_required")

    def test_site_timeout_is_504(self, client, session_headers, public_dns, monkeypatch):
        async def slow(*args, **kwargs):
            raise TimeoutError("Timeout 30000ms exceeded")

        monkeypatch.setattr(scraper_service.browser, "fetch_page", slow)
        resp = client.post("/api/v1/scrape", json=_payload(), headers=session_headers)
        _assert_error_body(resp, 504, "site_timeout")

    def test_rejected_user_key_is_400(self, client, session_headers, public_dns, monkeypatch):
        async def page(*args, **kwargs):
            return "<html><body><h1>Hi</h1></body></html>"

        async def bad_key(*args, **kwargs):
            raise RuntimeError("Error code: 401 - invalid api_key")

        monkeypatch.setattr(scraper_service.browser, "fetch_page", page)
        monkeypatch.setattr(scraper_service.llm_providers, "extract", bad_key)
        resp = client.post("/api/v1/scrape", json=_payload(), headers=session_headers)
        _assert_error_body(resp, 400, "provider_auth")

    def test_provider_rate_limit_is_429(self, client, session_headers, public_dns, monkeypatch):
        async def page(*args, **kwargs):
            return "<html><body><h1>Hi</h1></body></html>"

        async def limited(*args, **kwargs):
            raise RuntimeError("Rate limit reached for model")

        monkeypatch.setattr(scraper_service.browser, "fetch_page", page)
        monkeypatch.setattr(scraper_service.llm_providers, "extract", limited)
        resp = client.post("/api/v1/scrape", json=_payload(), headers=session_headers)
        _assert_error_body(resp, 429, "provider_rate_limited")

    def test_unknown_failure_is_500_with_reference(
        self, client, session_headers, public_dns, monkeypatch
    ):
        async def boom(*args, **kwargs):
            raise RuntimeError("something internal and private")

        monkeypatch.setattr(scraper_service.browser, "fetch_page", boom)
        resp = client.post("/api/v1/scrape", json=_payload(), headers=session_headers)
        body = _assert_error_body(resp, 500, "internal_error")
        # The raw exception text never reaches the client.
        assert "private" not in body["error"]
        assert "Reference ID" in body["error"]

    def test_scrape_limit_is_429_with_scrape_body(self, client, session_headers, monkeypatch):
        from app.core.session_manager import session_manager

        monkeypatch.setattr(session_manager, "can_scrape", lambda sid: False)
        resp = client.post("/api/v1/scrape", json=_payload(), headers=session_headers)
        _assert_error_body(resp, 429, "scrape_limit_reached")

    def test_missing_session_is_still_401(self, client):
        resp = client.post("/api/v1/scrape", json=_payload())
        assert resp.status_code == 401


class TestSuccessStatus:
    def test_success_is_200_without_schema_is_marked_unvalidated(
        self, client, session_headers, public_dns, monkeypatch
    ):
        async def page(*args, **kwargs):
            return "<html><body><h1>Example Domain</h1></body></html>"

        async def extract(*args, **kwargs):
            return {"title": "Example Domain", "registration_year": None}, 42

        monkeypatch.setattr(scraper_service.browser, "fetch_page", page)
        monkeypatch.setattr(scraper_service.llm_providers, "extract", extract)
        resp = client.post("/api/v1/scrape", json=_payload(), headers=session_headers)
        assert resp.status_code == 200, resp.text
        body = resp.json()
        assert body["success"] is True
        assert body["error_code"] is None
        # No schema: the API must not claim the output was validated.
        assert body["validation_passed"] is None


# --- Honesty of the extraction ------------------------------------------------


class TestNoInventedFields:
    def test_system_prompt_demands_null_for_missing_data(self):
        text = _INJECTION_SYSTEM_PROMPT.lower()
        assert "null" in text
        assert "explicitly" in text
        assert "infer" in text

    def test_schema_prompt_demands_null_for_missing_fields(self):
        prompt = OutputValidator.build_schema_prompt(
            [OutputField(name="registration_year", type="number", required=True)]
        ).lower()
        assert "null" in prompt
        assert "explicitly" in prompt

    def test_required_field_returned_as_null_is_reported_not_found(self):
        fields = [OutputField(name="registration_year", type="number", required=True)]
        valid, errors = OutputValidator.validate({"registration_year": None}, fields)
        assert valid is False
        assert any("not found" in e for e in errors)

    def test_optional_field_returned_as_null_is_fine(self):
        fields = [OutputField(name="nickname", type="string", required=False)]
        valid, errors = OutputValidator.validate({"nickname": None}, fields)
        assert valid is True
        assert errors == []

    @pytest.mark.asyncio
    async def test_provider_call_carries_the_rule(self, monkeypatch):
        """The rule is useless unless it reaches the model on every provider call."""
        captured = {}

        class FakeCompletions:
            async def create(self, **kwargs):
                captured.update(kwargs)

                class Msg:
                    content = '{"registration_year": null}'

                class Choice:
                    message = Msg()

                class Usage:
                    total_tokens = 7

                class Resp:
                    choices = [Choice()]
                    usage = Usage()

                return Resp()

        class FakeClient:
            def __init__(self, *args, **kwargs):
                self.chat = type("Chat", (), {"completions": FakeCompletions()})()

        monkeypatch.setattr(svc_module.openai, "AsyncOpenAI", FakeClient)
        from app.models.schemas import ModelType

        data, tokens = await scraper_service.llm_providers._extract_groq(
            "content", "Extract the year", ModelType.GPT_OSS_120B, "key"
        )
        assert data == {"registration_year": None}
        system = captured["messages"][0]
        assert system["role"] == "system"
        assert "null" in system["content"].lower()
