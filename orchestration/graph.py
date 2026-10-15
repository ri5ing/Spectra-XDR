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
        """Run 3-phase multi-agent swarm flow with parallel reasoning execution."""
        import asyncio
        logger.info(f"Initiating 3-Phase Parallel Swarm Orchestration for Incident {state.incident_human_id}")

        # === PHASE 1: ALERT INGESTION & DETECTION TRIAGE ===
        state = await self.supervisor.step_agent(AgentRole.DETECTION_AGENT, state)

        # === PHASE 2: PARALLEL SWARM INTELLIGENCE (MITRE, Threat Intel, Investigation, Correlation) ===
        # Run all 4 analytical agents simultaneously in parallel
        results = await asyncio.gather(
            self.supervisor.detection_agent.router.gemini.check_connectivity_and_health() if False else self.supervisor.mitre_agent.analyze(state),
            self.supervisor.threat_intel_agent.analyze(state),
            self.supervisor.investigation_agent.analyze(state),
            self.supervisor.correlation_agent.analyze(state),
            return_exceptions=True
        )

        for thought in results:
            if thought and not isinstance(thought, Exception):
                state.thoughts.append(thought)
                if thought.agent_role not in state.completed_agents:
                    state.completed_agents.append(thought.agent_role)
            elif isinstance(thought, Exception):
                logger.error(f"Error in parallel swarm agent execution: {thought}")

        # === PHASE 3: RISK SYNTHESIS & SOAR CONTAINMENT CONVERGENCE ===
        # 1. Deterministic Risk Engine Evaluation
        risk_result = calculate_incident_risk(
            event_data=state.event_data,
            mitre_mappings=state.mitre_mappings,
            extracted_iocs=state.extracted_iocs,
            detection_matches=state.detection_matches,
            attack_chain=state.attack_chain
        )
        state.risk_score = risk_result["risk_score"]
        state.risk_level = risk_result["risk_level"]

        # 2. Response Agent (SOAR Containment Playbook)
        state = await self.supervisor.step_agent(AgentRole.RESPONSE_AGENT, state)

        # 3. Policy Engine Evaluation (Deterministic Safety Boundary)
        policy_result = evaluate_response_policy(
            risk_score=state.risk_score,
            recommended_actions=state.recommended_actions
        )
        state.human_approval_required = policy_result["human_approval_required"]
        state.human_approval_status = policy_result["approval_status"]

        # 4. Supervisor Summary Node
        state = await self.supervisor.step_agent(AgentRole.SUPERVISOR, state)

        logger.info(f"Completed 3-Phase Swarm Orchestration for Incident {state.incident_human_id}. Final Risk: {state.risk_score} ({state.risk_level})")
        return state
