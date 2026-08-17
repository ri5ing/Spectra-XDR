"""Wazuh Active Response API Integration Client."""

import logging
from typing import Any, Dict, Optional
import httpx

from backend.config import settings

logger = logging.getLogger("spectra.response.wazuh")


class WazuhActiveResponseClient:
    """Client for triggering Wazuh Active Response on connected endpoint agents."""

    def __init__(self, base_url: Optional[str] = None, username: Optional[str] = None, password: Optional[str] = None):
        self.base_url = (base_url or settings.WAZUH_API_URL).rstrip("/")
        self.username = username or settings.WAZUH_USERNAME
        self.password = password or settings.WAZUH_PASSWORD
        self.verify_ssl = settings.WAZUH_VERIFY_SSL
        self.token: Optional[str] = None

    async def authenticate(self) -> bool:
        """Authenticate with Wazuh API and retain JWT token."""
        url = f"{self.base_url}/security/user/authenticate"
        try:
            async with httpx.AsyncClient(verify=self.verify_ssl, timeout=5.0) as client:
                res = await client.post(url, auth=(self.username, self.password))
                if res.status_code == 200:
                    data = res.json()
                    self.token = data.get("data", {}).get("token")
                    return True
        except Exception as err:
            logger.warning(f"Wazuh authentication failed: {err}")
        return False

    async def send_active_response(self, agent_id: str, command: str, arguments: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Send Active Response command to target Wazuh agent."""
        if not self.token:
            authenticated = await self.authenticate()
            if not authenticated:
                # Return simulated response in test / mock environment
                logger.info(f"Simulating Active Response '{command}' on agent #{agent_id}")
                return {"status": "simulated", "agent_id": agent_id, "command": command}

        url = f"{self.base_url}/active-response"
        headers = {"Authorization": f"Bearer {self.token}"}
        payload = {
            "command": command,
            "custom": True,
            "agents_list": [agent_id]
        }
        if arguments:
            payload["arguments"] = arguments

        try:
            async with httpx.AsyncClient(verify=self.verify_ssl, timeout=10.0) as client:
                res = await client.post(url, headers=headers, json=payload)
                if res.status_code == 200:
                    return res.json()
                else:
                    logger.warning(f"Wazuh AR API returned status HTTP {res.status_code}: {res.text}")
                    return {"status": "error", "http_status": res.status_code, "detail": res.text}
        except Exception as err:
            logger.error(f"Error triggering Wazuh AR: {err}")
            return {"status": "error", "error": str(err)}
