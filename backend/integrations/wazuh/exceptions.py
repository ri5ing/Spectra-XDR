"""Wazuh integration exception definitions."""


class WazuhError(Exception):
    """Base exception for all Wazuh API integration errors."""

    def __init__(self, message: str = "Wazuh API error occurred"):
        self.message = message
        super().__init__(self.message)


class WazuhAuthenticationError(WazuhError):
    """Raised when authentication with Wazuh API fails (e.g. invalid credentials or expired token)."""

    def __init__(self, message: str = "Failed to authenticate with Wazuh API"):
        super().__init__(message)


class WazuhConnectionError(WazuhError):
    """Raised when connection to Wazuh server fails (e.g. network down, unreachable host)."""

    def __init__(self, message: str = "Could not connect to Wazuh API server"):
        super().__init__(message)


class WazuhTimeoutError(WazuhError):
    """Raised when Wazuh API request times out."""

    def __init__(self, message: str = "Wazuh API request timed out"):
        super().__init__(message)


class WazuhResponseError(WazuhError):
    """Raised when Wazuh API returns unexpected HTTP error codes or malformed response JSON."""

    def __init__(self, message: str = "Invalid response received from Wazuh API", status_code: int = 500):
        self.status_code = status_code
        super().__init__(message)
