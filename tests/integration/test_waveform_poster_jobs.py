"""
Integration tests for video poster and audio waveform job workers

Tests ffmpeg video poster extraction and pydub audio waveform generation
"""

import tempfile
import time
from pathlib import Path

import pytest
from PIL import Image
from sqlmodel import Session

from app.backend.models.entities import Asset, AssetProvenance, AssetType, JobKind, JobStatus
from app.core.db import create_db_and_tables, get_engine, reset_engine
from app.workers.jobs.thumbnails import run_audio_waveform_job, run_video_poster_job
from app.workers.queue import enqueue_job, get_job_status


@pytest.fixture
def temp_workspace(monkeypatch):
    """Create temporary workspace with database and Work directory"""
    with tempfile.TemporaryDirectory() as tmpdir:
        workspace = Path(tmpdir)
        db_path = workspace / "test.db"
        work_dir = workspace / "Work"
        work_dir.mkdir()
        (work_dir / "posters").mkdir()
        (work_dir / "waveforms").mkdir()

        # Override settings
        from app.core import config

        monkeypatch.setattr(config.settings, "db_path", str(db_path))
        monkeypatch.setattr(config.settings, "work_dir", str(work_dir))
        reset_engine()

        # Create database
        create_db_and_tables()

        yield workspace


@pytest.fixture
def sample_video(temp_workspace):
    """Create a sample video file using ffmpeg"""
    video_path = temp_workspace / "test_video.mp4"

    # Create 2-second video with color test pattern using ffmpeg
    import subprocess

    try:
        subprocess.run(
            [
                "ffmpeg",
                "-f",
                "lavfi",
                "-i",
                "testsrc=duration=2:size=320x240:rate=30",
                "-c:v",
                "libx264",
                "-pix_fmt",
                "yuv420p",
                "-y",
                str(video_path),
            ],
            capture_output=True,
            timeout=10,
            creationflags=subprocess.CREATE_NO_WINDOW if hasattr(subprocess, "CREATE_NO_WINDOW") else 0,
        )
        return video_path
    except (FileNotFoundError, subprocess.TimeoutExpired):
        pytest.skip("ffmpeg not available or timeout")


@pytest.fixture
def sample_audio(temp_workspace):
    """Create a sample audio file using pydub"""
    audio_path = temp_workspace / "test_audio.mp3"

    try:
        from pydub.generators import Sine

        # Create 2-second sine wave at 440Hz (A4 note)
        tone = Sine(440).to_audio_segment(duration=2000)
        tone.export(str(audio_path), format="mp3")
        return audio_path
    except ImportError:
        pytest.skip("pydub not available")


def test_enqueue_video_poster_job(temp_workspace, sample_video):  # noqa: ARG001
    """Test enqueueing a video poster job"""
    engine = get_engine()

    # Create asset
    with Session(engine) as session:
        asset = Asset(
            path=str(sample_video),
            type=AssetType.VIDEO,
            hash="test_hash_video_1",
            provenance=AssetProvenance.UNKNOWN,
            approved=False,
        )
        session.add(asset)
        session.commit()
        session.refresh(asset)
        asset_id = asset.id

    # Enqueue job
    job_id = enqueue_job(
        kind=JobKind.THUMBNAIL,
        job_func=run_video_poster_job,
        asset_id=asset_id,
        params={"asset_id": asset_id, "type": "video_poster"},
    )

    assert job_id is not None

    # Check job status
    status = get_job_status(job_id)
    assert status is not None
    assert status["kind"] == JobKind.THUMBNAIL
    assert status["status"] in [JobStatus.PENDING, JobStatus.RUNNING, JobStatus.COMPLETED]


def test_video_poster_job_creates_output(temp_workspace, sample_video):  # noqa: ARG001
    """Test that video poster job creates output file"""
    engine = get_engine()

    # Create asset
    with Session(engine) as session:
        asset = Asset(
            path=str(sample_video),
            type=AssetType.VIDEO,
            hash="test_hash_video_2",
            provenance=AssetProvenance.UNKNOWN,
            approved=False,
        )
        session.add(asset)
        session.commit()
        session.refresh(asset)
        asset_id = asset.id

    # Enqueue job
    job_id = enqueue_job(
        kind=JobKind.THUMBNAIL,
        job_func=run_video_poster_job,
        asset_id=asset_id,
        params={"asset_id": asset_id, "type": "video_poster"},
    )

    # Wait for job completion (max 30 seconds for ffmpeg)
    max_wait = 30
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
    assert output_path.suffix == ".jpg"
    assert "_poster" in output_path.stem

    # Verify output is valid image
    output_img = Image.open(output_path)
    assert output_img.size == (320, 240)  # Should match video dimensions


def test_enqueue_audio_waveform_job(temp_workspace, sample_audio):  # noqa: ARG001
    """Test enqueueing an audio waveform job"""
    engine = get_engine()

    # Create asset
    with Session(engine) as session:
        asset = Asset(
            path=str(sample_audio),
            type=AssetType.AUDIO,
            hash="test_hash_audio_1",
            provenance=AssetProvenance.UNKNOWN,
            approved=False,
        )
        session.add(asset)
        session.commit()
        session.refresh(asset)
        asset_id = asset.id

    # Enqueue job
    job_id = enqueue_job(
        kind=JobKind.THUMBNAIL,
        job_func=run_audio_waveform_job,
        asset_id=asset_id,
        params={"asset_id": asset_id, "type": "audio_waveform"},
    )

    assert job_id is not None

    # Check job status
    status = get_job_status(job_id)
    assert status is not None
    assert status["kind"] == JobKind.THUMBNAIL
    assert status["status"] in [JobStatus.PENDING, JobStatus.RUNNING, JobStatus.COMPLETED]


