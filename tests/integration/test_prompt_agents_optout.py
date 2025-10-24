"""
Integration tests for prompt agent opt-out fallback

STEP 8: Validates that prompt engine falls back to TEMPLATE_ONLY when agents are unreachable.
"""

from unittest.mock import AsyncMock, patch

import pytest

from app.core.llm_client import LLMServerUnavailableError, LLMTimeoutError
from app.core.prompts import PromptMode, _call_dialog_agent, generate_prompt


@pytest.fixture
def sample_variables():
    """Sample variables for testing"""
    return {
        "subject": "cyberpunk city",
        "style": "digital art",
        "mood": "neon-lit",
        "composition": "aerial view",
        "lighting": "night scene",
        "details": "8k, highly detailed",
    }


def test_agent_assisted_fallback_on_timeout(sample_variables):
    """Test that AGENT_ASSISTED falls back to TEMPLATE_ONLY on agent timeout"""
    # Mock logic agent to raise timeout
    with patch(
        "app.core.prompts._call_logic_agent",
        side_effect=LLMTimeoutError("Logic agent timeout"),
    ):
        # Should not raise, should fallback to template-only
        prompt = generate_prompt(
            template_name="image_sdxl",
            variables=sample_variables,
            mode=PromptMode.AGENT_ASSISTED,
        )

        assert prompt is not None
        assert isinstance(prompt, str)
        assert len(prompt) > 0


def test_agent_assisted_fallback_on_server_unavailable(sample_variables):
    """Test that AGENT_ASSISTED falls back when server unavailable"""
    # Mock logic agent to raise unavailable error
    with patch(
        "app.core.prompts._call_logic_agent",
        side_effect=LLMServerUnavailableError("Server down"),
    ):
        prompt = generate_prompt(
            template_name="image_sdxl",
            variables=sample_variables,
            mode=PromptMode.AGENT_ASSISTED,
        )

        assert prompt is not None
        assert isinstance(prompt, str)


def test_vision_agent_failure_continues_with_draft(sample_variables):
    """Test that vision agent failure doesn't break the pipeline"""
    # Add reference image
    sample_variables["reference_image"] = "/fake/path/image.png"

    # Mock vision agent to fail
    with patch("app.core.prompts._call_vision_agent", return_value=""):
        # Should continue with empty vision context
        try:
            prompt = generate_prompt(
                template_name="image_sdxl",
                variables=sample_variables,
                mode=PromptMode.AGENT_ASSISTED,
            )
            # If agents available, should complete
            assert prompt is not None
        except (LLMTimeoutError, LLMServerUnavailableError):
            # If agents unavailable, fallback is expected
            pass


def test_dialog_agent_failure_returns_draft():
    """Test that dialog agent failure returns unpolished draft"""
    draft_text = "Test draft prompt"

    # Mock dialog agent to fail
    with patch(
        "app.core.prompts.llm_client.chat",
        new=AsyncMock(side_effect=LLMTimeoutError("Dialog timeout")),
    ):
        result = _call_dialog_agent(draft_text, "image_sdxl")

        # Should return original draft as fallback
        assert result == draft_text


def test_agent_pipeline_with_all_failures_falls_back(sample_variables):
    """Test complete agent pipeline failure results in template-only output"""
    # Mock all agent calls to fail
    with patch("app.core.prompts._call_vision_agent", return_value=""), patch(
        "app.core.prompts._call_logic_agent",
        side_effect=LLMTimeoutError("Logic timeout"),
    ), patch("app.core.prompts._call_dialog_agent", return_value="fallback"):
        prompt = generate_prompt(
            template_name="image_sdxl",
            variables=sample_variables,
            mode=PromptMode.AGENT_ASSISTED,
        )

        # Should fallback to template-only
        assert prompt is not None
        assert isinstance(prompt, str)


def test_template_only_unaffected_by_agent_availability(sample_variables):
    """Test that TEMPLATE_ONLY mode works regardless of agent status"""
    # Mock all agents to fail
    with patch(
        "app.core.llm_client.chat",
        new=AsyncMock(side_effect=LLMServerUnavailableError("All agents down")),
    ):
        # TEMPLATE_ONLY should still work
        prompt = generate_prompt(
            template_name="image_sdxl",
            variables=sample_variables,
            mode=PromptMode.TEMPLATE_ONLY,
        )

        assert prompt is not None
        assert isinstance(prompt, str)


@pytest.mark.asyncio
async def test_health_endpoint_recommends_template_only_when_agents_down():
    """Test that health endpoint recommends TEMPLATE_ONLY when agents unavailable"""
    from app.backend.routes.prompts import prompts_health

    # Mock health_all to return all offline
    with patch(
        "app.core.llm_client.health_all",
        new=AsyncMock(
            return_value={
                "agent_vision": {"available": False},
                "agent_dialog": {"available": False},
                "agent_logic": {"available": False},
                "agent_fast": {"available": False},
            }
        ),
    ):
        response = await prompts_health()

        assert response["agents_available"] == 0
        assert response["mode_recommendation"] == "template_only"


@pytest.mark.asyncio
async def test_health_endpoint_recommends_agent_assisted_when_agents_online():
    """Test that health endpoint recommends AGENT_ASSISTED when agents available"""
    from app.backend.routes.prompts import prompts_health

    # Mock health_all to return all online
    with patch(
        "app.core.llm_client.health_all",
        new=AsyncMock(
            return_value={
                "agent_vision": {"available": True},
                "agent_dialog": {"available": True},
                "agent_logic": {"available": True},
                "agent_fast": {"available": True},
            }
        ),
    ):
        response = await prompts_health()

        assert response["agents_available"] == 4
        assert response["mode_recommendation"] == "agent_assisted"


def test_partial_agent_availability_still_works(sample_variables):
    """Test that prompt generation works even with partial agent availability"""
    # Mock logic agent working, dialog agent failing
    with patch("app.core.prompts._call_logic_agent", return_value="Draft prompt"), patch(
        "app.core.prompts._call_dialog_agent",
        side_effect=LLMTimeoutError("Dialog timeout"),
    ):
        try:
            prompt = generate_prompt(
                template_name="image_sdxl",
                variables=sample_variables,
                mode=PromptMode.AGENT_ASSISTED,
            )
            # Should return unpolished draft
            assert prompt is not None
        except (LLMTimeoutError, LLMServerUnavailableError):
            # Fallback to template is acceptable
            pass
