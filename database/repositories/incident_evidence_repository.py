"""Async Repository for Incident Evidence log records."""

import uuid
from typing import List, Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from database.models.incident_evidence import IncidentEvidence


class IncidentEvidenceRepository:
    """Provides async database CRUD operations for IncidentEvidence records."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def add_evidence(
        self,
        incident_id: uuid.UUID,
        evidence_type: str,
        evidence_data: dict,
        event_id: Optional[uuid.UUID] = None,
        detection_match_id: Optional[uuid.UUID] = None
    ) -> IncidentEvidence:
        """Persists an auditable evidence record for an incident with uniqueness checking."""
        query = select(IncidentEvidence).where(
            IncidentEvidence.incident_id == incident_id,
            IncidentEvidence.event_id == event_id,
            IncidentEvidence.detection_match_id == detection_match_id,
            IncidentEvidence.evidence_type == evidence_type
        )
        existing = await self.session.execute(query)
        found = existing.scalar_one_or_none()
        if found:
            return found

        record = IncidentEvidence(
            incident_id=incident_id,
            event_id=event_id,
            detection_match_id=detection_match_id,
            evidence_type=evidence_type,
            evidence_data=evidence_data
        )
        self.session.add(record)
        await self.session.commit()
        await self.session.refresh(record)
        return record

    async def list_evidence_for_incident(self, incident_id: uuid.UUID) -> List[IncidentEvidence]:
        """Lists all auditable evidence items for an incident."""
        query = select(IncidentEvidence).where(IncidentEvidence.incident_id == incident_id).order_by(IncidentEvidence.created_at.asc())
        result = await self.session.execute(query)
        return list(result.scalars().all())
