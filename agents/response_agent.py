"""Response Agent for SPECTRA-XDR Multi-Agent Swarm."""

import logging
from datetime import datetime, timezone
from typing import Any, Dict, List

from agents.models import AgentRole, AgentThought, SwarmState
from models.router import ModelRouter

logger = logging.getLogger("spectra.agents.response")


class ResponseAgent:
    """Agent 6: Formulates approved containment playbooks and response actions."""

    def __init__(self, router: ModelRouter):
        self.router = router

    async def analyze(self, state: SwarmState) -> AgentThought:
        """Formulate recommended containment actions for the incident state."""
        event_data = state.event_data
        agent_name = event_data.get("agent_name", "Unknown Host")
        agent_id = event_data.get("agent_id", "000")
        risk_score = state.risk_score
        risk_level = state.risk_level

        prompt = f"""Formulate containment recommendations for this incident:
Affected Endpoint: {agent_name} (ID: {agent_id})
Current Risk Score: {risk_score} ({risk_level})
Attack Chain: {' -> '.join(state.attack_chain)}

Recommend controlled security responses (e.g. isolate_endpoint, block_ip, kill_process, monitor_only).

Provide structured output in valid JSON:
{{
  "response_plan_summary": "Recommended containment strategy",
  "recommended_actions": [
    {{
      "action_type": "isolate_endpoint",
      "target": "{agent_id}",
      "description": "Isolate affected host from local network via Wazuh Active Response",
      "high_impact": true
    }}
  ],
  "requires_human_approval": true
}}"""

        system_prompt = "You are a Controlled Response & Containment Agent in SPECTRA-XDR."

        raw_output, model_used = await self.router.execute_reasoning(
            agent_role=AgentRole.RESPONSE_AGENT,
            prompt=prompt,
            system_prompt=system_prompt,
            complexity="medium"
        )

        parsed = self.router.parse_json_response(raw_output)

        if parsed:
            summary = parsed.get("response_plan_summary", "Response strategy formulated.")
            actions = parsed.get("recommended_actions", [])
            state.recommended_actions = actions
            findings = [
                f"Recommended Strategy: {summary}",
                f"Action Count: {len(actions)}"
            ] + [f"Action: {a.get('action_type')} on {a.get('target')}" for a in actions]
            confidence = float(parsed.get("confidence", 0.95))
        else:
            # Deterministic Fallback
            actions = []
            if risk_score >= 80:
                actions.append({
                    "action_type": "isolate_endpoint",
                    "target": agent_id,
                    "description": f"Isolate endpoint #{agent_id} ({agent_name}) due to CRITICAL risk score ({risk_score}).",
                    "high_impact": True
                })
            elif risk_score >= 60:
                actions.append({
                    "action_type": "block_ip",
                    "target": event_data.get("src_ip", "0.0.0.0"),
                    "description": "Block suspicious source IP address.",
                    "high_impact": True
                })
            else:
                actions.append({
                    "action_type": "monitor_only",
                    "target": agent_id,
                    "description": "Continue active monitoring without disruptive endpoint changes.",
                    "high_impact": False
                })
            
            state.recommended_actions = actions
            summary = f"Deterministic Containment Plan: Prepared {len(actions)} action(s) for risk level {risk_level}."
            findings = [f"Recommended Action: {a['action_type']} ({a['description']})" for a in actions]
            confidence = 0.90

        thought = AgentThought(
            agent_role=AgentRole.RESPONSE_AGENT,
            model_used=model_used,
            summary=summary,
            findings=findings,
            confidence=confidence,
            timestamp=datetime.now(timezone.utc)
        )

        return thought
