"""Normalized security event schema definitions."""

from typing import Any, Dict, Optional
from pydantic import BaseModel, Field


class NormalizedEvent(BaseModel):
    """Standardized security event representation across SPECTRA-XDR."""

    event_id: str = Field(..., description="Unique event identifier")
    timestamp: str = Field(..., description="ISO 8601 or standard event timestamp")
    source: str = Field(default="wazuh", description="Telemetry source provider (e.g. wazuh)")
    agent_id: Optional[str] = Field(default=None, description="Monitored endpoint agent ID")
    agent_name: Optional[str] = Field(default=None, description="Monitored endpoint hostname/name")
    agent_ip: Optional[str] = Field(default=None, description="Monitored endpoint IP address")
    rule_id: Optional[str] = Field(default=None, description="Detection rule ID")
    rule_level: Optional[int] = Field(default=None, description="Detection rule severity level")
    rule_description: Optional[str] = Field(default=None, description="Detection rule summary or title")
    event_type: Optional[str] = Field(default=None, description="Categorized security event classification")
    location: Optional[str] = Field(default=None, description="Log source path or facility location")
    raw_event: Dict[str, Any] = Field(default_factory=dict, description="Preserved original telemetry payload evidence")
