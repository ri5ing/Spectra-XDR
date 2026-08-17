"""Pydantic API schemas for Incident Evidence endpoints."""

import uuid
from datetime import datetime
from typing import Any, Dict, Optional
from pydantic import BaseModel, ConfigDict


class IncidentEvidenceResponse(BaseModel):
    """API response schema for incident evidence records."""
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    incident_id: uuid.UUID
    event_id: Optional[uuid.UUID] = None
    detection_match_id: Optional[uuid.UUID] = None
    evidence_type: str
    evidence_data: Dict[str, Any]
    created_at: datetime
