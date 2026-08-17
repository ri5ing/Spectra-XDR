"""Unit tests for Database ORM models, repositories, and relationships."""

import asyncio
from datetime import datetime, timezone
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker
from database.repositories.event_repository import EventRepository
from database.repositories.incident_repository import IncidentRepository


def test_event_repository_crud(test_engine):
    """Verify creating, querying, filtering, and counting events."""
    async def _test():
        session_factory = async_sessionmaker(bind=test_engine, class_=AsyncSession, expire_on_commit=False)
        async with session_factory() as session:
            repo = EventRepository(session)
            
            event_data = {
                "event_id": "test-wazuh-alert-001",
                "timestamp": datetime.now(timezone.utc),
                "source": "wazuh",
                "agent_id": "007",
                "agent_name": "agent-bond",
                "agent_ip": "192.168.1.7",
                "rule_id": "5710",
                "rule_level": 5,
                "rule_description": "SSH authentication failure",
                "event_type": "sshd",
                "raw_event": {"key": "value"}
            }

            created = await repo.create_event(event_data)
            assert created.id is not None
            assert created.event_id == "test-wazuh-alert-001"
            assert created.agent_name == "agent-bond"

            # Query by UUID
            retrieved = await repo.get_event_by_id(created.id)
            assert retrieved is not None
            assert retrieved.event_id == "test-wazuh-alert-001"

            # Query by event_id string
            retrieved_by_str = await repo.get_event_by_event_id("test-wazuh-alert-001")
            assert retrieved_by_str is not None
            assert retrieved_by_str.id == created.id

            # List & Filter
            events = await repo.list_events(agent_id="007")
            assert len(events) >= 1
            assert events[0].agent_id == "007"

    asyncio.run(_test())


def test_incident_repository_crud(test_engine):
    """Verify creating, updating, and querying incidents."""
    async def _test():
        session_factory = async_sessionmaker(bind=test_engine, class_=AsyncSession, expire_on_commit=False)
        async with session_factory() as session:
            repo = IncidentRepository(session)
            
            inc_data = {
                "title": "Brute Force Attack Detected",
                "description": "Multiple failed SSH logins from single IP",
                "severity": "high",
                "status": "open"
            }

            created = await repo.create_incident(inc_data)
            assert created.id is not None
            assert created.incident_id.startswith("INC-")
            assert created.title == "Brute Force Attack Detected"
            assert created.severity == "high"

            # Query by human ID
            by_human = await repo.get_incident_by_human_id(created.incident_id)
            assert by_human is not None
            assert by_human.id == created.id

            # Update incident
            updated = await repo.update_incident(created, {"status": "investigating", "severity": "critical"})
            assert updated.status == "investigating"
            assert updated.severity == "critical"

    asyncio.run(_test())


def test_event_incident_relationship(test_engine):
    """Verify associating an unassigned event with an incident."""
    async def _test():
        session_factory = async_sessionmaker(bind=test_engine, class_=AsyncSession, expire_on_commit=False)
        async with session_factory() as session:
            event_repo = EventRepository(session)
            incident_repo = IncidentRepository(session)

            # Create unassigned event
            event = await event_repo.create_event({
                "event_id": "unassigned-event-1",
                "timestamp": datetime.now(timezone.utc),
                "source": "wazuh",
                "raw_event": {}
            })
            assert event.incident_id is None

            # Create incident
            incident = await incident_repo.create_incident({
                "title": "Unassigned Event Investigation",
                "severity": "medium"
            })

            # Associate
            associated = await event_repo.associate_event_with_incident(event, incident.id)
            assert associated.incident_id == incident.id

            # Query from a fresh session to verify database relationship persistence
            async with session_factory() as session2:
                fresh_inc_repo = IncidentRepository(session2)
                refreshed_inc = await fresh_inc_repo.get_incident_by_id(incident.id)
                assert refreshed_inc is not None
                assert len(refreshed_inc.events) == 1
                assert refreshed_inc.events[0].id == event.id

    asyncio.run(_test())

