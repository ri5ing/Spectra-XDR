"""Security and Idempotency tests for Incident Evidence and Detection Pipeline."""

import sys
import pytest
from fastapi.testclient import TestClient
from backend.main import app

client = TestClient(app)


def test_no_llm_or_ai_imported_in_detection():
    """Security Assertion: Verify no AI/LLM packages (openai, langchain, langgraph) are imported in detection engine."""
    detection_modules = [m for m in sys.modules.keys() if m.startswith("intelligence.detection")]
    for mod_name in detection_modules:
        mod = sys.modules[mod_name]
        for attr in dir(mod):
            val = str(getattr(mod, attr, "")).lower()
            assert "openai" not in val
            assert "langchain" not in val
            assert "langgraph" not in val
            assert "gemini" not in val


def test_idempotent_detection_execution():
    """Verify running detection multiple times over the same events does not duplicate matches or evidence."""
    # Ingest 5 events to satisfy DET-001 threshold condition (5 events from same agent)
    for i in range(5):
        evt_payload = {
            "event_id": f"idem-test-0{i}",
            "timestamp": f"2026-08-17T21:4{i}:00Z",
            "source": "wazuh",
            "agent_id": "010",
            "rule_id": "5710",
            "rule_description": "SSH authentication failure from 10.0.0.1"
        }
        client.post("/api/v1/events", json=evt_payload)

    # First detection run
    run1 = client.post("/api/v1/detections/run", json={"rule_id": "DET-001"}).json()
    assert run1["matches_generated"] >= 1

    # Second detection run over identical data
    run2 = client.post("/api/v1/detections/run", json={"rule_id": "DET-001"}).json()
    
    # Matches count in database should remain 1 (idempotent, no duplicates)
    matches = client.get("/api/v1/detections/matches").json()
    assert len(matches) == 1

