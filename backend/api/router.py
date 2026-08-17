"""Main API Router aggregator for SPECTRA-XDR."""

from fastapi import APIRouter
from backend.api.routes import health, wazuh, events

api_router = APIRouter()

# Core Root & App Health Endpoints
api_router.include_router(health.router, tags=["Health & Status"])

# Phase 1 Wazuh & Normalization Endpoints under /api/v1
api_router.include_router(wazuh.router, prefix="/api/v1/wazuh", tags=["Wazuh Integration"])
api_router.include_router(events.router, prefix="/api/v1/events", tags=["Normalized Telemetry Events"])
