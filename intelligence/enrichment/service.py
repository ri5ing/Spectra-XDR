"""Deterministic Enrichment Service for SPECTRA-XDR."""

import uuid
from datetime import datetime, timezone
from typing import Any, Dict
from intelligence.ioc.service import IOCService
from intelligence.mitre.service import MITREService
from intelligence.enrichment.models import EnrichedEventData, ENRICHMENT_VERSION


class EnrichmentService:
    """Orchestrates deterministic event enrichment pipeline."""

    def __init__(self):
        self.ioc_service = IOCService()
        self.mitre_service = MITREService()

    def enrich_event(self, event_id: uuid.UUID, event_dict: Dict[str, Any], raw_event: Dict[str, Any]) -> EnrichedEventData:
        """Runs deterministic enrichment pipeline on a persisted event."""
        # 1. IOC Extraction & Normalization
        iocs = self.ioc_service.process_event_payload(event_dict, raw_event)

        # 2. MITRE ATT&CK Mapping
        mitre_mappings = self.mitre_service.map_event(event_dict, raw_event)

        # 3. Assemble Enriched Event Data
        metadata = {
            "total_iocs_extracted": len(iocs),
            "total_mitre_techniques_mapped": len(mitre_mappings),
            "deterministic_pipeline": True,
            "ai_assisted": False
        }

        return EnrichedEventData(
            original_event_id=event_id,
            normalized_event_data=event_dict,
            extracted_iocs=iocs,
            mitre_mappings=mitre_mappings,
            enrichment_metadata=metadata,
            processing_timestamp=datetime.now(timezone.utc),
            enrichment_version=ENRICHMENT_VERSION
        )
