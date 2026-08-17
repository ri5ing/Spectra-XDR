"""Live Integration Tests for Real Wazuh Manager Deployment (Phase 2.5).

These tests run strictly when WAZUH_INTEGRATION_TESTS=true in settings/environment.
"""

import asyncio
import pytest
from fastapi.testclient import TestClient

from backend.config import settings
from backend.main import app
from backend.integrations.wazuh.client import WazuhClient

pytestmark = pytest.mark.skipif(
    not settings.WAZUH_INTEGRATION_TESTS,
    reason="Live Wazuh integration tests disabled. Set WAZUH_INTEGRATION_TESTS=true to enable."
)

client = TestClient(app)


def test_live_wazuh_authentication():
    """Verify JWT authentication against live Wazuh API server."""
    wazuh_client = WazuhClient(verify_ssl=settings.WAZUH_VERIFY_SSL)
    token = asyncio.run(wazuh_client.authenticate())
    assert token is not None
    assert isinstance(token, str)
    assert len(token) > 0


def test_live_wazuh_health():
    """Verify status check against live Wazuh API server."""
    wazuh_client = WazuhClient(verify_ssl=settings.WAZUH_VERIFY_SSL)
    status_data = asyncio.run(wazuh_client.health_check())
    assert status_data["status"] == "healthy"
    assert status_data["service"] == "wazuh"
    assert "details" in status_data


def test_live_wazuh_agents():
    """Verify agent inventory query against live Wazuh API server."""
    wazuh_client = WazuhClient(verify_ssl=settings.WAZUH_VERIFY_SSL)
    agents_data = asyncio.run(wazuh_client.get_agents(limit=5))
    assert "data" in agents_data
    assert agents_data["data"]["total_affected_items"] >= 1
    assert len(agents_data["data"]["affected_items"]) >= 1
    agent_000 = agents_data["data"]["affected_items"][0]
    assert agent_000["id"] == "000"


def test_live_wazuh_alerts():
    """Verify alert/log query against live Wazuh API server."""
    wazuh_client = WazuhClient(verify_ssl=settings.WAZUH_VERIFY_SSL)
    alerts_data = asyncio.run(wazuh_client.get_alerts(limit=5))
    assert "data" in alerts_data
    assert len(alerts_data["data"]["affected_items"]) >= 1


def test_live_spectra_wazuh_health_endpoint():
    """Verify GET /api/v1/wazuh/health against live Wazuh deployment."""
    response = client.get("/api/v1/wazuh/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["service"] == "wazuh"


def test_live_spectra_wazuh_agents_endpoint():
    """Verify GET /api/v1/wazuh/agents against live Wazuh deployment."""
    response = client.get("/api/v1/wazuh/agents?limit=5")
    assert response.status_code == 200
    data = response.json()
    assert "data" in data
    assert len(data["data"]["affected_items"]) >= 1


def test_live_spectra_wazuh_alerts_endpoint():
    """Verify GET /api/v1/wazuh/alerts against live Wazuh deployment."""
    response = client.get("/api/v1/wazuh/alerts?limit=5")
    assert response.status_code == 200
    data = response.json()
    assert "data" in data
    assert len(data["data"]["affected_items"]) >= 1
