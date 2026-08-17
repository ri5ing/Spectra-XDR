"""Deterministic Policy Engine & Safety Boundary for SPECTRA-XDR."""

import logging
from typing import Any, Dict, List

from agents.models import HumanApprovalStatus

logger = logging.getLogger("spectra.risk.policies")

HIGH_IMPACT_ACTION_TYPES = [
    "isolate_endpoint",
    "block_ip",
    "kill_process",
    "quarantine_file",
    "disable_user_account"
]


def evaluate_response_policy(
    risk_score: float,
    recommended_actions: List[Dict[str, Any]]
) -> Dict[str, Any]:
    """Evaluate response actions against security policies and human approval boundaries."""
    
    requires_approval = False
    
    # Policy Rule 1: High risk scores (>= 60) force human approval requirement
    if risk_score >= 60.0:
        requires_approval = True

    # Policy Rule 2: Any high-impact response action strictly requires human approval
    for action in recommended_actions:
        action_type = action.get("action_type", "")
        if action.get("high_impact", False) or action_type in HIGH_IMPACT_ACTION_TYPES:
            requires_approval = True
            action["requires_approval"] = True
            action["status"] = HumanApprovalStatus.PENDING_APPROVAL.value
        else:
            action["requires_approval"] = False
            action["status"] = HumanApprovalStatus.NOT_REQUIRED.value

    approval_status = (
        HumanApprovalStatus.PENDING_APPROVAL
        if requires_approval
        else HumanApprovalStatus.NOT_REQUIRED
    )

    return {
        "human_approval_required": requires_approval,
        "approval_status": approval_status,
        "evaluated_actions": recommended_actions
    }
