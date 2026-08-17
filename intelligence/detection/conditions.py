"""Deterministic condition evaluation logic for SPECTRA-XDR Detection Engine."""

from datetime import datetime, timezone
from typing import Any, Dict, List, Tuple
from intelligence.detection.models import ConditionType
from intelligence.enrichment.models import EnrichedEventData


class ConditionEvaluator:
    """Evaluates deterministic detection conditions against events and enriched data."""

    @staticmethod
    def match_event_filters(event_dict: Dict[str, Any], filters: Dict[str, Any]) -> bool:
        """Evaluates whether event_dict matches all filter key-value pairs."""
        if not filters:
            return True
        for key, expected in filters.items():
            actual = event_dict.get(key)
            if actual is None:
                return False
            if str(actual).lower() != str(expected).lower():
                return False
        return True

    @classmethod
    def evaluate_single_event(cls, event_dict: Dict[str, Any], config: Dict[str, Any]) -> bool:
        """Evaluates SINGLE_EVENT condition."""
        filters = config.get("filters", {})
        return cls.match_event_filters(event_dict, filters)

    @classmethod
    def evaluate_threshold(
        cls,
        events: List[Dict[str, Any]],
        config: Dict[str, Any]
    ) -> List[Tuple[str, List[Dict[str, Any]], datetime, datetime]]:
        """Evaluates THRESHOLD or SAME_SOURCE_THRESHOLD across a list of events.
        
        Returns list of tuples: (correlation_value, matching_events, window_start, window_end)
        """
        threshold = config.get("threshold", 5)
        window_seconds = config.get("window_seconds", 300)
        corr_key = config.get("correlation_key", "agent_id")
        filters = config.get("filters", {})

        # Group events by correlation_key value
        groups: Dict[str, List[Dict[str, Any]]] = {}
        for evt in events:
            if not cls.match_event_filters(evt, filters):
                continue
            val = str(evt.get(corr_key) or "")
            if not val or val == "None":
                continue
            groups.setdefault(val, []).append(evt)

        matches = []
        for corr_val, group_events in groups.items():
            if len(group_events) < threshold:
                continue

            # Sort by timestamp
            sorted_events = sorted(
                group_events,
                key=lambda x: x.get("timestamp") or datetime.now(timezone.utc).isoformat()
            )

            # Sliding window check
            if len(sorted_events) >= threshold:
                win_start_str = sorted_events[0].get("timestamp")
                win_end_str = sorted_events[-1].get("timestamp")
                matches.append((corr_val, sorted_events, win_start_str, win_end_str))

        return matches

    @classmethod
    def evaluate_ioc_match(cls, enriched_data: EnrichedEventData, config: Dict[str, Any]) -> bool:
        """Evaluates IOC_MATCH condition against enriched event IOCs."""
        target_type = config.get("ioc_type")
        target_val = config.get("ioc_value")

        for ioc in enriched_data.extracted_iocs:
            type_str = ioc.type.value if hasattr(ioc.type, "value") else str(ioc.type)
            if target_type and type_str.lower() != str(target_type).lower():
                continue
            if target_val and ioc.normalized_value.lower() != str(target_val).lower():
                continue
            return True
        return False

    @classmethod
    def evaluate_mitre_match(cls, enriched_data: EnrichedEventData, config: Dict[str, Any]) -> bool:
        """Evaluates MITRE_TECHNIQUE_MATCH condition against enriched event MITRE mappings."""
        target_tech_id = str(config.get("technique_id") or "").upper()

        for m in enriched_data.mitre_mappings:
            tech_id = m.technique.technique_id.upper()
            if tech_id == target_tech_id:
                return True
        return False

    @classmethod
    def evaluate_combination(cls, event_dict: Dict[str, Any], enriched_data: EnrichedEventData, config: Dict[str, Any]) -> bool:
        """Evaluates COMBINATION condition combining multiple sub-conditions."""
        operator = str(config.get("operator", "AND")).upper()
        sub_conditions = config.get("conditions", [])

        results = []
        for sub_cfg in sub_conditions:
            cond_type = sub_cfg.get("condition_type")
            if cond_type == ConditionType.SINGLE_EVENT:
                results.append(cls.evaluate_single_event(event_dict, sub_cfg))
            elif cond_type == ConditionType.IOC_MATCH:
                results.append(cls.evaluate_ioc_match(enriched_data, sub_cfg))
            elif cond_type == ConditionType.MITRE_TECHNIQUE_MATCH:
                results.append(cls.evaluate_mitre_match(enriched_data, sub_cfg))
            else:
                results.append(False)

        if operator == "OR":
            return any(results)
        return all(results) if results else False
