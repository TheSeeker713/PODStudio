"""
Prompt Template Engine v2 — Agent-Assisted + Zero-AI Fallback

STEP 8: Extends template-only mode with optional offline AI assistance.
- TEMPLATE_ONLY: Pure Jinja2 templates (zero-AI, always works)
- AGENT_ASSISTED: Calls offline LLM agents for drafting/polishing/analysis

Preserves backward compatibility: Zero-AI mode fully functional.
"""

import hashlib
import json
from enum import Enum
from pathlib import Path

from jinja2 import Environment, FileSystemLoader, TemplateNotFound
from loguru import logger

from app.core import llm_client


class PromptMode(str, Enum):
    """Prompt generation modes"""

    TEMPLATE_ONLY = "template_only"  # Pure template-based (zero-AI)
    AGENT_ASSISTED = "agent_assisted"  # Use offline agents


class PromptEngineError(Exception):
    """Base exception for prompt engine errors"""

    pass


class TemplateNotFoundError(PromptEngineError):
    """Raised when template file not found"""

    pass


class AgentTimeoutError(PromptEngineError):
    """Raised when agent call times out"""

    pass


# Template directories
TEMPLATE_DIR = Path(__file__).parent.parent.parent / "docs" / "prompt_templates"

# Jinja2 environment
_jinja_env = Environment(
    loader=FileSystemLoader(str(TEMPLATE_DIR)),
    autoescape=False,  # Prompts are plain text
    trim_blocks=True,
    lstrip_blocks=True,
)


def generate_prompt(
    template_name: str,
    variables: dict,
    mode: PromptMode = PromptMode.TEMPLATE_ONLY,
) -> str:
    """
    Generate prompt from template

    Args:
        template_name: Template ID (e.g., 'image_sdxl')
        variables: Dict of variables to substitute
        mode: PromptMode enum (TEMPLATE_ONLY or AGENT_ASSISTED)

    Returns:
        Rendered prompt string

    Raises:
        TemplateNotFoundError: If template file not found
    """
    if mode == PromptMode.TEMPLATE_ONLY:
        return _generate_template_only(template_name, variables)
    elif mode == PromptMode.AGENT_ASSISTED:
        return _generate_agent_assisted(template_name, variables)
    else:
        raise PromptEngineError(f"Unknown mode: {mode}")


def _generate_template_only(template_name: str, variables: dict) -> str:
    """
    Generate prompt using pure template substitution (zero-AI)

    Args:
        template_name: Template file name (e.g., 'image_sdxl')
        variables: Variables to substitute

    Returns:
        Rendered prompt string
    """
    template_file = f"{template_name}.txt"

    try:
        # Load template sections (templates have markdown structure)
        template_path = TEMPLATE_DIR / template_file
        if not template_path.exists():
            raise TemplateNotFoundError(f"Template not found: {template_file}")

        # Parse template file for the actual template string
        # Template files have a ## Template section with the template
        template_content = template_path.read_text(encoding="utf-8")

        # Extract template string from markdown
        template_string = _extract_template_from_markdown(template_content)

        # Render with Jinja2
        template = _jinja_env.from_string(template_string)
        rendered = template.render(**variables)

        return rendered.strip()

    except TemplateNotFound as e:
        raise TemplateNotFoundError(f"Template not found: {template_file}") from e


def _extract_template_from_markdown(content: str) -> str:
    """
    Extract template string from markdown template file

    Template files have structure:
    ## Template
    ```
    {{variable1}}, {{variable2}}, ...
    ```

    Args:
        content: Raw markdown content

    Returns:
        Template string (without markdown wrapper)
    """
    lines = content.split("\n")
    in_template_section = False
    in_code_block = False
    template_lines = []

    for line in lines:
        # Look for ## Template section
        if line.strip().startswith("## Template"):
            in_template_section = True
            continue

        # Look for next ## section (end of template)
        if in_template_section and line.strip().startswith("##"):
            break

        # Look for code block markers
        if in_template_section and line.strip().startswith("```"):
            if not in_code_block:
                in_code_block = True
                continue
            else:
                # End of template code block
                break

        # Collect template lines
        if in_template_section and in_code_block:
            template_lines.append(line)

    if not template_lines:
        # Fallback: use simple variable substitution
        return "{{subject}}, {{style}}, {{mood}}, {{composition}}, {{lighting}}, {{details}}"

    return "\n".join(template_lines)


