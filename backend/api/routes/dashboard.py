"""FastAPI Route Handlers for Backend Dashboard Aggregation API."""

from typing import Any, Dict
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from database.session import get_db_session
from backend.services.dashboard_service import DashboardService

router = APIRouter(prefix="/dashboard", tags=["Dashboard Aggregation"])


@router.get("/summary", response_model=Dict[str, Any], summary="Get SOC Security Posture Summary")
async def get_dashboard_summary(
    db: AsyncSession = Depends(get_db_session)
):
    """Retrieves aggregated security posture summary statistics for the SOC console."""
    service = DashboardService(db)
    return await service.get_dashboard_summary()
