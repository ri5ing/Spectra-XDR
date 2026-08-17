"""Async Repository for MITRE ATT&CK techniques and event mappings."""

import uuid
from typing import List, Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from database.models.mitre import MitreTechnique
from database.models.event_mitre import EventMitreMapping
from intelligence.mitre.models import MITRETechnique, MITREMapping


class MitreRepository:
    """Provides async database operations for MITRE ATT&CK techniques and mappings."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_technique_id(self, technique_id: str) -> Optional[MitreTechnique]:
        """Retrieves MITRE technique by ID (e.g. T1059)."""
        result = await self.session.execute(
            select(MitreTechnique).where(MitreTechnique.technique_id == technique_id)
        )
        return result.scalar_one_or_none()

    async def list_techniques(self, tactic: Optional[str] = None) -> List[MitreTechnique]:
        """Lists cataloged MITRE techniques."""
        query = select(MitreTechnique)
        if tactic:
            query = query.where(MitreTechnique.tactic == tactic)
        result = await self.session.execute(query.order_by(MitreTechnique.technique_id.asc()))
        return list(result.scalars().all())

    async def get_or_create_technique(self, model: MITRETechnique) -> MitreTechnique:
        """Retrieves or creates MITRE technique catalog record."""
        existing = await self.get_by_technique_id(model.technique_id)
        if existing:
            return existing

        db_tech = MitreTechnique(
            technique_id=model.technique_id,
            technique_name=model.technique_name,
            tactic=model.tactic,
            subtechnique_id=model.subtechnique_id,
            description=model.description,
            detection_rationale=model.detection_rationale,
            source=model.source
        )
        self.session.add(db_tech)
        await self.session.commit()
        await self.session.refresh(db_tech)
        return db_tech

    async def create_event_mapping(
        self,
        event_id: uuid.UUID,
        technique_db_id: uuid.UUID,
        mapping: MITREMapping
    ) -> EventMitreMapping:
        """Persists mapping between an event and a MITRE technique."""
        # Check if already mapped
        existing = await self.session.execute(
            select(EventMitreMapping).where(
                EventMitreMapping.event_id == event_id,
                EventMitreMapping.technique_id == technique_db_id
            )
        )
        found = existing.scalar_one_or_none()
        if found:
            return found

        db_map = EventMitreMapping(
            event_id=event_id,
            technique_id=technique_db_id,
            matched_rule_id=mapping.matched_rule_id,
            matched_group=mapping.matched_group,
            confidence=mapping.confidence
        )
        self.session.add(db_map)
        await self.session.commit()
        await self.session.refresh(db_map)
        return db_map
