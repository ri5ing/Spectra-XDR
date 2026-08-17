"""Database repositories package for SPECTRA-XDR."""

from database.repositories.event_repository import EventRepository
from database.repositories.incident_repository import IncidentRepository

__all__ = ["EventRepository", "IncidentRepository"]
