"""
Unit Tests for Pydantic Schemas
STEP 3: Validate schema models can instantiate with placeholder values
"""

from datetime import UTC, datetime

from pydantic import ValidationError

from app.backend.models.schemas import (
    HardwareMode,
    HealthResponse,
    JobCreate,
    JobResponse,
    JobStatus,
    JobType,
    ProbeResponse,
)


def test_health_response_defaults():
    """Test HealthResponse with default values"""
    response = HealthResponse()
    assert response.status == "ok"
    assert response.version == "0.1.0"
    assert response.timestamp is None


def test_health_response_with_values():
    """Test HealthResponse with explicit values"""
    now = datetime.now(UTC)
    response = HealthResponse(
        status="ok",
        version="1.0.0",
        timestamp=now,
    )
    assert response.status == "ok"
    assert response.version == "1.0.0"
    assert response.timestamp == now


def test_probe_response_defaults():
    """Test ProbeResponse with placeholder defaults"""
    response = ProbeResponse()
    assert response.gpu == "unknown"
    assert response.vram_gb is None
    assert response.cpu_threads is None
    assert response.ram_gb is None
    assert response.mode == HardwareMode.UNKNOWN


def test_probe_response_with_values():
    """Test ProbeResponse with real hardware info"""
    response = ProbeResponse(
        gpu="NVIDIA RTX 3060",
        vram_gb=12.0,
        cpu_threads=16,
        ram_gb=32.0,
        mode=HardwareMode.GREEN,
    )
    assert response.gpu == "NVIDIA RTX 3060"
    assert response.vram_gb == 12.0
    assert response.cpu_threads == 16
    assert response.ram_gb == 32.0
    assert response.mode == HardwareMode.GREEN


def test_hardware_mode_enum():
    """Test HardwareMode enum values"""
    assert HardwareMode.UNKNOWN == "unknown"
    assert HardwareMode.GREEN == "green"
    assert HardwareMode.YELLOW == "yellow"
    assert HardwareMode.RED == "red"


def test_job_type_enum():
    """Test JobType enum values"""
    assert JobType.UPSCALE == "upscale"
    assert JobType.BG_REMOVE == "bg_remove"
    assert JobType.TRANSCODE == "transcode"
    assert JobType.THUMBNAIL == "thumbnail"


def test_job_status_enum():
    """Test JobStatus enum values"""
    assert JobStatus.PENDING == "pending"
    assert JobStatus.RUNNING == "running"
    assert JobStatus.COMPLETED == "completed"
    assert JobStatus.FAILED == "failed"
    assert JobStatus.CANCELLED == "cancelled"


def test_job_create():
    """Test JobCreate schema"""
    job = JobCreate(
        job_type=JobType.UPSCALE,
        asset_id="asset_123",
        params={"scale": 2},
    )
    assert job.job_type == JobType.UPSCALE
    assert job.asset_id == "asset_123"
    assert job.params == {"scale": 2}


def test_job_create_empty_params():
    """Test JobCreate with default empty params"""
    job = JobCreate(
        job_type=JobType.BG_REMOVE,
        asset_id="asset_456",
    )
    assert job.job_type == JobType.BG_REMOVE
    assert job.asset_id == "asset_456"
    assert job.params == {}


def test_job_response():
    """Test JobResponse schema"""
    now = datetime.now(UTC)
    job = JobResponse(
        job_id="job_0001",
        job_type=JobType.TRANSCODE,
        status=JobStatus.PENDING,
        asset_id="asset_789",
        created_at=now,
        updated_at=now,
        progress=0.0,
        error=None,
    )
    assert job.job_id == "job_0001"
    assert job.job_type == JobType.TRANSCODE
    assert job.status == JobStatus.PENDING
    assert job.asset_id == "asset_789"
    assert job.created_at == now
    assert job.updated_at == now
    assert job.progress == 0.0
    assert job.error is None


def test_job_response_with_error():
    """Test JobResponse with error message"""
    now = datetime.now(UTC)
    job = JobResponse(
        job_id="job_0002",
        job_type=JobType.UPSCALE,
        status=JobStatus.FAILED,
        asset_id="asset_999",
        created_at=now,
        updated_at=now,
        progress=0.5,
        error="Out of memory",
    )
    assert job.job_id == "job_0002"
    assert job.status == JobStatus.FAILED
    assert job.progress == 0.5
    assert job.error == "Out of memory"


def test_job_response_progress_validation():
    """Test JobResponse progress is clamped to 0.0-1.0"""
    now = datetime.now(UTC)

    # Valid progress
    job = JobResponse(
        job_id="job_0003",
        job_type=JobType.THUMBNAIL,
        status=JobStatus.RUNNING,
        asset_id="asset_111",
        created_at=now,
        updated_at=now,
        progress=0.75,
    )
    assert job.progress == 0.75

    # Progress > 1.0 should fail validation
    try:
        JobResponse(
            job_id="job_0004",
            job_type=JobType.THUMBNAIL,
            status=JobStatus.RUNNING,
            asset_id="asset_222",
            created_at=now,
            updated_at=now,
            progress=1.5,
        )
        assert False, "Should have raised ValidationError"  # noqa: B011
    except ValidationError:
        pass  # Expected

    # Progress < 0.0 should fail validation
    try:
        JobResponse(
            job_id="job_0005",
            job_type=JobType.THUMBNAIL,
            status=JobStatus.RUNNING,
            asset_id="asset_333",
            created_at=now,
            updated_at=now,
            progress=-0.1,
        )
        assert False, "Should have raised ValidationError"  # noqa: B011
    except ValidationError:
        pass  # Expected
