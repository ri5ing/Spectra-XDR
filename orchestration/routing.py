"""Routing logic for LangGraph Swarm State Machine."""

from typing import Literal
from agents.models import AgentRole, SwarmState


AGENT_SEQUENCE = [
    AgentRole.DETECTION_AGENT,
    AgentRole.MITRE_AGENT,
    AgentRole.THREAT_INTEL_AGENT,
    AgentRole.CORRELATION_AGENT,
    AgentRole.INVESTIGATION_AGENT,
    AgentRole.RESPONSE_AGENT,
    AgentRole.SUPERVISOR
]


def determine_next_agent(state: SwarmState) -> str:
    """Determine next agent in sequence or END graph execution."""
    for agent in AGENT_SEQUENCE:
        if agent not in state.completed_agents:
            return agent.value
    return "end"
