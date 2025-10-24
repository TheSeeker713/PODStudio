"""
LLM Health API Routes

STEP 7: Health check endpoints for offline GGUF agent layer.
Reports availability and status of all 4 llama-server instances.
"""

from fastapi import APIRouter
from loguru import logger

from app.core import llm_client

router = APIRouter(prefix="/api/llm", tags=["llm"])


@router.get("/health")
async def get_llm_health():
    """
    Check health of all LLM agents

    Returns availability status for each of the 4 llama-server instances.
    Used by UI to display "LLM: X/4" indicator.

    Returns:
        dict with:
        - agents: dict mapping agent_id to health status
        - summary: overall stats (total, online, offline)
    """
    logger.info("[API] Checking LLM agent health...")

    try:
        health_statuses = await llm_client.health_all()

        # Count online vs offline
        total = len(health_statuses)
        online = sum(1 for status in health_statuses.values() if status.get("available"))
        offline = total - online

        return {
            "agents": health_statuses,
            "summary": {
                "total": total,
                "online": online,
                "offline": offline,
                "status": "healthy" if online == total else "degraded" if online > 0 else "down",
            },
        }

    except Exception as e:
        logger.error(f"[API] LLM health check failed: {e}")
        return {
            "agents": {},
            "summary": {
                "total": 0,
                "online": 0,
                "offline": 0,
                "status": "error",
                "error": str(e),
            },
        }


@router.get("/health/{agent_id}")
async def get_agent_health(agent_id: str):
    """
    Check health of specific LLM agent

    Args:
        agent_id: Agent identifier (e.g., "agent_vision")

    Returns:
        dict with agent health status
    """
    logger.info(f"[API] Checking health for agent: {agent_id}")

    try:
        health_status = await llm_client.health(agent_id)
        return {
            "agent_id": agent_id,
            "status": "success",
            "health": health_status,
        }

    except llm_client.LLMServerUnavailableError as e:
        logger.warning(f"[API] Agent {agent_id} unavailable: {e}")
        return {
            "agent_id": agent_id,
            "status": "unavailable",
            "error": str(e),
        }

    except llm_client.LLMTimeoutError as e:
        logger.warning(f"[API] Agent {agent_id} timeout: {e}")
        return {
            "agent_id": agent_id,
            "status": "timeout",
            "error": str(e),
        }

    except Exception as e:
        logger.error(f"[API] Agent {agent_id} health check failed: {e}")
        return {
            "agent_id": agent_id,
            "status": "error",
            "error": str(e),
        }
