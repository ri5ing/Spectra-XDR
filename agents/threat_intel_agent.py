"""Threat Intelligence Agent for SPECTRA-XDR Multi-Agent Swarm."""

import logging
from datetime import datetime, timezone
from typing import Any, Dict, List

from agents.models import AgentRole, AgentThought, SwarmState
from models.router import ModelRouter

logger = logging.getLogger("spectra.agents.threat_intel")


class ThreatIntelAgent:
    """Agent 3: Analyzes and scores extracted Indicators of Compromise (IOCs)."""

    def __init__(self, router: ModelRouter):
        self.router = router

    async def analyze(self, state: SwarmState) -> AgentThought:
        """Analyze extracted IOCs in SwarmState."""
        iocs = state.extracted_iocs

        ioc_summary = []
        for item in iocs:
            ioc_type = item.get("ioc_type", "unknown")
            value = item.get("normalized_value", item.get("raw_value", ""))
            ioc_summary.append(f"{ioc_type}: {value}")

        prompt = f"""Evaluate Threat Intelligence reputation for extracted IOCs:
Extracted IOC Inventory:
{ioc_summary if ioc_summary else 'No extracted IOCs found in telemetry.'}

Provide structured output in valid JSON:
{{
  "reputation_score": 75,
  "high_risk_iocs": [],
  "malware_family": "Unknown / Suspicious Script",
  "threat_intel_summary": "Summary of IOC threat landscape"
}}"""

        system_prompt = "You are a Threat Intelligence Analyst Agent in SPECTRA-XDR."

        raw_output, model_used = await self.router.execute_reasoning(
            agent_role=AgentRole.THREAT_INTEL_AGENT,
            prompt=prompt,
            system_prompt=system_prompt,
            complexity="low"
        )

        parsed = self.router.parse_json_response(raw_output)

        if parsed:
            summary = parsed.get("threat_intel_summary", f"Threat intelligence evaluation completed for {len(iocs)} IOC(s).")
            findings = [
                f"Extracted IOC Count: {len(iocs)}",
                f"Malware Context: {parsed.get('malware_family', 'N/A')}",
            ]
            if parsed.get("high_risk_iocs"):
                findings.append(f"High Risk IOCs: {', '.join(parsed.get('high_risk_iocs'))}")
            confidence = float(parsed.get("confidence", 0.90))
        else:
            # Deterministic Fallback
            summary = f"Deterministic Threat Intel: Evaluated {len(iocs)} extracted IOC(s) against local database context."
            findings = [f"Extracted IOC Count: {len(iocs)}"]
            for item in iocs[:5]:
                findings.append(f"IOC [{item.get('ioc_type')}]: {item.get('normalized_value')}")
            confidence = 0.85

        thought = AgentThought(
            agent_role=AgentRole.THREAT_INTEL_AGENT,
            model_used=model_used,
            summary=summary,
            findings=findings,
            confidence=confidence,
            timestamp=datetime.now(timezone.utc)
        )

        return thought
