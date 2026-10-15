"""FastAPI Endpoints for Deterministic Risk Engine."""

import uuid
from typing import Any, Dict
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from database.session import get_db
from database.repositories.incident_repository import IncidentRepository
from database.repositories.risk_repository import RiskRepository
from risk.scoring import calculate_incident_risk

router = APIRouter(prefix="/risk", tags=["Deterministic Risk Engine"])


@router.get("/assessments/{incident_id}", response_model=Dict[str, Any])
async def get_incident_risk_assessment(
    incident_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Retrieve stored deterministic risk assessment for an incident."""
    inc_repo = IncidentRepository(db)
    risk_repo = RiskRepository(db)

    try:
        inc_uuid = uuid.UUID(incident_id)
        incident = await inc_repo.get_incident_by_id(inc_uuid)
    except ValueError:
        incident = await inc_repo.get_incident_by_human_id(incident_id)

    if not incident:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Incident '{incident_id}' not found."
        )

    assessment = await risk_repo.get_latest_risk_assessment(incident.id)
    if not assessment:
        primary_event = incident.events[0] if incident.events else None
        agent_name = getattr(primary_event, 'agent_name', None) or "Local Endpoint"
        agent_id_str = getattr(primary_event, 'agent_id', None) or "002"
        agent_ip = getattr(primary_event, 'agent_ip', None) or "127.0.0.1"
        rule_id_str = getattr(primary_event, 'rule_id', None) or "T1070.004"

        event_dict = {
            "severity": incident.severity or "medium",
            "agent_name": agent_name
        }

        mitre_list = []
        if primary_event and hasattr(primary_event, "mitre_mappings") and primary_event.mitre_mappings:
            mitre_list = [{"technique_id": getattr(m, 'technique_id', str(m))} for m in primary_event.mitre_mappings]
        elif rule_id_str and str(rule_id_str).startswith("T"):
            mitre_list = [{"technique_id": rule_id_str}]

        ioc_list = []
        if primary_event and hasattr(primary_event, "extracted_iocs") and primary_event.extracted_iocs:
            ioc_list = [{"ioc_type": getattr(i, 'ioc_type', 'ip')} for i in primary_event.extracted_iocs]
        elif agent_ip:
            ioc_list = [{"ioc_type": "ip", "normalized_value": agent_ip}]

        det_list = []
        if hasattr(incident, "detections") and incident.detections:
            det_list = [{"rule_id": getattr(d, 'rule_id', str(d))} for d in incident.detections]
        else:
            det_list = [{"rule_id": rule_id_str}]

        res = calculate_incident_risk(
            event_data=event_dict,
            mitre_mappings=mitre_list,
            extracted_iocs=ioc_list,
            detection_matches=det_list,
            attack_chain=["Execution"]
        )
        assessment = await risk_repo.save_risk_assessment(
            incident_id=incident.id,
            risk_score=res["risk_score"],
            risk_level=res["risk_level"],
            breakdown=res["breakdown"]
        )

    # Ensure actions exist for this incident
    from database.repositories.response_repository import ResponseRepository
    resp_repo = ResponseRepository(db)
    actions = await resp_repo.list_actions_for_incident(incident.id)
    if not actions:
        primary_event = incident.events[0] if incident.events else None
        agent_name = getattr(primary_event, 'agent_name', None) or "Local Endpoint"
        agent_id_str = getattr(primary_event, 'agent_id', None) or "002"
        agent_ip = getattr(primary_event, 'agent_ip', None) or "127.0.0.1"
        if assessment.risk_score >= 60 or incident.severity in ["high", "critical"]:
            await resp_repo.create_action(
                incident_id=incident.id,
                action_type="isolate_endpoint",
                target=agent_name,
                description=f"Host network quarantine on {agent_name} (Agent #{agent_id_str}) to halt adversary lateral movement.",
                high_impact=True,
                approval_status="pending"
            )
            await resp_repo.create_action(
                incident_id=incident.id,
                action_type="block_ip",
                target=agent_ip,
                description=f"Automated edge firewall C2 egress block for malicious indicator {agent_ip}.",
                high_impact=False,
                approval_status="pending"
            )
        else:
            await resp_repo.create_action(
                incident_id=incident.id,
                action_type="monitor_only",
                target=agent_name,
                description=f"Elevate endpoint telemetry logging and syscheck audit interval on {agent_name}.",
                high_impact=False,
                approval_status="pending"
            )

    return {
        "incident_human_id": incident.human_id,
        "risk_score": assessment.risk_score,
        "risk_level": assessment.risk_level,
        "breakdown": assessment.score_breakdown,
        "assessed_at": assessment.created_at.isoformat()
    }


@router.post("/recalculate/{incident_id}", response_model=Dict[str, Any])
async def recalculate_risk(
    incident_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Force recalculation of deterministic risk score for an incident."""
    inc_repo = IncidentRepository(db)
    risk_repo = RiskRepository(db)

    try:
        inc_uuid = uuid.UUID(incident_id)
        incident = await inc_repo.get_incident_by_id(inc_uuid)
    except ValueError:
        incident = await inc_repo.get_incident_by_human_id(incident_id)

    if not incident:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Incident '{incident_id}' not found."
        )

    primary_event = incident.events[0] if incident.events else None
    agent_name = getattr(primary_event, 'agent_name', None) or "Local Endpoint"
    agent_id_str = getattr(primary_event, 'agent_id', None) or "002"
    agent_ip = getattr(primary_event, 'agent_ip', None) or "127.0.0.1"
    rule_id_str = getattr(primary_event, 'rule_id', None) or "T1070.004"

    event_dict = {
        "severity": incident.severity or "medium",
        "agent_name": agent_name
    }

    # Safely extract mitre techniques and iocs
    mitre_list = []
    if primary_event and hasattr(primary_event, "mitre_mappings") and primary_event.mitre_mappings:
        mitre_list = [{"technique_id": getattr(m, 'technique_id', str(m))} for m in primary_event.mitre_mappings]
    elif rule_id_str and str(rule_id_str).startswith("T"):
        mitre_list = [{"technique_id": rule_id_str}]

    ioc_list = []
    if primary_event and hasattr(primary_event, "extracted_iocs") and primary_event.extracted_iocs:
        ioc_list = [{"ioc_type": getattr(i, 'ioc_type', 'ip')} for i in primary_event.extracted_iocs]
    elif agent_ip:
        ioc_list = [{"ioc_type": "ip", "normalized_value": agent_ip}]

    det_list = []
    if hasattr(incident, "detections") and incident.detections:
        det_list = [{"rule_id": getattr(d, 'rule_id', str(d))} for d in incident.detections]
    else:
        det_list = [{"rule_id": rule_id_str}]

    res = calculate_incident_risk(
        event_data=event_dict,
        mitre_mappings=mitre_list,
        extracted_iocs=ioc_list,
        detection_matches=det_list,
        attack_chain=["Initial Access", "Execution"]
    )

    assessment = await risk_repo.save_risk_assessment(
        incident_id=incident.id,
        risk_score=res["risk_score"],
        risk_level=res["risk_level"],
        breakdown=res["breakdown"]
    )

    # Ensure actionable SOAR playbook actions exist in response repository
    from database.repositories.response_repository import ResponseRepository
    resp_repo = ResponseRepository(db)
    existing_actions = await resp_repo.list_actions_for_incident(incident.id)
    if not existing_actions:
        score = res["risk_score"]
        if score >= 60 or incident.severity in ["high", "critical"]:
            await resp_repo.create_action(
                incident_id=incident.id,
                action_type="isolate_endpoint",
                target=agent_name,
                description=f"Host network quarantine on {agent_name} (Agent #{agent_id_str}) to halt adversary lateral movement.",
                high_impact=True,
                approval_status="pending"
            )
            await resp_repo.create_action(
                incident_id=incident.id,
                action_type="block_ip",
                target=agent_ip,
                description=f"Automated edge firewall C2 egress block for malicious indicator {agent_ip}.",
                high_impact=False,
                approval_status="pending"
            )
        else:
            await resp_repo.create_action(
                incident_id=incident.id,
                action_type="monitor_only",
                target=agent_name,
                description=f"Elevate endpoint telemetry logging and syscheck audit interval on {agent_name}.",
                high_impact=False,
                approval_status="pending"
            )

    return {
        "incident_human_id": incident.human_id,
        "risk_score": assessment.risk_score,
        "risk_level": assessment.risk_level,
        "breakdown": assessment.score_breakdown,
        "recalculated_at": assessment.created_at.isoformat()
    }
