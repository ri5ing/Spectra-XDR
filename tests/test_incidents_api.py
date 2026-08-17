"""Integration tests for Security Incidents API routes and Database Health endpoint."""

from fastapi.testclient import TestClient
from backend.main import app

client = TestClient(app)


def test_database_health_endpoint():
    """Verify GET /api/v1/database/health returns 200 and healthy status."""
    response = client.get("/api/v1/database/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["service"] == "postgresql"


def test_incident_lifecycle_api():
    """Verify complete CRUD lifecycle of Incidents via REST API."""
    inc_payload = {
        "title": "SQL Injection Pattern Detected",
        "description": "WAF log matched known SQLi payload signature",
        "severity": "high",
        "status": "open"
    }

    # 1. Create Incident
    res_create = client.post("/api/v1/incidents", json=inc_payload)
    assert res_create.status_code == 201
    created = res_create.json()
    assert created["title"] == "SQL Injection Pattern Detected"
    assert created["severity"] == "high"
    assert created["status"] == "open"
    assert created["incident_id"].startswith("INC-")
    
    db_uuid = created["id"]
    human_id = created["incident_id"]

    # 2. List Incidents
    res_list = client.get("/api/v1/incidents?status=open&severity=high")
    assert res_list.status_code == 200
    incidents = res_list.json()
    assert len(incidents) >= 1
    assert incidents[0]["incident_id"] == human_id

    # 3. Get Incident by Human ID
    res_get = client.get(f"/api/v1/incidents/{human_id}")
    assert res_get.status_code == 200
    assert res_get.json()["id"] == db_uuid

    # 4. Patch Incident
    patch_payload = {"status": "investigating", "severity": "critical"}
    res_patch = client.patch(f"/api/v1/incidents/{human_id}", json=patch_payload)
    assert res_patch.status_code == 200
    patched = res_patch.json()
    assert patched["status"] == "investigating"
    assert patched["severity"] == "critical"

    # 5. Ingest an event and associate it with the incident
    event_payload = {
        "event_id": "sqli-event-001",
        "timestamp": "2026-08-17T18:45:00Z",
        "source": "wazuh",
        "agent_name": "web-waf",
        "raw_event": {}
    }
    res_event = client.post("/api/v1/events", json=event_payload)
    assert res_event.status_code == 201
    event_uuid = res_event.json()["id"]

    # Associate event with incident
    res_assoc = client.post(f"/api/v1/incidents/{human_id}/events/{event_uuid}")
    assert res_assoc.status_code == 200
    assoc_data = res_assoc.json()
    assert assoc_data["incident_id"] == db_uuid

    # Verify event appears in incident event list
    res_inc_updated = client.get(f"/api/v1/incidents/{human_id}")
    assert res_inc_updated.status_code == 200
    assert event_uuid in res_inc_updated.json()["events"]
