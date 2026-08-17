"""Async Repository for Response Action Persistence and Audit Trails."""

import uuid
from datetime import datetime, timezone
from typing import List, Optional, Dict, Any
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from database.models.response import ResponseActionRecord, AuditTrailRecord


class ResponseRepository:
    """Repository managing Response Actions and immutable Audit Logs."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_action(
        self,
        incident_id: uuid.UUID,
        action_type: str,
        target: str,
        description: str,
        high_impact: bool = False,
        approval_status: str = "pending_approval"
    ) -> ResponseActionRecord:
        """Create a response action record."""
        action = ResponseActionRecord(
            incident_id=incident_id,
            action_type=action_type,
            target=target,
            description=description,
            high_impact=high_impact,
            approval_status=approval_status,
            execution_status="PENDING"
        )
        self.session.add(action)
        await self.session.commit()
        await self.session.refresh(action)
        return action

    async def get_action_by_id(self, action_id: uuid.UUID) -> Optional[ResponseActionRecord]:
        """Fetch response action record by ID."""
        stmt = select(ResponseActionRecord).where(ResponseActionRecord.id == action_id)
        res = await self.session.execute(stmt)
        return res.scalars().first()

    async def list_actions_for_incident(self, incident_id: uuid.UUID) -> List[ResponseActionRecord]:
        """List response actions for an incident."""
        stmt = (
            select(ResponseActionRecord)
            .where(ResponseActionRecord.incident_id == incident_id)
            .order_by(ResponseActionRecord.created_at.desc())
        )
        res = await self.session.execute(stmt)
        return list(res.scalars().all())

    async def update_action_approval(self, action_id: uuid.UUID, status: str, approved_by: str) -> Optional[ResponseActionRecord]:
        """Update approval status of a response action."""
        action = await self.get_action_by_id(action_id)
        if action:
            action.approval_status = status
            action.approved_by = approved_by
            await self.session.commit()
            await self.session.refresh(action)
        return action

    async def record_execution(self, action_id: uuid.UUID, result: Dict[str, Any]) -> Optional[ResponseActionRecord]:
        """Record execution result for a response action."""
        action = await self.get_action_by_id(action_id)
        if action:
            action.execution_status = "EXECUTED"
            action.execution_result = result
            action.executed_at = datetime.now(timezone.utc)
            await self.session.commit()
            await self.session.refresh(action)
        return action

    async def log_audit_trail(self, actor: str, action: str, details: Dict[str, Any], incident_id: Optional[uuid.UUID] = None) -> AuditTrailRecord:
        """Create an append-only audit log entry."""
        log = AuditTrailRecord(
            incident_id=incident_id,
            actor=actor,
            action=action,
            details=details
        )
        self.session.add(log)
        await self.session.commit()
        await self.session.refresh(log)
        return log
