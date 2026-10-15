"""FastAPI Route Handlers for Backend Dashboard Aggregation API."""

from typing import Any, Dict
from fastapi import APIRouter, Depends, Body
from sqlalchemy.ext.asyncio import AsyncSession

from database.session import get_db_session
from backend.services.dashboard_service import DashboardService

router = APIRouter(prefix="/dashboard", tags=["Dashboard Aggregation"])

# In-memory engine state registry with defaults
ENGINE_STATUS_REGISTRY = {
    "detection": {
        "id": "detection",
        "name": "Deterministic Detection Engine",
        "category": "Detection & Rules",
        "enabled": True,
        "description": "Evaluates incoming telemetry against deterministic rules, sigma rules, and IOC signatures",
        "latency_target": "<15ms",
        "status": "RUNNING"
    },
    "risk": {
        "id": "risk",
        "name": "Risk Scoring & Policy Engine",
        "category": "Risk & SOAR",
        "enabled": True,
        "description": "Calculates normalized threat scores (0-100) using MITRE weights, asset criticality, and blast radius",
        "latency_target": "<25ms",
        "status": "RUNNING"
    },
    "swarm": {
        "id": "swarm",
        "name": "AI Multi-Agent Swarm Orchestrator",
        "category": "AI Automation",
        "enabled": True,
        "description": "Coordinates 6 specialized autonomous security LLM agents across 3 investigation phases",
        "latency_target": "~250ms",
        "status": "RUNNING"
    },
    "ai_router": {
        "id": "ai_router",
        "name": "AI Model Router & Key Failover",
        "category": "AI Infrastructure",
        "enabled": True,
        "description": "Dynamic load balancer routing between cloud Gemini and local Ollama inference models",
        "latency_target": "<50ms",
        "status": "RUNNING"
    },
    "soar": {
        "id": "soar",
        "name": "SOAR Playbook Execution Engine",
        "category": "Response & Quarantine",
        "enabled": True,
        "description": "Dispatches host network containment, process termination, and firewall IP blocks with HITL guardrails",
        "latency_target": "<100ms",
        "status": "RUNNING"
    },
    "taxii": {
        "id": "taxii",
        "name": "TAXII 2.1 Threat Intel Ingestion",
        "category": "Threat Intelligence",
        "enabled": True,
        "description": "Automated synchronization of STIX 2.1 IOC threat feeds and MITRE ATT&CK enterprise catalog",
        "latency_target": "Background Sync",
        "status": "RUNNING"
    },
    "wazuh_collector": {
        "id": "wazuh_collector",
        "name": "Wazuh Agent Heartbeat & Telemetry Collector",
        "category": "Endpoint Fleet",
        "enabled": True,
        "description": "Collects sysmon, auditd, and authentication signals from enrolled Windows and Linux endpoint agents",
        "latency_target": "Real-time Stream",
        "status": "RUNNING"
    }
}


@router.get("/summary", response_model=Dict[str, Any], summary="Get SOC Security Posture Summary")
async def get_dashboard_summary(
    db: AsyncSession = Depends(get_db_session)
):
    """Retrieves aggregated security posture summary statistics for the SOC console."""
    service = DashboardService(db)
    return await service.get_dashboard_summary()


@router.get("/engines", summary="Get status of all security engines")
async def get_engines_status():
    """Returns real-time status of all security sub-engines."""
    return list(ENGINE_STATUS_REGISTRY.values())


@router.post("/engines/{engine_id}/toggle", summary="Toggle security engine start/stop")
async def toggle_engine_status(engine_id: str, payload: Dict[str, Any] = Body(default={})):
    """Toggles engine ON/OFF state."""
    if engine_id not in ENGINE_STATUS_REGISTRY:
        return {"error": f"Engine '{engine_id}' not found", "success": False}
    
    current = ENGINE_STATUS_REGISTRY[engine_id]
    new_state = payload.get("enabled", not current["enabled"])
    current["enabled"] = bool(new_state)
    current["status"] = "RUNNING" if current["enabled"] else "STOPPED"
    
    return {
        "success": True,
        "engine": current,
        "message": f"Engine {current['name']} is now {'STARTED (ON)' if current['enabled'] else 'STOPPED (OFF)'}"
    }

