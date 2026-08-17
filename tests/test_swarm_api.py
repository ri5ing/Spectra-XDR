"""API integration tests for Swarm, Risk, Response, and AI Router endpoints."""

import pytest
from httpx import AsyncClient, ASGITransport
from backend.main import app


@pytest.mark.anyio
async def test_ai_status_endpoint():
    """Test /api/v1/ai/status endpoint."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.get("/api/v1/ai/status")
        assert response.status_code == 200
        data = response.json()
        assert "ollama_local" in data
        assert "gemini_cloud" in data
        assert "fallback_active" in data


@pytest.mark.anyio
async def test_response_actions_execution_endpoint():
    """Test /api/v1/response/actions/execute endpoint."""
    payload = {
        "action_type": "isolate_endpoint",
        "target": "001",
        "incident_id": "INC-000001",
        "approved_by": "Lead Analyst"
    }
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.post("/api/v1/response/actions/execute", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert data["action_type"] == "isolate_endpoint"
        assert data["target"] == "001"
