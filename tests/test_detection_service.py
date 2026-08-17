"""Unit tests for BackendDetectionService."""

import asyncio
from backend.services.detection_service import get_higher_severity


def test_severity_precedence():
    """Verify deterministic severity precedence: critical > high > medium > low."""
    assert get_higher_severity("low", "medium") == "medium"
    assert get_higher_severity("high", "medium") == "high"
    assert get_higher_severity("high", "critical") == "critical"
    assert get_higher_severity("critical", "low") == "critical"
