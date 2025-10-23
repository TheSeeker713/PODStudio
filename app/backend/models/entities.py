"""
SQLModel Entity Classes
STEP 4: Database models for Asset, Pack, and Job

These are the core domain models stored in SQLite.
"""

from datetime import UTC, datetime
from enum import Enum

from sqlmodel import Field, SQLModel

# ============================================================
# Enums
# ============================================================


class AssetType(str, Enum):
    """Type of media asset"""

    IMAGE = "image"
    AUDIO = "audio"
    VIDEO = "video"


class AssetProvenance(str, Enum):
    """Source/origin of the asset"""

    UNKNOWN = "unknown"
    AI_GENERATED = "ai_generated"
    USER_PROVIDED = "user_provided"
    ENHANCED = "enhanced"  # Processed by PODStudio


class JobKind(str, Enum):
    """Type of background job"""

    UPSCALE = "upscale"
    BG_REMOVE = "bg_remove"
    TRANSCODE = "transcode"
    NORMALIZE_AUDIO = "normalize_audio"
    THUMBNAIL = "thumbnail"
    EXPORT_PACK = "export_pack"


class JobStatus(str, Enum):
    """Status of a background job"""

    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class LicenseType(str, Enum):
    """Pack license type"""

    PERSONAL = "personal"
    COMMERCIAL = "commercial"
    EDITORIAL = "editorial"
    CUSTOM = "custom"


# ============================================================
# Entity Models
# ============================================================


class Asset(SQLModel, table=True):
    """
    Asset - Individual media file (image, audio, video)

    Represents a single asset in the Library.
    Created by file watcher when new files are detected.
    """

    __tablename__ = "assets"

    id: int | None = Field(default=None, primary_key=True)

    # File Information
    path: str = Field(index=True, unique=True, description="Absolute file path")
    type: AssetType = Field(index=True, description="Asset media type")
    hash: str | None = Field(default=None, index=True, description="File content hash (SHA256)")

    # Metadata (filled by probing in future steps)
    width: int | None = Field(default=None, description="Image/video width in pixels")
    height: int | None = Field(default=None, description="Image/video height in pixels")
    duration: float | None = Field(default=None, description="Audio/video duration in seconds")
    samplerate: int | None = Field(default=None, description="Audio sample rate in Hz")

    # Classification
    theme: str | None = Field(default=None, index=True, description="Asset theme/category (fantasy, sci-fi, etc)")
    source: str | None = Field(default=None, description="Source model/tool (e.g., 'Midjourney', 'DALL-E')")
    provenance: AssetProvenance = Field(
        default=AssetProvenance.UNKNOWN, index=True, description="Asset origin/source type"
    )

    # Curation
    approved: bool = Field(default=False, index=True, description="User approved for inclusion in pack")

    # Timestamps
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC), description="When asset was ingested")
    updated_at: datetime = Field(default_factory=lambda: datetime.now(UTC), description="Last modification time")


class Pack(SQLModel, table=True):
    """
    Pack - Collection of assets ready for export

    Represents a curated collection of assets packaged for distribution.
    """

    __tablename__ = "packs"

    id: int | None = Field(default=None, primary_key=True)

    # Pack Information
    name: str = Field(index=True, description="Pack display name")
    theme: str | None = Field(default=None, index=True, description="Pack theme (fantasy, sci-fi, etc)")
    description: str | None = Field(default=None, description="Pack description for README")

    # Licensing
    license_type: LicenseType = Field(default=LicenseType.PERSONAL, description="License type")

    # Metadata
    asset_count: int = Field(default=0, description="Number of assets in pack")
    total_size_mb: float = Field(default=0.0, description="Total pack size in MB")

    # Export
    export_path: str | None = Field(default=None, description="Path to exported .zip file")
    exported_at: datetime | None = Field(default=None, description="When pack was last exported")

    # Timestamps
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC), description="When pack was created")
    updated_at: datetime = Field(default_factory=lambda: datetime.now(UTC), description="Last modification time")


class Job(SQLModel, table=True):
    """
    Job - Background processing task

    Tracks async operations like upscaling, transcoding, etc.
    """

    __tablename__ = "jobs"

    id: int | None = Field(default=None, primary_key=True)

    # Job Details
    kind: JobKind = Field(index=True, description="Type of job")
    asset_id: int | None = Field(default=None, index=True, description="Asset being processed (if applicable)")
    pack_id: int | None = Field(default=None, index=True, description="Pack being processed (if applicable)")

    # Parameters (JSON-serialized)
    params_json: str | None = Field(default=None, description="Job parameters as JSON string")

    # Status
    status: JobStatus = Field(default=JobStatus.PENDING, index=True, description="Current job status")
    progress: float = Field(default=0.0, ge=0.0, le=1.0, description="Progress (0.0 to 1.0)")

    # Results
    result_path: str | None = Field(default=None, description="Path to output file (if applicable)")
    error_message: str | None = Field(default=None, description="Error message if failed")

    # Timestamps
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC), description="When job was created")
    started_at: datetime | None = Field(default=None, description="When job started running")
    completed_at: datetime | None = Field(default=None, description="When job finished (success or failure)")
