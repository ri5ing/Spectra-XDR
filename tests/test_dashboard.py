"""Integration tests for Backend Dashboard Aggregation API."""

from fastapi.testclient import TestClient
from backend.main import app

client = TestClient(app)


def test_dashboard_summary_endpoint():
    """Verify GET /api/v1/dashboard/summary returns aggregated counts and posture metrics."""
    # 1. Query dashboard summary
    response = client.get("/api/v1/dashboard/summary")
    assert response.status_code == 200
    data = response.json()

    assert "incidents" in data
    assert "severity" in data
    assert "detections" in data
    assert "intelligence" in data
    assert "wazuh" in data
    assert "recent_incidents" in data

    inc = data["incidents"]
    assert "total" in inc
    assert "open" in inc
    assert "investigating" in inc
    assert "contained" in inc
    assert "resolved" in inc
    assert "closed" in inc

    sev = data["severity"]
    assert "critical" in sev
    assert "high" in sev
    assert "medium" in sev
    assert "low" in sev

    # Ensure no credentials or JWT tokens exist in payload
    raw_str = str(data).lower()
    assert "wazuh_password" not in raw_str
    assert "authorization" not in raw_str
    assert "bearer" not in raw_str
