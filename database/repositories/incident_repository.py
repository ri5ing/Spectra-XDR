"""Async Repository for security incidents."""

import uuid
from typing import List, Optional
from sqlalchemy import select, func, text
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from database.models.incident import Incident


class IncidentRepository:
    """Async repository providing database CRUD operations for Incident model."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def generate_next_incident_id(self) -> str:
        """Generates sequential human-readable identifier (e.g. INC-000001) atomically via sequence."""
        try:
            result = await self.session.execute(text("SELECT nextval('incident_id_seq')"))
            seq_val = result.scalar_one()
        except Exception:
            result = await self.session.execute(select(func.count(Incident.id)))
            seq_val = (result.scalar_one() or 0) + 1
        return f"INC-{seq_val:06d}"

    async def create_incident(self, incident_data: dict) -> Incident:
        """Persists a new incident record in the database."""
        if "incident_id" not in incident_data or not incident_data["incident_id"]:
            incident_data["incident_id"] = await self.generate_next_incident_id()

        incident = Incident(**incident_data)
        self.session.add(incident)
        await self.session.commit()
        return await self.get_incident_by_id(incident.id)

    async def get_incident_by_id(self, id_val: uuid.UUID) -> Optional[Incident]:
        """Retrieves an incident by its internal UUID primary key, eager loading events."""
        result = await self.session.execute(
            select(Incident).options(selectinload(Incident.events)).where(Incident.id == id_val)
        )
        return result.scalar_one_or_none()

    async def get_incident_by_human_id(self, incident_id: str) -> Optional[Incident]:
        """Retrieves an incident by human-readable string (e.g. INC-000001)."""
        result = await self.session.execute(
            select(Incident).options(selectinload(Incident.events)).where(Incident.incident_id == incident_id)
        )
        return result.scalar_one_or_none()

    async def list_incidents(
        self,
        limit: int = 10,
        offset: int = 0,
        status: Optional[str] = None,
        severity: Optional[str] = None,
    ) -> List[Incident]:
        """Lists incidents with optional filtering and pagination."""
        query = select(Incident).options(selectinload(Incident.events))

        if status:
            query = query.where(Incident.status == status)
        if severity:
            query = query.where(Incident.severity == severity)

        query = query.order_by(Incident.created_at.desc()).offset(offset).limit(limit)
        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def update_incident(self, incident: Incident, update_data: dict) -> Incident:
        """Updates attributes of an existing incident."""
        for key, value in update_data.items():
            if value is not None and hasattr(incident, key):
                setattr(incident, key, value)

        self.session.add(incident)
        await self.session.commit()
        return await self.get_incident_by_id(incident.id)
