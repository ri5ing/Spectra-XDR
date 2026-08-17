"""Hybrid AI Model Router for SPECTRA-XDR."""

import json
import logging
import re
from typing import Any, Dict, Optional, Tuple

from agents.models import ModelChoice, AgentRole
from models.ollama import OllamaClient
from models.gemini import GeminiClient

logger = logging.getLogger("spectra.models.router")


class ModelRouter:
    """Intelligent Router selecting the optimal LLM backend (Ollama, Gemini, Fallback)."""

    def __init__(self):
        self.ollama = OllamaClient()
        self.gemini = GeminiClient()

    async def get_model_status(self) -> Dict[str, Any]:
        """Check status and availability of local and cloud models."""
        ollama_active = await self.ollama.is_available()
        gemini_configured = self.gemini.is_configured()
        return {
            "ollama_local": {
                "available": ollama_active,
                "base_url": self.ollama.base_url,
                "model": self.ollama.model
            },
            "gemini_cloud": {
                "configured": gemini_configured,
                "model": self.gemini.model
            },
            "fallback_active": True
        }

    def select_model(self, agent_role: AgentRole, complexity: str = "medium") -> ModelChoice:
        """Select best model based on agent role and task complexity."""
        # High reasoning roles like investigation or complex correlation benefit from Cloud LLM if available
        if complexity == "high" or agent_role in [AgentRole.CORRELATION_AGENT, AgentRole.INVESTIGATION_AGENT]:
            if self.gemini.is_configured():
                return ModelChoice.GEMINI_CLOUD
        
        # Local processing preferred for lower complexity, sensitive telemetry, or detection
        return ModelChoice.OLLAMA_LOCAL

    async def execute_reasoning(
        self,
        agent_role: AgentRole,
        prompt: str,
        system_prompt: Optional[str] = None,
        complexity: str = "medium"
    ) -> Tuple[str, ModelChoice]:
        """Execute reasoning request using routed model, falling back automatically if needed."""
        chosen_model = self.select_model(agent_role, complexity)
        
        # 1. Try Gemini Cloud if selected
        if chosen_model == ModelChoice.GEMINI_CLOUD:
            res = await self.gemini.generate_completion(prompt, system_prompt)
            if res:
                return res, ModelChoice.GEMINI_CLOUD
            logger.info("Gemini API call returned empty response. Falling back to Ollama.")
            chosen_model = ModelChoice.OLLAMA_LOCAL

        # 2. Try Ollama Local if selected or fallback
        if chosen_model == ModelChoice.OLLAMA_LOCAL:
            if await self.ollama.is_available():
                res = await self.ollama.generate_completion(prompt, system_prompt)
                if res:
                    return res, ModelChoice.OLLAMA_LOCAL
                logger.info("Ollama call returned empty response.")

        # 3. Fallback to Deterministic Reasoning
        logger.info("Local/Cloud models unavailable or failed. Using deterministic fallback engine.")
        return "", ModelChoice.DETERMINISTIC_FALLBACK

    @staticmethod
    def parse_json_response(raw_text: str) -> Optional[Dict[str, Any]]:
        """Extract and parse structured JSON payload from model string output."""
        if not raw_text:
            return None
        
        # Try direct JSON parse
        try:
            return json.loads(raw_text)
        except Exception:
            pass

        # Try extracting ```json ... ``` blocks
        match = re.search(r'```(?:json)?\s*(\{.*?\})\s*```', raw_text, re.DOTALL)
        if match:
            try:
                return json.loads(match.group(1))
            except Exception:
                pass
        
        # Try matching any {...} structure
        match = re.search(r'(\{.*?\})', raw_text, re.DOTALL)
        if match:
            try:
                return json.loads(match.group(1))
            except Exception:
                pass

        return None
