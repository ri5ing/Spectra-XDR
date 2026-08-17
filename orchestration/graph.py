"""Swarm State Graph Orchestration Engine."""

import logging
from typing import Any, Dict, Optional

from agents.models import AgentRole, SwarmState
from agents.supervisor import SwarmSupervisor
from risk.scoring import calculate_incident_risk
from risk.policies import evaluate_response_policy

logger = logging.getLogger("spectra.orchestration.graph")


class SwarmOrchestrator:
    """Orchestration Engine executing the Multi-Agent Swarm state workflow."""

    def __init__(self, supervisor: Optional[SwarmSupervisor] = None):
        self.supervisor = supervisor or SwarmSupervisor()

    async def run_swarm(self, state: SwarmState) -> SwarmState:
        """Run complete multi-agent reasoning flow over the SwarmState."""
        logger.info(f"Initiating Swarm Orchestration for Incident {state.incident_human_id}")

        # 1. Detection Agent Node
        state = await self.supervisor.step_agent(AgentRole.DETECTION_AGENT, state)

        # 2. MITRE Agent Node
        state = await self.supervisor.step_agent(AgentRole.MITRE_AGENT, state)

        # 3. Threat Intel Agent Node
        state = await self.supervisor.step_agent(AgentRole.THREAT_INTEL_AGENT, state)

        # 4. Correlation Agent Node
        state = await self.supervisor.step_agent(AgentRole.CORRELATION_AGENT, state)

        # 5. Investigation Agent Node
        state = await self.supervisor.step_agent(AgentRole.INVESTIGATION_AGENT, state)

        # 6. Risk Engine Evaluation (Deterministic Core)
        risk_result = calculate_incident_risk(
            event_data=state.event_data,
            mitre_mappings=state.mitre_mappings,
            extracted_iocs=state.extracted_iocs,
            detection_matches=state.detection_matches,
            attack_chain=state.attack_chain
        )
        state.risk_score = risk_result["risk_score"]
        state.risk_level = risk_result["risk_level"]

        # 7. Response Agent Node
        state = await self.supervisor.step_agent(AgentRole.RESPONSE_AGENT, state)

        # 8. Policy Engine Evaluation (Deterministic Safety Boundary)
        policy_result = evaluate_response_policy(
            risk_score=state.risk_score,
            recommended_actions=state.recommended_actions
        )
        state.human_approval_required = policy_result["human_approval_required"]
        state.human_approval_status = policy_result["approval_status"]

        # 9. Reporting / Supervisor Summary Node
        state = await self.supervisor.step_agent(AgentRole.SUPERVISOR, state)

        logger.info(f"Completed Swarm Orchestration for Incident {state.incident_human_id}. Final Risk: {state.risk_score} ({state.risk_level})")
        return state
