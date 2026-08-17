"""Unit tests for deterministic DetectionEngine."""

import uuid
from intelligence.detection.engine import DetectionEngine
from intelligence.detection.models import ConditionType
from intelligence.enrichment.models import EnrichedEventData


def test_engine_single_event_evaluation():
    """Verify DetectionEngine evaluates single-event rules."""
    engine = DetectionEngine()
    rule_def = {
        "rule_id": "DET-003",
        "name": "PowerShell Execution",
        "severity": "medium",
        "condition_type": ConditionType.SINGLE_EVENT,
        "condition_config": {"filters": {"rule_id": "91800"}}
    }
    event_dict = {"id": str(uuid.uuid4()), "event_id": "e-1", "rule_id": "91800", "agent_id": "001"}
    enriched_data = EnrichedEventData(original_event_id=uuid.uuid4(), normalized_event_data={})

    result = engine.evaluate_rule_on_event(rule_def, event_dict, enriched_data)
    assert result is not None
    assert result.rule_id == "DET-003"
    assert result.severity == "medium"
