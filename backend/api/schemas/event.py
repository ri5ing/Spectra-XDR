"""API Pydantic schemas for Security Telemetry Events."""

import uuid
from datetime import datetime
from typing import Any, Dict, Optional
from pydantic import BaseModel, Field


class EventResponse(BaseModel):
    """API schema for returning persisted security event details."""

    id: uuid.UUID = Field(..., description="Internal database UUID")
    event_id: str = Field(..., description="Telemetry event identifier")
    timestamp: datetime = Field(..., description="Event timestamp")
    source: str = Field(default="wazuh", description="Telemetry source provider")
    agent_id: Optional[str] = Field(default=None)
    agent_name: Optional[str] = Field(default=None)
    agent_ip: Optional[str] = Field(default=None)
    rule_id: Optional[str] = Field(default=None)
    rule_level: Optional[int] = Field(default=None)
    rule_description: Optional[str] = Field(default=None)
    event_type: Optional[str] = Field(default=None)
    location: Optional[str] = Field(default=None)
    raw_event: Dict[str, Any] = Field(default_factory=dict)
    incident_id: Optional[uuid.UUID] = Field(default=None)
    created_at: datetime = Field(...)

    model_config = {"from_attributes": True}
