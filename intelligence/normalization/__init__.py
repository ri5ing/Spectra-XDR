"""Event Normalization package for SPECTRA-XDR."""

from intelligence.normalization.models import NormalizedEvent
from intelligence.normalization.wazuh import normalize_wazuh_alert

__all__ = ["NormalizedEvent", "normalize_wazuh_alert"]
