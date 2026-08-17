"""Unit tests for Deterministic Risk Engine."""

from risk.scoring import calculate_incident_risk


def test_calculate_incident_risk_low():
    """Test LOW risk score calculation for minor events."""
    event_data = {"severity": "low", "agent_name": "host-01"}
    res = calculate_incident_risk(
        event_data=event_data,
        mitre_mappings=[],
        extracted_iocs=[],
        detection_matches=[],
        attack_chain=["Execution"]
    )
    assert res["risk_score"] < 30.0
    assert res["risk_level"] == "LOW"


def test_calculate_incident_risk_critical():
    """Test CRITICAL risk score calculation for multi-stage attacks on domain controllers."""
    event_data = {"severity": "critical", "agent_name": "dc-prod-01"}
    res = calculate_incident_risk(
        event_data=event_data,
        mitre_mappings=[{"t": 1}, {"t": 2}, {"t": 3}, {"t": 4}],
        extracted_iocs=[{"i": 1}, {"i": 2}, {"i": 3}, {"i": 4}, {"i": 5}],
        detection_matches=[{"d": 1}, {"d": 2}],
        attack_chain=["Auth Anomaly", "Execution", "Persistence", "Command & Control"]
    )
    assert res["risk_score"] >= 80.0
    assert res["risk_level"] == "CRITICAL"
