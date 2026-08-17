"""Async Repository for Event Enrichment data."""

import uuid
from typing import List, Tuple
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from database.models.event_ioc import EventIOC
from database.models.event_mitre import EventMitreMapping
from database.models.ioc import IOC
from database.models.mitre import MitreTechnique


class EnrichmentRepository:
    """Provides async database operations for querying and associating enriched event data."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def associate_ioc_with_event(self, event_id: uuid.UUID, ioc_id: uuid.UUID) -> EventIOC:
        """Associates an IOC record with an event."""
        existing = await self.session.execute(
            select(EventIOC).where(EventIOC.event_id == event_id, EventIOC.ioc_id == ioc_id)
        )
        found = existing.scalar_one_or_none()
        if found:
            return found

        db_link = EventIOC(event_id=event_id, ioc_id=ioc_id)
        self.session.add(db_link)
        await self.session.commit()
        await self.session.refresh(db_link)
        return db_link

    async def get_event_iocs(self, event_id: uuid.UUID) -> List[IOC]:
        """Retrieves all associated IOC records for an event."""
        result = await self.session.execute(
            select(IOC).join(EventIOC, EventIOC.ioc_id == IOC.id).where(EventIOC.event_id == event_id)
        )
        return list(result.scalars().all())

    async def get_event_mitre_mappings(self, event_id: uuid.UUID) -> List[Tuple[MitreTechnique, EventMitreMapping]]:
        """Retrieves all mapped MITRE techniques and mapping details for an event."""
        result = await self.session.execute(
            select(MitreTechnique, EventMitreMapping)
            .join(EventMitreMapping, EventMitreMapping.technique_id == MitreTechnique.id)
            .where(EventMitreMapping.event_id == event_id)
        )
        return list(result.all())
