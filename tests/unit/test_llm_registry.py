"""
Unit tests for LLM registry configuration

STEP 7: Validates llm_registry.yaml loads correctly and contains all 4 agents.
"""

from pathlib import Path

import pytest
import yaml


@pytest.fixture
def registry_path():
    """Path to llm_registry.yaml"""
    return Path(__file__).parent.parent.parent / "app" / "core" / "llm_registry.yaml"


def test_registry_file_exists(registry_path):
    """Test that llm_registry.yaml file exists"""
    assert registry_path.exists(), f"Registry file not found: {registry_path}"


def test_registry_loads(registry_path):
    """Test that registry YAML loads without errors"""
    with registry_path.open() as f:
        config = yaml.safe_load(f)

    assert config is not None
    assert isinstance(config, dict)


def test_registry_has_agents_section(registry_path):
    """Test that registry has 'agents' section"""
    with registry_path.open() as f:
        config = yaml.safe_load(f)

    assert "agents" in config
    assert isinstance(config["agents"], dict)


def test_registry_has_four_agents(registry_path):
    """Test that registry defines exactly 4 agents"""
    with registry_path.open() as f:
        config = yaml.safe_load(f)

    agents = config["agents"]
    assert len(agents) == 4, f"Expected 4 agents, found {len(agents)}"


def test_registry_agent_ids(registry_path):
    """Test that all expected agent IDs are present"""
    with registry_path.open() as f:
        config = yaml.safe_load(f)

    agents = config["agents"]
    expected_ids = {"agent_vision", "agent_dialog", "agent_logic", "agent_fast"}
    actual_ids = set(agents.keys())

    assert actual_ids == expected_ids, f"Agent IDs mismatch. Expected: {expected_ids}, Got: {actual_ids}"


def test_agent_vision_config(registry_path):
    """Test agent_vision configuration"""
    with registry_path.open() as f:
        config = yaml.safe_load(f)

    vision = config["agents"]["agent_vision"]

    assert vision["id"] == "agent_vision"
    assert vision["purpose"]  # Has purpose description
    assert vision["model_name"] == "google/gemma-3-12b"
    assert "gemma-3-12b" in vision["model_path"]
    assert vision["mmproj_path"] is not None  # Vision agent needs mmproj
    assert vision["n_gpu_layers"] == 0  # CPU-only
    assert "vision" in vision["capabilities"] or "multimodal" in vision["capabilities"]


def test_agent_dialog_config(registry_path):
    """Test agent_dialog configuration"""
    with registry_path.open() as f:
        config = yaml.safe_load(f)

    dialog = config["agents"]["agent_dialog"]

    assert dialog["id"] == "agent_dialog"
    assert dialog["model_name"] == "discopop-zephyr-7b-gemma"
    assert "zephyr" in dialog["model_path"].lower()
    assert dialog["mmproj_path"] is None  # Dialog doesn't need vision
    assert dialog["n_gpu_layers"] == 0
    assert "dialog" in dialog["capabilities"] or "fluency" in dialog["capabilities"]


def test_agent_logic_config(registry_path):
    """Test agent_logic configuration"""
    with registry_path.open() as f:
        config = yaml.safe_load(f)

    logic = config["agents"]["agent_logic"]

    assert logic["id"] == "agent_logic"
    assert logic["model_name"] == "google/gemma-3n-e4b"
    assert "gemma" in logic["model_path"].lower()
    assert logic["n_gpu_layers"] == 0
    assert "logic" in logic["capabilities"] or "planning" in logic["capabilities"]


def test_agent_fast_config(registry_path):
    """Test agent_fast configuration"""
    with registry_path.open() as f:
        config = yaml.safe_load(f)

    fast = config["agents"]["agent_fast"]

    assert fast["id"] == "agent_fast"
    assert fast["model_name"] == "liquid/lfm2-1.2b"
    assert "liquid" in fast["model_path"].lower() or "lfm" in fast["model_path"].lower()
    assert fast["n_gpu_layers"] == 0
    assert fast["ctx_len"] <= 8192  # Fast agent should have smaller context
    assert "fast" in fast["capabilities"] or "fallback" in fast["capabilities"]


def test_all_agents_cpu_only(registry_path):
    """Test that all agents are configured for CPU-only (n_gpu_layers=0)"""
    with registry_path.open() as f:
        config = yaml.safe_load(f)

    agents = config["agents"]

    for agent_id, agent_config in agents.items():
        assert agent_config["n_gpu_layers"] == 0, f"Agent {agent_id} has n_gpu_layers != 0 (should be CPU-only)"


def test_all_agents_have_required_fields(registry_path):
    """Test that all agents have required configuration fields"""
    with registry_path.open() as f:
        config = yaml.safe_load(f)

    agents = config["agents"]
    required_fields = [
        "id",
        "purpose",
        "model_name",
        "model_path",
        "quantization",
        "ctx_len",
        "n_threads",
        "n_batch",
        "n_gpu_layers",
        "temperature",
        "top_p",
        "capabilities",
    ]

    for agent_id, agent_config in agents.items():
        for field in required_fields:
            assert field in agent_config, f"Agent {agent_id} missing required field: {field}"


def test_defaults_section_exists(registry_path):
    """Test that registry has defaults section"""
    with registry_path.open() as f:
        config = yaml.safe_load(f)

    assert "defaults" in config
    defaults = config["defaults"]

    # Check for expected default fields
    assert "timeout_seconds" in defaults
    assert "max_tokens" in defaults
    assert "stop_sequences" in defaults
