"""Unit tests for event normalization module."""

from intelligence.normalization.wazuh import normalize_wazuh_alert
from intelligence.normalization.models import NormalizedEvent


def test_normalize_full_wazuh_alert():
    """Verify full Wazuh alert is correctly mapped into NormalizedEvent."""
    raw_alert = {
        "id": "alert-9999",
        "timestamp": "2026-08-17T12:34:56.789Z",
        "agent": {
            "id": "002",
            "name": "kali-box",
            "ip": "10.0.0.15"
        },
        "rule": {
            "id": 100200,
            "level": 10,
            "description": "Multiple failed authentication attempts detected",
            "groups": ["sshd", "authentication_failed"]
        },
        "decoder": {
            "name": "sshd"
        },
        "location": "/var/log/auth.log",
        "full_log": "Aug 17 12:34:56 kali-box sshd[1234]: Failed password for root from 192.168.1.100 port 54321 ssh2"
    }

    event = normalize_wazuh_alert(raw_alert)

    assert isinstance(event, NormalizedEvent)
    assert event.event_id == "alert-9999"
    assert event.timestamp == "2026-08-17T12:34:56.789Z"
    assert event.source == "wazuh"
    assert event.agent_id == "002"
    assert event.agent_name == "kali-box"
    assert event.agent_ip == "10.0.0.15"
    assert event.rule_id == "100200"
    assert event.rule_level == 10
    assert event.rule_description == "Multiple failed authentication attempts detected"
    assert event.event_type == "sshd"
    assert event.location == "/var/log/auth.log"
    assert event.raw_event == raw_alert


def test_normalize_missing_optional_fields():
    """Verify normalization does not crash when optional Wazuh fields are absent."""
    raw_alert = {
        "timestamp": "2026-08-17T13:00:00Z"
    }

    event = normalize_wazuh_alert(raw_alert)

    assert isinstance(event, NormalizedEvent)
    assert event.event_id is not None  # Fallback generated UUID
    assert event.timestamp == "2026-08-17T13:00:00Z"
    assert event.source == "wazuh"
    assert event.agent_id is None
    assert event.agent_name is None
    assert event.agent_ip is None
    assert event.rule_id is None
    assert event.rule_level is None
    assert event.rule_description is None
    assert event.event_type is None
    assert event.location is None
    assert event.raw_event == raw_alert
