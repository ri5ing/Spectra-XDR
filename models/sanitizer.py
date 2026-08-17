"""Telemetry Sanitizer Utility for SPECTRA-XDR.

Sanitizes sensitive endpoint telemetry (passwords, private API keys, credentials)
prior to cloud LLM inference (e.g. Gemini API), while preserving threat indicators.
"""

import re
from typing import Any, Dict, List, Union


PATTERNS_TO_REDACT = [
    (re.compile(r'(?i)(password|passwd|secret|api_key|token|access_token|private_key)\s*[:=]\s*["\']?([^"\'\s&]+)["\']?'), r'\1=[REDACTED]'),
    (re.compile(r'(?i)Bearer\s+[A-Za-z0-9\-\._~\+\/]+=*'), r'Bearer [REDACTED]'),
]


def sanitize_text(text: str) -> str:
    """Sanitize sensitive credentials and tokens in string telemetry."""
    if not isinstance(text, str):
        return text
    sanitized = text
    for pattern, replacement in PATTERNS_TO_REDACT:
        sanitized = pattern.sub(replacement, sanitized)
    return sanitized


def sanitize_telemetry(data: Union[Dict[str, Any], List[Any], str]) -> Union[Dict[str, Any], List[Any], str]:
    """Recursively sanitize dictionary or list telemetry data structures."""
    if isinstance(data, str):
        return sanitize_text(data)
    elif isinstance(data, dict):
        sanitized_dict = {}
        for key, value in data.items():
            if any(sensitive_word in key.lower() for sensitive_word in ["password", "secret", "private_key", "token", "auth"]):
                sanitized_dict[key] = "[REDACTED]"
            else:
                sanitized_dict[key] = sanitize_telemetry(value)
        return sanitized_dict
    elif isinstance(data, list):
        return [sanitize_telemetry(item) for item in data]
    return data
