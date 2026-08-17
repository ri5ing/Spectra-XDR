"""Deterministic MITRE ATT&CK Mapper for SPECTRA-XDR."""

from typing import Any, Dict, List
from intelligence.mitre.models import MITREMapping, MITRETechnique
from intelligence.mitre.catalog import GROUP_MAPPINGS, MITRE_CATALOG, RULE_MAPPINGS, MITRECatalog


class MITREMapper:
    """Deterministically maps security telemetry events to MITRE ATT&CK techniques."""

    def __init__(self):
        self.catalog = MITRECatalog()

    def map_event(self, event_data: Dict[str, Any], raw_event: Dict[str, Any]) -> List[MITREMapping]:
        """Maps event data deterministically against the local MITRE ATT&CK catalog."""
        mappings: List[MITREMapping] = []
        seen_technique_ids = set()

        def _add_mapping(tech_id: str, rule_id: str = None, group: str = None, confidence: float = 1.0):
            if tech_id in seen_technique_ids:
                return
            tech = self.catalog.get_technique(tech_id)
            if tech:
                seen_technique_ids.add(tech_id)
                mappings.append(MITREMapping(
                    technique=tech,
                    matched_rule_id=rule_id,
                    matched_group=group,
                    confidence=confidence
                ))

        # 1. Explicit Rule ID Mapping
        rule_id = str(event_data.get("rule_id") or "")
        if rule_id in RULE_MAPPINGS:
            for tech_id in RULE_MAPPINGS[rule_id]:
                _add_mapping(tech_id, rule_id=rule_id, confidence=1.0)

        # 2. Rule Group & Event Type Mapping
        event_type = (event_data.get("event_type") or "").lower()
        if event_type in GROUP_MAPPINGS:
            for tech_id in GROUP_MAPPINGS[event_type]:
                _add_mapping(tech_id, group=event_type, confidence=0.9)

        rule_groups = raw_event.get("rule", {}).get("groups", []) if isinstance(raw_event.get("rule"), dict) else []
        for g in rule_groups:
            g_lower = str(g).lower()
            if g_lower in GROUP_MAPPINGS:
                for tech_id in GROUP_MAPPINGS[g_lower]:
                    _add_mapping(tech_id, group=g_lower, confidence=0.9)

        # 3. Rule Description / Text Keyword Mapping
        desc = (event_data.get("rule_description") or "").lower()
        if "powershell" in desc:
            _add_mapping("T1059.001", confidence=0.85)
        elif "command" in desc or "script" in desc or "bash" in desc or "sh" in desc:
            _add_mapping("T1059", confidence=0.8)

        if "brute force" in desc or "authentication failure" in desc:
            _add_mapping("T1110", confidence=0.85)

        if "privilege escalation" in desc or "sudo" in desc:
            _add_mapping("T1068", confidence=0.85)

        return mappings
