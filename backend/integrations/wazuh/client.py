"""Async Read-Only Client for Wazuh API (v4.x)."""

from typing import Any, Dict, Optional
import httpx

from backend.config import settings
from backend.logging_config import get_logger
from backend.integrations.wazuh.exceptions import (
    WazuhAuthenticationError,
    WazuhConnectionError,
    WazuhResponseError,
    WazuhTimeoutError,
)

logger = get_logger("spectra.wazuh.client")


class WazuhClient:
    """Read-only API Client for interacting with Wazuh Manager API (v4.x)."""

    def __init__(
        self,
        api_url: Optional[str] = None,
        username: Optional[str] = None,
        password: Optional[str] = None,
        verify_ssl: Optional[bool] = None,
        timeout: Optional[int] = None,
    ):
        self.api_url = (api_url or settings.WAZUH_API_URL).rstrip("/")
        self.username = username or settings.WAZUH_USERNAME
        self.password = password or settings.WAZUH_PASSWORD
        self.verify_ssl = verify_ssl if verify_ssl is not None else settings.WAZUH_VERIFY_SSL
        self.timeout = timeout if timeout is not None else settings.WAZUH_TIMEOUT
        
        self.token: Optional[str] = None

    def _get_client(self, headers: Optional[Dict[str, str]] = None) -> httpx.AsyncClient:
        """Returns configured httpx.AsyncClient instance."""
        return httpx.AsyncClient(
            verify=self.verify_ssl,
            timeout=self.timeout,
            headers=headers or {}
        )

    async def authenticate(self) -> str:
        """Authenticates against /security/user/authenticate and retrieves JWT token."""
        logger.info(f"Authenticating with Wazuh API at {self.api_url}")
        auth_url = f"{self.api_url}/security/user/authenticate"

        try:
            async with httpx.AsyncClient(verify=self.verify_ssl, timeout=self.timeout) as client:
                response = await client.post(
                    auth_url,
                    auth=(self.username, self.password)
                )
                
                if response.status_code in (401, 403):
                    logger.error(f"Wazuh authentication failed: HTTP {response.status_code}")
                    raise WazuhAuthenticationError("Invalid Wazuh credentials or unauthorized")
                
                if response.status_code != 200:
                    logger.error(f"Unexpected status during Wazuh auth: {response.status_code}")
                    raise WazuhResponseError(f"Authentication failed with status {response.status_code}", status_code=response.status_code)

                data = response.json()
                token = data.get("data", {}).get("token")
                if not token:
                    raise WazuhResponseError("Token not found in Wazuh auth response")

                self.token = token
                logger.info("Successfully authenticated with Wazuh API")
                return self.token

        except httpx.TimeoutException as e:
            logger.error("Wazuh authentication timed out")
            raise WazuhTimeoutError("Connection timed out while authenticating with Wazuh API") from e
        except httpx.RequestError as e:
            logger.error(f"Wazuh connection error: {str(e)}")
            raise WazuhConnectionError("Failed to connect to Wazuh API server") from e

    async def _request(self, method: str, endpoint: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Internal helper for making authorized read-only requests."""
        if not self.token:
            await self.authenticate()

        url = f"{self.api_url}{endpoint}"
        headers = {"Authorization": f"Bearer {self.token}"}

        try:
            async with self._get_client(headers=headers) as client:
                response = await client.request(method=method, url=url, params=params)

                # Retry authentication once if token expired
                if response.status_code in (401, 403):
                    logger.warning("Wazuh token expired or invalid, re-authenticating...")
                    await self.authenticate()
                    headers = {"Authorization": f"Bearer {self.token}"}
                    async with self._get_client(headers=headers) as retry_client:
                        response = await retry_client.request(method=method, url=url, params=params)

                if response.status_code != 200:
                    logger.error(f"Wazuh request {method} {endpoint} failed: {response.status_code}")
                    raise WazuhResponseError(f"Wazuh request failed with status {response.status_code}", status_code=response.status_code)

                return response.json()

        except httpx.TimeoutException as e:
            logger.error(f"Wazuh request to {endpoint} timed out")
            raise WazuhTimeoutError(f"Request to Wazuh endpoint {endpoint} timed out") from e
        except httpx.RequestError as e:
            logger.error(f"Wazuh connection error on {endpoint}: {str(e)}")
            raise WazuhConnectionError(f"Failed to communicate with Wazuh server on {endpoint}") from e

    async def health_check(self) -> Dict[str, Any]:
        """Performs a read-only health and status check against Wazuh API."""
        try:
            # Query manager status endpoint
            res = await self._request("GET", "/manager/status")
            return {
                "status": "healthy",
                "service": "wazuh",
                "details": res.get("data", {})
            }
        except Exception as e:
            logger.warning(f"Wazuh health check failed: {str(e)}")
            raise

    async def get_agents(self, limit: int = 10, offset: int = 0) -> Dict[str, Any]:
        """Retrieves read-only agent inventory from Wazuh."""
        params = {"limit": limit, "offset": offset}
        return await self._request("GET", "/agents", params=params)

    async def get_alerts(self, limit: int = 10, offset: int = 0) -> Dict[str, Any]:
        """Retrieves read-only alert/log records from Wazuh (supporting /alerts and /manager/logs)."""
        params = {"limit": limit, "offset": offset}
        try:
            return await self._request("GET", "/alerts", params=params)
        except WazuhResponseError as e:
            if getattr(e, "status_code", None) == 404:
                logger.info("Wazuh /alerts endpoint returned 404, falling back to /manager/logs")
                return await self._request("GET", "/manager/logs", params=params)
            raise

