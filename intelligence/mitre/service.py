"""MITRE ATT&CK Service for SPECTRA-XDR."""

from typing import Any, Dict, List, Optional
from intelligence.mitre.models import MITREMapping, MITRETechnique
from intelligence.mitre.catalog import MITRECatalog
from intelligence.mitre.mapper import MITREMapper


class MITREService:
    """Provides MITRE ATT&CK technique lookup and deterministic event mapping services."""

    def __init__(self):
        self.catalog = MITRECatalog()
        self.mapper = MITREMapper()

    def get_technique(self, technique_id: str) -> Optional[MITRETechnique]:
        return self.catalog.get_technique(technique_id)

    def list_techniques(self) -> List[MITRETechnique]:
        return self.catalog.list_techniques()

    def map_event(self, event_data: Dict[str, Any], raw_event: Dict[str, Any]) -> List[MITREMapping]:
        return self.mapper.map_event(event_data, raw_event)
