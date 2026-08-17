"""FastAPI Endpoints for Controlled Response Execution and Analyst Approval."""

import uuid
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from database.session import get_db
from database.repositories.incident_repository import IncidentRepository
from database.repositories.response_repository import ResponseRepository
from response import actions as response_actions

router = APIRouter(prefix="/response", tags=["Controlled Response Execution"])


class ApprovalRequest(BaseModel):
    approved: bool = True
    approved_by: str = Field(default="Analyst", description="Identity of approving analyst")
    reason: Optional[str] = None


class ActionExecutionRequest(BaseModel):
    action_type: str
    target: str
    incident_id: str
    approved_by: str = Field(default="SOC Lead")


@router.get("/actions/{incident_id}", response_model=List[Dict[str, Any]])
async def list_incident_response_actions(
    incident_id: str,
    db: AsyncSession = Depends(get_db)
):
    """List response actions associated with an incident."""
    inc_repo = IncidentRepository(db)
    resp_repo = ResponseRepository(db)

    try:
        inc_uuid = uuid.UUID(incident_id)
        incident = await inc_repo.get_incident_by_id(inc_uuid)
    except ValueError:
        incident = await inc_repo.get_incident_by_human_id(incident_id)

    if not incident:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Incident '{incident_id}' not found.")

    action_recs = await resp_repo.list_actions_for_incident(incident.id)
    return [
        {
            "action_id": str(a.id),
            "incident_human_id": incident.human_id,
            "action_type": a.action_type,
            "target": a.target,
            "description": a.description,
            "high_impact": a.high_impact,
            "approval_status": a.approval_status,
            "approved_by": a.approved_by,
            "execution_status": a.execution_status,
            "created_at": a.created_at.isoformat(),
            "executed_at": a.executed_at.isoformat() if a.executed_at else None
        }
        for a in action_recs
    ]


@router.post("/actions/{action_id}/approve", response_model=Dict[str, Any])
async def approve_response_action(
    action_id: str,
    req: ApprovalRequest,
    db: AsyncSession = Depends(get_db)
):
    """Analyst Human-in-the-Loop decision to approve or reject a response action."""
    resp_repo = ResponseRepository(db)

    try:
        act_uuid = uuid.UUID(action_id)
    except ValueError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid action_id UUID.")

    target_status = "approved" if req.approved else "rejected"
    action_rec = await resp_repo.update_action_approval(act_uuid, target_status, req.approved_by)

    if not action_rec:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Response action record not found.")

    # Audit log entry
    await resp_repo.log_audit_trail(
        actor=req.approved_by,
        action=f"RESPONSE_ACTION_{target_status.upper()}",
        details={"action_id": str(act_uuid), "action_type": action_rec.action_type, "reason": req.reason},
        incident_id=action_rec.incident_id
    )

    return {
        "status": "success",
        "action_id": str(action_rec.id),
        "approval_status": action_rec.approval_status,
        "approved_by": action_rec.approved_by
    }


@router.post("/actions/execute", response_model=Dict[str, Any])
async def execute_approved_action(
    req: ActionExecutionRequest,
    db: AsyncSession = Depends(get_db)
):
    """Execute an approved response action via Wazuh Active Response."""
    resp_repo = ResponseRepository(db)
    inc_repo = IncidentRepository(db)

    try:
        inc_uuid = uuid.UUID(req.incident_id)
        incident = await inc_repo.get_incident_by_id(inc_uuid)
    except ValueError:
        incident = await inc_repo.get_incident_by_human_id(req.incident_id)

    inc_id_str = incident.human_id if incident else req.incident_id
    real_inc_uuid = incident.id if incident else None

    # Call corresponding approved response function
    if req.action_type == "isolate_endpoint":
        result = await response_actions.isolate_endpoint(req.target, inc_id_str, req.approved_by)
    elif req.action_type == "block_ip":
        result = await response_actions.block_ip(req.target, "001", inc_id_str, req.approved_by)
    elif req.action_type == "kill_process":
        result = await response_actions.kill_process(1234, req.target, "001", inc_id_str, req.approved_by)
    elif req.action_type == "quarantine_file":
        result = await response_actions.quarantine_file(req.target, "001", inc_id_str, req.approved_by)
    elif req.action_type == "disable_user_account":
        result = await response_actions.disable_user_account(req.target, "001", inc_id_str, req.approved_by)
    else:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Unsupported action type '{req.action_type}'.")

    # Record action execution and log to audit trail
    if real_inc_uuid:
        action_rec = await resp_repo.create_action(
            incident_id=real_inc_uuid,
            action_type=req.action_type,
            target=req.target,
            description=f"Execution of {req.action_type} on {req.target}",
            high_impact=True,
            approval_status="approved"
        )
        await resp_repo.record_execution(action_rec.id, result)
        await resp_repo.log_audit_trail(
            actor=req.approved_by,
            action="RESPONSE_ACTION_EXECUTED",
            details=result,
            incident_id=real_inc_uuid
        )

    return {
        "status": "success",
        "action_type": req.action_type,
        "target": req.target,
        "execution_result": result
    }
