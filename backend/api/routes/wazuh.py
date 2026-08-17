"""Wazuh API Integration Endpoints."""

from fastapi import APIRouter, Depends, Query, HTTPException, status
from backend.integrations.wazuh.client import WazuhClient
from backend.integrations.wazuh.exceptions import (
    WazuhAuthenticationError,
    WazuhConnectionError,
    WazuhError,
    WazuhTimeoutError,
)

router = APIRouter()


def get_wazuh_client() -> WazuhClient:
    """Dependency provider for WazuhClient."""
    return WazuhClient()


@router.get("/health", summary="Wazuh Connectivity Health Check")
async def wazuh_health(client: WazuhClient = Depends(get_wazuh_client)):
    """Verifies read-only connectivity and authentication with Wazuh API server."""
    try:
        health_data = await client.health_check()
        return health_data
    except (WazuhConnectionError, WazuhTimeoutError) as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Wazuh service unavailable: {e.message}"
        )
    except WazuhAuthenticationError as e:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"Wazuh authentication error: {e.message}"
        )
    except WazuhError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Wazuh integration error: {e.message}"
        )


@router.get("/agents", summary="Retrieve Wazuh Monitored Endpoints")
async def get_wazuh_agents(
    limit: int = Query(default=10, ge=1, le=500),
    offset: int = Query(default=0, ge=0),
    client: WazuhClient = Depends(get_wazuh_client)
):
    """Retrieves read-only agent inventory from Wazuh."""
    try:
        return await client.get_agents(limit=limit, offset=offset)
    except (WazuhConnectionError, WazuhTimeoutError) as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Wazuh service unavailable: {e.message}"
        )
    except WazuhError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve Wazuh agents: {e.message}"
        )


@router.get("/alerts", summary="Retrieve Raw Wazuh Alerts")
async def get_wazuh_alerts(
    limit: int = Query(default=10, ge=1, le=500),
    offset: int = Query(default=0, ge=0),
    client: WazuhClient = Depends(get_wazuh_client)
):
    """Retrieves read-only raw alert logs from Wazuh."""
    try:
        return await client.get_alerts(limit=limit, offset=offset)
    except (WazuhConnectionError, WazuhTimeoutError) as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Wazuh service unavailable: {e.message}"
        )
    except WazuhError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve Wazuh alerts: {e.message}"
        )
