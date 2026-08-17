"""Supervisor Agent for SPECTRA-XDR Multi-Agent Swarm."""

import logging
from typing import Any, Dict, List, Optional

from agents.models import AgentRole, SwarmState
from agents.detection_agent import DetectionAgent
from agents.mitre_agent import MitreAgent
from agents.threat_intel_agent import ThreatIntelAgent
from agents.correlation_agent import CorrelationAgent
from agents.investigation_agent import InvestigationAgent
from agents.response_agent import ResponseAgent
from agents.reporting_agent import ReportingAgent
from models.router import ModelRouter

logger = logging.getLogger("spectra.agents.supervisor")


class SwarmSupervisor:
    """Orchestrator for SPECTRA-XDR Multi-Agent Swarm execution."""

    def __init__(self, router: Optional[ModelRouter] = None):
        self.router = router or ModelRouter()
        self.detection_agent = DetectionAgent(self.router)
        self.mitre_agent = MitreAgent(self.router)
        self.threat_intel_agent = ThreatIntelAgent(self.router)
        self.correlation_agent = CorrelationAgent(self.router)
        self.investigation_agent = InvestigationAgent(self.router)
        self.response_agent = ResponseAgent(self.router)
        self.reporting_agent = ReportingAgent(self.router)

    async def step_agent(self, agent_role: AgentRole, state: SwarmState) -> SwarmState:
        """Execute specified agent node and record thought in shared SwarmState."""
        logger.info(f"Executing swarm node: {agent_role}")
        state.current_agent = agent_role

        thought = None
        if agent_role == AgentRole.DETECTION_AGENT:
            thought = await self.detection_agent.analyze(state)
        elif agent_role == AgentRole.MITRE_AGENT:
            thought = await self.mitre_agent.analyze(state)
        elif agent_role == AgentRole.THREAT_INTEL_AGENT:
            thought = await self.threat_intel_agent.analyze(state)
        elif agent_role == AgentRole.CORRELATION_AGENT:
            thought = await self.correlation_agent.analyze(state)
        elif agent_role == AgentRole.INVESTIGATION_AGENT:
            thought = await self.investigation_agent.analyze(state)
        elif agent_role == AgentRole.RESPONSE_AGENT:
            thought = await self.response_agent.analyze(state)
        elif agent_role == AgentRole.SUPERVISOR:
            thought = await self.reporting_agent.analyze(state)

        if thought:
            state.thoughts.append(thought)
            if agent_role not in state.completed_agents:
                state.completed_agents.append(agent_role)

        return state
