"""
Agent Router — Maps tasks to appropriate LLM agents

STEP 7: Route map for connecting prompt generation tasks to specific agents.
Implements orchestration logic for selecting the right model based on task type.
"""

from enum import Enum

from loguru import logger


class AgentTask(str, Enum):
    """Task types that can be routed to LLM agents"""

    # Prompt generation tasks
    PROMPT_DRAFT = "prompt-draft"  # Initial prompt creation
    PROMPT_FLUENCY_POLISH = "prompt-fluency-polish"  # Polish and refine language
    PROMPT_EXPAND = "prompt-expand"  # Add detail and context
    PROMPT_SIMPLIFY = "prompt-simplify"  # Simplify complex prompts

    # Vision tasks
    VISION_CAPTION = "vision-caption"  # Generate image caption
    VISION_DESCRIBE = "vision-describe"  # Detailed image description
    VISION_ANALYZE = "vision-analyze"  # Analyze image composition

    # Quick tasks
    FAST_SUMMARIZE = "fast-summarize"  # Quick text summary
    FAST_KEYWORDS = "fast-keywords"  # Extract keywords
    FAST_TAG = "fast-tag"  # Generate tags

    # Logic tasks
    LOGIC_PLAN = "logic-plan"  # Plan multi-step process
    LOGIC_REASON = "logic-reason"  # Logical reasoning
    LOGIC_STRUCTURE = "logic-structure"  # Structure information


# Task-to-Agent routing table
TASK_ROUTING: dict[AgentTask, str] = {
    # Prompt tasks → Logic agent (for drafting) or Dialog (for polish)
    AgentTask.PROMPT_DRAFT: "agent_logic",
    AgentTask.PROMPT_FLUENCY_POLISH: "agent_dialog",
    AgentTask.PROMPT_EXPAND: "agent_dialog",
    AgentTask.PROMPT_SIMPLIFY: "agent_dialog",
    # Vision tasks → Vision agent
    AgentTask.VISION_CAPTION: "agent_vision",
    AgentTask.VISION_DESCRIBE: "agent_vision",
    AgentTask.VISION_ANALYZE: "agent_vision",
    # Fast tasks → Fast agent
    AgentTask.FAST_SUMMARIZE: "agent_fast",
    AgentTask.FAST_KEYWORDS: "agent_fast",
    AgentTask.FAST_TAG: "agent_fast",
    # Logic tasks → Logic agent
    AgentTask.LOGIC_PLAN: "agent_logic",
    AgentTask.LOGIC_REASON: "agent_logic",
    AgentTask.LOGIC_STRUCTURE: "agent_logic",
}


# Fallback routing (if primary agent unavailable)
FALLBACK_ROUTING: dict[str, str | None] = {
    "agent_vision": "agent_fast",  # Vision → Fast (basic captions)
    "agent_dialog": "agent_fast",  # Dialog → Fast (simpler language)
    "agent_logic": "agent_fast",  # Logic → Fast (basic reasoning)
    "agent_fast": None,  # No fallback for Fast (it's the fallback)
}


def route_task(task: AgentTask) -> str:
    """
    Route task to appropriate agent

    Args:
        task: AgentTask enum value

    Returns:
        agent_id string (e.g., "agent_vision")

    Raises:
        ValueError: If task not found in routing table
    """
    agent_id = TASK_ROUTING.get(task)

    if not agent_id:
        logger.error(f"[Agent Router] Unknown task: {task}")
        raise ValueError(f"No agent mapping for task: {task}")

    logger.debug(f"[Agent Router] {task} → {agent_id}")
    return agent_id


def get_fallback_agent(primary_agent_id: str) -> str | None:
    """
    Get fallback agent if primary is unavailable

    Args:
        primary_agent_id: Primary agent identifier

    Returns:
        Fallback agent_id or None if no fallback
    """
    fallback = FALLBACK_ROUTING.get(primary_agent_id)

    if fallback:
        logger.info(f"[Agent Router] Fallback: {primary_agent_id} → {fallback} (primary unavailable)")

    return fallback


