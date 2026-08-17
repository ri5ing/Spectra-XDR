"""Integration tests for Persisted Security Events API routes."""

from fastapi.testclient import TestClient
from backend.main import app

client = TestClient(app)


def test_ingest_and_get_events():
    """Verify POST /api/v1/events ingests telemetry and GET /api/v1/events retrieves it."""
    payload = {
        "event_id": "api-ingest-alert-001",
        "timestamp": "2026-08-17T18:30:00Z",
        "source": "wazuh",
        "agent_id": "010",
        "agent_name": "db-server",
        "agent_ip": "10.0.0.50",
        "rule_id": "100200",
        "rule_level": 8,
        "rule_description": "PostgreSQL unauthorized connection attempt",
        "event_type": "postgresql",
        "location": "/var/log/postgresql/postgresql.log",
        "raw_event": {"foo": "bar"}
    }

    # Ingest event
    res_post = client.post("/api/v1/events", json=payload)
    assert res_post.status_code == 201
    created = res_post.json()
    assert created["event_id"] == "api-ingest-alert-001"
    assert created["agent_name"] == "db-server"
    assert "id" in created
    assert "created_at" in created

    # List events
    res_get = client.get("/api/v1/events?limit=10&offset=0")
    assert res_get.status_code == 200
    events = res_get.json()
    assert isinstance(events, list)
    assert len(events) >= 1
    
    # Filter by agent_id
    res_filtered = client.get("/api/v1/events?agent_id=010")
    assert res_filtered.status_code == 200
    filtered_events = res_filtered.json()
    assert len(filtered_events) >= 1
    assert filtered_events[0]["agent_id"] == "010"
