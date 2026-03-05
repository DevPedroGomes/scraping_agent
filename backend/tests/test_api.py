"""Tests for API endpoints."""

import pytest
from fastapi.testclient import TestClient
from app.main import app


@pytest.fixture
def client():
    return TestClient(app)


class TestHealthEndpoint:
    def test_health_returns_200(self, client: TestClient):
        response = client.get("/api/v1/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "active_sessions" in data
        assert "max_sessions" in data
        assert "version" in data

    def test_health_has_features(self, client: TestClient):
        response = client.get("/api/v1/health")
        data = response.json()
        assert isinstance(data["features"], list)


class TestSessionEndpoints:
    def test_create_session(self, client: TestClient):
        response = client.post("/api/v1/session")
        assert response.status_code == 200
        data = response.json()
        assert "session_id" in data
        assert "created_at" in data
        assert "scrape_count" in data
        assert "max_scrapes" in data
        assert data["scrape_count"] == 0

    def test_get_session(self, client: TestClient):
        # Create
        create_resp = client.post("/api/v1/session")
        session_id = create_resp.json()["session_id"]

        # Get
        response = client.get(f"/api/v1/session/{session_id}")
        assert response.status_code == 200
        data = response.json()
        assert data["session_id"] == session_id

    def test_get_nonexistent_session(self, client: TestClient):
        response = client.get("/api/v1/session/nonexistent-id")
        assert response.status_code == 404

    def test_delete_session(self, client: TestClient):
        create_resp = client.post("/api/v1/session")
        session_id = create_resp.json()["session_id"]

        response = client.delete(f"/api/v1/session/{session_id}")
        assert response.status_code == 200

        # Confirm deleted
        get_resp = client.get(f"/api/v1/session/{session_id}")
        assert get_resp.status_code == 404

    def test_delete_nonexistent_session(self, client: TestClient):
        response = client.delete("/api/v1/session/nonexistent-id")
        assert response.status_code == 404


class TestModelsEndpoint:
    def test_list_models(self, client: TestClient):
        response = client.get("/api/v1/models")
        assert response.status_code == 200
        data = response.json()
        assert "models" in data
        assert len(data["models"]) > 0
        assert "default_model" in data

    def test_model_has_required_fields(self, client: TestClient):
        response = client.get("/api/v1/models")
        model = response.json()["models"][0]
        assert "id" in model
        assert "name" in model
        assert "provider" in model
        assert "tier" in model
        assert "input_price" in model
        assert "output_price" in model


class TestExamplesEndpoint:
    def test_list_examples(self, client: TestClient):
        response = client.get("/api/v1/examples")
        assert response.status_code == 200
        data = response.json()
        assert "examples" in data
        assert len(data["examples"]) > 0

    def test_example_has_required_fields(self, client: TestClient):
        response = client.get("/api/v1/examples")
        example = response.json()["examples"][0]
        assert "id" in example
        assert "name" in example
        assert "url" in example
        assert "prompt" in example
        assert "model" in example


class TestRootEndpoint:
    def test_root(self, client: TestClient):
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "docs" in data
