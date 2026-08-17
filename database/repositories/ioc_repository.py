"""Async Repository for IOC records."""

import uuid
from typing import List, Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from database.models.ioc import IOC
from intelligence.ioc.models import IOCRecord


class IOCRepository:
    """Provides async database CRUD operations for IOC records."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_ioc(self, record: IOCRecord) -> IOC:
        """Persists a new IOC record."""
        ioc = IOC(
            id=record.id,
            type=record.type.value if hasattr(record.type, "value") else str(record.type),
            value=record.value,
            normalized_value=record.normalized_value,
            source=record.source,
            confidence=record.confidence,
            first_seen=record.first_seen,
            last_seen=record.last_seen,
            evidence=record.evidence
        )
        self.session.add(ioc)
        await self.session.commit()
        await self.session.refresh(ioc)
        return ioc

    async def get_by_id(self, ioc_id: uuid.UUID) -> Optional[IOC]:
        """Retrieves an IOC record by primary key UUID."""
        result = await self.session.execute(select(IOC).where(IOC.id == ioc_id))
        return result.scalar_one_or_none()

    async def get_by_value(self, ioc_type: str, normalized_value: str) -> Optional[IOC]:
        """Retrieves an IOC record by type and canonical normalized value."""
        result = await self.session.execute(
            select(IOC).where(IOC.type == ioc_type, IOC.normalized_value == normalized_value)
        )
        return result.scalar_one_or_none()

    async def list_iocs(self, limit: int = 10, offset: int = 0, ioc_type: Optional[str] = None) -> List[IOC]:
        """Lists IOC records with optional filtering."""
        query = select(IOC)
        if ioc_type:
            query = query.where(IOC.type == ioc_type)
        query = query.order_by(IOC.created_at.desc()).offset(offset).limit(limit)
        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def get_or_create(self, record: IOCRecord) -> IOC:
        """Retrieves an existing IOC by type+normalized_value or creates a new record."""
        type_str = record.type.value if hasattr(record.type, "value") else str(record.type)
        existing = await self.get_by_value(type_str, record.normalized_value)
        if existing:
            existing.last_seen = record.last_seen
            self.session.add(existing)
            await self.session.commit()
            return existing
        return await self.create_ioc(record)
