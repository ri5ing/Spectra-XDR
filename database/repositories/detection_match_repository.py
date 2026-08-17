"""Async Repository for Detection Matches."""

import uuid
from datetime import datetime
from typing import List, Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from database.models.detection_match import DetectionMatch


class DetectionMatchRepository:
    """Provides async database CRUD operations for DetectionMatches."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_match(
        self,
        detection_rule_id: uuid.UUID,
        incident_id: Optional[uuid.UUID],
        match_reason: dict,
        event_count: int = 1,
        window_start: Optional[datetime] = None,
        window_end: Optional[datetime] = None
    ) -> DetectionMatch:
        """Persists a new detection match with uniqueness checking."""
        # Check idempotency
        existing = await self.get_existing_match(detection_rule_id, incident_id, window_start, window_end)
        if existing:
            return existing

        match_obj = DetectionMatch(
            detection_rule_id=detection_rule_id,
            incident_id=incident_id,
            event_count=event_count,
            match_reason=match_reason,
            window_start=window_start,
            window_end=window_end
        )
        self.session.add(match_obj)
        await self.session.commit()
        await self.session.refresh(match_obj)
        return match_obj

    async def get_by_id(self, id_val: uuid.UUID) -> Optional[DetectionMatch]:
        """Retrieves match by UUID."""
        result = await self.session.execute(select(DetectionMatch).where(DetectionMatch.id == id_val))
        return result.scalar_one_or_none()

    async def list_matches(self, limit: int = 10, offset: int = 0, incident_id: Optional[uuid.UUID] = None) -> List[DetectionMatch]:
        """Lists detection matches."""
        query = select(DetectionMatch)
        if incident_id:
            query = query.where(DetectionMatch.incident_id == incident_id)
        query = query.order_by(DetectionMatch.matched_at.desc()).offset(offset).limit(limit)
        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def get_existing_match(
        self,
        rule_db_id: uuid.UUID,
        incident_id: Optional[uuid.UUID],
        window_start: Optional[datetime],
        window_end: Optional[datetime]
    ) -> Optional[DetectionMatch]:
        """Queries for existing match with identical rule, incident, and window bounds."""
        query = select(DetectionMatch).where(
            DetectionMatch.detection_rule_id == rule_db_id,
            DetectionMatch.incident_id == incident_id,
            DetectionMatch.window_start == window_start,
            DetectionMatch.window_end == window_end
        )
        result = await self.session.execute(query)
        return result.scalar_one_or_none()
