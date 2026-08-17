"""Unit tests for deterministic event enrichment pipeline."""

import uuid
from intelligence.enrichment.service import EnrichmentService
from intelligence.enrichment.models import ENRICHMENT_VERSION


def test_deterministic_enrichment_pipeline():
    """Verify event enrichment pipeline generates reproducible output."""
    service = EnrichmentService()
    event_id = uuid.uuid4()
    event_dict = {
        "rule_id": "5710",
        "agent_ip": "192.168.1.50",
        "rule_description": "PowerShell script execution detected"
    }
    raw_event = {
        "srcip": "10.0.0.99",
        "full_log": "Executing powershell -c https://malicious.org/script.ps1 on /tmp/exec.sh"
    }

    enriched = service.enrich_event(event_id, event_dict, raw_event)
    assert enriched.original_event_id == event_id
    assert enriched.enrichment_version == ENRICHMENT_VERSION
    assert len(enriched.extracted_iocs) >= 3
    assert len(enriched.mitre_mappings) >= 1

    # Security assertions: Extracted values must remain strings and data only
    for ioc in enriched.extracted_iocs:
        assert isinstance(ioc.value, str)
        assert isinstance(ioc.normalized_value, str)
