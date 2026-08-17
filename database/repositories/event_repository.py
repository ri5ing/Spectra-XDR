"""Async Repository for security telemetry events."""

import uuid
from typing import List, Optional
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from database.models.event import Event


class EventRepository:
    """Async repository providing database CRUD operations for Event model."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_event(self, event_data: dict) -> Event:
        """Persists a new event record in the database."""
        event = Event(**event_data)
        self.session.add(event)
        await self.session.commit()
        await self.session.refresh(event)
        return event

    async def get_event_by_id(self, id_val: uuid.UUID) -> Optional[Event]:
        """Retrieves an event by its internal database UUID primary key."""
        result = await self.session.execute(select(Event).where(Event.id == id_val))
        return result.scalar_one_or_none()

    async def get_event_by_event_id(self, event_id: str) -> Optional[Event]:
        """Retrieves an event by its telemetry event_id string."""
        result = await self.session.execute(select(Event).where(Event.event_id == event_id))
        return result.scalar_one_or_none()

    async def list_events(
        self,
        limit: int = 10,
        offset: int = 0,
        agent_id: Optional[str] = None,
        rule_id: Optional[str] = None,
        source: Optional[str] = None,
        incident_id: Optional[uuid.UUID] = None,
    ) -> List[Event]:
        """Lists events with optional filtering and pagination."""
        query = select(Event)

        if agent_id:
            query = query.where(Event.agent_id == agent_id)
        if rule_id:
            query = query.where(Event.rule_id == rule_id)
        if source:
            query = query.where(Event.source == source)
        if incident_id:
            query = query.where(Event.incident_id == incident_id)

        query = query.order_by(Event.timestamp.desc()).offset(offset).limit(limit)
        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def count_events(self) -> int:
        """Returns total count of events in database."""
        result = await self.session.execute(select(func.count(Event.id)))
        return result.scalar_one() or 0

    async def associate_event_with_incident(
        self, event: Event, incident_id: uuid.UUID
    ) -> Event:
        """Associates an existing event with an incident ID."""
        event.incident_id = incident_id
        self.session.add(event)
        await self.session.commit()
        await self.session.refresh(event)
        return event
