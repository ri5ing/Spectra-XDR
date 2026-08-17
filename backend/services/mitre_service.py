"""Backend service for MITRE ATT&CK technique catalog and event mapping."""

import uuid
from typing import List, Optional, Tuple
from sqlalchemy.ext.asyncio import AsyncSession
from database.repositories.mitre_repository import MitreRepository
from database.models.mitre import MitreTechnique
from database.models.event_mitre import EventMitreMapping
from intelligence.mitre.service import MITREService as LocalMITREService


class BackendMitreService:
    """Service layer bridging database storage with deterministic MITRE mapping."""

    def __init__(self, session: AsyncSession):
        self.repo = MitreRepository(session)
        self.local_service = LocalMITREService()

    async def get_technique_by_id(self, technique_id: str) -> Optional[MitreTechnique]:
        return await self.repo.get_by_technique_id(technique_id)

    async def list_techniques(self, tactic: Optional[str] = None) -> List[MitreTechnique]:
        # Sync catalog to DB first
        for tech in self.local_service.list_techniques():
            await self.repo.get_or_create_technique(tech)
        return await self.repo.list_techniques(tactic=tactic)

    async def map_and_persist_event(self, event_id: uuid.UUID, event_dict: dict, raw_event: dict) -> List[Tuple[MitreTechnique, EventMitreMapping]]:
        mappings = self.local_service.map_event(event_dict, raw_event)
        results = []
        for m in mappings:
            db_tech = await self.repo.get_or_create_technique(m.technique)
            db_map = await self.repo.create_event_mapping(event_id, db_tech.id, m)
            results.append((db_tech, db_map))
        return results
