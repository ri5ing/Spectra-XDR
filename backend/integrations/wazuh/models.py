"""Pydantic data models for Wazuh API responses."""

from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class WazuhAgent(BaseModel):
    """Model representing a Wazuh monitored endpoint agent."""

    id: str = Field(..., description="Unique agent identifier")
    name: str = Field(..., description="Hostname or descriptive agent name")
    ip: Optional[str] = Field(default=None, description="Registered agent IP address")
    status: Optional[str] = Field(default=None, description="Agent connection status (e.g. active, disconnected)")
    os: Optional[Dict[str, Any]] = Field(default=None, description="Operating system details")
    version: Optional[str] = Field(default=None, description="Wazuh agent version")
    group: Optional[List[str]] = Field(default=None, description="Assigned agent groups")


class WazuhAgentListResponse(BaseModel):
    """Response container for Wazuh agent listing."""

    total_affected_items: int = Field(default=0)
    affected_items: List[WazuhAgent] = Field(default_factory=list)


class WazuhAlert(BaseModel):
    """Model representing a raw Wazuh telemetry alert."""

    id: Optional[str] = Field(default=None, description="Alert event unique ID")
    timestamp: str = Field(..., description="Alert timestamp")
    agent: Optional[Dict[str, Any]] = Field(default=None, description="Originating agent metadata")
    rule: Optional[Dict[str, Any]] = Field(default=None, description="Triggered rule metadata")
    location: Optional[str] = Field(default=None, description="Log source location")
    decoder: Optional[Dict[str, Any]] = Field(default=None, description="Decoder metadata")
    full_log: Optional[str] = Field(default=None, description="Raw log text")
    data: Optional[Dict[str, Any]] = Field(default=None, description="Extracted alert fields")


class WazuhAlertListResponse(BaseModel):
    """Response container for Wazuh alert listing."""

    total_affected_items: int = Field(default=0)
    affected_items: List[Dict[str, Any]] = Field(default_factory=list)
