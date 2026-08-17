"""Unit tests for Hybrid AI Model Router."""

import pytest
from agents.models import AgentRole, ModelChoice
from models.router import ModelRouter
from models.sanitizer import sanitize_text, sanitize_telemetry


def test_telemetry_sanitizer():
    """Test sanitization of passwords and bearer tokens."""
    raw = "User password='SecretPassword123' token: 'abc123xyz' Bearer eyJhbGci"
    sanitized = sanitize_text(raw)
    assert "SecretPassword123" not in sanitized
    assert "[REDACTED]" in sanitized

    dict_data = {"user": "admin", "password": "SuperSecretPassword", "nested": {"api_key": "key99"}}
    sanitized_dict = sanitize_telemetry(dict_data)
    assert sanitized_dict["password"] == "[REDACTED]"


@pytest.mark.anyio
async def test_model_router_fallback():
    """Test model selection and fallback to deterministic reasoning when LLMs are offline."""
    router = ModelRouter()
    
    # Test router selection
    choice = router.select_model(AgentRole.DETECTION_AGENT, complexity="low")
    assert choice in [ModelChoice.OLLAMA_LOCAL, ModelChoice.GEMINI_CLOUD]

    # Test reasoning execution with fallback
    output, model_used = await router.execute_reasoning(
        agent_role=AgentRole.DETECTION_AGENT,
        prompt="Test alert prompt",
        system_prompt="Test system prompt"
    )
    assert model_used in [ModelChoice.OLLAMA_LOCAL, ModelChoice.GEMINI_CLOUD, ModelChoice.DETERMINISTIC_FALLBACK]


def test_json_parsing():
    """Test extraction of JSON payloads from LLM outputs."""
    raw = "Here is the result:\n```json\n{\"classification\": \"suspicious\", \"confidence\": 0.95}\n```"
    parsed = ModelRouter.parse_json_response(raw)
    assert parsed is not None
    assert parsed["classification"] == "suspicious"
    assert parsed["confidence"] == 0.95
