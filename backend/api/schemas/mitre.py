"""Pydantic API schemas for MITRE ATT&CK endpoints."""

import uuid
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict


class MitreTechniqueResponse(BaseModel):
    """API response schema for MITRE ATT&CK techniques."""
    model_config = ConfigDict(from_attributes=True)

    id: Optional[uuid.UUID] = None
    technique_id: str
    technique_name: str
    tactic: str
    subtechnique_id: Optional[str] = None
    description: str
    detection_rationale: str
    source: str = "spectra_catalog"
    created_at: Optional[datetime] = None


class MitreMappingResponse(BaseModel):
    """API response schema for MITRE technique mappings."""
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    technique: MitreTechniqueResponse
    matched_rule_id: Optional[str] = None
    matched_group: Optional[str] = None
    confidence: float = 1.0
