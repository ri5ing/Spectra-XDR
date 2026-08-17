"""Unit tests for deterministic MITRE ATT&CK technique mapping."""

from intelligence.mitre.mapper import MITREMapper
from intelligence.mitre.catalog import MITRECatalog


def test_mitre_catalog_lookup():
    """Verify listing and looking up techniques from catalog."""
    catalog = MITRECatalog()
    techs = catalog.list_techniques()
    assert len(techs) >= 8

    t1059 = catalog.get_technique("T1059.001")
    assert t1059 is not None
    assert t1059.technique_name == "PowerShell"
    assert t1059.tactic == "Execution"


def test_mitre_event_mapping():
    """Verify mapping event to MITRE techniques via rule ID and groups."""
    mapper = MITREMapper()
    event_data = {
        "rule_id": "5710",
        "event_type": "sshd",
        "rule_description": "SSH authentication failure"
    }
    raw_event = {"rule": {"groups": ["authentication_failed", "sshd"]}}

    mappings = mapper.map_event(event_data, raw_event)
    assert len(mappings) >= 1
    technique_ids = [m.technique.technique_id for m in mappings]
    assert "T1110" in technique_ids  # Brute Force
