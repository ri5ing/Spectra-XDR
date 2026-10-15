"""Hybrid AI Model Router with Strict User Policy Enforcement.

If Gemini is selected, it ONLY uses Gemini.
If Ollama is selected, it ONLY uses Ollama.
If Auto is selected, it uses Gemini when internet & key are healthy, else Ollama.
"""

import json
import logging
from typing import Any, Dict, Optional, Tuple

from agents.models import ModelChoice, AgentRole
from models.ollama import OllamaClient
from models.gemini import GeminiClient, GEMINI_STATS

logger = logging.getLogger("spectra.models.router")

# Router Mode configuration: 'auto' | 'gemini' | 'ollama'
ROUTER_CONFIG = {
    "mode": "auto",
    "active_backend": "ollama_local",
    "fallback_active": True
}


class ModelRouter:
    """Intelligent Router strictly enforcing active model policy across all agents and endpoints."""

    def __init__(self):
        self.ollama = OllamaClient()
        self.gemini = GeminiClient()

    async def get_model_status(self) -> Dict[str, Any]:
        """Check status, internet connectivity, and token accounting across both providers."""
        ollama_active = await self.ollama.is_available()
        gemini_health = await self.gemini.check_connectivity_and_health()

        mode = ROUTER_CONFIG["mode"]
        if mode == "gemini":
            current_choice = "gemini_cloud"
        elif mode == "ollama":
            current_choice = "ollama_local"
        else:
            # Auto Mode
            if gemini_health.get("healthy"):
                current_choice = "gemini_cloud"
            elif ollama_active:
                current_choice = "ollama_local"
            else:
                current_choice = "deterministic_fallback"

        ROUTER_CONFIG["active_backend"] = current_choice

        return {
            "router_mode": mode,
            "active_backend": current_choice,
            "internet_connected": gemini_health.get("internet_connected", False),
            "gemini_cloud": {
                "configured": self.gemini.is_configured(),
                "healthy": gemini_health.get("healthy", False),
                "status": gemini_health.get("status", "UNCONFIGURED"),
                "model": self.gemini.model,
                "display_name": gemini_health.get("display_name", "Gemini 2.5 Flash"),
                "message": gemini_health.get("message", ""),
                "masked_key": (GeminiClient.get_active_key_item() or {}).get("name", "No Active Key"),
                "active_key_id": (GeminiClient.get_active_key_item() or {}).get("id"),
                "keys": GeminiClient.get_keys(),
                "stats": GEMINI_STATS,
                "input_token_limit": gemini_health.get("input_token_limit", 1048576),
                "output_token_limit": gemini_health.get("output_token_limit", 8192)
            },
            "ollama_local": {
                "available": ollama_active,
                "base_url": self.ollama.base_url,
                "model": self.ollama.model,
                "status": "ONLINE" if ollama_active else "OFFLINE"
            },
            "fallback_active": True
        }

    async def select_model_dynamic(self) -> Tuple[ModelChoice, str]:
        """Strictly select model based on user policy. No unwanted cross-bleeding."""
        mode = ROUTER_CONFIG["mode"]
        
        # 1. Strict Gemini Mode: ONLY Gemini Cloud allowed
        if mode == "gemini":
            if not self.gemini.is_configured():
                return ModelChoice.DETERMINISTIC_FALLBACK, "gemini_strict_key_missing"
            return ModelChoice.GEMINI_CLOUD, "gemini_strict_enforced"

        # 2. Strict Ollama Mode: ONLY Local Ollama allowed
        if mode == "ollama":
            if not await self.ollama.is_available():
                return ModelChoice.DETERMINISTIC_FALLBACK, "ollama_strict_offline"
            return ModelChoice.OLLAMA_LOCAL, "ollama_strict_enforced"

        # 3. Auto Mode: Internet + Valid Gemini Key -> Gemini; Else Local Ollama
        gemini_health = await self.gemini.check_connectivity_and_health()
        if gemini_health.get("healthy"):
            return ModelChoice.GEMINI_CLOUD, "auto_cloud_gemini_active"

        if await self.ollama.is_available():
            return ModelChoice.OLLAMA_LOCAL, "auto_offline_ollama_active"

        return ModelChoice.DETERMINISTIC_FALLBACK, "deterministic_engine_fallback"

    async def execute_reasoning(
        self,
        agent_role: AgentRole,
        prompt: str,
        system_prompt: Optional[str] = None,
        complexity: str = "medium"
    ) -> Tuple[str, ModelChoice]:
        """Execute reasoning strictly respecting the configured model."""
        chosen_model, reason = await self.select_model_dynamic()
        mode = ROUTER_CONFIG["mode"]
        logger.info(f"Model Router policy [{mode}] -> executing {chosen_model} (Reason: {reason})")

        # 1. Gemini Cloud Execution
        if chosen_model == ModelChoice.GEMINI_CLOUD:
            res = await self.gemini.generate_completion(prompt, system_prompt)
            if res:
                return res, ModelChoice.GEMINI_CLOUD
            
            # If in strict Gemini mode, do NOT switch to Ollama
            if mode == "gemini":
                logger.warning("Gemini API call failed in strict Gemini mode. Returning empty response.")
                return "", ModelChoice.DETERMINISTIC_FALLBACK

            # If in Auto mode, fall back to Ollama
            logger.warning("Gemini failed in Auto mode. Falling back to local Ollama.")
            chosen_model = ModelChoice.OLLAMA_LOCAL

        # 2. Ollama Local Execution
        if chosen_model == ModelChoice.OLLAMA_LOCAL:
            if await self.ollama.is_available():
                res = await self.ollama.generate_completion(prompt, system_prompt)
                if res:
                    return res, ModelChoice.OLLAMA_LOCAL
            
            # In strict Ollama mode, do NOT switch to Gemini
            if mode == "ollama":
                logger.warning("Local Ollama call failed in strict Ollama mode.")
                return "", ModelChoice.DETERMINISTIC_FALLBACK

        # 3. Deterministic Security Fallback
        return "", ModelChoice.DETERMINISTIC_FALLBACK

    @staticmethod
    def parse_json_response(raw_text: str) -> Optional[Dict[str, Any]]:
        """Clean and parse JSON from LLM outputs, including markdown code blocks."""
        if not raw_text or not raw_text.strip():
            return None
        text = raw_text.strip()
        # Strip ```json ... ``` blocks
        import re
        if "```" in text:
            code_match = re.search(r"```(?:json)?\s*([\s\S]*?)\s*```", text)
            if code_match:
                text = code_match.group(1).strip()
        try:
            return json.loads(text)
        except Exception:
            pass

        match = re.search(r"\{[\s\S]*\}", text)
        if match:
            try:
                return json.loads(match.group(0))
            except Exception:
                pass
        return None
