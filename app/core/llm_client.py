"""
LLM Client — HTTP adapter for llama.cpp servers

STEP 7: Provides HTTP client stubs for communicating with offline GGUF agents.
All requests are sent to local llama-server instances (ports 9091-9094).
"""

import time
from pathlib import Path
from typing import Any

import httpx
import yaml
from loguru import logger

# Load server configurations
_SERVERS_CONFIG_PATH = Path(__file__).parent / "llm_servers.yaml"
_REGISTRY_CONFIG_PATH = Path(__file__).parent / "llm_registry.yaml"

# Global config cache
_SERVERS: dict | None = None
_REGISTRY: dict | None = None


class LLMClientError(Exception):
    """Base exception for LLM client errors"""

    pass


class LLMServerUnavailableError(LLMClientError):
    """Raised when LLM server is not reachable"""

    pass


class LLMTimeoutError(LLMClientError):
    """Raised when LLM request times out"""

    pass


def load_servers_config() -> dict:
    """Load llm_servers.yaml configuration."""
    global _SERVERS
    if _SERVERS is None:
        config_path = Path(__file__).parent / "llm_servers.yaml"
        with config_path.open("r", encoding="utf-8") as f:
            _SERVERS = yaml.safe_load(f)
    return _SERVERS


def load_registry_config() -> dict:
    """Load llm_registry.yaml configuration."""
    global _REGISTRY
    if _REGISTRY is None:
        config_path = Path(__file__).parent / "llm_registry.yaml"
        with config_path.open("r", encoding="utf-8") as f:
            _REGISTRY = yaml.safe_load(f)
    return _REGISTRY


def get_server_url(agent_id: str) -> str:
    """Get base URL for agent server"""
    servers = load_servers_config()
    server_config = servers.get("servers", {}).get(agent_id)
    if not server_config:
        raise LLMClientError(f"Server config not found for agent: {agent_id}")

    return server_config["base_url"]


def get_server_timeout(agent_id: str) -> int:
    """Get timeout for agent server (in seconds)"""
    servers = load_servers_config()
    server_config = servers.get("servers", {}).get(agent_id, {})
    return server_config.get("timeout", 30)


async def health(agent_id: str) -> dict[str, Any]:
    """
    Check health of llama-server instance

    Args:
        agent_id: Agent identifier (e.g., "agent_vision")

    Returns:
        dict with status, model_name, and uptime if available

    Raises:
        LLMServerUnavailableError: If server is not reachable
        LLMTimeoutError: If request times out
    """
    base_url = get_server_url(agent_id)
    timeout = get_server_timeout(agent_id)

    url = f"{base_url}/health"

    try:
        async with httpx.AsyncClient(timeout=timeout) as client:
            response = await client.get(url)
            response.raise_for_status()

            data = response.json()
            return {
                "agent_id": agent_id,
                "status": "online",
                "model_name": data.get("model", "unknown"),
                "available": True,
            }

    except httpx.TimeoutException as e:
        logger.error(f"[LLM] Health check timeout for {agent_id}: {e}")
        raise LLMTimeoutError(f"Health check timeout for {agent_id}") from e

    except httpx.HTTPError as e:
        logger.error(f"[LLM] Health check failed for {agent_id}: {e}")
        raise LLMServerUnavailableError(f"Server unavailable: {agent_id}") from e


async def chat(
    agent_id: str,
    messages: list[dict[str, str]],
    temperature: float | None = None,
    max_tokens: int | None = None,
    stop: list[str] | None = None,
) -> dict[str, Any]:
    """
    Send chat completion request to llama-server

    Args:
        agent_id: Agent identifier
        messages: List of message dicts with "role" and "content"
        temperature: Sampling temperature (overrides agent default)
        max_tokens: Max tokens to generate
        stop: Stop sequences

    Returns:
        dict with "content", "finish_reason", "usage" fields

    Raises:
        LLMServerUnavailableError: If server is not reachable
        LLMTimeoutError: If request times out
    """
    base_url = get_server_url(agent_id)
    timeout = get_server_timeout(agent_id)

    # Get agent defaults from registry
    registry = load_registry_config()
    agent_config = registry.get("agents", {}).get(agent_id, {})
    defaults = registry.get("defaults", {})

    # Build request payload
    payload = {
        "messages": messages,
        "temperature": temperature or agent_config.get("temperature", 0.7),
        "max_tokens": max_tokens or defaults.get("max_tokens", 512),
        "stop": stop or defaults.get("stop_sequences", []),
    }

    url = f"{base_url}/v1/chat/completions"

    try:
        async with httpx.AsyncClient(timeout=timeout) as client:
            # Add custom header for agent tracking
            headers = {"X-Agent-ID": agent_id}

            response = await client.post(url, json=payload, headers=headers)
            response.raise_for_status()

            data = response.json()

            # Extract response content
            choice = data.get("choices", [{}])[0]
            message = choice.get("message", {})

            return {
                "content": message.get("content", ""),
                "finish_reason": choice.get("finish_reason", "unknown"),
                "usage": data.get("usage", {}),
            }

    except httpx.TimeoutException as e:
        logger.error(f"[LLM] Chat timeout for {agent_id}: {e}")
        raise LLMTimeoutError(f"Chat timeout for {agent_id}") from e

    except httpx.HTTPError as e:
        logger.error(f"[LLM] Chat request failed for {agent_id}: {e}")
        raise LLMServerUnavailableError(f"Server error: {agent_id}") from e


