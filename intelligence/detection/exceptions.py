"""Custom Detection exceptions for SPECTRA-XDR."""


class DetectionError(Exception):
    """Base exception for detection processing errors."""
    pass


class InvalidConditionConfigError(DetectionError):
    """Raised when a condition configuration is invalid."""
    pass


class RuleExecutionError(DetectionError):
    """Raised when a rule fails to execute."""
    pass
