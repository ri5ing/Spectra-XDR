"""Reporting Agent for SPECTRA-XDR Multi-Agent Swarm."""

import logging
from datetime import datetime, timezone
from typing import Any, Dict, List

from agents.models import AgentRole, AgentThought, SwarmState
from models.router import ModelRouter

logger = logging.getLogger("spectra.agents.reporting")


class ReportingAgent:
    """Agent 7: Generates executive incident summary reports and threat hunting briefs."""

    def __init__(self, router: ModelRouter):
        self.router = router

    async def analyze(self, state: SwarmState) -> AgentThought:
        """Compile executive incident summary report from SwarmState artifacts."""
        event_data = state.event_data
        thoughts = state.thoughts
        risk_score = state.risk_score
        risk_level = state.risk_level

        prompt = f"""Generate an executive incident summary report:
Incident ID: {state.incident_human_id}
Affected Host: {event_data.get('agent_name', 'Unknown')}
Risk Score: {risk_score} ({risk_level})
Attack Chain: {' -> '.join(state.attack_chain)}
Total Swarm Agent Thoughts: {len(thoughts)}

Provide structured output in valid JSON:
{{
  "executive_summary": "High-level summary of the security incident and swarm analysis",
  "key_findings": ["Finding A", "Finding B"],
  "remediation_roadmap": ["Step 1", "Step 2"]
}}"""

        system_prompt = "You are an Incident Reporting & Executive Communications Agent in SPECTRA-XDR."

        raw_output, model_used = await self.router.execute_reasoning(
            agent_role=AgentRole.SUPERVISOR,
            prompt=prompt,
            system_prompt=system_prompt,
            complexity="medium"
        )

        parsed = self.router.parse_json_response(raw_output)

        if parsed:
            summary = parsed.get("executive_summary", "Executive incident report compiled successfully.")
            findings = parsed.get("key_findings", []) + [f"Remediation: {r}" for r in parsed.get("remediation_roadmap", [])]
            confidence = 0.96
        else:
            # Deterministic Fallback
            summary = f"Executive Summary for {state.incident_human_id}: Risk level evaluated as {risk_level} ({risk_score}/100)."
            findings = [
                f"Incident Identifier: {state.incident_human_id}",
                f"Risk Score: {risk_score} / 100 ({risk_level})",
                f"Attack Progression: {' -> '.join(state.attack_chain) if state.attack_chain else 'Telemetry Anomaly'}",
                f"Swarm Analysis Completed by {len(thoughts)} specialized agents.",
                "Remediation: Apply recommended policy actions and review analyst audit log."
            ]
            confidence = 0.92

        thought = AgentThought(
            agent_role=AgentRole.SUPERVISOR,
            model_used=model_used,
            summary=summary,
            findings=findings,
            confidence=confidence,
            timestamp=datetime.now(timezone.utc)
        )

        return thought
