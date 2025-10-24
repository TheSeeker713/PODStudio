"""
Unit tests for LLM policy engine.
Tests the matrix of hardware states vs. policy decisions.
"""

from unittest.mock import patch

import pytest

from app.core.policy import LLMPolicy, PolicyDecision


@pytest.fixture
def mock_hardware_high():
    """Mock hardware with high resources (GREEN tier)."""
    return {
        "gpu_name": "NVIDIA RTX 3090",
        "vram_gb": 24.0,
        "cpu_cores_logical": 16,
        "cpu_cores_physical": 8,
        "cpu_load_percent": 25.0,
        "ram_total_gb": 32.0,
        "ram_available_gb": 20.0,
        "ram_percent_used": 37.5,
        "llm_budget": "HIGH",
        "llm_tokens_per_sec_estimate": 20,
        "tier": "GREEN",
    }


@pytest.fixture
def mock_hardware_medium():
    """Mock hardware with medium resources (YELLOW tier)."""
    return {
        "gpu_name": "None",
        "vram_gb": 0.0,
        "cpu_cores_logical": 8,
        "cpu_cores_physical": 4,
        "cpu_load_percent": 50.0,
        "ram_total_gb": 16.0,
        "ram_available_gb": 10.0,
        "ram_percent_used": 37.5,
        "llm_budget": "MEDIUM",
        "llm_tokens_per_sec_estimate": 8,
        "tier": "YELLOW",
    }


@pytest.fixture
def mock_hardware_low():
    """Mock hardware with low resources (RED tier)."""
    return {
        "gpu_name": "None",
        "vram_gb": 0.0,
        "cpu_cores_logical": 4,
        "cpu_cores_physical": 2,
        "cpu_load_percent": 85.0,
        "ram_total_gb": 8.0,
        "ram_available_gb": 3.0,
        "ram_percent_used": 62.5,
        "llm_budget": "LOW",
        "llm_tokens_per_sec_estimate": 2,
        "tier": "RED",
    }


class TestLLMPolicyVisionAgent:
    """Test vision agent (A1) policy decisions."""

    @patch("app.core.policy.probe_hardware")
    def test_vision_allowed_with_high_resources(self, mock_probe, mock_hardware_high):
        """Vision agent allowed when resources are high and workload present."""
        mock_probe.return_value = mock_hardware_high
        policy = LLMPolicy()

        decision, message = policy.evaluate_llm_request(agent_type="vision", has_vision_workload=True)

        assert decision == PolicyDecision.ALLOW
        assert "approved" in message.lower()

    @patch("app.core.policy.probe_hardware")
    def test_vision_blocked_no_workload(self, mock_probe, mock_hardware_high):
        """Vision agent blocked when no vision workload present."""
        mock_probe.return_value = mock_hardware_high
        policy = LLMPolicy()

        decision, message = policy.evaluate_llm_request(agent_type="vision", has_vision_workload=False)

        assert decision == PolicyDecision.BLOCK
        assert "no vision workload" in message.lower()

    @patch("app.core.policy.probe_hardware")
    def test_vision_blocked_low_ram(self, mock_probe, mock_hardware_low):
        """Vision agent blocked when RAM < 12GB."""
        mock_probe.return_value = mock_hardware_low
        policy = LLMPolicy()

        decision, message = policy.evaluate_llm_request(agent_type="vision", has_vision_workload=True)

        assert decision == PolicyDecision.BLOCK
        assert "low ram" in message.lower()

    @patch("app.core.policy.probe_hardware")
    def test_vision_blocked_high_cpu(self, mock_probe, mock_hardware_high):
        """Vision agent blocked when CPU load > 75%."""
        mock_hardware_high["cpu_load_percent"] = 85.0
        mock_probe.return_value = mock_hardware_high
        policy = LLMPolicy()

        decision, message = policy.evaluate_llm_request(agent_type="vision", has_vision_workload=True)

        assert decision == PolicyDecision.BLOCK
        assert "high cpu" in message.lower()


class TestLLMPolicyResourceConstraints:
    """Test resource-based downgrade and warning policies."""

    @patch("app.core.policy.probe_hardware")
    def test_logic_downgrade_low_ram(self, mock_probe, mock_hardware_low):
        """Logic agent downgraded to fast when RAM < 12GB."""
        mock_probe.return_value = mock_hardware_low
        policy = LLMPolicy()

        decision, message = policy.evaluate_llm_request(agent_type="logic")

        assert decision == PolicyDecision.DOWNGRADE_AGENT
        assert "downgraded to fast" in message.lower()
        assert "ram" in message.lower()

    @patch("app.core.policy.probe_hardware")
    def test_dialog_downgrade_high_cpu(self, mock_probe, mock_hardware_medium):
        """Dialog agent downgraded to fast when CPU > 75%."""
        mock_hardware_medium["cpu_load_percent"] = 80.0
        mock_hardware_medium["ram_available_gb"] = 14.0  # RAM OK
        mock_probe.return_value = mock_hardware_medium
        policy = LLMPolicy()

        decision, message = policy.evaluate_llm_request(agent_type="dialog")

        assert decision == PolicyDecision.DOWNGRADE_AGENT
        assert "downgraded to fast" in message.lower()
        assert "cpu" in message.lower()

    @patch("app.core.policy.probe_hardware")
    def test_fast_agent_always_allowed(self, mock_probe, mock_hardware_low):
        """Fast agent always allowed even under constraints."""
        mock_probe.return_value = mock_hardware_low
        policy = LLMPolicy()

        decision, message = policy.evaluate_llm_request(agent_type="fast")

        assert decision in [PolicyDecision.ALLOW, PolicyDecision.ALLOW_WITH_WARNING]


