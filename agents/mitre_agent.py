"""MITRE ATT&CK Agent for SPECTRA-XDR Multi-Agent Swarm."""

import logging
from datetime import datetime, timezone
from typing import Any, Dict, List

from agents.models import AgentRole, AgentThought, SwarmState
from models.router import ModelRouter

logger = logging.getLogger("spectra.agents.mitre")


class MitreAgent:
    """Agent 2: Maps telemetry to MITRE ATT&CK tactics, techniques, and mitigations."""

    def __init__(self, router: ModelRouter):
        self.router = router

    async def analyze(self, state: SwarmState) -> AgentThought:
        """Enrich incident with MITRE ATT&CK context."""
        mitre_mappings = state.mitre_mappings
        detection_matches = state.detection_matches
        event_data = state.event_data

        techniques = []
        for m in mitre_mappings:
            tech_id = m.get("technique_id", "")
            tech_name = m.get("technique_name", "")
            tactic = m.get("tactic", "")
            if tech_id:
                techniques.append(f"{tech_id} ({tech_name} - {tactic})")

        prompt = f"""Evaluate MITRE ATT&CK alignment for this incident:
Event Details: {event_data.get('rule_description', 'No description')}
Mapped ATT&CK Techniques: {techniques if techniques else 'None specified'}
Detection Rules Triggered: {len(detection_matches)}

Provide structured output in valid JSON:
{{
  "attack_tactics": ["Execution", "Persistence"],
  "primary_technique": "T1059.001",
  "threat_context": "Summary of adversary behavior",
  "mitigation_recommendations": ["Enforce Script Block Logging", "Restrict PowerShell Execution Policy"]
}}"""

        system_prompt = "You are a MITRE ATT&CK Threat Specialist Agent in SPECTRA-XDR."

        raw_output, model_used = await self.router.execute_reasoning(
            agent_role=AgentRole.MITRE_AGENT,
            prompt=prompt,
            system_prompt=system_prompt,
            complexity="medium"
        )

        parsed = self.router.parse_json_response(raw_output)

        if parsed:
            summary = parsed.get("threat_context", "Mapped ATT&CK techniques and threat context.")
            mitigations = parsed.get("mitigation_recommendations", [])
            findings = [
                f"Primary Technique: {parsed.get('primary_technique', 'T1059')}",
                f"Tactics Identified: {', '.join(parsed.get('attack_tactics', []))}",
            ] + [f"Mitigation: {m}" for m in mitigations]
            confidence = float(parsed.get("confidence", 0.92))
        else:
            # Deterministic Fallback
            summary = f"Deterministic ATT&CK Mapping: Identified {len(mitre_mappings)} technique(s) across telemetry."
            findings = []
            for m in mitre_mappings:
                findings.append(f"Technique {m.get('technique_id', 'T1059')}: {m.get('technique_name', 'Command Interpreter')} [{m.get('tactic', 'Execution')}]")
            if not findings:
                findings.append("No explicit MITRE ATT&CK techniques matched in local catalog for this alert.")
            confidence = 0.88

        thought = AgentThought(
            agent_role=AgentRole.MITRE_AGENT,
            model_used=model_used,
            summary=summary,
            findings=findings,
            confidence=confidence,
            timestamp=datetime.now(timezone.utc)
        )

        return thought
