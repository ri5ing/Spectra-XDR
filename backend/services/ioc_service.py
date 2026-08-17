"""Backend service for IOC management and database operations."""

import uuid
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from database.repositories.ioc_repository import IOCRepository
from database.models.ioc import IOC
from intelligence.ioc.service import IOCService as LocalIOCService
from intelligence.ioc.models import IOCRecord


class BackendIOCService:
    """Service layer bridging database storage with deterministic IOC extraction."""

    def __init__(self, session: AsyncSession):
        self.repo = IOCRepository(session)
        self.local_service = LocalIOCService()

    async def get_ioc_by_id(self, ioc_id: uuid.UUID) -> Optional[IOC]:
        return await self.repo.get_by_id(ioc_id)

    async def list_iocs(self, limit: int = 10, offset: int = 0, ioc_type: Optional[str] = None) -> List[IOC]:
        return await self.repo.list_iocs(limit=limit, offset=offset, ioc_type=ioc_type)

    async def extract_and_persist_iocs(self, event_dict: dict, raw_event: dict) -> List[IOC]:
        records: List[IOCRecord] = self.local_service.process_event_payload(event_dict, raw_event)
        persisted: List[IOC] = []
        for r in records:
            ioc_obj = await self.repo.get_or_create(r)
            persisted.append(ioc_obj)
        return persisted
