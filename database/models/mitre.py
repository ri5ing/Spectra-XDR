"""SQLAlchemy ORM model for MITRE ATT&CK techniques."""

import uuid
from datetime import datetime, timezone
from typing import Optional
from sqlalchemy import DateTime, String, Text, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from database.base import Base


class MitreTechnique(Base):
    """ORM representation of a MITRE ATT&CK technique catalog item."""

    __tablename__ = "mitre_techniques"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    technique_id: Mapped[str] = mapped_column(String(50), unique=True, index=True, nullable=False)
    technique_name: Mapped[str] = mapped_column(String(255), nullable=False)
    tactic: Mapped[str] = mapped_column(String(100), index=True, nullable=False)

    subtechnique_id: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    detection_rationale: Mapped[str] = mapped_column(Text, nullable=False)
    source: Mapped[str] = mapped_column(String(50), default="spectra_catalog", nullable=False)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        default=lambda: datetime.now(timezone.utc),
        nullable=False
    )
