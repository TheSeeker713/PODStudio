"""
Health Check Routes
STEP 3: Simple health endpoint to verify API is running
"""

from datetime import UTC, datetime

from fastapi import APIRouter

from app.backend.models.schemas import HealthResponse

router = APIRouter()


@router.get("/health", response_model=HealthResponse)
async def health_check():
    """
    Health check endpoint

    Returns API status and version. Used by UI to verify backend is running.
    """
    return HealthResponse(
        status="ok",
        version="0.1.0",
        timestamp=datetime.now(UTC),
    )
