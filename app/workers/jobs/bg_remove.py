"""
Background Removal Job

STEP 6: Image background removal using rembg (U2Net model)

Uses rembg with U2Net model for background removal.
Outputs to Work/edits/ with _nobg suffix.
"""

from pathlib import Path

from PIL import Image
from rembg import remove
from sqlmodel import Session

from app.backend.models.entities import Asset, Job
from app.core.db import get_engine
from app.core.logging import get_logger
from app.workers.queue import update_job_progress

logger = get_logger(__name__)

# Output directory for edited assets
WORK_DIR = Path("Work/edits")


def run_bg_remove_job(job_id: int) -> Path | None:
    """
    Execute background removal job

    Args:
        job_id: Job ID from database

    Returns:
        Path to output file, or None if failed

    Process:
        1. Load asset from database
        2. Read input image
        3. Run rembg removal
        4. Save to Work/edits/{original_name}_nobg.png
        5. Update progress throughout
    """
    logger.info(f"[Job {job_id}] Starting background removal")

    try:
        # Ensure output directory exists
        WORK_DIR.mkdir(parents=True, exist_ok=True)

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

        # Load input image
        logger.info(f"[Job {job_id}] Loading image: {input_path}")
        input_image = Image.open(input_path)
        update_job_progress(job_id, 0.2)

        # Run background removal
        logger.info(f"[Job {job_id}] Running rembg background removal...")
        output_image = remove(input_image)
        update_job_progress(job_id, 0.8)

        # Generate output path
        output_filename = f"{input_path.stem}_nobg.png"
        output_path = WORK_DIR / output_filename

        # Handle collisions
        counter = 1
        while output_path.exists():
            output_filename = f"{input_path.stem}_nobg_{counter}.png"
            output_path = WORK_DIR / output_filename
            counter += 1

        # Save output
        logger.info(f"[Job {job_id}] Saving output: {output_path}")
        output_image.save(output_path, "PNG")
        update_job_progress(job_id, 1.0)

        logger.info(f"[Job {job_id}] Background removal complete: {output_path}")
        return output_path

    except Exception as e:
        logger.error(f"[Job {job_id}] Background removal failed: {e}", exc_info=True)
        raise


def run_bg_remove_batch(job_id: int, asset_ids: list[int]) -> list[Path]:
    """
    Execute batch background removal job

    Args:
        job_id: Job ID from database
        asset_ids: List of asset IDs to process

    Returns:
        List of output file paths

    TODO: Implement batch processing with shared progress
    """
    logger.info(f"[Job {job_id}] Starting batch background removal for {len(asset_ids)} assets")

    output_paths = []
    for idx, asset_id in enumerate(asset_ids):
        try:
            # Process each asset (reuse single asset logic)
            # Update overall progress based on batch position
            progress = (idx + 1) / len(asset_ids)
            update_job_progress(job_id, progress)

            # Note: This is simplified - ideally we'd create sub-jobs
            logger.warning(f"Batch processing not fully implemented - processing asset {asset_id}")

        except Exception as e:
            logger.error(f"[Job {job_id}] Failed to process asset {asset_id}: {e}")
            continue

    return output_paths
