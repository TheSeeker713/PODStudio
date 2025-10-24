"""
Hardware Policy Engine
Enforce guardrails for LLM usage, media processing, and resource allocation.
"""

from enum import Enum
from typing import Literal

from app.core.probe import probe_hardware


class PolicyDecision(str, Enum):
    """Policy decision outcomes."""

    ALLOW = "ALLOW"
    ALLOW_WITH_WARNING = "ALLOW_WITH_WARNING"
    DOWNGRADE_AGENT = "DOWNGRADE_AGENT"
    BLOCK = "BLOCK"


class LLMPolicy:
    """
    Policy engine for LLM agent routing and resource management.

    Rules:
    1. If RAM < 12 GB free OR CPU > 75% sustained:
       - Prefer A4 (fast) for summarize/keywords
       - Limit to single call
       - Disable A1 (vision)
    2. If no vision workload present → never spawn A1
    3. If ctx-size requested > model ctx → truncate with notice
    4. Global cap: max 3 agent calls per "Generate" action
    """

    # Thresholds
    RAM_LOW_THRESHOLD_GB = 12.0
    CPU_HIGH_THRESHOLD_PERCENT = 75.0
    MAX_AGENT_CALLS_PER_ACTION = 3
    MAX_CONTEXT_SIZE = 8192  # Conservative default for Q5_K_M models

    def __init__(self):
        self.hardware = probe_hardware()

    def refresh_hardware(self):
        """Re-probe hardware for updated metrics."""
        self.hardware = probe_hardware()

    def evaluate_llm_request(
        self,
        agent_type: Literal["vision", "logic", "dialog", "fast"],
        context_size: int = 2048,
        has_vision_workload: bool = False,
    ) -> tuple[PolicyDecision, str]:
        """
        Evaluate a single LLM agent request against current hardware state.

        Args:
            agent_type: Which agent is being requested (A1/A2/A3/A4)
            context_size: Requested context window size
            has_vision_workload: Whether vision analysis is needed

        Returns:
            (PolicyDecision, message: str)
        """
        ram_available = self.hardware["ram_available_gb"]
        cpu_load = self.hardware["cpu_load_percent"]
        llm_budget = self.hardware["llm_budget"]

        # Rule 1: Vision agent (A1) restrictions
        if agent_type == "vision":
            if not has_vision_workload:
                return (
                    PolicyDecision.BLOCK,
                    "Vision agent blocked: No vision workload present.",
                )
            if ram_available < self.RAM_LOW_THRESHOLD_GB:
                return (
                    PolicyDecision.BLOCK,
                    f"Vision agent blocked: Low RAM ({ram_available:.1f}GB < {self.RAM_LOW_THRESHOLD_GB}GB).",
                )
            if cpu_load > self.CPU_HIGH_THRESHOLD_PERCENT:
                return (
                    PolicyDecision.BLOCK,
                    f"Vision agent blocked: High CPU load ({cpu_load:.1f}% > {self.CPU_HIGH_THRESHOLD_PERCENT}%).",
                )

        # Rule 2: Resource-constrained downgrade
        if (ram_available < self.RAM_LOW_THRESHOLD_GB or cpu_load > self.CPU_HIGH_THRESHOLD_PERCENT) and agent_type in [
            "logic",
            "dialog",
        ]:
            return (
                PolicyDecision.DOWNGRADE_AGENT,
                f"Downgraded to FAST agent due to system constraints (RAM: {ram_available:.1f}GB, CPU: {cpu_load:.1f}%).",
            )

        # Rule 3: Context size validation
        if context_size > self.MAX_CONTEXT_SIZE:
            return (
                PolicyDecision.ALLOW_WITH_WARNING,
                f"Context size truncated from {context_size} to {self.MAX_CONTEXT_SIZE} tokens.",
            )

        # Rule 4: Low budget warning
        if llm_budget == "LOW" and agent_type in ["logic", "dialog"]:
            return (
                PolicyDecision.ALLOW_WITH_WARNING,
                f"LLM Budget is LOW ({self.hardware['llm_tokens_per_sec_estimate']} tokens/sec). Expect slow inference.",
            )

        return (PolicyDecision.ALLOW, "Request approved.")

    def plan_agent_pipeline(
        self,
        requested_agents: list[Literal["vision", "logic", "dialog", "fast"]],
        has_vision_workload: bool = False,
    ) -> tuple[list[str], list[str]]:
        """
        Plan an agent execution pipeline with guardrails applied.

        Args:
            requested_agents: List of agent types requested (e.g., ["vision", "logic", "dialog", "fast"])
            has_vision_workload: Whether vision analysis is needed

        Returns:
            (approved_agents: list[str], warnings: list[str])
        """
        approved_agents = []
        warnings = []
        ram_available = self.hardware["ram_available_gb"]
        cpu_load = self.hardware["cpu_load_percent"]

        # Apply global cap
        if len(requested_agents) > self.MAX_AGENT_CALLS_PER_ACTION:
            warnings.append(
                f"Agent pipeline limited to {self.MAX_AGENT_CALLS_PER_ACTION} calls (requested: {len(requested_agents)})."
            )
            requested_agents = requested_agents[: self.MAX_AGENT_CALLS_PER_ACTION]

        # Evaluate each agent
        for agent in requested_agents:
            decision, message = self.evaluate_llm_request(agent, has_vision_workload=has_vision_workload)

            if decision == PolicyDecision.ALLOW:
                approved_agents.append(agent)
            elif decision == PolicyDecision.ALLOW_WITH_WARNING:
                approved_agents.append(agent)
                warnings.append(message)
            elif decision == PolicyDecision.DOWNGRADE_AGENT:
                approved_agents.append("fast")
                warnings.append(message)
            elif decision == PolicyDecision.BLOCK:
                warnings.append(message)

        # Special case: If we're resource-constrained, limit to 1 call
        if (ram_available < self.RAM_LOW_THRESHOLD_GB or cpu_load > self.CPU_HIGH_THRESHOLD_PERCENT) and len(
            approved_agents
        ) > 1:
            warnings.append(
                f"Limited to single agent call due to resource constraints (RAM: {ram_available:.1f}GB, CPU: {cpu_load:.1f}%)."
            )
            approved_agents = approved_agents[:1]

        return approved_agents, warnings

    def get_llm_budget_display(self) -> dict:
        """
        Get user-friendly LLM budget display info.

        Returns:
            dict with keys: level, tokens_per_sec, color, description
        """
        budget = self.hardware["llm_budget"]
        tokens_per_sec = self.hardware["llm_tokens_per_sec_estimate"]

        color_map = {
            "LOW": "#ff6b6b",  # Red
            "MEDIUM": "#ffa500",  # Orange
            "HIGH": "#51cf66",  # Green
        }

        description_map = {
            "LOW": "Limited inference speed. Consider using FAST agent only.",
            "MEDIUM": "Moderate inference speed. Multi-agent workflows supported.",
            "HIGH": "Excellent inference speed. All workflows supported.",
        }

        return {
            "level": budget,
            "tokens_per_sec": tokens_per_sec,
            "color": color_map[budget],
            "description": description_map[budget],
        }
