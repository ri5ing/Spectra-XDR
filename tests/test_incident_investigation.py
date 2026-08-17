"""Integration & Security tests for Incident Investigation, Analyst Workflows, Timelines, and Audit Logs."""

import sys
from fastapi.testclient import TestClient
from backend.main import app

client = TestClient(app)


def test_no_llm_or_ai_imported_in_investigation():
    """Security Assertion: Verify no AI/LLM packages (openai, langchain, langgraph) are imported in investigation service."""
    investigation_modules = [m for m in sys.modules.keys() if "investigation" in m]
    for mod_name in investigation_modules:
        mod = sys.modules[mod_name]
        for attr in dir(mod):
            val = str(getattr(mod, attr, "")).lower()
            assert "openai" not in val
            assert "langchain" not in val
            assert "langgraph" not in val
            assert "gemini" not in val


def test_full_incident_investigation_lifecycle():
    """Verify complete investigation workflow: create event -> detection -> incident -> summary/timeline/iocs/mitre/notes/audit."""
    # 1. Ingest event matching DET-003
    evt_payload = {
        "event_id": "inv-test-event-100",
        "timestamp": "2026-08-17T22:00:00Z",
        "source": "wazuh",
        "agent_id": "007",
        "agent_name": "workstation-07",
        "rule_id": "91800",
        "rule_description": "PowerShell script execution detected",
        "raw_event": {"full_log": "powershell -c Get-Service"}
    }
    create_evt = client.post("/api/v1/events", json=evt_payload)
    assert create_evt.status_code == 201

    # 2. Run detection engine
    run_resp = client.post("/api/v1/detections/run", json={"rule_id": "DET-003"})
    assert run_resp.status_code == 200

    # 3. Get matches & incident ID
    matches = client.get("/api/v1/detections/matches").json()
    assert len(matches) >= 1
    inc_id = matches[0]["incident_id"]
    assert inc_id is not None

    # 4. Get Incident Summary
    summary_resp = client.get(f"/api/v1/incidents/{inc_id}/summary")
    assert summary_resp.status_code == 200
    summary = summary_resp.json()
    assert summary["event_count"] >= 1
    assert summary["detection_match_count"] >= 1
    assert "007" in summary["agents"]

    # 5. Get Incident Events
    events_resp = client.get(f"/api/v1/incidents/{inc_id}/events")
    assert events_resp.status_code == 200
    events = events_resp.json()
    assert len(events) >= 1

    # 6. Get Incident Detections
    dets_resp = client.get(f"/api/v1/incidents/{inc_id}/detections")
    assert dets_resp.status_code == 200
    assert len(dets_resp.json()) >= 1

    # 7. Get Incident IOCs & MITRE
    iocs_resp = client.get(f"/api/v1/incidents/{inc_id}/iocs")
    assert iocs_resp.status_code == 200

    mitre_resp = client.get(f"/api/v1/incidents/{inc_id}/mitre")
    assert mitre_resp.status_code == 200

    # 8. Get Investigation Timeline
    timeline_resp = client.get(f"/api/v1/incidents/{inc_id}/timeline")
    assert timeline_resp.status_code == 200
    timeline = timeline_resp.json()
    assert timeline["total_items"] >= 2
    types = [t["type"] for t in timeline["timeline"]]
    assert "event" in types or "detection" in types

    # 9. Add Analyst Note
    note_resp = client.post(f"/api/v1/incidents/{inc_id}/notes", json={"content": "Investigating workstation-07 activity", "author": "lead_analyst"})
    assert note_resp.status_code == 201
    note_data = note_resp.json()
    note_id = note_data["id"]
    assert note_data["content"] == "Investigating workstation-07 activity"

    # List Notes
    notes_list = client.get(f"/api/v1/incidents/{inc_id}/notes").json()
    assert len(notes_list) >= 1

    # 10. Update Incident Status Workflow & Verify Audit Log
    update_resp = client.patch(f"/api/v1/incidents/{inc_id}", json={"status": "investigating", "assigned_to": "alice"})
    assert update_resp.status_code == 200
    updated_inc = update_resp.json()
    assert updated_inc["status"] == "investigating"
    assert updated_inc["assigned_to"] == "alice"

    # Query Audit Log
    audit_resp = client.get(f"/api/v1/incidents/{inc_id}/audit")
    assert audit_resp.status_code == 200
    audits = audit_resp.json()
    assert len(audits) >= 1
    actions = [a["action"] for a in audits]
    assert "STATUS_CHANGED" in actions or "NOTE_CREATED" in actions


def test_invalid_status_transition():
    """Verify status transition rules: OPEN -> RESOLVED succeeds, but CLOSED -> OPEN fails."""
    # Create incident
    inc = client.post("/api/v1/incidents", json={"title": "Test Incident", "severity": "medium"}).json()
    inc_id = inc["id"]

    # Valid transition: open -> investigating
    r1 = client.patch(f"/api/v1/incidents/{inc_id}", json={"status": "investigating"})
    assert r1.status_code == 200

    # Valid transition: investigating -> resolved
    r2 = client.patch(f"/api/v1/incidents/{inc_id}", json={"status": "resolved"})
    assert r2.status_code == 200

    # Valid transition: resolved -> closed
    r3 = client.patch(f"/api/v1/incidents/{inc_id}", json={"status": "closed"})
    assert r3.status_code == 200

    # Invalid transition: closed -> open
    r4 = client.patch(f"/api/v1/incidents/{inc_id}", json={"status": "open"})
    assert r4.status_code == 400
