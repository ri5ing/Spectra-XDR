"""Built-in Detection Rule Catalog Registry for SPECTRA-XDR."""

from typing import Dict, List, Optional
from intelligence.detection.models import ConditionType

DETECTION_REGISTRY_VERSION = "1.0.0"

BUILTIN_DETECTION_RULES: List[Dict] = [
    {
        "rule_id": "DET-001",
        "name": "Repeated Authentication Failures",
        "description": "Triggers when 5 or more authentication failure events occur on the same agent within 5 minutes.",
        "version": "1.0.0",
        "enabled": True,
        "severity": "medium",
        "condition_type": ConditionType.SAME_SOURCE_THRESHOLD,
        "condition_config": {
            "threshold": 5,
            "window_seconds": 300,
            "correlation_key": "agent_id",
            "filters": {"rule_id": "5710"}
        },
        "mitre_technique_id": "T1110"
    },
    {
        "rule_id": "DET-002",
        "name": "Brute Force Threshold Violation",
        "description": "Triggers when 10 or more failed login attempts occur within 10 minutes.",
        "version": "1.0.0",
        "enabled": True,
        "severity": "high",
        "condition_type": ConditionType.THRESHOLD,
        "condition_config": {
            "threshold": 10,
            "window_seconds": 600,
            "correlation_key": "agent_id",
            "filters": {}
        },
        "mitre_technique_id": "T1110"
    },
    {
        "rule_id": "DET-003",
        "name": "PowerShell Script Execution",
        "description": "Triggers when an event is mapped to MITRE T1059.001 (PowerShell Execution).",
        "version": "1.0.0",
        "enabled": True,
        "severity": "medium",
        "condition_type": ConditionType.MITRE_TECHNIQUE_MATCH,
        "condition_config": {
            "technique_id": "T1059.001"
        },
        "mitre_technique_id": "T1059.001"
    },
    {
        "rule_id": "DET-004",
        "name": "OS Credential Dumping Activity",
        "description": "Triggers when telemetry matches MITRE T1003 (OS Credential Dumping).",
        "version": "1.0.0",
        "enabled": True,
        "severity": "high",
        "condition_type": ConditionType.MITRE_TECHNIQUE_MATCH,
        "condition_config": {
            "technique_id": "T1003"
        },
        "mitre_technique_id": "T1003"
    },
    {
        "rule_id": "DET-005",
        "name": "Privilege Escalation Exploitation",
        "description": "Triggers when telemetry matches MITRE T1068 (Privilege Escalation).",
        "version": "1.0.0",
        "enabled": True,
        "severity": "high",
        "condition_type": ConditionType.MITRE_TECHNIQUE_MATCH,
        "condition_config": {
            "technique_id": "T1068"
        },
        "mitre_technique_id": "T1068"
    },
]


class DetectionRegistry:
    """Catalog registry for built-in detection rules."""

    @classmethod
    def list_builtin_rules(cls) -> List[Dict]:
        return BUILTIN_DETECTION_RULES

    @classmethod
    def get_builtin_rule(cls, rule_id: str) -> Optional[Dict]:
        for r in BUILTIN_DETECTION_RULES:
            if r["rule_id"] == rule_id:
                return r
        return None
