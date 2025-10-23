"""
Thumbnail Generation Jobs

STEP 6: Video poster frames and audio waveforms

- Video: Extract poster frame using ffmpeg
- Audio: Generate waveform PNG (audiowaveform or matplotlib fallback)
"""

import subprocess
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw
from pydub import AudioSegment
from sqlmodel import Session

from app.backend.models.entities import Asset, Job
from app.core.db import get_engine
from app.core.logging import get_logger
from app.workers.queue import update_job_progress

logger = get_logger(__name__)

# Output directories
VIDEO_POSTERS_DIR = Path("Work/posters")
AUDIO_WAVEFORMS_DIR = Path("Work/waveforms")


def run_video_poster_job(job_id: int) -> Path | None:
    """
    Generate video poster frame using ffmpeg

    Args:
        job_id: Job ID from database

    Returns:
        Path to output poster image

    Process:
        1. Load video asset from database
        2. Extract frame at 1 second using ffmpeg
        3. Save to Work/posters/{video_name}_poster.jpg
    """
    logger.info(f"[Job {job_id}] Starting video poster generation")

    try:
        VIDEO_POSTERS_DIR.mkdir(parents=True, exist_ok=True)

        # Get asset from database
        engine = get_engine()
        with Session(engine) as session:
            job = session.get(Job, job_id)
            if not job or not job.asset_id:
                raise ValueError("Job has no associated asset")

            asset = session.get(Asset, job.asset_id)
            if not asset:
                raise ValueError(f"Asset {job.asset_id} not found")

            input_path = Path(asset.path)
            if not input_path.exists():
                raise FileNotFoundError(f"Input file not found: {input_path}")

        update_job_progress(job_id, 0.2)

        # Generate output path
        output_filename = f"{input_path.stem}_poster.jpg"
        output_path = VIDEO_POSTERS_DIR / output_filename

        # Handle collisions
        counter = 1
        while output_path.exists():
            output_filename = f"{input_path.stem}_poster_{counter}.jpg"
            output_path = VIDEO_POSTERS_DIR / output_filename
            counter += 1

        # Extract frame using ffmpeg
        logger.info(f"[Job {job_id}] Extracting poster frame from: {input_path}")
        cmd = [
            "ffmpeg",
            "-ss",
            "00:00:01",  # Seek to 1 second
            "-i",
            str(input_path),
            "-vframes",
            "1",  # Extract 1 frame
            "-q:v",
            "2",  # Quality (2 is high)
            "-y",  # Overwrite
            str(output_path),
        ]

        result = subprocess.run(
            cmd, capture_output=True, text=True, timeout=30, creationflags=subprocess.CREATE_NO_WINDOW
        )

        if result.returncode != 0:
            logger.warning(f"[Job {job_id}] ffmpeg stderr: {result.stderr}")
            if not output_path.exists():
                raise RuntimeError(f"ffmpeg failed: {result.stderr}")

        update_job_progress(job_id, 1.0)
        logger.info(f"[Job {job_id}] Video poster complete: {output_path}")
        return output_path

    except Exception as e:
        logger.error(f"[Job {job_id}] Video poster generation failed: {e}", exc_info=True)
        raise


def run_audio_waveform_job(job_id: int) -> Path | None:
    """
    Generate audio waveform PNG

    Args:
        job_id: Job ID from database

    Returns:
        Path to output waveform image

    Process:
        1. Load audio asset from database
        2. Extract waveform data using pydub
        3. Generate PNG visualization
        4. Save to Work/waveforms/{audio_name}_waveform.png

    Note: Uses pydub + Pillow for portability.
    For production, consider audiowaveform tool for better quality.
    """
    logger.info(f"[Job {job_id}] Starting audio waveform generation")

    try:
        AUDIO_WAVEFORMS_DIR.mkdir(parents=True, exist_ok=True)

        # Get asset from database
        engine = get_engine()
        with Session(engine) as session:
            job = session.get(Job, job_id)
            if not job or not job.asset_id:
                raise ValueError("Job has no associated asset")

            asset = session.get(Asset, job.asset_id)
            if not asset:
                raise ValueError(f"Asset {job.asset_id} not found")

            input_path = Path(asset.path)
            if not input_path.exists():
                raise FileNotFoundError(f"Input file not found: {input_path}")

        update_job_progress(job_id, 0.1)

        # Generate output path
        output_filename = f"{input_path.stem}_waveform.png"
        output_path = AUDIO_WAVEFORMS_DIR / output_filename

        # Handle collisions
        counter = 1
        while output_path.exists():
            output_filename = f"{input_path.stem}_waveform_{counter}.png"
            output_path = AUDIO_WAVEFORMS_DIR / output_filename
            counter += 1

        # Load audio file
        logger.info(f"[Job {job_id}] Loading audio: {input_path}")
        try:
            audio = AudioSegment.from_file(str(input_path))
        except Exception as e:
            logger.error(f"[Job {job_id}] Failed to load audio with pydub: {e}")
            # Create placeholder waveform
            return _create_placeholder_waveform(output_path, input_path.stem)

        update_job_progress(job_id, 0.3)

        # Get audio samples (downsample for visualization)
        samples = np.array(audio.get_array_of_samples())
        channels = audio.channels

        # If stereo, take mean of channels
        if channels == 2:
            samples = samples.reshape((-1, 2))
            samples = samples.mean(axis=1)

        update_job_progress(job_id, 0.5)

        # Downsample for visualization (max 2000 points)
        target_points = 2000
        if len(samples) > target_points:
            step = len(samples) // target_points
            samples = samples[::step]

        # Normalize to -1 to 1
        samples = samples / np.max(np.abs(samples))

        # Generate waveform image
        logger.info(f"[Job {job_id}] Generating waveform PNG")
        width = 800
        height = 200
        img = Image.new("RGB", (width, height), color=(30, 30, 30))
        draw = ImageDraw.Draw(img)

        # Draw waveform
        center_y = height // 2
        x_scale = width / len(samples)

        for i in range(len(samples) - 1):
            x1 = int(i * x_scale)
            x2 = int((i + 1) * x_scale)
            y1 = int(center_y - samples[i] * center_y * 0.9)
            y2 = int(center_y - samples[i + 1] * center_y * 0.9)
            draw.line([(x1, y1), (x2, y2)], fill=(100, 200, 100), width=1)

        # Draw center line
        draw.line([(0, center_y), (width, center_y)], fill=(50, 50, 50), width=1)

        # Save image
        img.save(output_path, "PNG")
        update_job_progress(job_id, 1.0)

        logger.info(f"[Job {job_id}] Audio waveform complete: {output_path}")
        return output_path

    except Exception as e:
        logger.error(f"[Job {job_id}] Audio waveform generation failed: {e}", exc_info=True)
        raise


def _create_placeholder_waveform(output_path: Path, filename: str) -> Path:
    """Create a placeholder waveform image when audio can't be loaded"""
    logger.warning(f"Creating placeholder waveform for {filename}")

    width = 800
    height = 200
    img = Image.new("RGB", (width, height), color=(30, 30, 30))
    draw = ImageDraw.Draw(img)

    # Draw placeholder text
    center_y = height // 2
    draw.text((width // 2 - 100, center_y - 10), f"Waveform: {filename}", fill=(150, 150, 150))
    draw.line([(0, center_y), (width, center_y)], fill=(100, 100, 100), width=2)

    img.save(output_path, "PNG")
    return output_path
