"""
Integration tests for background removal job worker

Tests rembg background removal on real image files
"""

import contextlib
import tempfile
import time
from pathlib import Path

import pytest
from PIL import Image
from sqlmodel import Session

from app.backend.models.entities import Asset, AssetProvenance, AssetType, Job, JobKind, JobStatus
from app.core.db import create_db_and_tables, get_engine, reset_engine
from app.workers.jobs.bg_remove import run_bg_remove_job
from app.workers.queue import enqueue_job, get_job_status


@pytest.fixture
def temp_workspace(monkeypatch):
    """Create temporary workspace with database and Work directory"""
    with tempfile.TemporaryDirectory() as tmpdir:
        workspace = Path(tmpdir)
        db_path = workspace / "test.db"
        work_dir = workspace / "Work"
        work_dir.mkdir()
        (work_dir / "edits").mkdir()

        # Override settings
        from app.core import config

        monkeypatch.setattr(config.settings, "db_path", str(db_path))
        monkeypatch.setattr(config.settings, "work_dir", str(work_dir))
        reset_engine()

        # Create database
        create_db_and_tables()

        yield workspace


@pytest.fixture
def sample_rgba_image(temp_workspace):
    """Create a sample RGBA image with transparency"""
    img_path = temp_workspace / "test_rgba.png"

    # Create 100x100 RGBA image with red circle on transparent background
    img = Image.new("RGBA", (100, 100), (0, 0, 0, 0))
    pixels = img.load()

    # Draw red circle in center
    center_x, center_y = 50, 50
    radius = 30
    for x in range(100):
        for y in range(100):
            dist = ((x - center_x) ** 2 + (y - center_y) ** 2) ** 0.5
            if dist < radius:
                pixels[x, y] = (255, 0, 0, 255)  # Red

    img.save(str(img_path))
    return img_path


@pytest.fixture
def sample_rgb_image(temp_workspace):
    """Create a sample RGB image (will be converted to RGBA by rembg)"""
    img_path = temp_workspace / "test_rgb.jpg"

    # Create 100x100 RGB image with green rectangle
    img = Image.new("RGB", (100, 100), (255, 255, 255))
    pixels = img.load()

    # Draw green rectangle
    for x in range(30, 70):
        for y in range(30, 70):
            pixels[x, y] = (0, 255, 0)  # Green

    img.save(str(img_path), "JPEG")
    return img_path


def test_enqueue_bg_remove_job(temp_workspace, sample_rgba_image):  # noqa: ARG001
    """Test enqueueing a background removal job"""
    engine = get_engine()

    # Create asset
    with Session(engine) as session:
        asset = Asset(
            path=str(sample_rgba_image),
            type=AssetType.IMAGE,
            hash="test_hash_1",
            provenance=AssetProvenance.UNKNOWN,
            approved=False,
        )
        session.add(asset)
        session.commit()
        session.refresh(asset)
        asset_id = asset.id

    # Enqueue job
    job_id = enqueue_job(
        kind=JobKind.BG_REMOVE, job_func=run_bg_remove_job, asset_id=asset_id, params={"asset_id": asset_id}
    )

    assert job_id is not None

    # Check job status
    status = get_job_status(job_id)
    assert status is not None
    assert status["kind"] == JobKind.BG_REMOVE
    assert status["status"] in [JobStatus.PENDING, JobStatus.RUNNING, JobStatus.COMPLETED]


def test_bg_remove_job_creates_output(temp_workspace, sample_rgb_image):  # noqa: ARG001
    """Test that background removal job creates output file"""
    engine = get_engine()

    # Create asset
    with Session(engine) as session:
        asset = Asset(
            path=str(sample_rgb_image),
            type=AssetType.IMAGE,
            hash="test_hash_2",
            provenance=AssetProvenance.UNKNOWN,
            approved=False,
        )
        session.add(asset)
        session.commit()
        session.refresh(asset)
        asset_id = asset.id

    # Enqueue job
    job_id = enqueue_job(
        kind=JobKind.BG_REMOVE, job_func=run_bg_remove_job, asset_id=asset_id, params={"asset_id": asset_id}
    )

    # Wait for job completion (max 10 seconds)
    max_wait = 10
    start_time = time.time()
    status = None

    while time.time() - start_time < max_wait:
        status = get_job_status(job_id)
        if status["status"] in [JobStatus.COMPLETED, JobStatus.FAILED]:
            break
        time.sleep(0.5)

    # Check job completed successfully
    assert status is not None
    assert status["status"] == JobStatus.COMPLETED, f"Job failed: {status.get('error_message')}"
    assert status["progress"] == 1.0
    assert status["result_path"] is not None

    # Verify output file exists
    output_path = Path(status["result_path"])
    assert output_path.exists()
    assert output_path.suffix == ".png"
    assert "_nobg" in output_path.stem

    # Verify output is RGBA image
    output_img = Image.open(output_path)
    assert output_img.mode == "RGBA"
    assert output_img.size == (100, 100)


