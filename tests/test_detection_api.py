"""Integration tests for Detection and Incident Evidence APIs."""

from fastapi.testclient import TestClient
from backend.main import app

client = TestClient(app)


def test_list_detection_rules():
    """Verify GET /api/v1/detections/rules endpoint."""
    response = client.get("/api/v1/detections/rules")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 5
    rule_ids = [r["rule_id"] for r in data]
    assert "DET-001" in rule_ids
    assert "DET-002" in rule_ids


def test_run_detection_pipeline_and_evidence():
    """Verify triggering POST /api/v1/detections/run and querying GET /incidents/{id}/evidence."""
    # 1. Ingest event that matches DET-003 (PowerShell)
    evt_payload = {
        "event_id": "det-api-event-1",
        "timestamp": "2026-08-17T21:30:00Z",
        "source": "wazuh",
        "agent_id": "007",
        "agent_name": "workstation-07",
        "rule_id": "91800",
        "rule_level": 7,
        "rule_description": "PowerShell script execution detected",
        "raw_event": {"full_log": "powershell -c Get-Process"}
    }
    create_evt = client.post("/api/v1/events", json=evt_payload)
    assert create_evt.status_code == 201

    # 2. Run detection pipeline
    run_resp = client.post("/api/v1/detections/run", json={"rule_id": "DET-003"})
    assert run_resp.status_code == 200
    run_result = run_resp.json()
    assert run_result["rules_evaluated"] >= 1
    assert run_result["matches_generated"] >= 1

    # 3. Query generated detection matches
    matches_resp = client.get("/api/v1/detections/matches")
    assert matches_resp.status_code == 200
    matches = matches_resp.json()
    assert len(matches) >= 1
    incident_uuid = matches[0]["incident_id"]
    assert incident_uuid is not None

    # 4. Query incident evidence
    ev_resp = client.get(f"/api/v1/incidents/{incident_uuid}/evidence")
    assert ev_resp.status_code == 200
    evidence_list = ev_resp.json()
    assert len(evidence_list) >= 1
    ev_types = [e["evidence_type"] for e in evidence_list]
    assert "event" in ev_types or "detection" in ev_types
