"""Pydantic API schemas for Incident Investigation and Analyst Workflows."""

import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, ConfigDict


class IncidentDetailResponse(BaseModel):
    """API response schema for detailed incident view."""
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    incident_id: str
    title: str
    description: Optional[str] = None
    status: str
    severity: str
    assigned_to: Optional[str] = None
    resolution: Optional[str] = None
    resolved_at: Optional[datetime] = None
    first_seen: Optional[datetime] = None
    last_seen: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime
    events: List[uuid.UUID] = []


class IncidentSummaryResponse(BaseModel):
    """API response schema for incident summary statistics."""
    incident_id: str
    severity: str
    status: str
    title: str
    description: Optional[str] = None
    assigned_to: Optional[str] = None
    resolution: Optional[str] = None
    resolved_at: Optional[str] = None
    event_count: int
    detection_match_count: int
    evidence_count: int
    ioc_count: int
    mitre_technique_count: int
    first_seen_at: Optional[str] = None
    last_seen_at: Optional[str] = None
    sources: List[str]
    agents: List[str]
    rule_ids: List[str]
    mitre_techniques: List[str]


class IncidentTimelineItem(BaseModel):
    """API response schema for a single investigation timeline item."""
    timestamp: str
    type: str  # event, detection, note, audit
    source_id: str
    summary: str
    severity: str = "low"
    details: Dict[str, Any] = {}


class IncidentTimelineResponse(BaseModel):
    """API response schema for an incident investigation timeline."""
    incident_id: str
    total_items: int
    timeline: List[IncidentTimelineItem]


class IncidentNoteCreate(BaseModel):
    """API request schema for adding an analyst note."""
    content: str
    author: str = "analyst"


class IncidentNoteUpdate(BaseModel):
    """API request schema for updating an analyst note."""
    content: str
    author: str = "analyst"


class IncidentNoteResponse(BaseModel):
    """API response schema for analyst notes."""
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    incident_id: uuid.UUID
    author: str
    content: str
    created_at: datetime
    updated_at: datetime


class IncidentAuditEntryResponse(BaseModel):
    """API response schema for incident audit log entries."""
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    incident_id: uuid.UUID
    action: str
    field_name: Optional[str] = None
    old_value: Optional[str] = None
    new_value: Optional[str] = None
    actor: str
    timestamp: datetime
    metadata_json: Dict[str, Any] = {}
