"""Unit tests for canonical IOC normalization."""

from intelligence.ioc.models import ExtractedIOC, IOCType
from intelligence.ioc.normalizer import IOCNormalizer


def test_ip_normalization():
    """Verify stripping octet leading zeros for IPv4."""
    normalizer = IOCNormalizer()
    ext = ExtractedIOC(type=IOCType.IP, value="192.168.001.001", source_field="test")
    record = normalizer.normalize(ext)
    assert record.value == "192.168.001.001"
    assert record.normalized_value == "192.168.1.1"


def test_domain_and_hash_normalization():
    """Verify lowercasing domains and hashes."""
    normalizer = IOCNormalizer()
    ext_domain = ExtractedIOC(type=IOCType.DOMAIN, value="Malicious-Domain.COM.", source_field="test")
    rec_domain = normalizer.normalize(ext_domain)
    assert rec_domain.value == "Malicious-Domain.COM."
    assert rec_domain.normalized_value == "malicious-domain.com"

    ext_hash = ExtractedIOC(type=IOCType.MD5, value="5D41402ABC4B2A76B9719D911017C592", source_field="test")
    rec_hash = normalizer.normalize(ext_hash)
    assert rec_hash.normalized_value == "5d41402abc4b2a76b9719d911017c592"


def test_url_normalization():
    """Verify normalizing URL scheme and host while preserving path case."""
    normalizer = IOCNormalizer()
    ext_url = ExtractedIOC(type=IOCType.URL, value="HTTP://Example.COM/PathWithCamelCase", source_field="test")
    rec_url = normalizer.normalize(ext_url)
    assert rec_url.normalized_value == "http://example.com/PathWithCamelCase"
