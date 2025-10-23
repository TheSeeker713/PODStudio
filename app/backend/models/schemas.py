"""
Pydantic Schemas for Backend API
STEP 3: Stub models for health, probe, and jobs endpoints
"""

from datetime import datetime
from enum import Enum

from pydantic import BaseModel, Field

# ============================================================
# Health Endpoint Schemas
# ============================================================


class HealthResponse(BaseModel):
    """Response from /api/health endpoint"""

    status: str = Field(default="ok", description="Health status of the API")
    version: str = Field(default="0.1.0", description="API version")
    timestamp: datetime | None = Field(default=None, description="Server timestamp")


# ============================================================
# Probe Endpoint Schemas
# ============================================================


class HardwareMode(str, Enum):
    """Hardware capability tier"""

    UNKNOWN = "unknown"
    GREEN = "green"  # GPU available, plenty of VRAM
    YELLOW = "yellow"  # Limited GPU or low VRAM
    RED = "red"  # CPU only


class ProbeResponse(BaseModel):
    """Response from /api/probe endpoint - hardware detection stub"""

    gpu: str = Field(default="unknown", description="GPU name or 'unknown'")
    vram_gb: float | None = Field(default=None, description="Available VRAM in GB")
    cpu_threads: int | None = Field(default=None, description="CPU thread count")
    ram_gb: float | None = Field(default=None, description="System RAM in GB")
    mode: HardwareMode = Field(default=HardwareMode.UNKNOWN, description="Hardware capability tier")


# ============================================================
# Jobs Endpoint Schemas
# ============================================================


class JobType(str, Enum):
    """Type of processing job"""

    UPSCALE = "upscale"
    BG_REMOVE = "bg_remove"
    TRANSCODE = "transcode"
    THUMBNAIL = "thumbnail"


class JobStatus(str, Enum):
    """Status of a job"""

    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class JobCreate(BaseModel):
    """Request to create a new job"""

    job_type: JobType = Field(..., description="Type of job to run")
    asset_id: str = Field(..., description="ID of asset to process")
    params: dict = Field(default_factory=dict, description="Job-specific parameters")


class JobResponse(BaseModel):
    """Response from job creation or retrieval"""

    job_id: str = Field(..., description="Unique job ID")
    job_type: JobType = Field(..., description="Type of job")
    status: JobStatus = Field(..., description="Current job status")
    asset_id: str = Field(..., description="Asset being processed")
    created_at: datetime = Field(..., description="Job creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")
    progress: float = Field(default=0.0, ge=0.0, le=1.0, description="Progress (0.0 to 1.0)")
    error: str | None = Field(default=None, description="Error message if failed")
