"""Unit tests for WazuhClient with mocked HTTP responses."""

import asyncio
import pytest
import httpx
from unittest.mock import AsyncMock, patch, MagicMock

from backend.integrations.wazuh.client import WazuhClient
from backend.integrations.wazuh.exceptions import (
    WazuhAuthenticationError,
    WazuhConnectionError,
    WazuhTimeoutError,
)


def test_authenticate_success():
    """Verify successful authentication extracts bearer token."""
    client = WazuhClient(api_url="https://wazuh-test:55000", username="admin", password="password")
    
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"data": {"token": "mocked_jwt_token_123"}}

    with patch("httpx.AsyncClient.post", new_callable=AsyncMock) as mock_post:
        mock_post.return_value = mock_response
        token = asyncio.run(client.authenticate())

        assert token == "mocked_jwt_token_123"
        assert client.token == "mocked_jwt_token_123"
        mock_post.assert_called_once()


def test_authenticate_invalid_credentials():
    """Verify 401 response raises WazuhAuthenticationError."""
    client = WazuhClient(api_url="https://wazuh-test:55000", username="admin", password="wrong_password")
    
    mock_response = MagicMock()
    mock_response.status_code = 401

    with patch("httpx.AsyncClient.post", new_callable=AsyncMock) as mock_post:
        mock_post.return_value = mock_response
        with pytest.raises(WazuhAuthenticationError):
            asyncio.run(client.authenticate())


def test_authenticate_connection_error():
    """Verify network connection error raises WazuhConnectionError."""
    client = WazuhClient(api_url="https://unreachable-wazuh:55000")

    with patch("httpx.AsyncClient.post", new_callable=AsyncMock) as mock_post:
        mock_post.side_effect = httpx.ConnectError("Network unreachable")
        with pytest.raises(WazuhConnectionError):
            asyncio.run(client.authenticate())


def test_authenticate_timeout_error():
    """Verify request timeout raises WazuhTimeoutError."""
    client = WazuhClient(api_url="https://wazuh-test:55000")

    with patch("httpx.AsyncClient.post", new_callable=AsyncMock) as mock_post:
        mock_post.side_effect = httpx.TimeoutException("Connection timed out")
        with pytest.raises(WazuhTimeoutError):
            asyncio.run(client.authenticate())


def test_get_agents_success():
    """Verify get_agents parses and returns agent listing."""
    client = WazuhClient(api_url="https://wazuh-test:55000")
    client.token = "valid_token"

    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "data": {
            "total_affected_items": 2,
            "affected_items": [
                {"id": "000", "name": "wazuh-server", "ip": "127.0.0.1", "status": "active"},
                {"id": "001", "name": "win-endpoint", "ip": "192.168.1.50", "status": "active"}
            ]
        }
    }

    with patch("httpx.AsyncClient.request", new_callable=AsyncMock) as mock_request:
        mock_request.return_value = mock_response
        result = asyncio.run(client.get_agents(limit=2, offset=0))

        assert "data" in result
        assert result["data"]["total_affected_items"] == 2
        assert len(result["data"]["affected_items"]) == 2


def test_get_alerts_success():
    """Verify get_alerts parses and returns alert log entries."""
    client = WazuhClient(api_url="https://wazuh-test:55000")
    client.token = "valid_token"

    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "data": {
            "total_affected_items": 1,
            "affected_items": [
                {
                    "id": "alert-101",
                    "timestamp": "2026-08-17T18:00:00Z",
                    "agent": {"id": "001", "name": "win-endpoint", "ip": "192.168.1.50"},
                    "rule": {"id": 5710, "level": 5, "description": "Attempt to login using SSH failed"}
                }
            ]
        }
    }

    with patch("httpx.AsyncClient.request", new_callable=AsyncMock) as mock_request:
        mock_request.return_value = mock_response
        result = asyncio.run(client.get_alerts(limit=1, offset=0))

        assert "data" in result
        assert len(result["data"]["affected_items"]) == 1
        assert result["data"]["affected_items"][0]["id"] == "alert-101"
