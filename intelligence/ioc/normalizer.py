"""Canonical IOC Normalizer for SPECTRA-XDR."""

from urllib.parse import urlparse, urlunparse
from intelligence.ioc.models import ExtractedIOC, IOCRecord, IOCType


class IOCNormalizer:
    """Normalizes extracted IOCs into canonical representations while preserving original evidence."""

    def normalize(self, extracted: ExtractedIOC, source: str = "wazuh") -> IOCRecord:
        """Transforms ExtractedIOC into normalized IOCRecord."""
        raw_val = extracted.value
        norm_val = self.normalize_value(extracted.type, raw_val)

        return IOCRecord(
            type=extracted.type,
            value=raw_val,
            normalized_value=norm_val,
            source=source,
            confidence=extracted.confidence,
            evidence=extracted.evidence or {}
        )

    def normalize_value(self, ioc_type: IOCType, value: str) -> str:
        """Applies type-specific canonical normalization rules."""
        if not value:
            return ""

        val = value.strip()

        if ioc_type == IOCType.IP:
            # Strip leading zeros in IPv4 octets (e.g. 192.168.001.001 -> 192.168.1.1)
            if "." in val and ":" not in val:
                parts = val.split(".")
                if len(parts) == 4:
                    try:
                        return ".".join(str(int(p)) for p in parts)
                    except ValueError:
                        pass
            return val.lower()

        elif ioc_type == IOCType.DOMAIN:
            # Lowercase domain, strip trailing dot
            return val.rstrip(".").lower()

        elif ioc_type == IOCType.URL:
            # Normalize scheme and host casing, preserve path casing
            try:
                parsed = urlparse(val)
                scheme = parsed.scheme.lower()
                netloc = parsed.netloc.lower()
                return urlunparse((scheme, netloc, parsed.path, parsed.params, parsed.query, parsed.fragment))
            except Exception:
                return val.lower()

        elif ioc_type in (IOCType.MD5, IOCType.SHA1, IOCType.SHA256):
            # Hashes normalized to lowercase
            return val.lower()

        elif ioc_type == IOCType.USERNAME:
            return val.strip()

        elif ioc_type == IOCType.FILE_PATH:
            # Strip redundant whitespace
            return val.strip()

        return val
