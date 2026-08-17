"""Deterministic IOC Extractor for SPECTRA-XDR."""

import re
from typing import Any, Dict, List
from intelligence.ioc.models import ExtractedIOC, IOCType

# Regular Expression Patterns
IPV4_REGEX = re.compile(r"\b(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\b")
IPV6_REGEX = re.compile(r"\b(?:[0-9a-fA-F]{1,4}:){7}[0-9a-fA-F]{1,4}\b")
DOMAIN_REGEX = re.compile(r"\b(?:[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?\.)+[a-zA-Z]{2,6}\b")
URL_REGEX = re.compile(r"https?://[^\s<>'\"`]+")
MD5_REGEX = re.compile(r"\b[a-fA-F0-9]{32}\b")
SHA1_REGEX = re.compile(r"\b[a-fA-F0-9]{40}\b")
SHA256_REGEX = re.compile(r"\b[a-fA-F0-9]{64}\b")
WIN_FILEPATH_REGEX = re.compile(r"\b[a-zA-Z]:\\(?:[^\s\\/:*?\"<>|]+\\)*[^\s\\/:*?\"<>|]+\b")
LINUX_FILEPATH_REGEX = re.compile(r"/(?:[a-zA-Z0-9._-]+/)+[a-zA-Z0-9._-]+")

# Field mappings in Wazuh raw_event payloads
USERNAME_FIELDS = ["srcuser", "dstuser", "user", "username", "account_name", "syscheck.user_name"]
FILEPATH_FIELDS = ["file", "path", "syscheck.path", "syscheck.file", "syscheck.audit.file.name"]
IP_FIELDS = ["srcip", "dstip", "agent.ip", "syscheck.audit.login.ip"]


class IOCExtractor:
    """Deterministic extractor for Indicators of Compromise (IOCs)."""

    def extract_from_payload(self, event_data: Dict[str, Any], raw_event: Dict[str, Any]) -> List[ExtractedIOC]:
        """Extracts IOCs deterministically from normalized fields and raw_event evidence."""
        iocs: List[ExtractedIOC] = []
        seen_keys = set()

        def _add_ioc(ioc_type: IOCType, value: str, source_field: str, confidence: float = 1.0):
            if not value or not isinstance(value, str):
                return
            val_clean = value.strip()
            if not val_clean:
                return
            key = (ioc_type, val_clean)
            if key not in seen_keys:
                seen_keys.add(key)
                iocs.append(ExtractedIOC(
                    type=ioc_type,
                    value=val_clean,
                    source_field=source_field,
                    confidence=confidence,
                    evidence={"field": source_field, "extracted_value": val_clean}
                ))

        # 1. Structured Field Extraction
        for field in USERNAME_FIELDS:
            val = self._get_nested_field(raw_event, field)
            if val and isinstance(val, str) and val not in ("-", "root", "SYSTEM"):
                _add_ioc(IOCType.USERNAME, val, f"raw_event.{field}", confidence=0.95)

        for field in FILEPATH_FIELDS:
            val = self._get_nested_field(raw_event, field)
            if val and isinstance(val, str):
                _add_ioc(IOCType.FILE_PATH, val, f"raw_event.{field}", confidence=0.95)

        for field in IP_FIELDS:
            val = self._get_nested_field(raw_event, field) or event_data.get(field)
            if val and isinstance(val, str) and IPV4_REGEX.match(val):
                _add_ioc(IOCType.IP, val, f"field.{field}", confidence=1.0)

        # Agent IP & Location
        agent_ip = event_data.get("agent_ip")
        if agent_ip and IPV4_REGEX.match(agent_ip):
            _add_ioc(IOCType.IP, agent_ip, "agent_ip", confidence=1.0)

        # 2. Text / Full Payload Regex Scanning
        text_payload = self._convert_to_searchable_text(raw_event)

        # URLs
        for match in URL_REGEX.finditer(text_payload):
            _add_ioc(IOCType.URL, match.group(0), "raw_event.text", confidence=0.9)

        # Hashes (SHA256, SHA1, MD5) - match longest first to avoid partial string matches
        for match in SHA256_REGEX.finditer(text_payload):
            _add_ioc(IOCType.SHA256, match.group(0), "raw_event.text", confidence=1.0)

        for match in SHA1_REGEX.finditer(text_payload):
            val = match.group(0)
            # Ensure not substring of sha256
            if not any(val in i.value for i in iocs if i.type == IOCType.SHA256):
                _add_ioc(IOCType.SHA1, val, "raw_event.text", confidence=1.0)

        for match in MD5_REGEX.finditer(text_payload):
            val = match.group(0)
            if not any(val in i.value for i in iocs if i.type in (IOCType.SHA256, IOCType.SHA1)):
                _add_ioc(IOCType.MD5, val, "raw_event.text", confidence=1.0)

        # IPv4
        for match in IPV4_REGEX.finditer(text_payload):
            val = match.group(0)
            if not val.startswith("127.0.0."):  # Exclude loopback
                _add_ioc(IOCType.IP, val, "raw_event.text", confidence=0.9)

        # IPv6
        for match in IPV6_REGEX.finditer(text_payload):
            val = match.group(0)
            if val != "0:0:0:0:0:0:0:1" and val != "::1":
                _add_ioc(IOCType.IP, val, "raw_event.text", confidence=0.9)

        # File Paths regex scanning
        for match in WIN_FILEPATH_REGEX.finditer(text_payload):
            _add_ioc(IOCType.FILE_PATH, match.group(0), "raw_event.text", confidence=0.85)

        for match in LINUX_FILEPATH_REGEX.finditer(text_payload):
            val = match.group(0)
            if val.startswith(("/usr/", "/etc/", "/var/", "/tmp/", "/home/", "/bin/", "/sbin/")):
                _add_ioc(IOCType.FILE_PATH, val, "raw_event.text", confidence=0.85)

        # Domains (excluding IP matches and common code extensions)
        for match in DOMAIN_REGEX.finditer(text_payload):
            val = match.group(0)
            if not IPV4_REGEX.match(val) and not val.endswith((".py", ".json", ".txt", ".exe", ".dll", ".log", ".gz", ".tar")):
                _add_ioc(IOCType.DOMAIN, val, "raw_event.text", confidence=0.8)

        return iocs

    def _get_nested_field(self, data: Dict[str, Any], path: str) -> Any:
        """Retrieves field value from nested dict using dot notation."""
        parts = path.split(".")
        curr = data
        for p in parts:
            if not isinstance(curr, dict):
                return None
            curr = curr.get(p)
        return curr

    def _convert_to_searchable_text(self, data: Any) -> str:
        """Recursively formats dict/list structure into searchable text buffer."""
        if isinstance(data, dict):
            return " ".join(self._convert_to_searchable_text(v) for v in data.values())
        elif isinstance(data, list):
            return " ".join(self._convert_to_searchable_text(item) for item in data)
        return str(data)
