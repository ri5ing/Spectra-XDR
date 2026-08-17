"""Pydantic API schemas for IOC endpoints."""

import uuid
from datetime import datetime
from typing import Any, Dict, Optional
from pydantic import BaseModel, ConfigDict


class IOCResponse(BaseModel):
    """API response schema for IOC records."""
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    type: str
    value: str
    normalized_value: str
    source: str
    confidence: float
    first_seen: datetime
    last_seen: datetime
    evidence: Dict[str, Any]
    created_at: datetime