class TestLLMPolicyContextSize:
    """Test context size validation."""

    @patch("app.core.policy.probe_hardware")
    def test_context_size_truncated(self, mock_probe, mock_hardware_high):
        """Context size truncated when exceeding MAX_CONTEXT_SIZE."""
        mock_probe.return_value = mock_hardware_high
        policy = LLMPolicy()

        decision, message = policy.evaluate_llm_request(agent_type="logic", context_size=16384)

        assert decision == PolicyDecision.ALLOW_WITH_WARNING
        assert "truncated" in message.lower()
        assert "8192" in message

    @patch("app.core.policy.probe_hardware")
    def test_context_size_within_limit(self, mock_probe, mock_hardware_high):
        """Context size accepted when within limits."""
        mock_probe.return_value = mock_hardware_high
        policy = LLMPolicy()

        decision, message = policy.evaluate_llm_request(agent_type="logic", context_size=4096)

        assert decision == PolicyDecision.ALLOW


class TestLLMPolicyPipeline:
    """Test agent pipeline planning with guardrails."""

    @patch("app.core.policy.probe_hardware")
    def test_pipeline_all_approved_high_resources(self, mock_probe, mock_hardware_high):
        """All agents approved when resources are high."""
        mock_probe.return_value = mock_hardware_high
        policy = LLMPolicy()

        approved, warnings = policy.plan_agent_pipeline(["vision", "logic", "dialog"], has_vision_workload=True)

        assert len(approved) == 3
        assert "vision" in approved
        assert "logic" in approved
        assert "dialog" in approved

    @patch("app.core.policy.probe_hardware")
    def test_pipeline_limited_to_max_calls(self, mock_probe, mock_hardware_high):
        """Pipeline limited to MAX_AGENT_CALLS_PER_ACTION."""
        mock_probe.return_value = mock_hardware_high
        policy = LLMPolicy()

        approved, warnings = policy.plan_agent_pipeline(["vision", "logic", "dialog", "fast"], has_vision_workload=True)

        assert len(approved) == 3  # MAX_AGENT_CALLS_PER_ACTION
        assert len(warnings) == 1
        assert "limited to 3" in warnings[0].lower()

    @patch("app.core.policy.probe_hardware")
    def test_pipeline_single_call_low_resources(self, mock_probe, mock_hardware_low):
        """Pipeline limited to 1 call when resources are low."""
        mock_probe.return_value = mock_hardware_low
        policy = LLMPolicy()

        approved, warnings = policy.plan_agent_pipeline(["logic", "dialog"], has_vision_workload=False)

        assert len(approved) == 1
        assert approved[0] == "fast"  # Downgraded
        assert any("single agent call" in w.lower() for w in warnings)

    @patch("app.core.policy.probe_hardware")
    def test_pipeline_vision_removed_no_workload(self, mock_probe, mock_hardware_high):
        """Vision agent removed when no workload present."""
        mock_probe.return_value = mock_hardware_high
        policy = LLMPolicy()

        approved, warnings = policy.plan_agent_pipeline(["vision", "logic"], has_vision_workload=False)

        assert "vision" not in approved
        assert any("vision agent blocked" in w.lower() for w in warnings)

    @patch("app.core.policy.probe_hardware")
    def test_pipeline_downgrades_to_fast(self, mock_probe, mock_hardware_low):
        """Logic and dialog agents downgraded to fast under constraints."""
        mock_probe.return_value = mock_hardware_low
        policy = LLMPolicy()

        approved, warnings = policy.plan_agent_pipeline(["logic", "dialog"], has_vision_workload=False)

        # Should have downgrades
        assert approved.count("fast") > 0
        assert any("downgraded" in w.lower() for w in warnings)


class TestLLMBudgetDisplay:
    """Test LLM budget display information."""

    @patch("app.core.policy.probe_hardware")
    def test_budget_display_high(self, mock_probe, mock_hardware_high):
        """High budget displays correctly."""
        mock_probe.return_value = mock_hardware_high
        policy = LLMPolicy()

        display = policy.get_llm_budget_display()

        assert display["level"] == "HIGH"
        assert display["tokens_per_sec"] == 20
        assert "#51cf66" in display["color"]  # Green
        assert "excellent" in display["description"].lower()

    @patch("app.core.policy.probe_hardware")
    def test_budget_display_medium(self, mock_probe, mock_hardware_medium):
        """Medium budget displays correctly."""
        mock_probe.return_value = mock_hardware_medium
        policy = LLMPolicy()

        display = policy.get_llm_budget_display()

        assert display["level"] == "MEDIUM"
        assert display["tokens_per_sec"] == 8
        assert "#ffa500" in display["color"]  # Orange

    @patch("app.core.policy.probe_hardware")
    def test_budget_display_low(self, mock_probe, mock_hardware_low):
        """Low budget displays correctly."""
        mock_probe.return_value = mock_hardware_low
        policy = LLMPolicy()

        display = policy.get_llm_budget_display()

        assert display["level"] == "LOW"
        assert display["tokens_per_sec"] == 2
        assert "#ff6b6b" in display["color"]  # Red
        assert "limited" in display["description"].lower()
