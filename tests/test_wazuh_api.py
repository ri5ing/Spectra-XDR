"""Integration tests for SPECTRA-XDR Wazuh and Normalized Events API routes."""

import pytest
from unittest.mock import AsyncMock, MagicMock
from fastapi.testclient import TestClient

from backend.main import app
from backend.api.routes.wazuh import get_wazuh_client
from backend.integrations.wazuh.exceptions import WazuhConnectionError

client = TestClient(app)


def test_phase0_endpoints_remain_functional():
    """Verify Phase 0 endpoints GET / and GET /health still function as expected."""
    res_root = client.get("/")
    assert res_root.status_code == 200
    assert res_root.json()["app"] == "SPECTRA-XDR"

    res_health = client.get("/health")
    assert res_health.status_code == 200
    assert res_health.json()["status"] == "healthy"


def test_wazuh_health_endpoint_success():
    """Verify GET /api/v1/wazuh/health returns 200 when Wazuh is reachable."""
    mock_wazuh_client = MagicMock()
    mock_wazuh_client.health_check = AsyncMock(return_value={
        "status": "healthy",
        "service": "wazuh"
    })

    app.dependency_overrides[get_wazuh_client] = lambda: mock_wazuh_client

    try:
        response = client.get("/api/v1/wazuh/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["service"] == "wazuh"
    finally:
        app.dependency_overrides.clear()


def test_wazuh_health_endpoint_unavailable():
    """Verify GET /api/v1/wazuh/health returns HTTP 503 when Wazuh is down."""
    mock_wazuh_client = MagicMock()
    mock_wazuh_client.health_check = AsyncMock(side_effect=WazuhConnectionError("Could not connect to Wazuh"))

    app.dependency_overrides[get_wazuh_client] = lambda: mock_wazuh_client

    try:
        response = client.get("/api/v1/wazuh/health")
        assert response.status_code == 503
        data = response.json()
        assert "detail" in data
        assert "Wazuh service unavailable" in data["detail"]
    finally:
        app.dependency_overrides.clear()


def test_wazuh_agents_endpoint():
    """Verify GET /api/v1/wazuh/agents returns agent list JSON."""
    mock_wazuh_client = MagicMock()
    mock_wazuh_client.get_agents = AsyncMock(return_value={
        "data": {
            "total_affected_items": 1,
            "affected_items": [{"id": "001", "name": "test-agent"}]
        }
    })

    app.dependency_overrides[get_wazuh_client] = lambda: mock_wazuh_client

    try:
        response = client.get("/api/v1/wazuh/agents?limit=10&offset=0")
        assert response.status_code == 200
        data = response.json()
        assert "data" in data
        assert data["data"]["total_affected_items"] == 1
    finally:
        app.dependency_overrides.clear()


def test_wazuh_alerts_endpoint():
    """Verify GET /api/v1/wazuh/alerts returns raw alert items."""
    mock_wazuh_client = MagicMock()
    mock_wazuh_client.get_alerts = AsyncMock(return_value={
        "data": {
            "total_affected_items": 1,
            "affected_items": [{"id": "alert-100", "timestamp": "2026-08-17T00:00:00Z"}]
        }
    })

    app.dependency_overrides[get_wazuh_client] = lambda: mock_wazuh_client

    try:
        response = client.get("/api/v1/wazuh/alerts?limit=5&offset=0")
        assert response.status_code == 200
        data = response.json()
        assert "data" in data
        assert len(data["data"]["affected_items"]) == 1
    finally:
        app.dependency_overrides.clear()


def test_normalized_events_endpoint():
    """Verify GET /api/v1/events normalizes Wazuh alerts into NormalizedEvents."""
    mock_wazuh_client = MagicMock()
    mock_wazuh_client.get_alerts = AsyncMock(return_value={
        "data": {
            "total_affected_items": 1,
            "affected_items": [
                {
                    "id": "alert-777",
                    "timestamp": "2026-08-17T15:00:00Z",
                    "agent": {"id": "005", "name": "web-server"},
                    "rule": {"id": 1001, "level": 7, "description": "Web attack detected"}
                }
            ]
        }
    })

    app.dependency_overrides[get_wazuh_client] = lambda: mock_wazuh_client

    try:
        response = client.get("/api/v1/events?limit=10&offset=0")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 1
        event = data[0]
        assert event["event_id"] == "alert-777"
        assert event["source"] == "wazuh"
        assert event["agent_name"] == "web-server"
        assert event["rule_id"] == "1001"
        assert event["rule_level"] == 7
        assert "raw_event" in event
    finally:
        app.dependency_overrides.clear()
