"""Async Gemini API Provider Client for Cloud LLM Reasoning."""

import logging
from typing import Any, Dict, Optional
import httpx

from backend.config import settings
from models.sanitizer import sanitize_telemetry

logger = logging.getLogger("spectra.models.gemini")


class GeminiClient:
    """Async client interface for Google Gemini API Cloud LLM."""

    def __init__(self, api_key: Optional[str] = None, model: str = "gemini-2.5-flash"):
        self.api_key = api_key or settings.GEMINI_API_KEY
        self.model = model

    def is_configured(self) -> bool:
        """Check if Gemini API Key is configured."""
        return bool(self.api_key and self.api_key.strip())

    async def generate_completion(self, prompt: str, system_prompt: Optional[str] = None, temperature: float = 0.2) -> str:
        """Send prompt to Gemini API and return response text."""
        if not self.is_configured():
            logger.warning("Gemini API key is not configured.")
            return ""

        url = f"https://generativelanguage.googleapis.com/v1beta/models/{self.model}:generateContent?key={self.api_key}"
        
        contents = []
        if system_prompt:
            contents.append({"role": "user", "parts": [{"text": f"System Instruction:\n{system_prompt}"}]})
            contents.append({"role": "model", "parts": [{"text": "Understood. I will follow these security analysis instructions."}]})
        
        # Sanitize text prompt before cloud submission
        sanitized_prompt = sanitize_telemetry(prompt)
        contents.append({"role": "user", "parts": [{"text": sanitized_prompt}]})

        payload = {
            "contents": contents,
            "generationConfig": {
                "temperature": temperature,
                "maxOutputTokens": 2048
            }
        }

        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(url, json=payload)
                if response.status_code == 200:
                    data = response.json()
                    candidates = data.get("candidates", [])
                    if candidates:
                        parts = candidates[0].get("content", {}).get("parts", [])
                        if parts:
                            return parts[0].get("text", "").strip()
                else:
                    logger.warning(f"Gemini API returned status HTTP {response.status_code}: {response.text}")
                    return ""
        except Exception as err:
            logger.error(f"Error during Gemini API generation: {err}")
            return ""
        return ""
