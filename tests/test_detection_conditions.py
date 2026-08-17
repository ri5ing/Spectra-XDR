"""Unit tests for deterministic detection condition evaluation."""

import uuid
from intelligence.detection.models import ConditionType
from intelligence.detection.conditions import ConditionEvaluator
from intelligence.enrichment.models import EnrichedEventData
from intelligence.ioc.models import IOCRecord, IOCType
from intelligence.mitre.models import MITRETechnique, MITREMapping


def test_single_event_condition():
    """Verify SINGLE_EVENT filter evaluation."""
    event = {"rule_id": "5710", "agent_id": "007", "source": "wazuh"}
    assert ConditionEvaluator.evaluate_single_event(event, {"filters": {"rule_id": "5710"}}) is True
    assert ConditionEvaluator.evaluate_single_event(event, {"filters": {"rule_id": "9999"}}) is False


def test_threshold_condition():
    """Verify THRESHOLD and SAME_SOURCE_THRESHOLD sliding window match."""
    events = [
        {"id": str(uuid.uuid4()), "agent_id": "007", "rule_id": "5710", "timestamp": f"2026-08-17T21:0{i}:00Z"}
        for i in range(5)
    ]
    config = {"threshold": 5, "window_seconds": 300, "correlation_key": "agent_id", "filters": {"rule_id": "5710"}}
    matches = ConditionEvaluator.evaluate_threshold(events, config)
    assert len(matches) == 1
    assert matches[0][0] == "007"
    assert len(matches[0][1]) == 5

    # Below threshold
    matches_below = ConditionEvaluator.evaluate_threshold(events[:3], config)
    assert len(matches_below) == 0


def test_ioc_and_mitre_condition_matches():
    """Verify IOC_MATCH and MITRE_TECHNIQUE_MATCH evaluation."""
    ioc_rec = IOCRecord(type=IOCType.IP, value="198.51.100.1", normalized_value="198.51.100.1")
    mitre_tech = MITRETechnique(
        technique_id="T1110", technique_name="Brute Force", tactic="Credential Access",
        description="", detection_rationale=""
    )
    mapping = MITREMapping(technique=mitre_tech)
    enriched = EnrichedEventData(
        original_event_id=uuid.uuid4(),
        normalized_event_data={},
        extracted_iocs=[ioc_rec],
        mitre_mappings=[mapping]
    )

    assert ConditionEvaluator.evaluate_ioc_match(enriched, {"ioc_type": "ip", "ioc_value": "198.51.100.1"}) is True
    assert ConditionEvaluator.evaluate_ioc_match(enriched, {"ioc_type": "ip", "ioc_value": "10.0.0.1"}) is False

    assert ConditionEvaluator.evaluate_mitre_match(enriched, {"technique_id": "T1110"}) is True
    assert ConditionEvaluator.evaluate_mitre_match(enriched, {"technique_id": "T1059"}) is False
