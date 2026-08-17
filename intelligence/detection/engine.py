"""Deterministic Detection Engine for SPECTRA-XDR."""

from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from intelligence.detection.models import ConditionType
from intelligence.detection.conditions import ConditionEvaluator
from intelligence.enrichment.models import EnrichedEventData


class DetectionMatchResult:
    """Result of a detection rule match evaluation."""

    def __init__(
        self,
        rule_id: str,
        severity: str,
        matched_events: List[Dict[str, Any]],
        match_reason: Dict[str, Any],
        window_start: Optional[datetime] = None,
        window_end: Optional[datetime] = None,
    ):
        self.rule_id = rule_id
        self.severity = severity
        self.matched_events = matched_events
        self.match_reason = match_reason
        self.window_start = window_start
        self.window_end = window_end


class DetectionEngine:
    """Evaluates detection rules deterministically over events and enriched intelligence."""

    def evaluate_rule_on_event(
        self,
        rule_def: Dict[str, Any],
        event_dict: Dict[str, Any],
        enriched_data: EnrichedEventData
    ) -> Optional[DetectionMatchResult]:
        """Evaluates single-event, IOC, MITRE, or COMBINATION rules against a single enriched event."""
        cond_type = rule_def.get("condition_type")
        cond_cfg = rule_def.get("condition_config", {})
        rule_id = rule_def.get("rule_id", "UNKNOWN")
        severity = rule_def.get("severity", "medium")

        matched = False

        if cond_type == ConditionType.SINGLE_EVENT:
            matched = ConditionEvaluator.evaluate_single_event(event_dict, cond_cfg)
        elif cond_type == ConditionType.IOC_MATCH:
            matched = ConditionEvaluator.evaluate_ioc_match(enriched_data, cond_cfg)
        elif cond_type == ConditionType.MITRE_TECHNIQUE_MATCH:
            matched = ConditionEvaluator.evaluate_mitre_match(enriched_data, cond_cfg)
        elif cond_type == ConditionType.COMBINATION:
            matched = ConditionEvaluator.evaluate_combination(event_dict, enriched_data, cond_cfg)

        if matched:
            reason = {
                "rule_id": rule_id,
                "condition_type": cond_type,
                "condition_config": cond_cfg,
                "matched_event_id": event_dict.get("id"),
                "event_id_str": event_dict.get("event_id"),
                "agent_id": event_dict.get("agent_id")
            }
            return DetectionMatchResult(
                rule_id=rule_id,
                severity=severity,
                matched_events=[event_dict],
                match_reason=reason
            )

        return None

    def evaluate_threshold_rule(
        self,
        rule_def: Dict[str, Any],
        events: List[Dict[str, Any]]
    ) -> List[DetectionMatchResult]:
        """Evaluates THRESHOLD or SAME_SOURCE_THRESHOLD rules over a set of events."""
        cond_cfg = rule_def.get("condition_config", {})
        rule_id = rule_def.get("rule_id", "UNKNOWN")
        severity = rule_def.get("severity", "medium")

        matches = ConditionEvaluator.evaluate_threshold(events, cond_cfg)
        results = []

        for corr_val, matched_evts, win_start_str, win_end_str in matches:
            reason = {
                "rule_id": rule_id,
                "condition_type": rule_def.get("condition_type"),
                "threshold": cond_cfg.get("threshold"),
                "actual_count": len(matched_evts),
                "window_seconds": cond_cfg.get("window_seconds"),
                "correlation_key": cond_cfg.get("correlation_key"),
                "correlation_value": corr_val
            }
            results.append(DetectionMatchResult(
                rule_id=rule_id,
                severity=severity,
                matched_events=matched_evts,
                match_reason=reason,
            ))

        return results
