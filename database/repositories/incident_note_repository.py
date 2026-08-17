"""Async Repository for Analyst Incident Notes."""

import uuid
from typing import List, Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from database.models.incident_note import IncidentNote


class IncidentNoteRepository:
    """Provides async database CRUD operations for IncidentNote records."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_note(self, incident_id: uuid.UUID, content: str, author: str = "analyst") -> IncidentNote:
        """Persists a new analyst note for an incident."""
        note = IncidentNote(incident_id=incident_id, content=content, author=author)
        self.session.add(note)
        await self.session.commit()
        await self.session.refresh(note)
        return note

    async def get_note_by_id(self, note_id: uuid.UUID) -> Optional[IncidentNote]:
        """Retrieves a note by primary key UUID."""
        result = await self.session.execute(select(IncidentNote).where(IncidentNote.id == note_id))
        return result.scalar_one_or_none()

    async def list_notes_for_incident(self, incident_id: uuid.UUID) -> List[IncidentNote]:
        """Lists all analyst notes for an incident ordered chronologically."""
        query = select(IncidentNote).where(IncidentNote.incident_id == incident_id).order_by(IncidentNote.created_at.asc())
        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def update_note(self, note: IncidentNote, content: str) -> IncidentNote:
        """Updates content of an existing analyst note."""
        note.content = content
        self.session.add(note)
        await self.session.commit()
        await self.session.refresh(note)
        return note

    async def delete_note(self, note: IncidentNote) -> None:
        """Deletes an analyst note."""
        await self.session.delete(note)
        await self.session.commit()
