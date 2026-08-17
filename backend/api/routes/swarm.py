"""FastAPI Endpoints for Multi-Agent AI Swarm Orchestration."""

import uuid
from typing import Any, Dict, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from database.session import get_db
from database.repositories.incident_repository import IncidentRepository
from database.repositories.swarm_repository import SwarmRepository
from agents.models import SwarmState, AgentRole, HumanApprovalStatus
from orchestration.graph import SwarmOrchestrator

router = APIRouter(prefix="/swarm", tags=["AI Swarm Orchestration"])


@router.post("/analyze/{incident_id}", response_model=Dict[str, Any])
async def trigger_swarm_analysis(
    incident_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Trigger Multi-Agent Swarm reasoning flow on a security incident."""
    inc_repo = IncidentRepository(db)
    swarm_repo = SwarmRepository(db)

    # 1. Resolve Incident UUID
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

    # 2. Extract Event & Intelligence Context
    primary_event = incident.events[0] if incident.events else None
    event_dict = {
        "rule_id": primary_event.rule_id if primary_event else "UNKNOWN",
        "rule_description": incident.title or "Security Telemetry Event",
        "severity": incident.severity or "medium",
        "agent_name": primary_event.agent_name if primary_event else "Local Endpoint",
        "agent_id": primary_event.agent_id if primary_event else "001",
        "full_log": primary_event.full_log if primary_event else ""
    }

    # 3. Construct SwarmState
    initial_state = SwarmState(
        incident_id=incident.id,
        incident_human_id=incident.human_id,
        event_data=event_dict,
        mitre_mappings=[{"technique_id": m.technique_id, "technique_name": m.technique_name, "tactic": m.tactic} for m in (primary_event.mitre_mappings if primary_event else [])],
        extracted_iocs=[{"ioc_type": i.ioc_type, "normalized_value": i.normalized_value} for i in (primary_event.extracted_iocs if primary_event else [])],
        detection_matches=[{"rule_id": d.rule_id} for d in incident.detections]
    )

    # 4. Run Swarm Orchestrator
    orchestrator = SwarmOrchestrator()
    final_state = await orchestrator.run_swarm(initial_state)

    # 5. Persist Swarm Run & Agent Thoughts
    swarm_run = await swarm_repo.save_swarm_run(final_state)

    return {
        "status": "success",
        "swarm_run_id": str(swarm_run.id),
        "incident_human_id": incident.human_id,
        "risk_score": final_state.risk_score,
        "risk_level": final_state.risk_level,
        "human_approval_required": final_state.human_approval_required,
        "human_approval_status": final_state.human_approval_status.value if hasattr(final_state.human_approval_status, "value") else str(final_state.human_approval_status),
        "attack_chain": final_state.attack_chain,
        "recommended_actions": final_state.recommended_actions,
        "agent_thoughts": [
            {
                "agent_role": t.agent_role.value if hasattr(t.agent_role, "value") else str(t.agent_role),
                "model_used": t.model_used.value if hasattr(t.model_used, "value") else str(t.model_used),
                "summary": t.summary,
                "findings": t.findings,
                "confidence": t.confidence,
                "timestamp": t.timestamp.isoformat()
            }
            for t in final_state.thoughts
        ]
    }


@router.get("/runs/{incident_id}", response_model=Dict[str, Any])
async def get_latest_swarm_run(
    incident_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Retrieve latest Swarm execution run and agent thoughts for an incident."""
    inc_repo = IncidentRepository(db)
    swarm_repo = SwarmRepository(db)

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

    swarm_run = await swarm_repo.get_latest_swarm_run(incident.id)
    if not swarm_run:
        return {
            "status": "not_analyzed",
            "incident_human_id": incident.human_id,
            "message": "Swarm analysis has not been executed for this incident yet."
        }

    return {
        "swarm_run_id": str(swarm_run.id),
        "incident_human_id": swarm_run.human_incident_id,
        "risk_score": swarm_run.risk_score,
        "risk_level": swarm_run.risk_level,
        "human_approval_required": swarm_run.human_approval_required,
        "human_approval_status": swarm_run.human_approval_status,
        "attack_chain": swarm_run.attack_chain,
        "completed_agents": swarm_run.completed_agents,
        "created_at": swarm_run.created_at.isoformat(),
        "thoughts": [
            {
                "agent_role": t.agent_role,
                "model_used": t.model_used,
                "summary": t.summary,
                "findings": t.findings,
                "confidence": t.confidence,
                "created_at": t.created_at.isoformat()
            }
            for t in swarm_run.thoughts
        ]
    }
