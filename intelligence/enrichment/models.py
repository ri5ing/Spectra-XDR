"""Enrichment Models for SPECTRA-XDR."""

import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List
from pydantic import BaseModel, Field

from intelligence.ioc.models import IOCRecord
from intelligence.mitre.models import MITREMapping

ENRICHMENT_VERSION = "1.0.0"


class EnrichedEventData(BaseModel):
    """Container for a deterministically enriched security event."""
    original_event_id: uuid.UUID
    normalized_event_data: Dict[str, Any]
    extracted_iocs: List[IOCRecord] = Field(default_factory=list)
    mitre_mappings: List[MITREMapping] = Field(default_factory=list)
    enrichment_metadata: Dict[str, Any] = Field(default_factory=dict)
    processing_timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    enrichment_version: str = ENRICHMENT_VERSION
