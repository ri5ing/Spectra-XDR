"""Unit tests for Swarm Orchestrator and Agent Swarm workflow."""

import uuid
import pytest
from agents.models import SwarmState, AgentRole
from orchestration.graph import SwarmOrchestrator


@pytest.mark.anyio
async def test_full_swarm_orchestration():
    """Test end-to-end multi-agent swarm execution."""
    state = SwarmState(
        incident_id=uuid.uuid4(),
        incident_human_id="INC-000042",
        event_data={
            "rule_id": "100201",
            "rule_description": "Suspicious PowerShell command execution",
            "severity": "high",
            "agent_name": "Win10-Endpoint",
            "agent_id": "001"
        },
        mitre_mappings=[{"technique_id": "T1059.001", "technique_name": "PowerShell", "tactic": "Execution"}],
        extracted_iocs=[{"ioc_type": "ip", "normalized_value": "192.168.1.50"}],
        detection_matches=[{"rule_id": "100201"}]
    )

    orchestrator = SwarmOrchestrator()
    final_state = await orchestrator.run_swarm(state)

    assert len(final_state.thoughts) >= 7
    assert AgentRole.DETECTION_AGENT in final_state.completed_agents
    assert AgentRole.RESPONSE_AGENT in final_state.completed_agents
    assert final_state.risk_score > 0.0
    assert len(final_state.recommended_actions) > 0
