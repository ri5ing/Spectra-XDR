"""SQLAlchemy ORM model for append-only Incident Audit Log entries."""

import uuid
from datetime import datetime, timezone
from typing import Any, Dict, Optional
from sqlalchemy import DateTime, ForeignKey, JSON, String, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from database.base import Base


class IncidentAuditLog(Base):
    """ORM representation of an immutable, append-only incident audit trail record."""

    __tablename__ = "incident_audit_log"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    incident_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("incidents.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    action: Mapped[str] = mapped_column(String(100), nullable=False)  # STATUS_CHANGED, SEVERITY_CHANGED, NOTE_CREATED, etc.
    field_name: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    old_value: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    new_value: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    actor: Mapped[str] = mapped_column(String(255), default="analyst", nullable=False)
    timestamp: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        default=lambda: datetime.now(timezone.utc),
        nullable=False
    )
    metadata_json: Mapped[Dict[str, Any]] = mapped_column("metadata", JSON, default=dict, nullable=False)
