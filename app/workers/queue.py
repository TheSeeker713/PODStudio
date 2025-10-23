"""
Worker Queue - Job Management

STEP 6: ThreadPool-based job queue for background processing

Uses ThreadPoolExecutor by default; RQ optional with Redis
"""

import json
from collections.abc import Callable
from concurrent.futures import Future, ThreadPoolExecutor
from datetime import UTC, datetime
from typing import Any

from sqlmodel import Session, select

from app.backend.models.entities import Job, JobKind, JobStatus
from app.core.db import get_engine
from app.core.logging import get_logger

logger = get_logger(__name__)

# Global executor instance
_executor: ThreadPoolExecutor | None = None
_active_jobs: dict[int, Future] = {}  # job_id -> Future

# Default settings
MAX_WORKERS = 4  # Can be overridden by settings in future


def get_executor() -> ThreadPoolExecutor:
    """Get or create the global thread pool executor"""
    global _executor
    if _executor is None:
        _executor = ThreadPoolExecutor(max_workers=MAX_WORKERS, thread_name_prefix="job_worker")
        logger.info(f"Initialized job executor with {MAX_WORKERS} workers")
    return _executor


def shutdown_executor():
    """Shutdown the executor (for testing/cleanup)"""
    global _executor
    if _executor:
        _executor.shutdown(wait=True)
        _executor = None
        logger.info("Job executor shutdown")


def enqueue_job(
    kind: JobKind,
    job_func: Callable,
    asset_id: int | None = None,
    pack_id: int | None = None,
    params: dict[str, Any] | None = None,
) -> int:
    """
    Enqueue a background job

    Args:
        kind: Type of job (JobKind enum)
        job_func: Function to execute (must accept job_id as first arg)
        asset_id: Optional asset ID being processed
        pack_id: Optional pack ID being processed
        params: Optional job parameters

    Returns:
        job_id: ID of the created job
    """
    engine = get_engine()

    # Create job record in database
    with Session(engine) as session:
        job = Job(
            kind=kind,
            asset_id=asset_id,
            pack_id=pack_id,
            params_json=json.dumps(params) if params else None,
            status=JobStatus.PENDING,
            progress=0.0,
        )
        session.add(job)
        session.commit()
        session.refresh(job)
        job_id = job.id

    if job_id is None:
        raise ValueError("Failed to create job - no ID returned")

    logger.info(f"Enqueued job {job_id}: {kind.value} (asset={asset_id}, pack={pack_id})")

    # Submit to thread pool
    executor = get_executor()
    future = executor.submit(_run_job, job_id, job_func)
    _active_jobs[job_id] = future

    return job_id


def _run_job(job_id: int, job_func: Callable):
    """
    Internal wrapper to run a job function with error handling

    Updates job status in database during execution
    """
    engine = get_engine()

    try:
        # Mark as running
        with Session(engine) as session:
            job = session.get(Job, job_id)
            if job:
                job.status = JobStatus.RUNNING
                job.started_at = datetime.now(UTC)
                session.add(job)
                session.commit()

        logger.info(f"Job {job_id} started")

        # Execute job function
        result_path = job_func(job_id)

        # Mark as completed
        with Session(engine) as session:
            job = session.get(Job, job_id)
            if job:
                job.status = JobStatus.COMPLETED
                job.progress = 1.0
                job.result_path = str(result_path) if result_path else None
                job.completed_at = datetime.now(UTC)
                session.add(job)
                session.commit()

        logger.info(f"Job {job_id} completed successfully")

    except Exception as e:
        # Mark as failed
        logger.error(f"Job {job_id} failed: {e}", exc_info=True)
        with Session(engine) as session:
            job = session.get(Job, job_id)
            if job:
                job.status = JobStatus.FAILED
                job.error_message = str(e)
                job.completed_at = datetime.now(UTC)
                session.add(job)
                session.commit()

    finally:
        # Cleanup
        if job_id in _active_jobs:
            del _active_jobs[job_id]


def get_job_status(job_id: int) -> dict[str, Any] | None:
    """
    Get current status of a job

    Returns:
        dict with status, progress, result_path, error_message
        None if job not found
    """
    engine = get_engine()
    with Session(engine) as session:
        job = session.get(Job, job_id)
        if not job:
            return None

        return {
            "id": job.id,
            "kind": job.kind.value,
            "status": job.status.value,
            "progress": job.progress,
            "result_path": job.result_path,
            "error_message": job.error_message,
            "created_at": job.created_at.isoformat() if job.created_at else None,
            "started_at": job.started_at.isoformat() if job.started_at else None,
            "completed_at": job.completed_at.isoformat() if job.completed_at else None,
        }


def update_job_progress(job_id: int, progress: float):
    """
    Update job progress (called by job functions)

    Args:
        job_id: Job ID
        progress: Progress value (0.0 to 1.0)
    """
    engine = get_engine()
    with Session(engine) as session:
        job = session.get(Job, job_id)
        if job:
            job.progress = max(0.0, min(1.0, progress))
            session.add(job)
            session.commit()


def cancel_job(job_id: int) -> bool:
    """
    Cancel a pending or running job

    Note: ThreadPool doesn't support true cancellation,
    so this just marks the job as cancelled in DB.
    The actual function may continue running.

    Returns:
        True if job was cancelled, False if not found or already complete
    """
    engine = get_engine()
    with Session(engine) as session:
        job = session.get(Job, job_id)
        if not job or job.status in (JobStatus.COMPLETED, JobStatus.FAILED, JobStatus.CANCELLED):
            return False

        job.status = JobStatus.CANCELLED
        job.completed_at = datetime.now(UTC)
        session.add(job)
        session.commit()

    logger.info(f"Job {job_id} cancelled")
    return True


def get_active_jobs() -> list[dict[str, Any]]:
    """Get list of all active (pending/running) jobs"""
    engine = get_engine()
    with Session(engine) as session:
        # Query jobs with PENDING or RUNNING status
        statement = select(Job).where((Job.status == JobStatus.PENDING) | (Job.status == JobStatus.RUNNING))
        jobs = session.exec(statement).all()

        return [
            {
                "id": job.id,
                "kind": job.kind.value,
                "status": job.status.value,
                "progress": job.progress,
                "created_at": job.created_at.isoformat() if job.created_at else None,
            }
            for job in jobs
        ]
