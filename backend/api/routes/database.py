"""Database Health Check API Endpoint."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncEngine
from database.session import check_database_health, get_db_engine

router = APIRouter()


@router.get("/health", summary="PostgreSQL Database Health Check")
async def database_health(db_engine: AsyncEngine = Depends(get_db_engine)):
    """Performs a read-only database ping check."""
    result = await check_database_health(db_engine)
    if result.get("status") != "healthy":
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Database connection unavailable: {result.get('error')}"
        )
    return result
