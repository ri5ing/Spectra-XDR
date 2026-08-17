"""Backend Incident Investigation Service for analyst workflows, timelines, and audit trails."""

import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Tuple
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from database.models.incident import Incident
from database.models.event import Event
from database.models.detection_match import DetectionMatch
from database.models.incident_evidence import IncidentEvidence
from database.models.incident_note import IncidentNote
from database.models.incident_audit import IncidentAuditLog
from database.models.ioc import IOC
from database.models.mitre import MitreTechnique
from database.repositories.incident_repository import IncidentRepository
from database.repositories.incident_note_repository import IncidentNoteRepository
from database.repositories.incident_audit_repository import IncidentAuditRepository
from database.repositories.enrichment_repository import EnrichmentRepository
from database.repositories.detection_match_repository import DetectionMatchRepository


VALID_STATUSES = {"open", "investigating", "contained", "resolved", "closed"}

ALLOWED_STATUS_TRANSITIONS: Dict[str, set] = {
    "open": {"investigating", "contained", "resolved"},
    "investigating": {"contained", "resolved"},
    "contained": {"investigating", "resolved"},
    "resolved": {"closed"},
    "closed": set()
}


class IncidentInvestigationService:
    """Service layer orchestrating analyst incident investigations, timelines, notes, and audit trails."""

    def __init__(self, session: AsyncSession):
        self.session = session
        self.incident_repo = IncidentRepository(session)
        self.note_repo = IncidentNoteRepository(session)
        self.audit_repo = IncidentAuditRepository(session)
        self.enrichment_repo = EnrichmentRepository(session)
        self.match_repo = DetectionMatchRepository(session)

    async def get_incident(self, incident_id_str: str) -> Optional[Incident]:
        return await self.incident_repo.get_incident(incident_id_str)

    async def get_incident_summary(self, incident_id: uuid.UUID) -> Optional[Dict[str, Any]]:
        """Computes deterministic summary statistics for an incident."""
        incident = await self.session.get(Incident, incident_id)
        if not incident:
            return None

        events = await self._get_events_for_incident(incident_id)
        matches = await self.match_repo.list_matches(limit=100, incident_id=incident_id)
        evidence = await self._get_evidence_for_incident(incident_id)
        iocs = await self.get_incident_iocs(incident_id)
        mitre_techs = await self.get_incident_mitre(incident_id)

        sources = sorted(list({e.source for e in events if e.source}))
        agents = sorted(list({e.agent_id for e in events if e.agent_id}))
        rule_ids = sorted(list({e.rule_id for e in events if e.rule_id}))
        tech_ids = sorted(list({t.technique_id for t in mitre_techs}))

        return {
            "incident_id": incident.incident_id,
            "severity": incident.severity,
            "status": incident.status,
            "title": incident.title,
            "description": incident.description,
            "assigned_to": incident.assigned_to,
            "resolution": incident.resolution,
            "resolved_at": incident.resolved_at.isoformat() if incident.resolved_at else None,
            "event_count": len(events),
            "detection_match_count": len(matches),
            "evidence_count": len(evidence),
            "ioc_count": len(iocs),
            "mitre_technique_count": len(mitre_techs),
            "first_seen_at": incident.first_seen.isoformat() if incident.first_seen else None,
            "last_seen_at": incident.last_seen.isoformat() if incident.last_seen else None,
            "sources": sources,
            "agents": agents,
            "rule_ids": rule_ids,
            "mitre_techniques": tech_ids
        }

    async def get_incident_events(
        self,
        incident_id: uuid.UUID,
        limit: int = 50,
        offset: int = 0,
        severity: Optional[str] = None,
        source: Optional[str] = None,
        agent_id: Optional[str] = None,
        rule_id: Optional[str] = None
    ) -> List[Event]:
        """Lists persisted events associated with an incident with optional filtering."""
        query = select(Event).where(Event.incident_id == incident_id)

        if severity:
            query = query.where(Event.rule_level >= (10 if severity == "high" else 1))
        if source:
            query = query.where(Event.source == source)
        if agent_id:
            query = query.where(Event.agent_id == agent_id)
        if rule_id:
            query = query.where(Event.rule_id == rule_id)

        query = query.order_by(Event.timestamp.asc()).offset(offset).limit(limit)
        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def get_incident_detections(self, incident_id: uuid.UUID) -> List[DetectionMatch]:
        """Lists all detection matches associated with an incident."""
        return await self.match_repo.list_matches(limit=100, incident_id=incident_id)

    async def get_incident_iocs(self, incident_id: uuid.UUID) -> List[IOC]:
        """Retrieves deduplicated IOC records extracted from all events linked to an incident."""
        events = await self._get_events_for_incident(incident_id)
        ioc_map: Dict[Tuple[str, str], IOC] = {}

        for evt in events:
            evt_iocs = await self.enrichment_repo.get_event_iocs(evt.id)
            for ioc in evt_iocs:
                key = (ioc.type, ioc.normalized_value)
                if key not in ioc_map:
                    ioc_map[key] = ioc

        return list(ioc_map.values())

    async def get_incident_mitre(self, incident_id: uuid.UUID) -> List[MitreTechnique]:
        """Retrieves deduplicated MITRE ATT&CK techniques mapped to all events linked to an incident."""
        events = await self._get_events_for_incident(incident_id)
        tech_map: Dict[str, MitreTechnique] = {}

        for evt in events:
            mappings = await self.enrichment_repo.get_event_mitre_mappings(evt.id)
            for tech, _ in mappings:
                if tech.technique_id not in tech_map:
                    tech_map[tech.technique_id] = tech

        return list(tech_map.values())

    async def get_incident_timeline(self, incident_id: uuid.UUID) -> List[Dict[str, Any]]:
        """Constructs a deterministic investigation timeline combining events, detections, evidence, status changes, notes."""
        timeline: List[Dict[str, Any]] = []

        # 1. Events
        events = await self._get_events_for_incident(incident_id)
        for e in events:
            ts = e.timestamp.isoformat() if e.timestamp else e.created_at.isoformat()
            timeline.append({
                "timestamp": ts,
                "type": "event",
                "source_id": str(e.id),
                "summary": f"Telemetry event {e.event_id} ({e.rule_description or 'No description'})",
                "severity": "medium",
                "details": {"agent_id": e.agent_id, "rule_id": e.rule_id, "source": e.source}
            })

        # 2. Detections
        matches = await self.match_repo.list_matches(limit=100, incident_id=incident_id)
        for m in matches:
            ts = m.matched_at.isoformat() if m.matched_at else m.created_at.isoformat()
            r_id = m.match_reason.get("rule_id", "DETECTION")
            timeline.append({
                "timestamp": ts,
                "type": "detection",
                "source_id": str(m.id),
                "summary": f"Detection match rule {r_id} triggered ({m.event_count} events)",
                "severity": m.match_reason.get("severity", "high"),
                "details": m.match_reason
            })

        # 3. Notes
        notes = await self.note_repo.list_notes_for_incident(incident_id)
        for n in notes:
            timeline.append({
                "timestamp": n.created_at.isoformat(),
                "type": "note",
                "source_id": str(n.id),
                "summary": f"Analyst note by {n.author}: {n.content[:100]}",
                "severity": "low",
                "details": {"author": n.author, "content": n.content}
            })

        # 4. Audit Log Entries (Status/Assignee Changes)
        audits = await self.audit_repo.list_audit_logs_for_incident(incident_id)
        for a in audits:
            timeline.append({
                "timestamp": a.timestamp.isoformat(),
                "type": "audit",
                "source_id": str(a.id),
                "summary": f"Audit [{a.action}]: {a.field_name or ''} changed from '{a.old_value}' to '{a.new_value}' by {a.actor}",
                "severity": "low",
                "details": {"action": a.action, "actor": a.actor, "old_value": a.old_value, "new_value": a.new_value}
            })

        # Deterministic sorting: Primary by timestamp ASC, Secondary by source_id ASC
        timeline.sort(key=lambda x: (x["timestamp"], x["source_id"]))
        return timeline

    async def update_incident_workflow(self, incident: Incident, updates: Dict[str, Any], actor: str = "analyst") -> Incident:
        """Updates incident workflow attributes, validates status transitions, and commits audit entries atomically."""
        new_status = updates.get("status")
        if new_status:
            new_status_clean = str(new_status).lower()
            if new_status_clean not in VALID_STATUSES:
                raise ValueError(f"Invalid status '{new_status}'. Allowed values: {VALID_STATUSES}")
            
            curr_status = incident.status.lower()
            if curr_status != new_status_clean:
                allowed = ALLOWED_STATUS_TRANSITIONS.get(curr_status, set())
                if new_status_clean not in allowed:
                    raise ValueError(f"Invalid status transition from '{curr_status}' to '{new_status_clean}'. Allowed transitions: {allowed}")
                
                # Log audit entry
                await self.audit_repo.log_audit_entry(
                    incident_id=incident.id,
                    action="STATUS_CHANGED",
                    field_name="status",
                    old_value=incident.status,
                    new_value=new_status_clean,
                    actor=actor
                )
                incident.status = new_status_clean

        if "severity" in updates and updates["severity"] and str(updates["severity"]).lower() != incident.severity:
            old_sev = incident.severity
            new_sev = str(updates["severity"]).lower()
            await self.audit_repo.log_audit_entry(
                incident_id=incident.id,
                action="SEVERITY_CHANGED",
                field_name="severity",
                old_value=old_sev,
                new_value=new_sev,
                actor=actor
            )
            incident.severity = new_sev

        if "assigned_to" in updates and updates["assigned_to"] != incident.assigned_to:

            old_assignee = incident.assigned_to
            new_assignee = updates["assigned_to"]
            await self.audit_repo.log_audit_entry(
                incident_id=incident.id,
                action="ASSIGNEE_CHANGED",
                field_name="assigned_to",
                old_value=old_assignee,
                new_value=new_assignee,
                actor=actor
            )
            incident.assigned_to = new_assignee

        if "title" in updates and updates["title"] != incident.title:
            incident.title = updates["title"]

        if "description" in updates and updates["description"] != incident.description:
            incident.description = updates["description"]

        if "resolution" in updates and updates["resolution"] != incident.resolution:
            incident.resolution = updates["resolution"]
            if incident.status == "resolved" and not incident.resolved_at:
                incident.resolved_at = datetime.now(timezone.utc)

        self.session.add(incident)
        await self.session.commit()
        await self.session.refresh(incident)
        return incident

    async def add_analyst_note(self, incident_id: uuid.UUID, content: str, author: str = "analyst") -> IncidentNote:
        """Adds an analyst note to an incident and creates an audit entry atomically."""
        note = await self.note_repo.create_note(incident_id=incident_id, content=content, author=author)
        await self.audit_repo.log_audit_entry(
            incident_id=incident_id,
            action="NOTE_CREATED",
            field_name="incident_notes",
            old_value=None,
            new_value=str(note.id),
            actor=author,
            metadata={"content_snippet": content[:50]}
        )
        await self.session.commit()
        return note

    async def update_analyst_note(self, note_id: uuid.UUID, content: str, actor: str = "analyst") -> Optional[IncidentNote]:
        """Updates an analyst note and creates an audit entry atomically."""
        note = await self.note_repo.get_note_by_id(note_id)
        if not note:
            return None
        updated_note = await self.note_repo.update_note(note, content)
        await self.audit_repo.log_audit_entry(
            incident_id=note.incident_id,
            action="NOTE_UPDATED",
            field_name="incident_notes",
            old_value=str(note_id),
            new_value=str(note_id),
            actor=actor
        )
        await self.session.commit()
        return updated_note

    async def delete_analyst_note(self, note_id: uuid.UUID, actor: str = "analyst") -> bool:
        """Deletes an analyst note and creates an audit entry atomically."""
        note = await self.note_repo.get_note_by_id(note_id)
        if not note:
            return False
        inc_id = note.incident_id
        await self.note_repo.delete_note(note)
        await self.audit_repo.log_audit_entry(
            incident_id=inc_id,
            action="NOTE_DELETED",
            field_name="incident_notes",
            old_value=str(note_id),
            new_value=None,
            actor=actor
        )
        await self.session.commit()
        return True

    async def _get_events_for_incident(self, incident_id: uuid.UUID) -> List[Event]:
        query = select(Event).where(Event.incident_id == incident_id)
        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def _get_evidence_for_incident(self, incident_id: uuid.UUID) -> List[IncidentEvidence]:
        query = select(IncidentEvidence).where(IncidentEvidence.incident_id == incident_id)
        result = await self.session.execute(query)
        return list(result.scalars().all())
