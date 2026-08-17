"""Pydantic Models for SPECTRA-XDR Multi-Agent AI Swarm."""

import uuid
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field, ConfigDict


class ModelChoice(str, Enum):
    """Supported LLM models in AI Model Router."""
    OLLAMA_LOCAL = "ollama_local"
    GEMINI_CLOUD = "gemini_cloud"
    DETERMINISTIC_FALLBACK = "deterministic_fallback"


class AgentRole(str, Enum):
    """Specialized Agent Roles in Swarm."""
    DETECTION_AGENT = "detection_agent"
    MITRE_AGENT = "mitre_agent"
    CORRELATION_AGENT = "correlation_agent"
    INVESTIGATION_AGENT = "investigation_agent"
    THREAT_INTEL_AGENT = "threat_intel_agent"
    RESPONSE_AGENT = "response_agent"
    SUPERVISOR = "supervisor"


class HumanApprovalStatus(str, Enum):
    """Approval status for high-risk response actions."""
    NOT_REQUIRED = "not_required"
    PENDING_APPROVAL = "pending_approval"
    APPROVED = "approved"
    REJECTED = "rejected"


class AgentThought(BaseModel):
    """Individual reasoning output from a swarm agent."""
    agent_role: AgentRole
    model_used: ModelChoice
    summary: str
    findings: List[str] = Field(default_factory=list)
    confidence: float = Field(default=0.9, ge=0.0, le=1.0)
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class SwarmState(BaseModel):
    """Shared short-term memory & state graph for LangGraph Supervisor."""
    model_config = ConfigDict(arbitrary_types_allowed=True)

    incident_id: uuid.UUID
    incident_human_id: str
    current_agent: AgentRole = AgentRole.SUPERVISOR
    completed_agents: List[AgentRole] = Field(default_factory=list)
    
    # Event & Telemetry Context
    event_data: Dict[str, Any] = Field(default_factory=dict)
    extracted_iocs: List[Dict[str, Any]] = Field(default_factory=list)
    mitre_mappings: List[Dict[str, Any]] = Field(default_factory=list)
    detection_matches: List[Dict[str, Any]] = Field(default_factory=list)
    
    # Agent Reasoning Artifacts
    thoughts: List[AgentThought] = Field(default_factory=list)
    attack_chain: List[str] = Field(default_factory=list)
    intel_enrichments: Dict[str, Any] = Field(default_factory=dict)
    recommended_actions: List[Dict[str, Any]] = Field(default_factory=list)
    
    # Risk & Policy Engine Results
    risk_score: float = 0.0
    risk_level: str = "LOW"
    human_approval_required: bool = False
    human_approval_status: HumanApprovalStatus = HumanApprovalStatus.NOT_REQUIRED
