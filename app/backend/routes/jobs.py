"""
Jobs Routes - Background Job Management

STEP 6: Integrated with threadpool queue for bg-remove, poster, waveform jobs
"""

from datetime import UTC, datetime

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.backend.models.entities import JobKind
from app.backend.models.schemas import JobCreate, JobResponse, JobStatus
from app.core.logging import get_logger
from app.workers.jobs.bg_remove import run_bg_remove_job
from app.workers.jobs.thumbnails import run_audio_waveform_job, run_video_poster_job
from app.workers.queue import enqueue_job, get_job_status

logger = get_logger(__name__)
router = APIRouter()


# Request/Response Models
class BgRemoveRequest(BaseModel):
    """Request model for background removal job"""

    asset_ids: list[int]
    """List of asset IDs to process"""


class JobIdResponse(BaseModel):
    """Response with job ID"""

    job_ids: list[int]
    """List of created job IDs"""


class JobStatusResponse(BaseModel):
    """Job status response"""

    id: int
    kind: str
    status: str
    progress: float
    result_path: str | None
    error_message: str | None
    created_at: str | None
    started_at: str | None
    completed_at: str | None


@router.post("/jobs/bg-remove", response_model=JobIdResponse, status_code=201)
async def create_bg_remove_jobs(request: BgRemoveRequest):
    """
    Create background removal job(s)

    Accepts list of asset IDs and enqueues background removal jobs.
    Returns list of created job IDs.

    Args:
        request: BgRemoveRequest with asset_ids

    Returns:
        JobIdResponse with list of job IDs
    """
    logger.info(f"Creating {len(request.asset_ids)} background removal jobs")

    job_ids = []
    for asset_id in request.asset_ids:
        try:
            job_id = enqueue_job(
                kind=JobKind.BG_REMOVE,
                job_func=run_bg_remove_job,
                asset_id=asset_id,
                params={"asset_id": asset_id},
            )
            job_ids.append(job_id)
            logger.info(f"Enqueued BG removal job {job_id} for asset {asset_id}")

        except Exception as e:
            logger.error(f"Failed to enqueue job for asset {asset_id}: {e}")
            continue

    if not job_ids:
        raise HTTPException(status_code=500, detail="Failed to enqueue any jobs")

    return JobIdResponse(job_ids=job_ids)


@router.post("/jobs/video-poster", response_model=JobIdResponse, status_code=201)
async def create_video_poster_jobs(request: BgRemoveRequest):
    """
    Create video poster frame generation job(s)

    Accepts list of video asset IDs and enqueues poster generation jobs.

    Args:
        request: Request with asset_ids

    Returns:
        JobIdResponse with list of job IDs
    """
    logger.info(f"Creating {len(request.asset_ids)} video poster jobs")

    job_ids = []
    for asset_id in request.asset_ids:
        try:
            job_id = enqueue_job(
                kind=JobKind.THUMBNAIL,
                job_func=run_video_poster_job,
                asset_id=asset_id,
                params={"asset_id": asset_id, "type": "video_poster"},
            )
            job_ids.append(job_id)

        except Exception as e:
            logger.error(f"Failed to enqueue video poster job for asset {asset_id}: {e}")
            continue

    if not job_ids:
        raise HTTPException(status_code=500, detail="Failed to enqueue any jobs")

    return JobIdResponse(job_ids=job_ids)


@router.post("/jobs/audio-waveform", response_model=JobIdResponse, status_code=201)
async def create_audio_waveform_jobs(request: BgRemoveRequest):
    """
    Create audio waveform generation job(s)

    Accepts list of audio asset IDs and enqueues waveform generation jobs.

    Args:
        request: Request with asset_ids

    Returns:
        JobIdResponse with list of job IDs
    """
    logger.info(f"Creating {len(request.asset_ids)} audio waveform jobs")

    job_ids = []
    for asset_id in request.asset_ids:
        try:
            job_id = enqueue_job(
                kind=JobKind.THUMBNAIL,
                job_func=run_audio_waveform_job,
                asset_id=asset_id,
                params={"asset_id": asset_id, "type": "audio_waveform"},
            )
            job_ids.append(job_id)

        except Exception as e:
            logger.error(f"Failed to enqueue audio waveform job for asset {asset_id}: {e}")
            continue

    if not job_ids:
        raise HTTPException(status_code=500, detail="Failed to enqueue any jobs")

    return JobIdResponse(job_ids=job_ids)


@router.get("/jobs/{job_id}", response_model=JobStatusResponse)
async def get_job(job_id: int):
    """
    Retrieve job status by ID

    Returns job details if found, 404 otherwise.

    Args:
        job_id: Job ID

    Returns:
        JobStatusResponse with current status and progress
    """
    status = get_job_status(job_id)
    if not status:
        raise HTTPException(status_code=404, detail=f"Job {job_id} not found")

    return JobStatusResponse(**status)


# Legacy endpoints (keep for compatibility)
@router.post("/jobs", response_model=JobResponse, status_code=201)
async def create_job(job: JobCreate):
    """
    Create a new background job (LEGACY STUB)

    Kept for compatibility. Use specific endpoints instead:
    - POST /api/jobs/bg-remove
    - POST /api/jobs/video-poster
    - POST /api/jobs/audio-waveform
    """
    global _job_counter
    _job_counter += 1
    job_id_str = f"job_{_job_counter:04d}"

    now = datetime.now(UTC)
    job_response = JobResponse(
        job_id=job_id_str,
        job_type=job.job_type,
        status=JobStatus.PENDING,
        asset_id=job.asset_id,
        created_at=now,
        updated_at=now,
        progress=0.0,
        error=None,
    )

    _jobs_store[job_id_str] = job_response
    return job_response


# In-memory job storage for legacy endpoints
_jobs_store: dict[str, JobResponse] = {}
_job_counter = 0
