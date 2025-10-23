"""
Jobs Routes - Background Job Management
STEP 3: Stub endpoints for job CRUD operations
"""

from datetime import UTC, datetime

from fastapi import APIRouter, HTTPException

from app.backend.models.schemas import JobCreate, JobResponse, JobStatus

router = APIRouter()

# In-memory job storage (placeholder - will use database later)
_jobs_store: dict[str, JobResponse] = {}
_job_counter = 0


@router.post("/jobs", response_model=JobResponse, status_code=201)
async def create_job(job: JobCreate):
    """
    Create a new background job (STUB)

    Accepts job creation request and returns job ID.
    Does not actually process anything yet.

    TODO (Step 4+): Connect to actual job queue (RQ or ThreadPoolExecutor)
    """
    global _job_counter
    _job_counter += 1
    job_id = f"job_{_job_counter:04d}"

    now = datetime.now(UTC)
    job_response = JobResponse(
        job_id=job_id,
        job_type=job.job_type,
        status=JobStatus.PENDING,
        asset_id=job.asset_id,
        created_at=now,
        updated_at=now,
        progress=0.0,
        error=None,
    )

    _jobs_store[job_id] = job_response
    return job_response


@router.get("/jobs/{job_id}", response_model=JobResponse)
async def get_job(job_id: str):
    """
    Retrieve job status by ID (STUB)

    Returns job details if found, 404 otherwise.
    """
    if job_id not in _jobs_store:
        raise HTTPException(status_code=404, detail=f"Job {job_id} not found")

    return _jobs_store[job_id]


@router.delete("/jobs/{job_id}", status_code=204)
async def delete_job(job_id: str):
    """
    Cancel/delete a job (STUB)

    Removes job from in-memory store.
    Does not actually cancel running processes yet.

    TODO (Step 4+): Implement actual job cancellation
    """
    if job_id not in _jobs_store:
        raise HTTPException(status_code=404, detail=f"Job {job_id} not found")

    del _jobs_store[job_id]
    return None
