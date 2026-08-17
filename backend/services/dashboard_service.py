"""Backend Dashboard Aggregation Service for SPECTRA-XDR."""

from typing import Any, Dict
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from database.models.incident import Incident
from database.models.detection_match import DetectionMatch
from database.models.ioc import IOC
from database.models.mitre import MitreTechnique
from database.repositories.incident_repository import IncidentRepository
from backend.integrations.wazuh.client import WazuhClient


class DashboardService:
    """Provides aggregated metrics and security posture summaries for the SOC console."""

    def __init__(self, session: AsyncSession):
        self.session = session
        self.incident_repo = IncidentRepository(session)
        self.wazuh_client = WazuhClient()

    async def get_dashboard_summary(self) -> Dict[str, Any]:
        """Aggregates security posture metrics across incidents, detections, intelligence, and Wazuh."""
        # 1. Incident status counts
        inc_status_query = select(Incident.status, func.count(Incident.id)).group_by(Incident.status)
        inc_status_res = await self.session.execute(inc_status_query)
        status_counts = {"open": 0, "investigating": 0, "contained": 0, "resolved": 0, "closed": 0}
        total_incidents = 0
        for st, count in inc_status_res.all():
            st_clean = str(st).lower()
            if st_clean in status_counts:
                status_counts[st_clean] = count
            total_incidents += count

        # 2. Incident severity counts
        inc_sev_query = select(Incident.severity, func.count(Incident.id)).group_by(Incident.severity)
        inc_sev_res = await self.session.execute(inc_sev_query)
        severity_counts = {"critical": 0, "high": 0, "medium": 0, "low": 0}
        for sev, count in inc_sev_res.all():
            sev_clean = str(sev).lower()
            if sev_clean in severity_counts:
                severity_counts[sev_clean] = count

        # 3. Total detection matches count
        matches_query = select(func.count(DetectionMatch.id))
        matches_res = await self.session.execute(matches_query)
        matches_count = matches_res.scalar_one() or 0

        # 4. Total IOCs & MITRE techniques count
        iocs_query = select(func.count(IOC.id))
        iocs_res = await self.session.execute(iocs_query)
        iocs_count = iocs_res.scalar_one() or 0

        mitre_query = select(func.count(MitreTechnique.id))
        mitre_res = await self.session.execute(mitre_query)
        mitre_count = mitre_res.scalar_one() or 0

        # 5. Wazuh operational health status (gracefully handle unreachability)
        wazuh_status = "unavailable"
        try:
            w_health = await self.wazuh_client.health_check()
            if w_health.get("status") == "healthy":
                wazuh_status = "healthy"
        except Exception:
            wazuh_status = "unavailable"

        # 6. Fetch recent incidents (sorted by newest)
        recent_incidents = await self.incident_repo.list_incidents(limit=5)
        recent_list = []
        for inc in recent_incidents:
            recent_list.append({
                "id": str(inc.id),
                "incident_id": inc.incident_id,
                "title": inc.title,
                "severity": inc.severity,
                "status": inc.status,
                "assigned_to": inc.assigned_to,
                "created_at": inc.created_at.isoformat() if inc.created_at else None,
                "updated_at": inc.updated_at.isoformat() if inc.updated_at else None,
            })

        return {
            "incidents": {
                "total": total_incidents,
                "open": status_counts["open"],
                "investigating": status_counts["investigating"],
                "contained": status_counts["contained"],
                "resolved": status_counts["resolved"],
                "closed": status_counts["closed"],
            },
            "severity": severity_counts,
            "detections": {
                "matches": matches_count
            },
            "intelligence": {
                "iocs": iocs_count,
                "mitre_techniques": mitre_count
            },
            "wazuh": {
                "status": wazuh_status
            },
            "recent_incidents": recent_list
        }
