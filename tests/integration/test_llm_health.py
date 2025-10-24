"""
Integration tests for LLM health API

STEP 7: Tests /api/llm/health endpoint aggregation.
Allows skip if llama-server instances are not running.
"""

import pytest
from fastapi.testclient import TestClient

from app.backend.server import app


@pytest.fixture
def client():
    """FastAPI test client"""
    return TestClient(app)


def test_llm_health_endpoint_exists(client):
    """Test that /api/llm/health endpoint exists"""
    response = client.get("/api/llm/health")

    # Should return 200 even if servers are down (reports status)
    assert response.status_code == 200


def test_llm_health_response_structure(client):
    """Test that health response has expected structure"""
    response = client.get("/api/llm/health")
    data = response.json()

    # Check top-level structure
    assert "agents" in data
    assert "summary" in data

    # Check summary structure
    summary = data["summary"]
    assert "total" in summary
    assert "online" in summary
    assert "offline" in summary
    assert "status" in summary


def test_llm_health_reports_all_agents(client):
    """Test that health endpoint reports status for all 4 agents"""
    response = client.get("/api/llm/health")
    data = response.json()

    agents = data["agents"]
    expected_agents = {"agent_vision", "agent_dialog", "agent_logic", "agent_fast"}

    # Should report all 4 agents (even if offline)
    assert set(agents.keys()) == expected_agents


def test_llm_health_summary_counts(client):
    """Test that summary counts are consistent"""
    response = client.get("/api/llm/health")
    data = response.json()

    summary = data["summary"]
    total = summary["total"]
    online = summary["online"]
    offline = summary["offline"]

    # Total should equal online + offline
    assert total == online + offline

    # Total should be 4 (number of agents)
    assert total == 4


@pytest.mark.skipif(
    True,  # Skip by default (requires running servers)
    reason="Requires llama-server instances running on ports 9091-9094",
)
def test_llm_health_with_running_servers(client):
    """
    Test health endpoint with actual running servers

    This test is skipped by default. To run:
    1. Start all 4 llama-server instances (see docs/ops/run_llama_servers.md)
    2. Run pytest with: pytest -m "not skip" tests/integration/test_llm_health.py

    Expected: All 4 agents online, summary.online == 4
    """
    response = client.get("/api/llm/health")
    data = response.json()

    summary = data["summary"]

    # All agents should be online
    assert summary["online"] == 4
    assert summary["offline"] == 0
    assert summary["status"] == "healthy"

    # Each agent should report as available
    for _agent_id, agent_status in data["agents"].items():
        assert agent_status["available"] is True
        assert agent_status["status"] == "online"
        assert "model_name" in agent_status


def test_llm_health_agent_specific_endpoint(client):
    """Test health endpoint for specific agent"""
    # Test with agent_vision
    response = client.get("/api/llm/health/agent_vision")

    assert response.status_code == 200

    data = response.json()
    assert "agent_id" in data
    assert data["agent_id"] == "agent_vision"
    assert "status" in data

    # Status should be one of: success, unavailable, timeout, error
    assert data["status"] in ["success", "unavailable", "timeout", "error"]


def test_llm_health_degraded_status():
    """Test that summary.status is 'degraded' when some agents are offline"""
    # This is a conceptual test - actual implementation would require
    # mocking llm_client.health_all() to return mixed online/offline statuses

    # Example expected behavior:
    # - If 4/4 online → status: "healthy"
    # - If 1-3 online → status: "degraded"
    # - If 0/4 online → status: "down"
    # - If error → status: "error"

    pass  # Placeholder for future mock-based test


def test_llm_health_error_handling(client):
    """Test that health endpoint handles errors gracefully"""
    # Even if all servers are down, should return 200 with error info
    response = client.get("/api/llm/health")

    assert response.status_code == 200
    data = response.json()

    # Should still have proper structure even on failure
    assert "agents" in data
    assert "summary" in data
