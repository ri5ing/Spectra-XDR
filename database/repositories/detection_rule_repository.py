"""Async Repository for Detection Rules."""

import uuid
from typing import List, Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from database.models.detection_rule import DetectionRule


class DetectionRuleRepository:
    """Provides async database CRUD operations for DetectionRules."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_rule(self, rule_data: dict) -> DetectionRule:
        """Persists a new detection rule."""
        rule = DetectionRule(**rule_data)
        self.session.add(rule)
        await self.session.commit()
        await self.session.refresh(rule)
        return rule

    async def get_by_id(self, id_val: uuid.UUID) -> Optional[DetectionRule]:
        """Retrieves a rule by internal UUID primary key."""
        result = await self.session.execute(select(DetectionRule).where(DetectionRule.id == id_val))
        return result.scalar_one_or_none()

    async def get_by_rule_id(self, rule_id: str) -> Optional[DetectionRule]:
        """Retrieves a rule by string rule_id (e.g. DET-001)."""
        result = await self.session.execute(select(DetectionRule).where(DetectionRule.rule_id == rule_id))
        return result.scalar_one_or_none()

    async def list_rules(self, enabled_only: bool = False) -> List[DetectionRule]:
        """Lists detection rules."""
        query = select(DetectionRule)
        if enabled_only:
            query = query.where(DetectionRule.enabled == True)
        result = await self.session.execute(query.order_by(DetectionRule.rule_id.asc()))
        return list(result.scalars().all())

    async def sync_builtin_rule(self, rule_def: dict) -> DetectionRule:
        """Synchronizes a built-in detection rule into the database cleanly."""
        existing = await self.get_by_rule_id(rule_def["rule_id"])
        if existing:
            return existing
        return await self.create_rule(rule_def)
