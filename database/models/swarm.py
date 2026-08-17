"""SQLAlchemy Models for AI Swarm Execution Records."""

import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from sqlalchemy import String, Float, Boolean, DateTime, ForeignKey, JSON, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID

from database.base import Base


class SwarmRun(Base):
    """DB Model for a Multi-Agent Swarm execution run."""

    __tablename__ = "swarm_runs"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    incident_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("incidents.id", ondelete="CASCADE"), nullable=False, index=True)
    human_incident_id: Mapped[str] = mapped_column(String(64), nullable=False)
    
    current_agent: Mapped[str] = mapped_column(String(64), default="supervisor")
    completed_agents: Mapped[List[str]] = mapped_column(JSON, default=list)
    attack_chain: Mapped[List[str]] = mapped_column(JSON, default=list)
    
    risk_score: Mapped[float] = mapped_column(Float, default=0.0)
    risk_level: Mapped[str] = mapped_column(String(32), default="LOW")
    human_approval_required: Mapped[bool] = mapped_column(Boolean, default=False)
    human_approval_status: Mapped[str] = mapped_column(String(32), default="not_required")

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    thoughts: Mapped[List["AgentThoughtRecord"]] = relationship("AgentThoughtRecord", back_populates="swarm_run", cascade="all, delete-orphan")


class AgentThoughtRecord(Base):
    """DB Model for an individual agent thought artifact."""

    __tablename__ = "agent_thought_records"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    swarm_run_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("swarm_runs.id", ondelete="CASCADE"), nullable=False, index=True)
    
    agent_role: Mapped[str] = mapped_column(String(64), nullable=False)
    model_used: Mapped[str] = mapped_column(String(64), nullable=False)
    summary: Mapped[str] = mapped_column(Text, nullable=False)
    findings: Mapped[List[str]] = mapped_column(JSON, default=list)
    confidence: Mapped[float] = mapped_column(Float, default=0.9)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    swarm_run: Mapped["SwarmRun"] = relationship("SwarmRun", back_populates="thoughts")
