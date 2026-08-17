"""Normalized Events Endpoint for SPECTRA-XDR."""

from typing import List
from fastapi import APIRouter, Depends, Query, HTTPException, status

from backend.api.routes.wazuh import get_wazuh_client
from backend.integrations.wazuh.client import WazuhClient
from backend.integrations.wazuh.exceptions import WazuhConnectionError, WazuhError, WazuhTimeoutError
from intelligence.normalization.models import NormalizedEvent
from intelligence.normalization.wazuh import normalize_wazuh_alert

router = APIRouter()


@router.get("", response_model=List[NormalizedEvent], summary="Retrieve Normalized Security Events")
async def get_normalized_events(
    limit: int = Query(default=10, ge=1, le=500),
    offset: int = Query(default=0, ge=0),
    client: WazuhClient = Depends(get_wazuh_client)
):
    """Fetches Wazuh alerts and transforms them into standardized SPECTRA NormalizedEvents."""
    try:
        raw_response = await client.get_alerts(limit=limit, offset=offset)
        
        # Extract alert items safely from response container
        items = []
        if isinstance(raw_response, dict):
            items = raw_response.get("data", {}).get("affected_items", [])
            if not items and isinstance(raw_response.get("affected_items"), list):
                items = raw_response["affected_items"]
        
        normalized_events = [normalize_wazuh_alert(item) for item in items if isinstance(item, dict)]
        return normalized_events

    except (WazuhConnectionError, WazuhTimeoutError) as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Telemetry provider unavailable: {e.message}"
        )
    except WazuhError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Event normalization failed: {e.message}"
        )
