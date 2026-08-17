"""Async repository tests for DetectionRule, DetectionMatch, and IncidentEvidence."""

import asyncio
import uuid
from database.repositories.detection_rule_repository import DetectionRuleRepository
from database.repositories.detection_match_repository import DetectionMatchRepository
from database.repositories.incident_evidence_repository import IncidentEvidenceRepository
from database.repositories.incident_repository import IncidentRepository


def test_detection_repositories_crud(test_engine):
    """Verify repository operations for rules, matches, and evidence."""
    async def _test():
        from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker
        session_factory = async_sessionmaker(bind=test_engine, class_=AsyncSession, expire_on_commit=False)
        async with session_factory() as session:
            rule_repo = DetectionRuleRepository(session)
            match_repo = DetectionMatchRepository(session)
            evidence_repo = IncidentEvidenceRepository(session)
            incident_repo = IncidentRepository(session)

            # 1. Create rule
            rule_data = {
                "rule_id": "DET-999",
                "name": "Test Rule",
                "severity": "high",
                "condition_type": "SINGLE_EVENT",
                "condition_config": {"filters": {"rule_id": "5710"}}
            }
            rule = await rule_repo.create_rule(rule_data)
            assert rule.id is not None
            assert rule.rule_id == "DET-999"

            # 2. Create incident
            incident = await incident_repo.create_incident({"title": "Test Incident", "severity": "high"})

            # 3. Create match
            match_obj = await match_repo.create_match(
                detection_rule_id=rule.id,
                incident_id=incident.id,
                match_reason={"reason": "test"},
                event_count=1
            )
            assert match_obj.id is not None
            assert match_obj.incident_id == incident.id

            # 4. Add evidence
            ev = await evidence_repo.add_evidence(
                incident_id=incident.id,
                detection_match_id=match_obj.id,
                evidence_type="detection",
                evidence_data={"rule": "DET-999"}
            )
            assert ev.id is not None
            evidence_list = await evidence_repo.list_evidence_for_incident(incident.id)
            assert len(evidence_list) == 1

    asyncio.run(_test())
