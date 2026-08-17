"""Main API Router aggregator for SPECTRA-XDR."""

from fastapi import APIRouter
from backend.api.routes import health, wazuh, events, database, incidents, intelligence, detections, dashboard, swarm, risk, response, ai_models

api_router = APIRouter()

# Core Root & App Health Endpoints
api_router.include_router(health.router, tags=["Health & Status"])

# Database Health Endpoint under /api/v1/database
api_router.include_router(database.router, prefix="/api/v1/database", tags=["Database Infrastructure"])

# Phase 1 Wazuh Integration Endpoints under /api/v1/wazuh
api_router.include_router(wazuh.router, prefix="/api/v1/wazuh", tags=["Wazuh Integration"])

# Phase 2 Persisted Security Events Endpoints under /api/v1/events
api_router.include_router(events.router, prefix="/api/v1/events", tags=["Security Events"])

# Phase 2 Security Incident Management Endpoints under /api/v1/incidents
api_router.include_router(incidents.router, prefix="/api/v1/incidents", tags=["Incidents"])

# Phase 3 Deterministic Security Intelligence Endpoints under /api/v1/intelligence
api_router.include_router(intelligence.router, prefix="/api/v1", tags=["Deterministic Security Intelligence"])

# Phase 4 Deterministic Detections & Correlation Endpoints under /api/v1/detections
api_router.include_router(detections.router, prefix="/api/v1", tags=["Deterministic Detections & Correlation"])

# Phase 5 Dashboard Aggregation Endpoints under /api/v1/dashboard
api_router.include_router(dashboard.router, prefix="/api/v1", tags=["Dashboard Aggregation"])

# Phase 6 Multi-Agent Swarm, Risk, Response, and AI Router Endpoints under /api/v1
api_router.include_router(swarm.router, prefix="/api/v1", tags=["AI Swarm Orchestration"])
api_router.include_router(risk.router, prefix="/api/v1", tags=["Deterministic Risk Engine"])
api_router.include_router(response.router, prefix="/api/v1", tags=["Controlled Response Execution"])
api_router.include_router(ai_models.router, prefix="/api/v1", tags=["AI Model Router & Providers"])




