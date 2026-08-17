"""IOC Service orchestrating extraction and normalization."""

from typing import Any, Dict, List
from intelligence.ioc.models import IOCRecord
from intelligence.ioc.extractor import IOCExtractor
from intelligence.ioc.normalizer import IOCNormalizer


class IOCService:
    """Provides high-level deterministic IOC extraction and normalization services."""

    def __init__(self):
        self.extractor = IOCExtractor()
        self.normalizer = IOCNormalizer()

    def process_event_payload(self, event_data: Dict[str, Any], raw_event: Dict[str, Any]) -> List[IOCRecord]:
        """Extracts and normalizes all IOCs present in event payload."""
        extracted_list = self.extractor.extract_from_payload(event_data, raw_event)
        records: List[IOCRecord] = []
        seen_normalized = set()

        for ext in extracted_list:
            record = self.normalizer.normalize(ext, source=event_data.get("source", "wazuh"))
            key = (record.type, record.normalized_value)
            if key not in seen_normalized:
                seen_normalized.add(key)
                records.append(record)

        return records
