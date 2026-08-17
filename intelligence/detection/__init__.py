"""Detection Package exports."""

from intelligence.detection.models import ConditionType
from intelligence.detection.conditions import ConditionEvaluator
from intelligence.detection.registry import DetectionRegistry, BUILTIN_DETECTION_RULES
from intelligence.detection.engine import DetectionEngine, DetectionMatchResult
from intelligence.detection.exceptions import DetectionError, InvalidConditionConfigError, RuleExecutionError

__all__ = [
    "ConditionType",
    "ConditionEvaluator",
    "DetectionRegistry",
    "BUILTIN_DETECTION_RULES",
    "DetectionEngine",
    "DetectionMatchResult",
    "DetectionError",
    "InvalidConditionConfigError",
    "RuleExecutionError",
]
