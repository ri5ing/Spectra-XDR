"""Unit tests for Controlled Response Execution functions."""

import pytest
from response import actions as response_actions


@pytest.mark.anyio
async def test_isolate_endpoint_action():
    """Test endpoint isolation function execution."""
    res = await response_actions.isolate_endpoint(
        agent_id="001",
        incident_id="INC-000001",
        approved_by="SOC Lead"
    )
    assert res["status"] == "EXECUTED"
    assert res["action_type"] == "isolate_endpoint"
    assert res["approved_by"] == "SOC Lead"


@pytest.mark.anyio
async def test_block_ip_action():
    """Test IP block response function execution."""
    res = await response_actions.block_ip(
        ip_address="192.168.1.100",
        agent_id="001",
        incident_id="INC-000001",
        approved_by="Analyst"
    )
    assert res["status"] == "EXECUTED"
    assert res["target"] == "192.168.1.100"
