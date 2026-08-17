"""Async Repository for append-only Incident Audit Log records."""

import uuid
from typing import List, Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from database.models.incident_audit import IncidentAuditLog


class IncidentAuditRepository:
    """Provides async database operations for logging and reading incident audit trail records."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def log_audit_entry(
        self,
        incident_id: uuid.UUID,
        action: str,
        field_name: Optional[str] = None,
        old_value: Optional[str] = None,
        new_value: Optional[str] = None,
        actor: str = "analyst",
        metadata: Optional[dict] = None
    ) -> IncidentAuditLog:
        """Logs an append-only audit trail entry for an incident action."""
        record = IncidentAuditLog(
            incident_id=incident_id,
            action=action,
            field_name=field_name,
            old_value=old_value,
            new_value=new_value,
            actor=actor,
            metadata_json=metadata or {}
        )
        self.session.add(record)
        # Note: Do not execute commit here so callers can combine with transaction
        return record

    async def list_audit_logs_for_incident(self, incident_id: uuid.UUID) -> List[IncidentAuditLog]:
        """Lists audit log records for an incident."""
        query = select(IncidentAuditLog).where(IncidentAuditLog.incident_id == incident_id).order_by(IncidentAuditLog.timestamp.asc())
        result = await self.session.execute(query)
        return list(result.scalars().all())
