"""API Pydantic schemas for Security Incidents."""

import uuid
from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field, ConfigDict


class IncidentCreate(BaseModel):
    """Schema for creating a new security incident."""

    title: str = Field(..., min_length=1, max_length=255, description="Incident title")
    description: Optional[str] = Field(default=None, description="Detailed incident narrative")
    status: str = Field(default="open", description="Status (open, investigating, contained, resolved, closed)")
    severity: str = Field(default="medium", description="Severity level (low, medium, high, critical)")
    assigned_to: Optional[str] = Field(default=None)
    resolution: Optional[str] = Field(default=None)
    first_seen: Optional[datetime] = Field(default=None)
    last_seen: Optional[datetime] = Field(default=None)


class IncidentUpdate(BaseModel):
    """Schema for updating an existing incident."""

    title: Optional[str] = Field(default=None, max_length=255)
    description: Optional[str] = Field(default=None)
    status: Optional[str] = Field(default=None)
    severity: Optional[str] = Field(default=None)
    assigned_to: Optional[str] = Field(default=None)
    resolution: Optional[str] = Field(default=None)
    resolved_at: Optional[datetime] = Field(default=None)
    first_seen: Optional[datetime] = Field(default=None)
    last_seen: Optional[datetime] = Field(default=None)


class IncidentResponse(BaseModel):
    """API schema returning complete incident details."""
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID = Field(..., description="Database internal UUID")
    incident_id: str = Field(..., description="Human-readable identifier (e.g. INC-000001)")
    title: str = Field(...)
    description: Optional[str] = Field(default=None)
    status: str = Field(...)
    severity: str = Field(...)
    assigned_to: Optional[str] = Field(default=None)
    resolution: Optional[str] = Field(default=None)
    resolved_at: Optional[datetime] = Field(default=None)
    first_seen: Optional[datetime] = Field(default=None)
    last_seen: Optional[datetime] = Field(default=None)
    created_at: datetime = Field(...)
    updated_at: datetime = Field(...)
    events: List[uuid.UUID] = Field(default_factory=list, description="Associated event UUIDs")