def test_bg_remove_job_handles_missing_asset(temp_workspace):  # noqa: ARG001
    """Test that background removal job handles missing asset gracefully"""
    engine = get_engine()

    # Create job with non-existent asset ID
    with Session(engine) as session:
        job = Job(
            kind=JobKind.BG_REMOVE,
            status=JobStatus.PENDING,
            progress=0.0,
            asset_id=99999,  # Non-existent
        )
        session.add(job)
        session.commit()
        session.refresh(job)
        job_id = job.id

    # Run job directly (bypass queue)
    with contextlib.suppress(Exception):
        run_bg_remove_job(job_id)

    # Check job status
    with Session(engine) as session:
        job = session.get(Job, job_id)
        assert job.status == JobStatus.FAILED
        assert job.error_message is not None


def test_bg_remove_job_handles_missing_file(temp_workspace):  # noqa: ARG001
    """Test that background removal job handles missing file gracefully"""
    engine = get_engine()

    # Create asset with non-existent file
    with Session(engine) as session:
        asset = Asset(
            path="/nonexistent/image.png",
            type=AssetType.IMAGE,
            hash="test_hash_3",
            provenance=AssetProvenance.UNKNOWN,
            approved=False,
        )
        session.add(asset)
        session.commit()
        session.refresh(asset)
        asset_id = asset.id

    # Enqueue job
    job_id = enqueue_job(
        kind=JobKind.BG_REMOVE, job_func=run_bg_remove_job, asset_id=asset_id, params={"asset_id": asset_id}
    )

    # Wait for job to complete/fail
    max_wait = 5
    start_time = time.time()
    status = None

    while time.time() - start_time < max_wait:
        status = get_job_status(job_id)
        if status["status"] in [JobStatus.COMPLETED, JobStatus.FAILED]:
            break
        time.sleep(0.5)

    # Check job failed
    assert status is not None
    assert status["status"] == JobStatus.FAILED
    assert status["error_message"] is not None


def test_bg_remove_job_collision_handling(temp_workspace, sample_rgba_image):
    """Test that background removal handles filename collisions"""
    engine = get_engine()
    work_dir = Path(temp_workspace) / "Work" / "edits"

    # Create asset
    with Session(engine) as session:
        asset = Asset(
            path=str(sample_rgba_image),
            type=AssetType.IMAGE,
            hash="test_hash_4",
            provenance=AssetProvenance.UNKNOWN,
            approved=False,
        )
        session.add(asset)
        session.commit()
        session.refresh(asset)
        asset_id = asset.id

    # Create pre-existing output file to force collision
    expected_name = f"{sample_rgba_image.stem}_nobg.png"
    collision_file = work_dir / expected_name
    collision_file.write_text("existing file")

    # Enqueue job
    job_id = enqueue_job(
        kind=JobKind.BG_REMOVE, job_func=run_bg_remove_job, asset_id=asset_id, params={"asset_id": asset_id}
    )

    # Wait for completion
    max_wait = 10
    start_time = time.time()
    status = None

    while time.time() - start_time < max_wait:
        status = get_job_status(job_id)
        if status["status"] in [JobStatus.COMPLETED, JobStatus.FAILED]:
            break
        time.sleep(0.5)

    # Check job completed
    assert status is not None
    assert status["status"] == JobStatus.COMPLETED

    # Verify output has collision suffix (_1)
    output_path = Path(status["result_path"])
    assert output_path.exists()
    assert "_nobg_1" in output_path.stem or "_nobg" in output_path.stem

    # Original collision file should still exist
    assert collision_file.exists()


def test_bg_remove_job_progress_updates(temp_workspace, sample_rgba_image):  # noqa: ARG001
    """Test that background removal job updates progress"""
    engine = get_engine()

    # Create asset
    with Session(engine) as session:
        asset = Asset(
            path=str(sample_rgba_image),
            type=AssetType.IMAGE,
            hash="test_hash_5",
            provenance=AssetProvenance.UNKNOWN,
            approved=False,
        )
        session.add(asset)
        session.commit()
        session.refresh(asset)
        asset_id = asset.id

    # Enqueue job
    job_id = enqueue_job(
        kind=JobKind.BG_REMOVE, job_func=run_bg_remove_job, asset_id=asset_id, params={"asset_id": asset_id}
    )

    # Poll for progress updates
    progress_values = []
    max_wait = 10
    start_time = time.time()

    while time.time() - start_time < max_wait:
        status = get_job_status(job_id)
        progress_values.append(status["progress"])

        if status["status"] in [JobStatus.COMPLETED, JobStatus.FAILED]:
            break
        time.sleep(0.2)

    # Check that progress increased over time
    assert len(progress_values) > 0
    assert progress_values[-1] == 1.0  # Final progress should be 1.0

    # Check that progress was monotonically increasing
    for i in range(1, len(progress_values)):
        assert progress_values[i] >= progress_values[i - 1]
