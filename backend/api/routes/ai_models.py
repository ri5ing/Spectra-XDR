"""FastAPI Endpoints for AI Model Status & Router Management."""

from typing import Any, Dict
from fastapi import APIRouter
from models.router import ModelRouter

router = APIRouter(prefix="/ai", tags=["AI Model Router & Providers"])


@router.get("/status", response_model=Dict[str, Any])
async def get_ai_models_status():
    """Retrieve status and availability of Ollama, Gemini API, and Router Fallbacks."""
    model_router = ModelRouter()
    status_dict = await model_router.get_model_status()
    return status_dict
