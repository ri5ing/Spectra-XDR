"""Async Ollama Provider Client for Local LLM Processing."""

import logging
from typing import Any, Dict, Optional
import httpx

from backend.config import settings

logger = logging.getLogger("spectra.models.ollama")


class OllamaClient:
    """Async client interface for local Ollama LLM server."""

    def __init__(self, base_url: Optional[str] = None, model: Optional[str] = None):
        self.base_url = base_url or settings.OLLAMA_BASE_URL
        self.model = model or settings.OLLAMA_MODEL

    async def is_available(self) -> bool:
        """Check if local Ollama server is running and reachable."""
        try:
            async with httpx.AsyncClient(timeout=3.0) as client:
                res = await client.get(f"{self.base_url}/api/version")
                return res.status_code == 200
        except Exception as e:
            logger.debug(f"Ollama server not reachable: {e}")
            return False

    async def generate_completion(self, prompt: str, system_prompt: Optional[str] = None, temperature: float = 0.2) -> str:
        """Send prompt to local Ollama LLM and return generated string text response."""
        payload: Dict[str, Any] = {
            "model": self.model,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": temperature
            }
        }
        if system_prompt:
            payload["system"] = system_prompt

        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(f"{self.base_url}/api/generate", json=payload)
                if response.status_code == 200:
                    data = response.json()
                    return data.get("response", "").strip()
                else:
                    logger.warning(f"Ollama API returned HTTP {response.status_code}: {response.text}")
                    return ""
        except Exception as err:
            logger.error(f"Error during Ollama generation: {err}")
            return ""
