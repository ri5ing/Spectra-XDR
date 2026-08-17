"""Backend Detection Service for executing rules and correlating incidents."""

import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from sqlalchemy.ext.asyncio import AsyncSession

from database.repositories.detection_rule_repository import DetectionRuleRepository
from database.repositories.detection_match_repository import DetectionMatchRepository
from database.repositories.incident_evidence_repository import IncidentEvidenceRepository
from database.repositories.event_repository import EventRepository
from database.repositories.incident_repository import IncidentRepository
from backend.services.enrichment_service import BackendEnrichmentService
from intelligence.detection.engine import DetectionEngine, DetectionMatchResult
from intelligence.detection.registry import DetectionRegistry
from intelligence.detection.models import ConditionType
from database.models.detection_rule import DetectionRule
from database.models.detection_match import DetectionMatch
from database.models.incident import Incident

SEVERITY_PRECEDENCE = {"low": 1, "medium": 2, "high": 3, "critical": 4}


def get_higher_severity(sev1: str, sev2: str) -> str:
    """Returns higher severity using strict precedence: critical > high > medium > low."""
    val1 = SEVERITY_PRECEDENCE.get(str(sev1).lower(), 1)
    val2 = SEVERITY_PRECEDENCE.get(str(sev2).lower(), 1)
    return sev1 if val1 >= val2 else sev2


