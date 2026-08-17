"""Security Incident Lifecycle Management Endpoints."""

import uuid
from typing import List, Optional
from fastapi import APIRouter, Depends, Query, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from database.session import get_db_session
from backend.services.incident_service import IncidentService
from backend.api.schemas.incident import IncidentCreate, IncidentUpdate, IncidentResponse
from backend.api.schemas.event import EventResponse

router = APIRouter()


def _format_incident_response(incident) -> dict:
    """Helper to extract event UUID list for response schema."""
    event_uuids = []
    if "events" in incident.__dict__ and incident.events:
        event_uuids = [e.id for e in incident.events]
    return {
        "id": incident.id,
        "incident_id": incident.incident_id,
        "title": incident.title,
        "description": incident.description,
        "status": incident.status,
        "severity": incident.severity,
        "first_seen": incident.first_seen,
        "last_seen": incident.last_seen,
        "created_at": incident.created_at,
        "updated_at": incident.updated_at,
        "events": event_uuids,
    }



@router.post("", response_model=IncidentResponse, status_code=status.HTTP_201_CREATED, summary="Create Security Incident")
async def create_incident(
    payload: IncidentCreate,
    session: AsyncSession = Depends(get_db_session)
):
    """Creates a new incident record in PostgreSQL."""
    try:
        service = IncidentService(session)
        incident = await service.create_incident(payload.model_dump())
        return _format_incident_response(incident)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create incident: {str(e)}"
        )


@router.get("", response_model=List[IncidentResponse], summary="List Security Incidents")
async def list_incidents(
    limit: int = Query(default=10, ge=1, le=500),
    offset: int = Query(default=0, ge=0),
    status_filter: Optional[str] = Query(default=None, alias="status"),
    severity_filter: Optional[str] = Query(default=None, alias="severity"),
    session: AsyncSession = Depends(get_db_session)
):
    """Lists incidents with optional status/severity filtering."""
    try:
        service = IncidentService(session)
        incidents = await service.list_incidents(
            limit=limit,
            offset=offset,
            status_filter=status_filter,
            severity_filter=severity_filter,
        )
        return [_format_incident_response(inc) for inc in incidents]
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to query incidents: {str(e)}"
        )


@router.get("/{incident_id}", response_model=IncidentResponse, summary="Get Incident Details")
async def get_incident(
    incident_id: str,
    session: AsyncSession = Depends(get_db_session)
):
    """Retrieves an incident by UUID or human-readable identifier (e.g. INC-000001)."""
    service = IncidentService(session)
    incident = await service.get_incident(incident_id)
    if not incident:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Incident '{incident_id}' not found"
        )
    return _format_incident_response(incident)


@router.patch("/{incident_id}", response_model=IncidentResponse, summary="Update Incident Attributes")
async def update_incident(
    incident_id: str,
    payload: IncidentUpdate,
    session: AsyncSession = Depends(get_db_session)
):
    """Updates attributes of an existing incident."""
    service = IncidentService(session)
    updated = await service.update_incident(incident_id, payload.model_dump(exclude_unset=True))
    return _format_incident_response(updated)


@router.post("/{incident_id}/events/{event_id}", response_model=EventResponse, summary="Associate Event with Incident")
async def associate_event_with_incident(
    incident_id: str,
    event_id: uuid.UUID,
    session: AsyncSession = Depends(get_db_session)
):
    """Associates an existing telemetry event with an incident."""
    service = IncidentService(session)
    updated_event = await service.associate_event(incident_id, event_id)
    return updated_event
