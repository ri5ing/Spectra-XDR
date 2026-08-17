"""Wazuh integration package for SPECTRA-XDR."""

from backend.integrations.wazuh.client import WazuhClient
from backend.integrations.wazuh.exceptions import (
    WazuhError,
    WazuhAuthenticationError,
    WazuhConnectionError,
    WazuhTimeoutError,
    WazuhResponseError,
)

__all__ = [
    "WazuhClient",
    "WazuhError",
    "WazuhAuthenticationError",
    "WazuhConnectionError",
    "WazuhTimeoutError",
    "WazuhResponseError",
]
