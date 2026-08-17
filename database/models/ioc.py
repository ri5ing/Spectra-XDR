"""SQLAlchemy ORM model for IOC records."""

import uuid
from datetime import datetime, timezone
from typing import Any, Dict
from sqlalchemy import DateTime, Float, JSON, String, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from database.base import Base


class IOC(Base):
    """ORM representation of a normalized Indicator of Compromise (IOC)."""

    __tablename__ = "iocs"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    type: Mapped[str] = mapped_column(String(50), index=True, nullable=False)
    value: Mapped[str] = mapped_column(String(2048), nullable=False)
    normalized_value: Mapped[str] = mapped_column(String(2048), index=True, nullable=False)

    source: Mapped[str] = mapped_column(String(50), default="wazuh", nullable=False)
    confidence: Mapped[float] = mapped_column(Float, default=1.0, nullable=False)

    first_seen: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False
    )
    last_seen: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False
    )

    evidence: Mapped[Dict[str, Any]] = mapped_column(JSON, default=dict, nullable=False)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        default=lambda: datetime.now(timezone.utc),
        nullable=False
    )