async def vision_chat(
    agent_id: str,
    messages: list[dict[str, str]],
    image_path: Path,
    temperature: float | None = None,
    max_tokens: int | None = None,
) -> dict[str, Any]:
    """
    Send multimodal chat request with image to llama-server

    Args:
        agent_id: Agent identifier (must support vision, e.g., agent_vision)
        messages: List of message dicts
        image_path: Path to image file
        temperature: Sampling temperature
        max_tokens: Max tokens to generate

    Returns:
        dict with "content", "finish_reason", "usage" fields

    Raises:
        LLMClientError: If agent doesn't support vision
        LLMServerUnavailableError: If server is not reachable
        LLMTimeoutError: If request times out
    """
    # Verify agent supports vision
    registry = load_registry_config()
    agent_config = registry.get("agents", {}).get(agent_id, {})
    capabilities = agent_config.get("capabilities", [])

    if "vision" not in capabilities and "multimodal" not in capabilities:
        raise LLMClientError(f"Agent {agent_id} does not support vision capabilities")

    base_url = get_server_url(agent_id)
    timeout = get_server_timeout(agent_id)

    # Build request payload (multipart form data)
    defaults = registry.get("defaults", {})

    with image_path.open("rb") as image_file:
        files = {"image": image_file}
        data = {
            "messages": str(messages),  # JSON string
            "temperature": temperature or agent_config.get("temperature", 0.7),
            "max_tokens": max_tokens or defaults.get("max_tokens", 512),
        }

        url = f"{base_url}/v1/chat/completions"

        try:
            async with httpx.AsyncClient(timeout=timeout) as client:
                headers = {"X-Agent-ID": agent_id}

                response = await client.post(url, files=files, data=data, headers=headers)
                response.raise_for_status()

                response_data = response.json()

                # Extract response content
                choice = response_data.get("choices", [{}])[0]
                message = choice.get("message", {})

                return {
                    "content": message.get("content", ""),
                    "finish_reason": choice.get("finish_reason", "unknown"),
                    "usage": response_data.get("usage", {}),
                }

        except httpx.TimeoutException as e:
            logger.error(f"[LLM] Vision chat timeout for {agent_id}: {e}")
            raise LLMTimeoutError(f"Vision chat timeout for {agent_id}") from e

        except httpx.HTTPError as e:
            logger.error(f"[LLM] Vision chat request failed for {agent_id}: {e}")
            raise LLMServerUnavailableError(f"Server error: {agent_id}") from e


async def chat_with_retry(
    agent_id: str,
    messages: list[dict[str, str]],
    max_retries: int = 3,
    **kwargs: Any,
) -> dict[str, Any]:
    """
    Send chat request with automatic retry on failure

    Args:
        agent_id: Agent identifier
        messages: List of message dicts
        max_retries: Maximum retry attempts
        **kwargs: Additional arguments passed to chat()

    Returns:
        dict with response content

    Raises:
        LLMServerUnavailableError: If all retries fail
    """
    servers = load_servers_config()
    retry_delay = servers.get("global", {}).get("retry_delay_ms", 1000) / 1000

    last_error = None
    for attempt in range(max_retries):
        try:
            return await chat(agent_id, messages, **kwargs)

        except (LLMServerUnavailableError, LLMTimeoutError) as e:
            last_error = e
            if attempt < max_retries - 1:
                logger.warning(f"[LLM] Chat attempt {attempt + 1}/{max_retries} failed for {agent_id}, retrying...")
                time.sleep(retry_delay * (attempt + 1))  # Exponential backoff
            else:
                logger.error(f"[LLM] All {max_retries} chat attempts failed for {agent_id}")

    raise last_error or LLMServerUnavailableError(f"Failed after {max_retries} retries")


async def health_all() -> dict[str, dict[str, Any]]:
    """
    Check health of all configured LLM agents

    Returns:
        dict mapping agent_id to health status dict
    """
    servers_config = load_servers_config()
    servers = servers_config.get("servers", {})
    results = {}

    for agent_id in servers:
        try:
            health_status = await health(agent_id)
            results[agent_id] = health_status
        except (LLMServerUnavailableError, LLMTimeoutError) as e:
            results[agent_id] = {
                "agent_id": agent_id,
                "status": "offline",
                "error": str(e),
                "available": False,
            }

    return results