def _generate_agent_assisted(template_name: str, variables: dict) -> str:
    """
    Generate prompt with offline agent assistance

    Flow:
    1. If reference_image provided → agent_vision for analysis
    2. agent_logic for structured draft
    3. agent_dialog for fluency polish
    4. Fallback to TEMPLATE_ONLY on timeout/error

    Args:
        template_name: Template file name
        variables: Variables including optional 'reference_image' path

    Returns:
        Agent-enhanced prompt string
    """
    logger.info(f"[Prompt] Agent-assisted generation for {template_name}")

    try:
        # Extract reference image if provided
        reference_image = variables.get("reference_image")

        # Step 1: Vision analysis (if image provided)
        vision_context = ""
        if reference_image:
            logger.info(f"[Prompt] Analyzing reference image: {reference_image}")
            vision_context = _call_vision_agent(reference_image, template_name)

        # Step 2: Logic agent for structured draft
        logger.info("[Prompt] Calling logic agent for draft")
        draft = _call_logic_agent(template_name, variables, vision_context)

        # Step 3: Dialog agent for fluency polish
        logger.info("[Prompt] Calling dialog agent for polish")
        polished = _call_dialog_agent(draft, template_name)

        return polished

    except (AgentTimeoutError, llm_client.LLMTimeoutError, llm_client.LLMServerUnavailableError) as e:
        logger.warning(f"[Prompt] Agent call failed, falling back to template-only: {e}")
        # Fallback to template-only mode
        return _generate_template_only(template_name, variables)


def _call_vision_agent(image_path: str, template_name: str) -> str:
    """
    Call agent_vision for image analysis

    Args:
        image_path: Path to reference image
        template_name: Target template (for context)

    Returns:
        Vision analysis text (descriptors, tags, composition notes)
    """
    import asyncio

    async def _vision_call():
        messages = [
            {
                "role": "system",
                "content": f"You are analyzing an image to generate prompt ideas for {template_name}. Describe the key visual elements, composition, style, mood, and details.",
            },
            {
                "role": "user",
                "content": "Analyze this image and provide descriptive tags for prompt generation.",
            },
        ]

        try:
            result = await llm_client.vision_chat(
                agent_id="agent_vision",
                messages=messages,
                image_path=Path(image_path),
                temperature=0.7,
                max_tokens=256,
            )
            return result.get("content", "")
        except Exception as e:
            logger.error(f"[Prompt] Vision agent error: {e}")
            return ""

    return asyncio.run(_vision_call())


def _call_logic_agent(template_name: str, variables: dict, vision_context: str = "") -> str:
    """
    Call agent_logic for structured prompt draft

    Args:
        template_name: Target template name
        variables: User variables (theme, style, etc.)
        vision_context: Optional vision analysis text

    Returns:
        Structured prompt draft
    """
    import asyncio

    async def _logic_call():
        # Build context for logic agent
        var_text = ", ".join([f"{k}: {v}" for k, v in variables.items() if k != "reference_image"])

        context_parts = [f"Template: {template_name}", f"Variables: {var_text}"]

        if vision_context:
            context_parts.append(f"Image analysis: {vision_context}")

        system_prompt = f"""You are drafting a prompt for {template_name}.
Create a structured, detailed prompt using the provided variables.
Focus on clarity, specificity, and completeness."""

        user_prompt = "\n".join(context_parts) + "\n\nGenerate the prompt:"

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ]

        try:
            result = await llm_client.chat(
                agent_id="agent_logic",
                messages=messages,
                temperature=0.6,
                max_tokens=512,
            )
            return result.get("content", "").strip()
        except Exception as e:
            logger.error(f"[Prompt] Logic agent error: {e}")
            raise AgentTimeoutError(f"Logic agent failed: {e}") from e

    return asyncio.run(_logic_call())


def _call_dialog_agent(draft: str, template_name: str) -> str:
    """
    Call agent_dialog for fluency polish

    Args:
        draft: Draft prompt text
        template_name: Target template (for context)

    Returns:
        Polished prompt
    """
    import asyncio

    async def _dialog_call():
        system_prompt = f"""You are polishing a prompt for {template_name}.
Improve fluency, remove passive voice, enhance descriptive language.
Keep the core meaning intact."""

        user_prompt = f"Polish this prompt:\n\n{draft}"

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ]

        try:
            result = await llm_client.chat(
                agent_id="agent_dialog",
                messages=messages,
                temperature=0.7,
                max_tokens=512,
            )
            return result.get("content", "").strip()
        except Exception as e:
            logger.error(f"[Prompt] Dialog agent error: {e}")
            # Return draft as fallback
            return draft

    return asyncio.run(_dialog_call())


