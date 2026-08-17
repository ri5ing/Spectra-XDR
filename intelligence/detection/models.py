"""Pydantic validation models for Detection Rule Condition configurations."""

from enum import Enum
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field, ConfigDict


class ConditionType(str, Enum):
    """Supported deterministic detection condition types."""
    SINGLE_EVENT = "SINGLE_EVENT"
    THRESHOLD = "THRESHOLD"
    SAME_SOURCE_THRESHOLD = "SAME_SOURCE_THRESHOLD"
    IOC_MATCH = "IOC_MATCH"
    MITRE_TECHNIQUE_MATCH = "MITRE_TECHNIQUE_MATCH"
    COMBINATION = "COMBINATION"


class SingleEventConditionConfig(BaseModel):
    """Configuration for SINGLE_EVENT condition type."""
    model_config = ConfigDict(extra="forbid")
    filters: Dict[str, Any] = Field(default_factory=dict, description="Exact key-value filter conditions (e.g., rule_id, source)")


class ThresholdConditionConfig(BaseModel):
    """Configuration for THRESHOLD and SAME_SOURCE_THRESHOLD condition types."""
    model_config = ConfigDict(extra="forbid")
    threshold: int = Field(..., ge=1, description="Minimum count of matching events")
    window_seconds: int = Field(..., ge=1, description="Time window in seconds")
    correlation_key: str = Field(default="agent_id", description="Correlation field (e.g. agent_id, agent_ip, source)")
    filters: Dict[str, Any] = Field(default_factory=dict, description="Event filter conditions")


class IOCMatchConditionConfig(BaseModel):
    """Configuration for IOC_MATCH condition type."""
    model_config = ConfigDict(extra="forbid")
    ioc_type: Optional[str] = Field(default=None, description="Optional IOC type filter (e.g., ip, domain, url, hash)")
    ioc_value: Optional[str] = Field(default=None, description="Optional specific IOC value filter")


class MitreMatchConditionConfig(BaseModel):
    """Configuration for MITRE_TECHNIQUE_MATCH condition type."""
    model_config = ConfigDict(extra="forbid")
    technique_id: str = Field(..., description="Target MITRE technique ID (e.g. T1059.001)")


class CombinationConditionConfig(BaseModel):
    """Configuration for COMBINATION condition type."""
    model_config = ConfigDict(extra="forbid")
    operator: str = Field(default="AND", description="Logical operator: AND or OR")
    conditions: List[Dict[str, Any]] = Field(..., min_length=1, description="Sub-condition dictionaries")
