"""Security Incident Lifecycle & Investigation Endpoints."""

import uuid
from typing import List, Optional
from fastapi import APIRouter, Depends, Query, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from database.session import get_db_session
from backend.services.incident_service import IncidentService
from backend.services.incident_investigation_service import IncidentInvestigationService
from backend.api.schemas.incident import IncidentCreate, IncidentUpdate, IncidentResponse
from backend.api.schemas.event import EventResponse
from backend.api.schemas.detection import DetectionMatchResponse
from backend.api.schemas.ioc import IOCResponse
from backend.api.schemas.mitre import MitreTechniqueResponse
from backend.api.schemas.evidence import IncidentEvidenceResponse
from backend.api.schemas.investigation import (
    IncidentDetailResponse,
    IncidentSummaryResponse,
    IncidentTimelineResponse,
    IncidentNoteCreate,
    IncidentNoteUpdate,
    IncidentNoteResponse,
    IncidentAuditEntryResponse
)

router = APIRouter()


def _format_incident_response(incident) -> dict:
    """Helper to format incident response schema."""
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
        "assigned_to": getattr(incident, "assigned_to", None),
        "resolution": getattr(incident, "resolution", None),
        "resolved_at": getattr(incident, "resolved_at", None),
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
    assigned_to: Optional[str] = Query(default=None, description="Filter by assigned analyst"),
    session: AsyncSession = Depends(get_db_session)
):
    """Lists incidents with filtering and deterministic ordering."""
    try:
        service = IncidentService(session)
        incidents = await service.list_incidents(
            limit=limit,
            offset=offset,
            status_filter=status_filter,
            severity_filter=severity_filter,
        )
        if assigned_to:
            incidents = [inc for inc in incidents if str(getattr(inc, "assigned_to", "")).lower() == str(assigned_to).lower()]
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
    """Retrieves an incident by UUID or human identifier (INC-XXXXXX)."""
    service = IncidentService(session)
    incident = await service.get_incident(incident_id)
    if not incident:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Incident '{incident_id}' not found"
        )
    return _format_incident_response(incident)


@router.get("/{incident_id}/summary", response_model=IncidentSummaryResponse, summary="Get Incident Investigation Summary")
async def get_incident_summary(
    incident_id: str,
    session: AsyncSession = Depends(get_db_session)
):
    """Retrieves deterministic summary statistics for an incident."""
    service = IncidentInvestigationService(session)
    incident = await service.get_incident(incident_id)
    if not incident:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Incident '{incident_id}' not found")
    summary = await service.get_incident_summary(incident.id)
    return summary


@router.get("/{incident_id}/events", response_model=List[EventResponse], summary="Get Persisted Events for Incident")
async def get_incident_events(
    incident_id: str,
    limit: int = Query(default=50, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    severity: Optional[str] = Query(default=None),
    source: Optional[str] = Query(default=None),
    agent_id: Optional[str] = Query(default=None),
    rule_id: Optional[str] = Query(default=None),
    session: AsyncSession = Depends(get_db_session)
):
    """Retrieves persisted SPECTRA events associated with an incident with optional filtering."""
    service = IncidentInvestigationService(session)
    incident = await service.get_incident(incident_id)
    if not incident:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Incident '{incident_id}' not found")
    events = await service.get_incident_events(
        incident.id, limit=limit, offset=offset, severity=severity, source=source, agent_id=agent_id, rule_id=rule_id
    )
    return events


@router.get("/{incident_id}/detections", response_model=List[DetectionMatchResponse], summary="Get Detection Matches for Incident")
async def get_incident_detections(
    incident_id: str,
    session: AsyncSession = Depends(get_db_session)
):
    """Retrieves detection matches contributing to an incident."""
    service = IncidentInvestigationService(session)
    incident = await service.get_incident(incident_id)
    if not incident:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Incident '{incident_id}' not found")
    return await service.get_incident_detections(incident.id)


@router.get("/{incident_id}/iocs", response_model=List[IOCResponse], summary="Get Aggregated IOCs for Incident")
async def get_incident_iocs(
    incident_id: str,
    session: AsyncSession = Depends(get_db_session)
):
    """Retrieves deduplicated extracted and normalized IOC records linked to an incident."""
    service = IncidentInvestigationService(session)
    incident = await service.get_incident(incident_id)
    if not incident:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Incident '{incident_id}' not found")
    return await service.get_incident_iocs(incident.id)


@router.get("/{incident_id}/mitre", response_model=List[MitreTechniqueResponse], summary="Get Aggregated MITRE Techniques for Incident")
async def get_incident_mitre(
    incident_id: str,
    session: AsyncSession = Depends(get_db_session)
):
    """Retrieves deduplicated MITRE ATT&CK techniques mapped to an incident."""
    service = IncidentInvestigationService(session)
    incident = await service.get_incident(incident_id)
    if not incident:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Incident '{incident_id}' not found")
    return await service.get_incident_mitre(incident.id)


@router.get("/{incident_id}/timeline", response_model=IncidentTimelineResponse, summary="Get Incident Investigation Timeline")
async def get_incident_timeline(
    incident_id: str,
    session: AsyncSession = Depends(get_db_session)
):
    """Retrieves a deterministic investigation timeline combining events, detections, evidence, status updates, notes."""
    service = IncidentInvestigationService(session)
    incident = await service.get_incident(incident_id)
    if not incident:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Incident '{incident_id}' not found")
    timeline_items = await service.get_incident_timeline(incident.id)
    return {
        "incident_id": incident.incident_id,
        "total_items": len(timeline_items),
        "timeline": timeline_items
    }


@router.get("/{incident_id}/evidence", response_model=List[IncidentEvidenceResponse], summary="List Auditable Evidence for Incident")
async def get_incident_evidence(
    incident_id: str,
    session: AsyncSession = Depends(get_db_session)
):
    """Retrieves all auditable evidence records linked to an incident."""
    service = IncidentService(session)
    incident = await service.get_incident(incident_id)
    if not incident:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Incident '{incident_id}' not found"
        )
    from backend.services.detection_service import BackendDetectionService
    det_service = BackendDetectionService(session)
    evidence_list = await det_service.list_evidence_for_incident(incident.id)
    return [IncidentEvidenceResponse.model_validate(ev) for ev in evidence_list]