def generate_keywords(text: str) -> list[str]:
    """
    Generate keywords/tags from text using agent_fast

    Args:
        text: Input text (e.g., prompt or description)

    Returns:
        List of keyword strings
    """
    import asyncio

    async def _keywords_call():
        messages = [
            {
                "role": "system",
                "content": "Extract 5-10 relevant keywords/tags from the text. Return comma-separated list.",
            },
            {"role": "user", "content": text},
        ]

        try:
            result = await llm_client.chat(
                agent_id="agent_fast",
                messages=messages,
                temperature=0.3,
                max_tokens=128,
            )
            content = result.get("content", "").strip()
            # Parse comma-separated keywords
            keywords = [k.strip() for k in content.split(",") if k.strip()]
            return keywords
        except Exception as e:
            logger.error(f"[Prompt] Fast agent error (keywords): {e}")
            return []

    return asyncio.run(_keywords_call())


def generate_negative_prompt(template_name: str, variables: dict) -> str:
    """
    Generate negative prompt for given template

    Args:
        template_name: Template name (e.g., 'image_sdxl')
        variables: Variables (may include style hints)

    Returns:
        Negative prompt string
    """
    # Default negatives by template type
    negative_defaults = {
        "image_sdxl": "cartoon, anime, sketch, blurry, low quality, jpeg artifacts, watermark, deformed, distorted, text, signature",
        "image_midjourney": "blurry, low resolution, distorted, deformed, watermark, text",
        "audio_suno": "distorted, clipping, noise, static, poor quality",
        "audio_elevenlabs": "robotic, monotone, muffled, distorted",
        "video_kling": "blurry, low framerate, artifacts, compression, watermark",
        "video_sora": "distorted motion, artifacts, low quality, flickering",
    }

    return negative_defaults.get(template_name, "low quality, artifacts, distorted")


def generate_variants(base_prompt: str, count: int = 3) -> list[str]:
    """
    Generate prompt variants using agent_dialog

    Args:
        base_prompt: Base prompt to create variants from
        count: Number of variants to generate

    Returns:
        List of variant prompts
    """
    import asyncio

    async def _variants_call():
        variants = []

        for i in range(count):
            messages = [
                {
                    "role": "system",
                    "content": f"Create variant {i+1} of this prompt. Keep core meaning but vary word choice, emphasis, and style.",
                },
                {"role": "user", "content": base_prompt},
            ]

            try:
                result = await llm_client.chat(
                    agent_id="agent_dialog",
                    messages=messages,
                    temperature=0.8 + (i * 0.1),  # Increase temperature per variant
                    max_tokens=512,
                )
                variant = result.get("content", "").strip()
                if variant:
                    variants.append(variant)
            except Exception as e:
                logger.error(f"[Prompt] Variant {i+1} generation failed: {e}")
                # Add slight variation to base prompt as fallback
                variants.append(f"{base_prompt} (variant {i+1})")

        return variants

    return asyncio.run(_variants_call())


def save_prompt_artifact(
    session_id: str,
    prompt: str,
    negative_prompt: str,
    template_name: str,
    variables: dict,
    mode: PromptMode,
    reference_image: str | None = None,
    agent_lineage: list[str] | None = None,
) -> Path:
    """
    Save prompt generation artifact to disk

    Args:
        session_id: Session identifier
        prompt: Final generated prompt
        negative_prompt: Negative prompt
        template_name: Template used
        variables: Input variables
        mode: PromptMode used
        reference_image: Optional reference image path
        agent_lineage: List of agents used (e.g., ["agent_vision", "agent_logic", "agent_dialog"])

    Returns:
        Path to saved artifact file
    """
    # Artifact structure
    artifact = {
        "session_id": session_id,
        "timestamp": _current_timestamp(),
        "mode": mode.value,
        "template": template_name,
        "prompt": prompt,
        "negative_prompt": negative_prompt,
        "variables": variables,
        "agent_lineage": agent_lineage or [],
        "reference_image": reference_image,
        "reference_image_hash": _hash_file(reference_image) if reference_image else None,
    }

    # Save to Work/prompts/<session_id>.json
    work_dir = Path(__file__).parent.parent.parent / "Work" / "prompts"
    work_dir.mkdir(parents=True, exist_ok=True)

    artifact_path = work_dir / f"{session_id}.json"

    with artifact_path.open("w", encoding="utf-8") as f:
        json.dump(artifact, f, indent=2)

    logger.info(f"[Prompt] Saved artifact: {artifact_path}")

    return artifact_path


def _current_timestamp() -> str:
    """Get current ISO timestamp"""
    from datetime import datetime

    return datetime.utcnow().isoformat() + "Z"


def _hash_file(file_path: str | Path) -> str:
    """Compute SHA256 hash of file"""
    hasher = hashlib.sha256()
    path = Path(file_path)

    if not path.exists():
        return ""

    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            hasher.update(chunk)

    return hasher.hexdigest()[:16]  # First 16 chars
