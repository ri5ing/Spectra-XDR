"""Normalized Security Telemetry Events API Endpoints."""

from typing import List, Optional
from fastapi import APIRouter, Depends, Query, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from database.session import get_db_session
from backend.services.event_service import EventService
from backend.api.schemas.event import EventResponse
from intelligence.normalization.models import NormalizedEvent

router = APIRouter()


@router.get("", response_model=List[EventResponse], summary="Retrieve Persisted Normalized Events")
async def get_persisted_events(
    limit: int = Query(default=10, ge=1, le=500),
    offset: int = Query(default=0, ge=0),
    agent_id: Optional[str] = Query(default=None),
    rule_id: Optional[str] = Query(default=None),
    source: Optional[str] = Query(default=None),
    session: AsyncSession = Depends(get_db_session)
):
    """Retrieves persisted security telemetry events from PostgreSQL database."""
    try:
        service = EventService(session)
        events = await service.list_persisted_events(
            limit=limit,
            offset=offset,
            agent_id=agent_id,
            rule_id=rule_id,
            source=source,
        )
        return events
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to query events database: {str(e)}"
        )


@router.post("", response_model=EventResponse, status_code=status.HTTP_201_CREATED, summary="Ingest Normalized Event")
async def ingest_event(
    event: NormalizedEvent,
    session: AsyncSession = Depends(get_db_session)
):
    """Ingests and persists a NormalizedEvent payload into PostgreSQL with autonomous AI Swarm trigger."""
    try:
        service = EventService(session)
        persisted = await service.ingest_normalized_event(event)

        # Autonomous AI Swarm Activation for alerts and simulations
        if (event.event_type == "alert" or (event.rule_level and event.rule_level >= 5)) and not persisted.incident_id:
            try:
                import asyncio
                from database.repositories.incident_repository import IncidentRepository
                from database.repositories.swarm_repository import SwarmRepository
                from agents.models import SwarmState
                from orchestration.graph import SwarmOrchestrator

                inc_repo = IncidentRepository(session)
                swarm_repo = SwarmRepository(session)

                # Determine incident severity based on rule level
                sev = "critical" if (event.rule_level and event.rule_level >= 10) else "high" if (event.rule_level and event.rule_level >= 7) else "medium"
                
                # 1. Create incident automatically
                inc_data = {
                    "title": f"Autonomous Triage: {event.rule_description or 'Threat Event Detected'}",
                    "description": f"Automatically generated security incident from endpoint {event.agent_name or event.agent_id or 'unknown'} ({event.agent_ip or 'unknown'}). Rule: {event.rule_id} Level: {event.rule_level}",
                    "severity": sev,
                    "status": "investigating",
                }
                incident = await inc_repo.create_incident(inc_data)

                # Link event to incident
                persisted.incident_id = incident.id
                await session.commit()
                await session.refresh(incident)

                # 2. Run Autonomous AI Multi-Agent Swarm Pipeline
                event_dict = {
                    "rule_id": event.rule_id or "UNKNOWN",
                    "rule_description": event.rule_description or "Security Alert",
                    "severity": sev,
                    "agent_name": event.agent_name or "Local Endpoint",
                    "agent_id": event.agent_id or "002",
                    "full_log": str(event.raw_event) if event.raw_event else ""
                }

                initial_state = SwarmState(
                    incident_id=incident.id,
                    incident_human_id=incident.incident_id,
                    event_data=event_dict,
                    mitre_mappings=[{"technique_id": event.rule_id, "technique_name": event.rule_description, "tactic": "Execution"}] if event.rule_id and event.rule_id.startswith("T") else [],
                    extracted_iocs=[{"ioc_type": "ip", "normalized_value": event.agent_ip}] if event.agent_ip else [],
                    detection_matches=[{"rule_id": event.rule_id}] if event.rule_id else []
                )

                orchestrator = SwarmOrchestrator()
                final_state = await orchestrator.run_swarm(initial_state)

                # 3. Save Swarm Run and all 6 Agent thoughts
                await swarm_repo.save_swarm_run(final_state)
            except Exception as swarm_err:
                import logging
                logging.getLogger("spectra.auto_swarm").error(f"Autonomous swarm execution error: {swarm_err}")

        return persisted
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to ingest event into database: {str(e)}"
        )
