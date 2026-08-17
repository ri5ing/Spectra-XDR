"""FastAPI Route Handlers for Deterministic Detections and Correlation API."""

import uuid
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from database.session import get_db_session
from backend.services.detection_service import BackendDetectionService
from backend.api.schemas.detection import (
    DetectionRuleResponse,
    DetectionMatchResponse,
    DetectionRunRequest,
    DetectionRunResponse
)

router = APIRouter(prefix="/detections", tags=["Deterministic Detections & Correlation"])


@router.get("/rules", response_model=List[DetectionRuleResponse], summary="List Detection Rules")
async def list_detection_rules(
    enabled_only: bool = Query(default=False, description="Filter for enabled rules only"),
    db: AsyncSession = Depends(get_db_session)
):
    """Lists deterministic detection rules."""
    service = BackendDetectionService(db)
    return await service.list_rules(enabled_only=enabled_only)


@router.get("/rules/{rule_id}", response_model=DetectionRuleResponse, summary="Get Detection Rule Details")
async def get_detection_rule(
    rule_id: str,
    db: AsyncSession = Depends(get_db_session)
):
    """Retrieves detection rule details by string rule_id (e.g. DET-001)."""
    service = BackendDetectionService(db)
    rule = await service.get_rule_by_rule_id(rule_id)
    if not rule:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Detection rule '{rule_id}' not found")
    return rule


@router.post("/run", response_model=DetectionRunResponse, summary="Run Deterministic Detection Engine")
async def run_detection_pipeline(
    payload: Optional[DetectionRunRequest] = None,
    db: AsyncSession = Depends(get_db_session)
):
    """Executes deterministic detection pipeline over persisted events."""
    service = BackendDetectionService(db)
    rule_id = payload.rule_id if payload else None
    limit_events = payload.limit_events if payload else 100
    res = await service.run_detection_pipeline(target_rule_id=rule_id, limit_events=limit_events)
    return res


@router.get("/matches", response_model=List[DetectionMatchResponse], summary="List Detection Matches")
async def list_detection_matches(
    limit: int = Query(default=10, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    incident_id: Optional[uuid.UUID] = Query(default=None, description="Filter matches by incident UUID"),
    db: AsyncSession = Depends(get_db_session)
):
    """Lists generated detection matches."""
    service = BackendDetectionService(db)
    return await service.list_matches(limit=limit, offset=offset, incident_id=incident_id)


@router.get("/matches/{match_id}", response_model=DetectionMatchResponse, summary="Get Detection Match Details")
async def get_detection_match(
    match_id: uuid.UUID,
    db: AsyncSession = Depends(get_db_session)
):
    """Retrieves single detection match by UUID primary key."""
    service = BackendDetectionService(db)
    match_obj = await service.get_match_by_id(match_id)
    if not match_obj:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Detection match '{match_id}' not found")
    return match_obj
