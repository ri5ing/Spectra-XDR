"""Event Service handling persistence and event telemetry logic."""

import uuid
from datetime import datetime, timezone
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession

from database.repositories.event_repository import EventRepository
from database.models.event import Event
from intelligence.normalization.models import NormalizedEvent


class EventService:
    """Service layer for managing security event telemetry persistence."""

    def __init__(self, session: AsyncSession):
        self.repo = EventRepository(session)

    async def ingest_normalized_event(self, normalized_event: NormalizedEvent) -> Event:
        """Parses a NormalizedEvent object and persists it to PostgreSQL."""
        # Convert timestamp string to datetime
        ts = datetime.now(timezone.utc)
        if normalized_event.timestamp:
            try:
                ts = datetime.fromisoformat(normalized_event.timestamp.replace("Z", "+00:00"))
            except ValueError:
                ts = datetime.now(timezone.utc)

        event_data = {
            "event_id": normalized_event.event_id,
            "timestamp": ts,
            "source": normalized_event.source,
            "agent_id": normalized_event.agent_id,
            "agent_name": normalized_event.agent_name,
            "agent_ip": normalized_event.agent_ip,
            "rule_id": normalized_event.rule_id,
            "rule_level": normalized_event.rule_level,
            "rule_description": normalized_event.rule_description,
            "event_type": normalized_event.event_type,
            "location": normalized_event.location,
            "raw_event": normalized_event.raw_event,
        }

        return await self.repo.create_event(event_data)

    async def list_persisted_events(
        self,
        limit: int = 10,
        offset: int = 0,
        agent_id: Optional[str] = None,
        rule_id: Optional[str] = None,
        source: Optional[str] = None,
    ) -> List[Event]:
        """Lists persisted events from database repository."""
        return await self.repo.list_events(
            limit=limit,
            offset=offset,
            agent_id=agent_id,
            rule_id=rule_id,
            source=source,
        )

    async def get_event_by_id(self, id_val: uuid.UUID) -> Optional[Event]:
        """Retrieves a single event by UUID."""
        return await self.repo.get_event_by_id(id_val)
