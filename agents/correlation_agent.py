"""Correlation Agent for SPECTRA-XDR Multi-Agent Swarm."""

import logging
from datetime import datetime, timezone
from typing import Any, Dict, List

from agents.models import AgentRole, AgentThought, SwarmState
from models.router import ModelRouter

logger = logging.getLogger("spectra.agents.correlation")


class CorrelationAgent:
    """Agent 4: Correlates multi-event attack chains and temporal security patterns."""

    def __init__(self, router: ModelRouter):
        self.router = router

    async def analyze(self, state: SwarmState) -> AgentThought:
        """Correlate security telemetry into an incident attack chain."""
        event_data = state.event_data
        detection_matches = state.detection_matches
        mitre_mappings = state.mitre_mappings

        prompt = f"""Perform event correlation and construct the attack chain for this incident:
Primary Security Event: {event_data.get('rule_description', '')}
Triggered Rules Count: {len(detection_matches)}
Mapped MITRE Techniques Count: {len(mitre_mappings)}

Reconstruct the attack chain progression (e.g. Authentication Anomaly -> Execution -> Persistence -> Command & Control).

Provide structured output in valid JSON:
{{
  "attack_chain": ["Initial Access", "Execution", "Persistence"],
  "correlation_confidence": 0.93,
  "attack_narrative": "Detailed temporal attack chain explanation",
  "key_findings": ["Stage 1: Suspicious login", "Stage 2: Script execution"]
}}"""

        system_prompt = "You are a Principal Threat Correlation Lead Agent in SPECTRA-XDR."

        raw_output, model_used = await self.router.execute_reasoning(
            agent_role=AgentRole.CORRELATION_AGENT,
            prompt=prompt,
            system_prompt=system_prompt,
            complexity="high"
        )

        parsed = self.router.parse_json_response(raw_output)

        if parsed:
            summary = parsed.get("attack_narrative", "Attack chain successfully correlated across telemetry.")
            attack_chain = parsed.get("attack_chain", ["Execution"])
            findings = parsed.get("key_findings", [f"Attack Chain: {' -> '.join(attack_chain)}"])
            confidence = float(parsed.get("correlation_confidence", 0.91))
            # Store attack chain in state
            state.attack_chain = attack_chain
        else:
            # Deterministic Fallback
            attack_chain = ["Authentication Anomaly", "Execution"]
            summary = f"Deterministic Correlation: Linked Rule {event_data.get('rule_id')} with {len(detection_matches)} rule match(es)."
            findings = [
                f"Attack Progression: {' -> '.join(attack_chain)}",
                f"Correlated Rule Matches: {len(detection_matches)}",
                f"Correlated ATT&CK Contexts: {len(mitre_mappings)}"
            ]
            confidence = 0.86
            state.attack_chain = attack_chain

        thought = AgentThought(
            agent_role=AgentRole.CORRELATION_AGENT,
            model_used=model_used,
            summary=summary,
            findings=findings,
            confidence=confidence,
            timestamp=datetime.now(timezone.utc)
        )

        return thought
