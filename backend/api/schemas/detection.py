"""Pydantic API schemas for Detection endpoints."""

import uuid
from datetime import datetime
from typing import Any, Dict, Optional, List
from pydantic import BaseModel, ConfigDict


class DetectionRuleResponse(BaseModel):
    """API response schema for detection rules."""
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    rule_id: str
    name: str
    description: Optional[str] = None
    version: str
    enabled: bool
    severity: str
    condition_type: str
    condition_config: Dict[str, Any]
    mitre_technique_id: Optional[str] = None
    created_at: datetime
    updated_at: datetime


class DetectionMatchResponse(BaseModel):
    """API response schema for detection match records."""
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    detection_rule_id: uuid.UUID
    incident_id: Optional[uuid.UUID] = None
    matched_at: datetime
    window_start: Optional[datetime] = None
    window_end: Optional[datetime] = None
    event_count: int
    match_reason: Dict[str, Any]
    created_at: datetime


class DetectionRunRequest(BaseModel):
    """API request schema for triggering detection pipeline."""
    rule_id: Optional[str] = None
    limit_events: int = 100


class DetectionRunResponse(BaseModel):
    """API response schema for detection pipeline execution summary."""
    rules_evaluated: int
    matches_generated: int
    incidents_affected: int
    events_correlated: int
