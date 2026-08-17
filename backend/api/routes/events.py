"""Normalized Security Telemetry Events API Endpoints."""

from typing import List, Optional
from fastapi import APIRouter, Depends, Query, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from database.session import get_db_session
from backend.services.event_service import EventService
from backend.api.schemas.event import EventResponse
from intelligence.normalization.models import NormalizedEvent

router = APIRouter()


@router.get("", response_model=List[EventResponse], summary="Retrieve Persisted Normalized Events")
async def get_persisted_events(
    limit: int = Query(default=10, ge=1, le=500),
    offset: int = Query(default=0, ge=0),
    agent_id: Optional[str] = Query(default=None),
    rule_id: Optional[str] = Query(default=None),
    source: Optional[str] = Query(default=None),
    session: AsyncSession = Depends(get_db_session)
):
    """Retrieves persisted security telemetry events from PostgreSQL database."""
    try:
        service = EventService(session)
        events = await service.list_persisted_events(
            limit=limit,
            offset=offset,
            agent_id=agent_id,
            rule_id=rule_id,
            source=source,
        )
        return events
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to query events database: {str(e)}"
        )


@router.post("", response_model=EventResponse, status_code=status.HTTP_201_CREATED, summary="Ingest Normalized Event")
async def ingest_event(
    event: NormalizedEvent,
    session: AsyncSession = Depends(get_db_session)
):
    """Ingests and persists a NormalizedEvent payload into PostgreSQL."""
    try:
        service = EventService(session)
        persisted = await service.ingest_normalized_event(event)
        return persisted
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to ingest event into database: {str(e)}"
        )
