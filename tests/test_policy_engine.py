"""Unit tests for Deterministic Policy Engine."""

from agents.models import HumanApprovalStatus
from risk.policies import evaluate_response_policy


def test_evaluate_policy_low_risk():
    """Test policy evaluation for low risk actions requiring no human approval."""
    actions = [{"action_type": "monitor_only", "target": "host1", "high_impact": False}]
    res = evaluate_response_policy(risk_score=20.0, recommended_actions=actions)
    assert res["human_approval_required"] is False
    assert res["approval_status"] == HumanApprovalStatus.NOT_REQUIRED


def test_evaluate_policy_high_impact_action():
    """Test policy evaluation forcing human approval for high-impact isolate_endpoint action."""
    actions = [{"action_type": "isolate_endpoint", "target": "001", "high_impact": True}]
    res = evaluate_response_policy(risk_score=45.0, recommended_actions=actions)
    assert res["human_approval_required"] is True
    assert res["approval_status"] == HumanApprovalStatus.PENDING_APPROVAL
