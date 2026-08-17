"""Approved Deterministic Response Execution Layer for SPECTRA-XDR."""

import logging
from typing import Any, Dict, Optional
from response.wazuh import WazuhActiveResponseClient

logger = logging.getLogger("spectra.response.actions")

wazuh_ar_client = WazuhActiveResponseClient()


async def isolate_endpoint(agent_id: str, incident_id: str, approved_by: str) -> Dict[str, Any]:
    """Isolate host endpoint from local network via Wazuh Active Response."""
    if not agent_id or not agent_id.strip():
        raise ValueError("Target agent_id is required for endpoint isolation.")

    logger.info(f"Executing Approved Action: Host Isolation for Agent #{agent_id} (Approved by: {approved_by})")
    
    result = await wazuh_ar_client.send_active_response(
        agent_id=agent_id,
        command="netsh-isolate" if "win" in agent_id.lower() else "host-deny",
        arguments={"incident_id": incident_id, "action": "isolate"}
    )
    return {
        "action_type": "isolate_endpoint",
        "target": agent_id,
        "incident_id": incident_id,
        "approved_by": approved_by,
        "status": "EXECUTED",
        "execution_result": result
    }


async def block_ip(ip_address: str, agent_id: str, incident_id: str, approved_by: str) -> Dict[str, Any]:
    """Block suspicious IP address on host firewall."""
    if not ip_address or not ip_address.strip():
        raise ValueError("Target ip_address is required for IP blocking.")

    logger.info(f"Executing Approved Action: Block IP {ip_address} on Agent #{agent_id} (Approved by: {approved_by})")

    result = await wazuh_ar_client.send_active_response(
        agent_id=agent_id,
        command="firewall-drop",
        arguments={"ip": ip_address, "incident_id": incident_id}
    )
    return {
        "action_type": "block_ip",
        "target": ip_address,
        "agent_id": agent_id,
        "incident_id": incident_id,
        "approved_by": approved_by,
        "status": "EXECUTED",
        "execution_result": result
    }


async def kill_process(pid: int, process_name: str, agent_id: str, incident_id: str, approved_by: str) -> Dict[str, Any]:
    """Kill malicious process on host."""
    logger.info(f"Executing Approved Action: Kill Process {process_name} (PID: {pid}) on Agent #{agent_id}")
    
    result = await wazuh_ar_client.send_active_response(
        agent_id=agent_id,
        command="kill-process",
        arguments={"pid": str(pid), "process_name": process_name, "incident_id": incident_id}
    )
    return {
        "action_type": "kill_process",
        "target": f"{process_name} (PID: {pid})",
        "agent_id": agent_id,
        "incident_id": incident_id,
        "approved_by": approved_by,
        "status": "EXECUTED",
        "execution_result": result
    }


async def quarantine_file(file_path: str, agent_id: str, incident_id: str, approved_by: str) -> Dict[str, Any]:
    """Quarantine suspicious file on host."""
    logger.info(f"Executing Approved Action: Quarantine File '{file_path}' on Agent #{agent_id}")
    
    result = await wazuh_ar_client.send_active_response(
        agent_id=agent_id,
        command="file-quarantine",
        arguments={"file_path": file_path, "incident_id": incident_id}
    )
    return {
        "action_type": "quarantine_file",
        "target": file_path,
        "agent_id": agent_id,
        "incident_id": incident_id,
        "approved_by": approved_by,
        "status": "EXECUTED",
        "execution_result": result
    }


async def disable_user_account(username: str, agent_id: str, incident_id: str, approved_by: str) -> Dict[str, Any]:
    """Disable compromised user account on host."""
    logger.info(f"Executing Approved Action: Disable Account '{username}' on Agent #{agent_id}")
    
    result = await wazuh_ar_client.send_active_response(
        agent_id=agent_id,
        command="disable-account",
        arguments={"username": username, "incident_id": incident_id}
    )
    return {
        "action_type": "disable_user_account",
        "target": username,
        "agent_id": agent_id,
        "incident_id": incident_id,
        "approved_by": approved_by,
        "status": "EXECUTED",
        "execution_result": result
    }
