"""Backend service orchestrating deterministic event enrichment pipeline and persistence."""

import uuid
from typing import Any, Dict, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from database.repositories.event_repository import EventRepository
from database.repositories.enrichment_repository import EnrichmentRepository
from backend.services.ioc_service import BackendIOCService
from backend.services.mitre_service import BackendMitreService
from intelligence.enrichment.service import EnrichmentService as LocalEnrichmentService
from intelligence.enrichment.models import EnrichedEventData


class BackendEnrichmentService:
    """Service layer orchestrating event enrichment, persistence, and retrieval."""

    def __init__(self, session: AsyncSession):
        self.session = session
        self.event_repo = EventRepository(session)
        self.enrichment_repo = EnrichmentRepository(session)
        self.ioc_service = BackendIOCService(session)
        self.mitre_service = BackendMitreService(session)
        self.local_enrichment = LocalEnrichmentService()

    async def enrich_persisted_event(self, event_id: uuid.UUID) -> Optional[EnrichedEventData]:
        """Runs deterministic enrichment on an existing SPECTRA event and persists database records."""
        event_obj = await self.event_repo.get_event_by_id(event_id)
        if not event_obj:
            return None

        event_dict = {
            "id": str(event_obj.id),
            "event_id": event_obj.event_id,
            "timestamp": event_obj.timestamp.isoformat() if event_obj.timestamp else "",
            "source": event_obj.source,
            "agent_id": event_obj.agent_id,
            "agent_name": event_obj.agent_name,
            "agent_ip": event_obj.agent_ip,
            "rule_id": event_obj.rule_id,
            "rule_level": event_obj.rule_level,
            "rule_description": event_obj.rule_description,
            "event_type": event_obj.event_type,
            "location": event_obj.location,
        }

        # 1. Run local deterministic enrichment pipeline
        enriched_data = self.local_enrichment.enrich_event(event_obj.id, event_dict, event_obj.raw_event)

        # 2. Extract & Persist IOCs + EventIOC junction records
        persisted_iocs = await self.ioc_service.extract_and_persist_iocs(event_dict, event_obj.raw_event)
        for ioc in persisted_iocs:
            await self.enrichment_repo.associate_ioc_with_event(event_obj.id, ioc.id)

        # 3. Map & Persist MITRE Techniques + EventMitreMapping junction records
        await self.mitre_service.map_and_persist_event(event_obj.id, event_dict, event_obj.raw_event)

        return enriched_data

    async def get_enriched_event(self, event_id: uuid.UUID) -> Optional[EnrichedEventData]:
        """Retrieves existing enrichment data for a persisted event."""
        event_obj = await self.event_repo.get_event_by_id(event_id)
        if not event_obj:
            return None

        # Try fetching existing associations or enrich on the fly
        return await self.enrich_persisted_event(event_id)