@router.patch("/{incident_id}", response_model=IncidentResponse, summary="Update Incident Attributes and Status Workflow")
async def update_incident(
    incident_id: str,
    payload: IncidentUpdate,
    session: AsyncSession = Depends(get_db_session)
):
    """Updates attributes of an incident with validated status transitions and atomic audit logging."""
    service = IncidentInvestigationService(session)
    incident = await service.get_incident(incident_id)
    if not incident:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Incident '{incident_id}' not found")
    try:
        updated = await service.update_incident_workflow(incident, payload.model_dump(exclude_unset=True))
        return _format_incident_response(updated)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


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


# Analyst Notes Endpoints

@router.post("/{incident_id}/notes", response_model=IncidentNoteResponse, status_code=status.HTTP_201_CREATED, summary="Add Analyst Note")
async def add_analyst_note(
    incident_id: str,
    payload: IncidentNoteCreate,
    session: AsyncSession = Depends(get_db_session)
):
    """Adds an analyst comment note to an incident."""
    service = IncidentInvestigationService(session)
    incident = await service.get_incident(incident_id)
    if not incident:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Incident '{incident_id}' not found")
    note = await service.add_analyst_note(incident.id, content=payload.content, author=payload.author)
    return note


@router.get("/{incident_id}/notes", response_model=List[IncidentNoteResponse], summary="List Analyst Notes for Incident")
async def list_analyst_notes(
    incident_id: str,
    session: AsyncSession = Depends(get_db_session)
):
    """Lists all analyst notes linked to an incident."""
    service = IncidentInvestigationService(session)
    incident = await service.get_incident(incident_id)
    if not incident:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Incident '{incident_id}' not found")
    return await service.note_repo.list_notes_for_incident(incident.id)


@router.patch("/{incident_id}/notes/{note_id}", response_model=IncidentNoteResponse, summary="Update Analyst Note")
async def update_analyst_note(
    incident_id: str,
    note_id: uuid.UUID,
    payload: IncidentNoteUpdate,
    session: AsyncSession = Depends(get_db_session)
):
    """Updates content of an analyst note."""
    service = IncidentInvestigationService(session)
    updated = await service.update_analyst_note(note_id, payload.content, actor=payload.author)
    if not updated:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Analyst note '{note_id}' not found")
    return updated


@router.delete("/{incident_id}/notes/{note_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Delete Analyst Note")
async def delete_analyst_note(
    incident_id: str,
    note_id: uuid.UUID,
    session: AsyncSession = Depends(get_db_session)
):
    """Deletes an analyst note."""
    service = IncidentInvestigationService(session)
    success = await service.delete_analyst_note(note_id)
    if not success:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Analyst note '{note_id}' not found")
    return None


@router.get("/{incident_id}/audit", response_model=List[IncidentAuditEntryResponse], summary="Get Incident Audit Log")
async def get_incident_audit_log(
    incident_id: str,
    session: AsyncSession = Depends(get_db_session)
):
    """Retrieves immutable append-only audit trail records for an incident."""
    service = IncidentInvestigationService(session)
    incident = await service.get_incident(incident_id)
    if not incident:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Incident '{incident_id}' not found")
    return await service.audit_repo.list_audit_logs_for_incident(incident.id)
