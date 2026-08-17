"""Incident Service handling security case lifecycle management."""

import uuid
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status

from database.repositories.incident_repository import IncidentRepository
from database.repositories.event_repository import EventRepository
from database.models.incident import Incident
from database.models.event import Event


class IncidentService:
    """Service layer managing Incident creation, updates, and event associations."""

    def __init__(self, session: AsyncSession):
        self.incident_repo = IncidentRepository(session)
        self.event_repo = EventRepository(session)

    async def create_incident(self, incident_data: dict) -> Incident:
        """Creates a new incident record."""
        return await self.incident_repo.create_incident(incident_data)

    async def get_incident(self, identifier: str) -> Optional[Incident]:
        """Finds an incident by either UUID primary key string or human-readable identifier (INC-XXXXXX)."""
        try:
            val_uuid = uuid.UUID(identifier)
            inc = await self.incident_repo.get_incident_by_id(val_uuid)
            if inc:
                return inc
        except ValueError:
            pass

        return await self.incident_repo.get_incident_by_human_id(identifier)

    async def list_incidents(
        self,
        limit: int = 10,
        offset: int = 0,
        status_filter: Optional[str] = None,
        severity_filter: Optional[str] = None,
    ) -> List[Incident]:
        """Lists incidents with status and severity filters."""
        return await self.incident_repo.list_incidents(
            limit=limit,
            offset=offset,
            status=status_filter,
            severity=severity_filter,
        )

    async def update_incident(self, identifier: str, update_data: dict) -> Incident:
        """Updates an existing incident by ID or human identifier."""
        incident = await self.get_incident(identifier)
        if not incident:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Incident '{identifier}' not found."
            )
        return await self.incident_repo.update_incident(incident, update_data)

    async def associate_event(self, incident_identifier: str, event_id_val: uuid.UUID) -> Event:
        """Associates an existing telemetry event with an incident after verifying both exist."""
        incident = await self.get_incident(incident_identifier)
        if not incident:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Incident '{incident_identifier}' not found."
            )

        event = await self.event_repo.get_event_by_id(event_id_val)
        if not event:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Event '{event_id_val}' not found."
            )

        return await self.event_repo.associate_event_with_incident(event, incident.id)