# Placeholder orchestration functions (not yet implemented)


async def execute_task(
    task: AgentTask,
    context: dict,
    fallback_enabled: bool = True,
) -> dict:
    """
    Execute task by routing to appropriate agent

    Args:
        task: Task type to execute
        context: Task-specific context (messages, images, etc.)
        fallback_enabled: Whether to use fallback agent on failure

    Returns:
        dict with result content and metadata

    Note:
        This is a placeholder. Actual implementation will call llm_client
        functions and handle fallback logic.
    """
    agent_id = route_task(task)

    # TODO: Call llm_client.chat() or vision_chat() based on task type
    # TODO: Handle fallback if primary agent unavailable
    # TODO: Return structured response

    logger.warning(f"[Agent Router] execute_task() not yet implemented (task={task}, agent={agent_id})")

    return {
        "success": False,
        "error": "Orchestration not yet implemented",
        "agent_id": agent_id,
        "task": task,
    }


async def prompt_draft(prompt_seed: str, style: str | None = None) -> str:
    """
    Generate initial prompt draft from seed text

    Args:
        prompt_seed: Initial idea or keywords
        style: Optional style guidance (e.g., "detailed", "concise")

    Returns:
        Generated prompt text

    Note:
        Placeholder. Will route to agent_logic with appropriate system prompt.
    """
    logger.warning("[Agent Router] prompt_draft() placeholder called")

    # TODO: Build messages with system prompt for drafting
    # TODO: Call execute_task(AgentTask.PROMPT_DRAFT, ...)
    # TODO: Return generated prompt

    return f"[PLACEHOLDER] Draft prompt for: {prompt_seed}"


async def prompt_polish(raw_prompt: str) -> str:
    """
    Polish and refine prompt for fluency

    Args:
        raw_prompt: Rough prompt text

    Returns:
        Polished prompt text

    Note:
        Placeholder. Will route to agent_dialog for fluency improvements.
    """
    logger.warning("[Agent Router] prompt_polish() placeholder called")

    # TODO: Build messages with polishing instructions
    # TODO: Call execute_task(AgentTask.PROMPT_FLUENCY_POLISH, ...)
    # TODO: Return polished prompt

    return f"[PLACEHOLDER] Polished: {raw_prompt}"


async def vision_caption(image_path: str, detail_level: str = "medium") -> str:
    """
    Generate caption for image

    Args:
        image_path: Path to image file
        detail_level: "brief", "medium", or "detailed"

    Returns:
        Generated caption text

    Note:
        Placeholder. Will route to agent_vision with image.
    """
    logger.warning("[Agent Router] vision_caption() placeholder called")

    # TODO: Call llm_client.vision_chat() with agent_vision
    # TODO: Adjust system prompt based on detail_level
    # TODO: Return caption

    return f"[PLACEHOLDER] Caption for: {image_path}"


async def quick_summarize(text: str, max_sentences: int = 3) -> str:
    """
    Quick text summary

    Args:
        text: Text to summarize
        max_sentences: Maximum sentences in summary

    Returns:
        Summary text

    Note:
        Placeholder. Will route to agent_fast for quick processing.
    """
    logger.warning("[Agent Router] quick_summarize() placeholder called")

    # TODO: Call execute_task(AgentTask.FAST_SUMMARIZE, ...)
    # TODO: Return summary

    return f"[PLACEHOLDER] Summary of {len(text)} chars"


async def extract_keywords(text: str, max_keywords: int = 10) -> list[str]:
    """
    Extract keywords from text

    Args:
        text: Text to analyze
        max_keywords: Maximum keywords to return

    Returns:
        List of keyword strings

    Note:
        Placeholder. Will route to agent_fast.
    """
    logger.warning("[Agent Router] extract_keywords() placeholder called")

    # TODO: Call execute_task(AgentTask.FAST_KEYWORDS, ...)
    # TODO: Parse response into list
    # TODO: Return keywords

    return ["placeholder", "keywords", "not", "implemented"]