class BackendDetectionService:
    """Service layer orchestrating detection rule execution, incident correlation, and evidence logging."""

    def __init__(self, session: AsyncSession):
        self.session = session
        self.rule_repo = DetectionRuleRepository(session)
        self.match_repo = DetectionMatchRepository(session)
        self.evidence_repo = IncidentEvidenceRepository(session)
        self.event_repo = EventRepository(session)
        self.incident_repo = IncidentRepository(session)
        self.enrichment_service = BackendEnrichmentService(session)
        self.engine = DetectionEngine()

    async def sync_builtin_rules(self) -> List[DetectionRule]:
        """Ensures all built-in detection rules are synchronized into the database."""
        rules = []
        for r_def in DetectionRegistry.list_builtin_rules():
            rule_obj = await self.rule_repo.sync_builtin_rule(r_def)
            rules.append(rule_obj)
        return rules

    async def list_rules(self, enabled_only: bool = False) -> List[DetectionRule]:
        await self.sync_builtin_rules()
        return await self.rule_repo.list_rules(enabled_only=enabled_only)

    async def get_rule_by_rule_id(self, rule_id: str) -> Optional[DetectionRule]:
        await self.sync_builtin_rules()
        return await self.rule_repo.get_by_rule_id(rule_id)

    async def list_matches(self, limit: int = 10, offset: int = 0, incident_id: Optional[uuid.UUID] = None) -> List[DetectionMatch]:
        return await self.match_repo.list_matches(limit=limit, offset=offset, incident_id=incident_id)

    async def get_match_by_id(self, match_id: uuid.UUID) -> Optional[DetectionMatch]:
        return await self.match_repo.get_by_id(match_id)

    async def list_evidence_for_incident(self, incident_id: uuid.UUID) -> List[Any]:
        return await self.evidence_repo.list_evidence_for_incident(incident_id)

    async def run_detection_pipeline(
        self,
        target_rule_id: Optional[str] = None,
        limit_events: int = 100
    ) -> Dict[str, Any]:
        """Runs deterministic detection pipeline over persisted events."""
        # 1. Sync rules & fetch target rules
        await self.sync_builtin_rules()
        if target_rule_id:
            rule_obj = await self.rule_repo.get_by_rule_id(target_rule_id)
            rules_to_run = [rule_obj] if rule_obj and rule_obj.enabled else []
        else:
            rules_to_run = await self.rule_repo.list_rules(enabled_only=True)

        if not rules_to_run:
            return {"rules_evaluated": 0, "matches_generated": 0, "incidents_affected": 0, "events_correlated": 0}

        # 2. Fetch events from database
        events_orm = await self.event_repo.list_events(limit=limit_events)
        if not events_orm:
            return {"rules_evaluated": len(rules_to_run), "matches_generated": 0, "incidents_affected": 0, "events_correlated": 0}

        event_dicts = []
        enriched_map = {}

        for e in events_orm:
            e_dict = {
                "id": str(e.id),
                "event_id": e.event_id,
                "timestamp": e.timestamp.isoformat() if e.timestamp else "",
                "source": e.source,
                "agent_id": e.agent_id,
                "agent_name": e.agent_name,
                "agent_ip": e.agent_ip,
                "rule_id": e.rule_id,
                "rule_level": e.rule_level,
                "rule_description": e.rule_description,
                "event_type": e.event_type,
                "location": e.location,
            }
            event_dicts.append(e_dict)
            
            # Enrich event to get IOCs/MITRE mappings
            enriched_data = await self.enrichment_service.get_enriched_event(e.id)
            if enriched_data:
                enriched_map[str(e.id)] = enriched_data

        matches_generated = 0
        incidents_affected = set()
        events_correlated = set()

        # 3. Evaluate rules
        for r_obj in rules_to_run:
            r_def = {
                "rule_id": r_obj.rule_id,
                "name": r_obj.name,
                "severity": r_obj.severity,
                "condition_type": r_obj.condition_type,
                "condition_config": r_obj.condition_config,
            }

            match_results: List[DetectionMatchResult] = []

            if r_obj.condition_type in (ConditionType.THRESHOLD, ConditionType.SAME_SOURCE_THRESHOLD):
                match_results = self.engine.evaluate_threshold_rule(r_def, event_dicts)
            else:
                for e_dict in event_dicts:
                    e_id_str = e_dict["id"]
                    en_data = enriched_map.get(e_id_str)
                    if en_data:
                        res = self.engine.evaluate_rule_on_event(r_def, e_dict, en_data)
                        if res:
                            match_results.append(res)

            # 4. Process matches: correlate incident & persist evidence
            for res in match_results:
                incident_obj = await self._correlate_or_create_incident(r_obj, res)
                incidents_affected.add(incident_obj.id)

                win_start = None
                win_end = None
                if res.window_start:
                    try:
                        win_start = datetime.fromisoformat(res.window_start)
                    except Exception:
                        pass
                if res.window_end:
                    try:
                        win_end = datetime.fromisoformat(res.window_end)
                    except Exception:
                        pass

                # Persist match record
                match_db = await self.match_repo.create_match(
                    detection_rule_id=r_obj.id,
                    incident_id=incident_obj.id,
                    match_reason=res.match_reason,
                    event_count=len(res.matched_events),
                    window_start=win_start,
                    window_end=win_end
                )
                matches_generated += 1

                # Persist evidence and associate events
                for m_evt in res.matched_events:
                    e_uuid = uuid.UUID(m_evt["id"])
                    events_correlated.add(e_uuid)
                    
                    # Link event to incident in database
                    evt_db = await self.event_repo.get_event_by_id(e_uuid)
                    if evt_db:
                        await self.event_repo.associate_event_with_incident(evt_db, incident_obj.id)

                    # Add event evidence
                    await self.evidence_repo.add_evidence(
                        incident_id=incident_obj.id,
                        event_id=e_uuid,
                        detection_match_id=match_db.id,
                        evidence_type="event",
                        evidence_data={"event_id": m_evt["event_id"], "rule_id": m_evt.get("rule_id"), "agent_id": m_evt.get("agent_id")}
                    )

                # Add detection match evidence
                await self.evidence_repo.add_evidence(
                    incident_id=incident_obj.id,
                    detection_match_id=match_db.id,
                    evidence_type="detection",
                    evidence_data=res.match_reason
                )

        return {
            "rules_evaluated": len(rules_to_run),
            "matches_generated": matches_generated,
            "incidents_affected": len(incidents_affected),
            "events_correlated": len(events_correlated)
        }

    async def _correlate_or_create_incident(self, rule_obj: DetectionRule, res: DetectionMatchResult) -> Incident:
        """Deterministically correlates match with an existing open incident or creates a new one."""
        corr_val = res.match_reason.get("correlation_value") or (res.matched_events[0].get("agent_id") if res.matched_events else None)
        
        # Check existing open incidents matching correlation value
        open_incidents = await self.incident_repo.list_incidents(status="open", limit=20)
        for inc in open_incidents:
            if corr_val and (corr_val in inc.title or (inc.description and corr_val in inc.description)):
                # Update severity if higher
                new_severity = get_higher_severity(inc.severity, rule_obj.severity)
                if new_severity != inc.severity:
                    await self.incident_repo.update_incident(inc, {"severity": new_severity})
                return inc

        # Create new deterministic incident title
        inc_title = f"{rule_obj.name}"
        if corr_val:
            inc_title += f" — agent {corr_val}"

        inc_desc = f"Deterministic detection match for rule {rule_obj.rule_id} ({rule_obj.name}). Reason: {res.match_reason}"
        
        new_inc = await self.incident_repo.create_incident({
            "title": inc_title,
            "description": inc_desc,
            "severity": rule_obj.severity,
            "status": "open"
        })
        return new_inc
