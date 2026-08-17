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
        # Calculate on the fly if not already persisted
        primary_event = incident.events[0] if incident.events else None
        event_dict = {
            "severity": incident.severity,
            "agent_name": primary_event.agent_name if primary_event else "Local Endpoint"
        }
        res = calculate_incident_risk(
            event_data=event_dict,
            mitre_mappings=[{"technique_id": m.technique_id} for m in (primary_event.mitre_mappings if primary_event else [])],
            extracted_iocs=[{"ioc_type": i.ioc_type} for i in (primary_event.extracted_iocs if primary_event else [])],
            detection_matches=[{"rule_id": d.rule_id} for d in incident.detections],
            attack_chain=["Execution"]
        )
        assessment = await risk_repo.save_risk_assessment(
            incident_id=incident.id,
            risk_score=res["risk_score"],
            risk_level=res["risk_level"],
            breakdown=res["breakdown"]
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
    event_dict = {
        "severity": incident.severity,
        "agent_name": primary_event.agent_name if primary_event else "Local Endpoint"
    }

    res = calculate_incident_risk(
        event_data=event_dict,
        mitre_mappings=[{"technique_id": m.technique_id} for m in (primary_event.mitre_mappings if primary_event else [])],
        extracted_iocs=[{"ioc_type": i.ioc_type} for i in (primary_event.extracted_iocs if primary_event else [])],
        detection_matches=[{"rule_id": d.rule_id} for d in incident.detections],
        attack_chain=["Execution"]
    )

    assessment = await risk_repo.save_risk_assessment(
        incident_id=incident.id,
        risk_score=res["risk_score"],
        risk_level=res["risk_level"],
        breakdown=res["breakdown"]
    )

    return {
        "incident_human_id": incident.human_id,
        "risk_score": assessment.risk_score,
        "risk_level": assessment.risk_level,
        "breakdown": assessment.score_breakdown,
        "recalculated_at": assessment.created_at.isoformat()
    }
