"""Pydantic API schemas for event enrichment endpoints."""

import uuid
from datetime import datetime
from typing import Any, Dict, List
from pydantic import BaseModel, ConfigDict
from backend.api.schemas.ioc import IOCResponse
from backend.api.schemas.mitre import MitreMappingResponse


class EnrichedEventResponse(BaseModel):
    """API response schema for deterministically enriched events."""
    model_config = ConfigDict(from_attributes=True)

    original_event_id: uuid.UUID
    normalized_event_data: Dict[str, Any]
    extracted_iocs: List[IOCResponse]
    mitre_mappings: List[MitreMappingResponse]
    enrichment_metadata: Dict[str, Any]
    processing_timestamp: datetime
    enrichment_version: str
