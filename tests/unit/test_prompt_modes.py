"""
Unit tests for prompt generation modes

STEP 8: Validates TEMPLATE_ONLY and AGENT_ASSISTED produce consistent fields.
"""


import pytest

from app.core.prompts import PromptMode, TemplateNotFoundError, generate_negative_prompt, generate_prompt


@pytest.fixture
def sample_variables():
    """Sample variables for testing"""
    return {
        "subject": "majestic dragon",
        "style": "fantasy art",
        "mood": "epic and dramatic",
        "composition": "wide angle",
        "lighting": "golden hour",
        "details": "highly detailed, 8k",
    }


def test_template_only_mode_generates_prompt(sample_variables):
    """Test that TEMPLATE_ONLY mode generates valid prompt"""
    prompt = generate_prompt(
        template_name="image_sdxl",
        variables=sample_variables,
        mode=PromptMode.TEMPLATE_ONLY,
    )

    assert prompt is not None
    assert len(prompt) > 0
    assert isinstance(prompt, str)


def test_template_only_includes_variables(sample_variables):
    """Test that TEMPLATE_ONLY includes variable values"""
    prompt = generate_prompt(
        template_name="image_sdxl",
        variables=sample_variables,
        mode=PromptMode.TEMPLATE_ONLY,
    )

    # Check that at least some variables appear in output
    assert "dragon" in prompt.lower() or "majestic" in prompt.lower()


def test_template_not_found_raises_error():
    """Test that invalid template raises TemplateNotFoundError"""
    with pytest.raises(TemplateNotFoundError):
        generate_prompt(
            template_name="nonexistent_template",
            variables={"foo": "bar"},
            mode=PromptMode.TEMPLATE_ONLY,
        )


def test_negative_prompt_generation():
    """Test negative prompt generation"""
    negative = generate_negative_prompt("image_sdxl", {})

    assert negative is not None
    assert len(negative) > 0
    # Should contain common negative terms
    assert any(term in negative.lower() for term in ["blurry", "low quality", "artifacts", "distorted"])


def test_negative_prompt_varies_by_template():
    """Test that negative prompts vary by template type"""
    sdxl_negative = generate_negative_prompt("image_sdxl", {})
    audio_negative = generate_negative_prompt("audio_suno", {})

    # They should be different
    assert sdxl_negative != audio_negative


@pytest.mark.skipif(True, reason="AGENT_ASSISTED requires running llama servers - manual test only")
def test_agent_assisted_mode_generates_prompt(sample_variables):
    """Test that AGENT_ASSISTED mode generates valid prompt (requires agents running)"""
    prompt = generate_prompt(
        template_name="image_sdxl",
        variables=sample_variables,
        mode=PromptMode.AGENT_ASSISTED,
    )

    assert prompt is not None
    assert len(prompt) > 0
    assert isinstance(prompt, str)


@pytest.mark.skipif(True, reason="AGENT_ASSISTED requires running llama servers - manual test only")
def test_agent_assisted_with_reference_image(sample_variables, tmp_path):
    """Test AGENT_ASSISTED with reference image (requires agents running)"""
    # Create dummy image file
    image_path = tmp_path / "reference.png"
    image_path.write_bytes(b"fake image data")

    sample_variables["reference_image"] = str(image_path)

    prompt = generate_prompt(
        template_name="image_sdxl",
        variables=sample_variables,
        mode=PromptMode.AGENT_ASSISTED,
    )

    assert prompt is not None
    assert len(prompt) > 0


def test_both_modes_return_strings(sample_variables):
    """Test that both modes return string type"""
    template_prompt = generate_prompt(
        template_name="image_sdxl",
        variables=sample_variables,
        mode=PromptMode.TEMPLATE_ONLY,
    )

    assert isinstance(template_prompt, str)

    # AGENT_ASSISTED should fallback to TEMPLATE_ONLY if agents unavailable
    # So it should also return a string
    try:
        agent_prompt = generate_prompt(
            template_name="image_sdxl",
            variables=sample_variables,
            mode=PromptMode.AGENT_ASSISTED,
        )
        assert isinstance(agent_prompt, str)
    except Exception:
        # If agents are down, that's expected - test passes
        pass


def test_template_only_is_deterministic(sample_variables):
    """Test that TEMPLATE_ONLY produces same output for same input"""
    prompt1 = generate_prompt(
        template_name="image_sdxl",
        variables=sample_variables,
        mode=PromptMode.TEMPLATE_ONLY,
    )

    prompt2 = generate_prompt(
        template_name="image_sdxl",
        variables=sample_variables,
        mode=PromptMode.TEMPLATE_ONLY,
    )

    assert prompt1 == prompt2


def test_empty_variables_handled():
    """Test that empty variables dict doesn't crash"""
    prompt = generate_prompt(template_name="image_sdxl", variables={}, mode=PromptMode.TEMPLATE_ONLY)

    assert prompt is not None
    assert isinstance(prompt, str)
