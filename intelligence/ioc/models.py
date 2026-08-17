"""IOC Models and Type Enums for SPECTRA-XDR."""

import uuid
from enum import Enum
from datetime import datetime, timezone
from typing import Any, Dict, Optional
from pydantic import BaseModel, Field


class IOCType(str, Enum):
    """Supported Indicators of Compromise (IOC) types."""
    IP = "ip"
    DOMAIN = "domain"
    URL = "url"
    MD5 = "md5"
    SHA1 = "sha1"
    SHA256 = "sha256"
    USERNAME = "username"
    FILE_PATH = "file_path"


class ExtractedIOC(BaseModel):
    """Raw IOC extracted from event payload before normalization/persistence."""
    type: IOCType
    value: str
    source_field: str
    confidence: float = Field(default=1.0, ge=0.0, le=1.0)
    evidence: Optional[Dict[str, Any]] = None


class IOCRecord(BaseModel):
    """Normalized IOC record representation."""
    id: uuid.UUID = Field(default_factory=uuid.uuid4)
    type: IOCType
    value: str
    normalized_value: str
    source: str = "wazuh"
    confidence: float = 1.0
    first_seen: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    last_seen: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    evidence: Dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
