"""SQLAlchemy ORM model for security telemetry events."""

import uuid
from datetime import datetime, timezone
from typing import Any, Dict, Optional, TYPE_CHECKING
from sqlalchemy import (
    DateTime,
    ForeignKey,
    Integer,
    JSON,
    String,
    Text,
    func,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database.base import Base

if TYPE_CHECKING:
    from database.models.incident import Incident


class Event(Base):
    """ORM representation of a normalized security telemetry event."""

    __tablename__ = "events"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    event_id: Mapped[str] = mapped_column(String(255), index=True, nullable=False)
    timestamp: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), index=True, nullable=False
    )
    source: Mapped[str] = mapped_column(
        String(50), default="wazuh", index=True, nullable=False
    )

    agent_id: Mapped[Optional[str]] = mapped_column(String(100), index=True, nullable=True)
    agent_name: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    agent_ip: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)

    rule_id: Mapped[Optional[str]] = mapped_column(String(100), index=True, nullable=True)
    rule_level: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    rule_description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    event_type: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    location: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    raw_event: Mapped[Dict[str, Any]] = mapped_column(JSON, nullable=False, default=dict)

    incident_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("incidents.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        default=lambda: datetime.now(timezone.utc),
    )

    # Relationships
    incident: Mapped[Optional["Incident"]] = relationship(
        "Incident", back_populates="events"
    )
