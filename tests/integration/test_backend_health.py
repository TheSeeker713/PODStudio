"""
Integration Tests for Backend API
STEP 3: Test FastAPI server with TestClient
"""

from fastapi.testclient import TestClient

from app.backend.server import app

client = TestClient(app)


def test_health_endpoint():
    """Test /api/health returns status ok"""
    response = client.get("/api/health")
    assert response.status_code == 200

    data = response.json()
    assert data["status"] == "ok"
    assert "version" in data
    assert "timestamp" in data


def test_probe_endpoint():
    """Test /api/probe returns placeholder hardware info"""
    response = client.get("/api/probe")
    assert response.status_code == 200

    data = response.json()
    assert data["gpu"] == "unknown"
    assert data["vram_gb"] is None
    assert data["cpu_threads"] is None
    assert data["ram_gb"] is None
    assert data["mode"] == "unknown"


def test_root_endpoint():
    """Test root endpoint returns API info"""
    response = client.get("/")
    assert response.status_code == 200

    data = response.json()
    assert "message" in data
    assert "version" in data
    assert "docs" in data


def test_create_job():
    """Test POST /api/jobs creates a job"""
    job_data = {
        "job_type": "upscale",
        "asset_id": "test_asset_123",
        "params": {"scale": 2},
    }

    response = client.post("/api/jobs", json=job_data)
    assert response.status_code == 201

    data = response.json()
    assert "job_id" in data
    assert data["job_type"] == "upscale"
    assert data["status"] == "pending"
    assert data["asset_id"] == "test_asset_123"
    assert data["progress"] == 0.0


def test_get_job():
    """Test GET /api/jobs/{job_id} retrieves job status"""
    # Create a job first
    job_data = {
        "job_type": "bg_remove",
        "asset_id": "test_asset_456",
        "params": {},
    }
    create_response = client.post("/api/jobs", json=job_data)
    job_id = create_response.json()["job_id"]

    # Retrieve the job
    response = client.get(f"/api/jobs/{job_id}")
    assert response.status_code == 200

    data = response.json()
    assert data["job_id"] == job_id
    assert data["job_type"] == "bg_remove"
    assert data["status"] == "pending"


def test_get_nonexistent_job():
    """Test GET /api/jobs/{job_id} returns 404 for missing job"""
    response = client.get("/api/jobs/nonexistent_job_999")
    assert response.status_code == 404


def test_delete_job():
    """Test DELETE /api/jobs/{job_id} removes job"""
    # Create a job first
    job_data = {
        "job_type": "transcode",
        "asset_id": "test_asset_789",
        "params": {},
    }
    create_response = client.post("/api/jobs", json=job_data)
    job_id = create_response.json()["job_id"]

    # Delete the job
    response = client.delete(f"/api/jobs/{job_id}")
    assert response.status_code == 204

    # Verify job is gone
    get_response = client.get(f"/api/jobs/{job_id}")
    assert get_response.status_code == 404