def test_audio_waveform_job_creates_output(temp_workspace, sample_audio):  # noqa: ARG001
    """Test that audio waveform job creates output file"""
    engine = get_engine()

    # Create asset
    with Session(engine) as session:
        asset = Asset(
            path=str(sample_audio),
            type=AssetType.AUDIO,
            hash="test_hash_audio_2",
            provenance=AssetProvenance.UNKNOWN,
            approved=False,
        )
        session.add(asset)
        session.commit()
        session.refresh(asset)
        asset_id = asset.id

    # Enqueue job
    job_id = enqueue_job(
        kind=JobKind.THUMBNAIL,
        job_func=run_audio_waveform_job,
        asset_id=asset_id,
        params={"asset_id": asset_id, "type": "audio_waveform"},
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
    assert "_waveform" in output_path.stem

    # Verify output is valid image with expected dimensions
    output_img = Image.open(output_path)
    assert output_img.size == (800, 200)  # Fixed waveform dimensions


def test_video_poster_job_handles_missing_file(temp_workspace):  # noqa: ARG001
    """Test that video poster job handles missing file gracefully"""
    engine = get_engine()

    # Create asset with non-existent file
    with Session(engine) as session:
        asset = Asset(
            path="/nonexistent/video.mp4",
            type=AssetType.VIDEO,
            hash="test_hash_video_3",
            provenance=AssetProvenance.UNKNOWN,
            approved=False,
        )
        session.add(asset)
        session.commit()
        session.refresh(asset)
        asset_id = asset.id

    # Enqueue job
    job_id = enqueue_job(
        kind=JobKind.THUMBNAIL,
        job_func=run_video_poster_job,
        asset_id=asset_id,
        params={"asset_id": asset_id, "type": "video_poster"},
    )

    # Wait for job to fail
    max_wait = 35  # ffmpeg timeout is 30s
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


def test_audio_waveform_job_handles_missing_file(temp_workspace):  # noqa: ARG001
    """Test that audio waveform job handles missing file gracefully"""
    engine = get_engine()

    # Create asset with non-existent file
    with Session(engine) as session:
        asset = Asset(
            path="/nonexistent/audio.mp3",
            type=AssetType.AUDIO,
            hash="test_hash_audio_3",
            provenance=AssetProvenance.UNKNOWN,
            approved=False,
        )
        session.add(asset)
        session.commit()
        session.refresh(asset)
        asset_id = asset.id

    # Enqueue job
    job_id = enqueue_job(
        kind=JobKind.THUMBNAIL,
        job_func=run_audio_waveform_job,
        asset_id=asset_id,
        params={"asset_id": asset_id, "type": "audio_waveform"},
    )

    # Wait for job to fail
    max_wait = 10
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


def test_video_poster_collision_handling(temp_workspace, sample_video):
    """Test that video poster job handles filename collisions"""
    engine = get_engine()
    work_dir = Path(temp_workspace) / "Work" / "posters"

    # Create asset
    with Session(engine) as session:
        asset = Asset(
            path=str(sample_video),
            type=AssetType.VIDEO,
            hash="test_hash_video_4",
            provenance=AssetProvenance.UNKNOWN,
            approved=False,
        )
        session.add(asset)
        session.commit()
        session.refresh(asset)
        asset_id = asset.id

    # Create pre-existing output file to force collision
    expected_name = f"{sample_video.stem}_poster.jpg"
    collision_file = work_dir / expected_name
    collision_file.write_text("existing file")

    # Enqueue job
    job_id = enqueue_job(
        kind=JobKind.THUMBNAIL,
        job_func=run_video_poster_job,
        asset_id=asset_id,
        params={"asset_id": asset_id, "type": "video_poster"},
    )

    # Wait for completion
    max_wait = 30
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
    assert "_poster_1" in output_path.stem or "_poster" in output_path.stem

    # Original collision file should still exist
    assert collision_file.exists()


def test_audio_waveform_collision_handling(temp_workspace, sample_audio):
    """Test that audio waveform job handles filename collisions"""
    engine = get_engine()
    work_dir = Path(temp_workspace) / "Work" / "waveforms"

    # Create asset
    with Session(engine) as session:
        asset = Asset(
            path=str(sample_audio),
            type=AssetType.AUDIO,
            hash="test_hash_audio_4",
            provenance=AssetProvenance.UNKNOWN,
            approved=False,
        )
        session.add(asset)
        session.commit()
        session.refresh(asset)
        asset_id = asset.id

    # Create pre-existing output file to force collision
    expected_name = f"{sample_audio.stem}_waveform.png"
    collision_file = work_dir / expected_name
    collision_file.write_text("existing file")

    # Enqueue job
    job_id = enqueue_job(
        kind=JobKind.THUMBNAIL,
        job_func=run_audio_waveform_job,
        asset_id=asset_id,
        params={"asset_id": asset_id, "type": "audio_waveform"},
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
    assert "_waveform_1" in output_path.stem or "_waveform" in output_path.stem

    # Original collision file should still exist
    assert collision_file.exists()
