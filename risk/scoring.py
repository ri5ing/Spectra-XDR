"""Deterministic Multi-Factor Risk Engine for SPECTRA-XDR."""

import logging
from typing import Any, Dict, List

logger = logging.getLogger("spectra.risk.scoring")


def calculate_incident_risk(
    event_data: Dict[str, Any],
    mitre_mappings: List[Dict[str, Any]],
    extracted_iocs: List[Dict[str, Any]],
    detection_matches: List[Dict[str, Any]],
    attack_chain: List[str]
) -> Dict[str, Any]:
    """Calculate deterministic multi-factor risk score (0 - 100)."""

    # 1. Base Alert Severity Weight (0 - 30 points)
    raw_severity = str(event_data.get("severity", "medium")).lower()
    if raw_severity in ["critical", "12", "13", "14", "15"]:
        severity_score = 30.0
    elif raw_severity in ["high", "8", "9", "10", "11"]:
        severity_score = 22.5
    elif raw_severity in ["medium", "5", "6", "7"]:
        severity_score = 15.0
    else:
        severity_score = 7.5

    # 2. MITRE ATT&CK Technique Risk Weight (0 - 25 points)
    mitre_count = len(mitre_mappings)
    if mitre_count >= 4:
        mitre_score = 25.0
    elif mitre_count >= 2:
        mitre_score = 18.0
    elif mitre_count == 1:
        mitre_score = 12.0
    else:
        mitre_score = 5.0

    # 3. IOC Reputation Score Weight (0 - 15 points)
    ioc_count = len(extracted_iocs)
    if ioc_count >= 5:
        ioc_score = 15.0
    elif ioc_count >= 2:
        ioc_score = 10.0
    elif ioc_count == 1:
        ioc_score = 5.0
    else:
        ioc_score = 0.0

    # 4. Attack Chain & Correlation Depth Weight (0 - 15 points)
    chain_depth = len(attack_chain)
    if chain_depth >= 4:
        chain_score = 15.0
    elif chain_depth >= 2:
        chain_score = 10.0
    else:
        chain_score = 5.0

    # 5. Asset Criticality Weight (0 - 15 points)
    agent_name = str(event_data.get("agent_name", "")).lower()
    if any(k in agent_name for k in ["dc", "domain", "prod", "server", "sql"]):
        asset_score = 15.0
    elif any(k in agent_name for k in ["linux", "workstation", "kali"]):
        asset_score = 10.0
    else:
        asset_score = 7.5

    total_score = severity_score + mitre_score + ioc_score + chain_score + asset_score
    total_score = min(100.0, max(0.0, total_score))

    if total_score >= 80.0:
        risk_level = "CRITICAL"
    elif total_score >= 60.0:
        risk_level = "HIGH"
    elif total_score >= 30.0:
        risk_level = "MEDIUM"
    else:
        risk_level = "LOW"

    return {
        "risk_score": round(total_score, 1),
        "risk_level": risk_level,
        "breakdown": {
            "severity_component": severity_score,
            "mitre_component": mitre_score,
            "ioc_component": ioc_score,
            "correlation_component": chain_score,
            "asset_component": asset_score
        }
    }
