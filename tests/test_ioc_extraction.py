"""Unit tests for deterministic IOC extraction."""

from intelligence.ioc.extractor import IOCExtractor
from intelligence.ioc.models import IOCType


def test_ipv4_and_ipv6_extraction():
    """Verify extracting IPv4 and IPv6 addresses."""
    extractor = IOCExtractor()
    event_data = {"agent_ip": "192.168.1.10"}
    raw_event = {
        "srcip": "10.0.0.5",
        "full_log": "Connection from 2001:0db8:85a3:0000:0000:8a2e:0370:7334 to 172.16.254.1"
    }

    iocs = extractor.extract_from_payload(event_data, raw_event)
    extracted_vals = [i.value for i in iocs if i.type == IOCType.IP]
    assert "192.168.1.10" in extracted_vals
    assert "10.0.0.5" in extracted_vals
    assert "172.16.254.1" in extracted_vals
    assert "2001:0db8:85a3:0000:0000:8a2e:0370:7334" in extracted_vals


def test_hash_extraction():
    """Verify extracting MD5, SHA1, and SHA256 hashes."""
    extractor = IOCExtractor()
    raw_event = {
        "md5": "5d41402abc4b2a76b9719d911017c592",
        "sha1": "aaf4c61ddcc5e8a2dabede0f3b482cd9aea9434d",
        "sha256": "2cf24dba5fb0a30e26e83b2ac5b9e29e1b161e5c1fa7425e73043362938b9824"
    }

    iocs = extractor.extract_from_payload({}, raw_event)
    types = [i.type for i in iocs]
    assert IOCType.MD5 in types
    assert IOCType.SHA1 in types
    assert IOCType.SHA256 in types


def test_url_domain_username_filepath_extraction():
    """Verify URL, Domain, Username, and File Path extraction."""
    extractor = IOCExtractor()
    raw_event = {
        "srcuser": "admin_user",
        "file": "C:\\Windows\\System32\\cmd.exe",
        "full_log": "Downloaded binary from https://malicious-domain.com/payload.exe on /tmp/malware.sh"
    }

    iocs = extractor.extract_from_payload({}, raw_event)
    types = {i.type for i in iocs}
    assert IOCType.USERNAME in types
    assert IOCType.FILE_PATH in types
    assert IOCType.URL in types
    assert IOCType.DOMAIN in types

    vals = {i.value for i in iocs}
    assert "admin_user" in vals
    assert "C:\\Windows\\System32\\cmd.exe" in vals
    assert "https://malicious-domain.com/payload.exe" in vals
