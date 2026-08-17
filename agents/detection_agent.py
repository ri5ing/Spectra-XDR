"""Detection Agent for SPECTRA-XDR Multi-Agent Swarm."""

import logging
from datetime import datetime, timezone
from typing import Any, Dict

from agents.models import AgentRole, AgentThought, SwarmState
from models.router import ModelRouter

logger = logging.getLogger("spectra.agents.detection")


class DetectionAgent:
    """Agent 1: Initial alert classification, severity assessment, and false-positive evaluation."""

    def __init__(self, router: ModelRouter):
        self.router = router

    async def analyze(self, state: SwarmState) -> AgentThought:
        """Analyze security alert telemetry in SwarmState."""
        event = state.event_data
        rule_id = event.get("rule_id", "Unknown")
        rule_description = event.get("rule_description", "No description")
        agent_name = event.get("agent_name", "Unknown Host")
        severity_level = event.get("severity", "medium")

        prompt = f"""Analyze the following Wazuh security event:
- Rule ID: {rule_id}
- Description: {rule_description}
- Affected Agent: {agent_name}
- Initial Severity: {severity_level}
- Event Payload: {event.get('full_log', '')}

Evaluate if this event is a genuine suspicious alert or a potential false positive.
Provide output in valid JSON:
{{
  "classification": "suspicious|benign|anomaly",
  "confidence": 0.95,
  "assessed_severity": "low|medium|high|critical",
  "reasoning_summary": "Short explanation",
  "findings": ["Finding 1", "Finding 2"]
}}"""

        system_prompt = "You are a Tier 1 SOC Detection Agent in SPECTRA-XDR. Perform accurate security triage."

        raw_output, model_used = await self.router.execute_reasoning(
            agent_role=AgentRole.DETECTION_AGENT,
            prompt=prompt,
            system_prompt=system_prompt,
            complexity="medium"
        )

        parsed = self.router.parse_json_response(raw_output)

        if parsed:
            summary = parsed.get("reasoning_summary", f"Alert triage completed for Rule {rule_id}")
            findings = parsed.get("findings", [
                f"Classification: {parsed.get('classification', 'suspicious')}",
                f"Assessed Severity: {parsed.get('assessed_severity', severity_level)}"
            ])
            confidence = float(parsed.get("confidence", 0.9))
        else:
            # Deterministic Fallback Logic
            summary = f"Deterministic Triage: Evaluated Rule {rule_id} on {agent_name}. Severity: {severity_level.upper()}."
            findings = [
                f"Rule {rule_id}: {rule_description}",
                f"Affected endpoint: {agent_name}",
                f"Telemetry classified as {severity_level.lower()} severity security event."
            ]
            confidence = 0.85

        thought = AgentThought(
            agent_role=AgentRole.DETECTION_AGENT,
            model_used=model_used,
            summary=summary,
            findings=findings,
            confidence=confidence,
            timestamp=datetime.now(timezone.utc)
        )

        return thought
