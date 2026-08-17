"""MITRE ATT&CK Models for SPECTRA-XDR."""

import uuid
from typing import Optional
from pydantic import BaseModel, Field


class MITRETechnique(BaseModel):
    """Represents a MITRE ATT&CK technique or sub-technique in the local catalog."""
    technique_id: str = Field(..., description="e.g. T1059 or T1059.001")
    technique_name: str
    tactic: str
    subtechnique_id: Optional[str] = None
    description: str
    detection_rationale: str
    source: str = "spectra_catalog"


class MITREMapping(BaseModel):
    """Deterministic association of an event to a MITRE ATT&CK technique."""
    id: uuid.UUID = Field(default_factory=uuid.uuid4)
    technique: MITRETechnique
    matched_rule_id: Optional[str] = None
    matched_group: Optional[str] = None
    confidence: float = 1.0
