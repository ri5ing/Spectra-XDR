"""Normalizer for Wazuh telemetry alerts and manager logs into SPECTRA NormalizedEvents."""

import uuid
from typing import Any, Dict
from intelligence.normalization.models import NormalizedEvent


def normalize_wazuh_alert(alert: Dict[str, Any]) -> NormalizedEvent:
    """Transforms a raw Wazuh alert or manager log dictionary into a standardized NormalizedEvent.
    
    Safely extracts available metadata while preserving the full original alert structure
    in `raw_event` for evidence retention.
    """
    agent_info = alert.get("agent", {}) if isinstance(alert.get("agent"), dict) else {}
    rule_info = alert.get("rule", {}) if isinstance(alert.get("rule"), dict) else {}
    decoder_info = alert.get("decoder", {}) if isinstance(alert.get("decoder"), dict) else {}

    # Extract event ID or generate deterministic fallback
    event_id = str(alert.get("id") or alert.get("_id") or uuid.uuid4())
    timestamp = str(alert.get("timestamp") or alert.get("@timestamp") or "")

    # Rule attributes conversion
    rule_id_raw = rule_info.get("id")
    rule_id = str(rule_id_raw) if rule_id_raw is not None else None

    rule_level_raw = rule_info.get("level") or alert.get("level")
    rule_level = None
    if rule_level_raw is not None:
        try:
            rule_level = int(rule_level_raw)
        except (ValueError, TypeError):
            rule_level = None

    rule_description = rule_info.get("description") or alert.get("description")

    # Event classification/type from decoder, manager log tag, or primary rule group
    event_type = decoder_info.get("name") or alert.get("tag")
    if not event_type and isinstance(rule_info.get("groups"), list) and rule_info["groups"]:
        event_type = rule_info["groups"][0]

    return NormalizedEvent(
        event_id=event_id,
        timestamp=timestamp,
        source="wazuh",
        agent_id=str(agent_info.get("id")) if agent_info.get("id") is not None else None,
        agent_name=agent_info.get("name"),
        agent_ip=agent_info.get("ip"),
        rule_id=rule_id,
        rule_level=rule_level,
        rule_description=rule_description,
        event_type=event_type,
        location=alert.get("location"),
        raw_event=alert
    )
