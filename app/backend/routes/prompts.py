"""
Prompt Generation API Routes

STEP 8: Endpoints for agent-assisted and template-only prompt generation.
"""

from typing import Any

from fastapi import APIRouter, HTTPException
from loguru import logger
from pydantic import BaseModel, Field

from app.core import llm_client
from app.core.prompts import (
    AgentTimeoutError,
    PromptEngineError,
    PromptMode,
    TemplateNotFoundError,
    generate_keywords,
    generate_negative_prompt,
    generate_prompt,
    generate_variants,
    save_prompt_artifact,
)

router = APIRouter(prefix="/api/prompts", tags=["prompts"])


class PromptGenerateRequest(BaseModel):
    """Request model for prompt generation"""

    template_name: str = Field(..., description="Template name (e.g., 'image_sdxl')")
    variables: dict[str, Any] = Field(..., description="Template variables")
    mode: PromptMode = Field(default=PromptMode.TEMPLATE_ONLY, description="Generation mode")
    reference_image: str | None = Field(default=None, description="Optional reference image path")


class PromptGenerateResponse(BaseModel):
    """Response model for prompt generation"""

    prompt: str
    negative_prompt: str
    template: str
    mode: str
    agent_lineage: list[str]
    keywords: list[str]


class PromptVariantsRequest(BaseModel):
    """Request model for generating prompt variants"""

    base_prompt: str = Field(..., description="Base prompt to create variants from")
    count: int = Field(default=3, ge=1, le=10, description="Number of variants")


class PromptVariantsResponse(BaseModel):
    """Response model for prompt variants"""

    base_prompt: str
    variants: list[str]
    count: int


class PromptPolishRequest(BaseModel):
    """Request model for prompt polishing"""

    draft: str = Field(..., description="Draft prompt to polish")
    template_name: str = Field(..., description="Target template name")


class PromptPolishResponse(BaseModel):
    """Response model for prompt polishing"""

    original: str
    polished: str


class PromptSaveRequest(BaseModel):
    """Request model for saving prompt artifact"""

    session_id: str
    prompt: str
    negative_prompt: str
    template_name: str
    variables: dict[str, Any]
    mode: PromptMode
    reference_image: str | None = None
    agent_lineage: list[str] | None = None


class PromptSaveResponse(BaseModel):
    """Response model for saving prompt"""

    artifact_path: str
    session_id: str


@router.post("/generate", response_model=PromptGenerateResponse)
async def generate_prompt_endpoint(request: PromptGenerateRequest):
    """
    Generate prompt from template

    Supports two modes:
    - TEMPLATE_ONLY: Pure template substitution (zero-AI)
    - AGENT_ASSISTED: Uses offline LLM agents for enhancement

    If reference_image provided, agent_vision will analyze it first.
    """
    try:
        # Add reference_image to variables if provided
        variables = request.variables.copy()
        if request.reference_image:
            variables["reference_image"] = request.reference_image

        # Generate prompt
        prompt = generate_prompt(
            template_name=request.template_name,
            variables=variables,
            mode=request.mode,
        )

        # Generate negative prompt
        negative_prompt = generate_negative_prompt(request.template_name, request.variables)

        # Track agent lineage for AGENT_ASSISTED mode
        agent_lineage = []
        if request.mode == PromptMode.AGENT_ASSISTED:
            if request.reference_image:
                agent_lineage.append("agent_vision")
            agent_lineage.extend(["agent_logic", "agent_dialog"])

        # Generate keywords
        keywords = []
        if request.mode == PromptMode.AGENT_ASSISTED:
            try:
                keywords = generate_keywords(prompt)
            except Exception as e:
                logger.warning(f"[Prompts API] Keyword generation failed: {e}")

        return PromptGenerateResponse(
            prompt=prompt,
            negative_prompt=negative_prompt,
            template=request.template_name,
            mode=request.mode.value,
            agent_lineage=agent_lineage,
            keywords=keywords,
        )

    except TemplateNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e)) from e
    except AgentTimeoutError as e:
        raise HTTPException(status_code=504, detail=f"Agent timeout: {e}") from e
    except PromptEngineError as e:
        raise HTTPException(status_code=500, detail=str(e)) from e


@router.post("/polish", response_model=PromptPolishResponse)
async def polish_prompt_endpoint(request: PromptPolishRequest):
    """
    Polish a draft prompt using agent_dialog

    Improves fluency, removes passive voice, enhances descriptive language.
    """
    try:
        from app.core.prompts import _call_dialog_agent

        polished = _call_dialog_agent(request.draft, request.template_name)

        return PromptPolishResponse(original=request.draft, polished=polished)

    except Exception as e:
        logger.error(f"[Prompts API] Polish failed: {e}")
        raise HTTPException(status_code=500, detail=f"Polish failed: {e}") from e


@router.post("/variants", response_model=PromptVariantsResponse)
async def generate_variants_endpoint(request: PromptVariantsRequest):
    """
    Generate prompt variants

    Creates multiple variations of a base prompt with different word choices
    and emphasis while maintaining core meaning.
    """
    try:
        variants = generate_variants(request.base_prompt, request.count)

        return PromptVariantsResponse(base_prompt=request.base_prompt, variants=variants, count=len(variants))

    except Exception as e:
        logger.error(f"[Prompts API] Variant generation failed: {e}")
        raise HTTPException(status_code=500, detail=f"Variant generation failed: {e}") from e


@router.post("/save", response_model=PromptSaveResponse)
async def save_prompt_endpoint(request: PromptSaveRequest):
    """
    Save prompt artifact to disk

    Stores prompt, variables, agent lineage, and reference image hash
    to Work/prompts/<session_id>.json
    """
    try:
        artifact_path = save_prompt_artifact(
            session_id=request.session_id,
            prompt=request.prompt,
            negative_prompt=request.negative_prompt,
            template_name=request.template_name,
            variables=request.variables,
            mode=request.mode,
            reference_image=request.reference_image,
            agent_lineage=request.agent_lineage,
        )

        return PromptSaveResponse(artifact_path=str(artifact_path), session_id=request.session_id)

    except Exception as e:
        logger.error(f"[Prompts API] Save failed: {e}")
        raise HTTPException(status_code=500, detail=f"Save failed: {e}") from e


@router.get("/health")
async def prompts_health():
    """
    Check prompt engine health

    Returns:
    - agents_available: Number of agents online
    - mode_recommendation: Suggested mode based on agent availability
    """
    try:
        # Check agent health
        agents_status = await llm_client.health_all()

        online_count = sum(1 for agent in agents_status.values() if agent.get("available", False))
        total_count = len(agents_status)

        # Recommend mode based on availability
        recommended_mode = PromptMode.AGENT_ASSISTED.value if online_count >= 3 else PromptMode.TEMPLATE_ONLY.value

        return {
            "status": "healthy",
            "agents_available": online_count,
            "agents_total": total_count,
            "mode_recommendation": recommended_mode,
            "agents": agents_status,
        }

    except Exception as e:
        logger.error(f"[Prompts API] Health check failed: {e}")
        return {
            "status": "degraded",
            "agents_available": 0,
            "agents_total": 4,
            "mode_recommendation": PromptMode.TEMPLATE_ONLY.value,
            "error": str(e),
        }
