"""Root and Health Check Endpoints for SPECTRA-XDR."""

from fastapi import APIRouter
from backend.config import settings

router = APIRouter()


@router.get("/", summary="Root Endpoint")
async def root():
    """Returns application name and operational status."""
    return {
        "app": settings.APP_NAME,
        "status": "running",
        "version": "0.1.0"
    }


@router.get("/health", summary="Health Check Endpoint")
async def health_check():
    """Returns system health status for monitoring."""
    return {
        "status": "healthy",
        "app": settings.APP_NAME,
        "environment": settings.APP_ENV
    }
