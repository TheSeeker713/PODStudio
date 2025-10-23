# Data Model - PODStudio Database Schema

## Overview

PODStudio uses SQLModel (Pydantic + SQLAlchemy) with SQLite for local data persistence. The database stores three main entity types: **Assets**, **Packs**, and **Jobs**.

## Database Location

- **Development**: `./podstudio.db` (configurable via `DB_PATH` in `.env`)
- **Production**: Same (local desktop app)

## Schema Version

**STEP 4** - Initial schema with metadata stubs (no FFmpeg extraction yet)

---

## Table: `asset`

Stores media files detected by the file watcher or manually imported.

### Columns

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `id` | INTEGER | PRIMARY KEY | Auto-incrementing asset ID |
| `path` | TEXT | UNIQUE, NOT NULL, INDEXED | Absolute file path |
| `type` | TEXT | NOT NULL | Asset type: `image`, `audio`, `video` |
| `hash` | TEXT | NOT NULL | SHA-256 file hash (for deduplication) |
| `width` | INTEGER | NULLABLE | Image/video width in pixels (stub) |
| `height` | INTEGER | NULLABLE | Image/video height in pixels (stub) |
| `duration_sec` | REAL | NULLABLE | Audio/video duration in seconds (stub) |
| `samplerate_hz` | INTEGER | NULLABLE | Audio sample rate in Hz (stub) |
| `theme` | TEXT | NULLABLE | User-assigned theme (e.g., "nature", "tech") |
| `source` | TEXT | NULLABLE | Source description (e.g., "Midjourney") |
| `provenance` | TEXT | NOT NULL | Provenance: `unknown`, `ai_generated`, `user_provided`, `enhanced` |
| `approved` | BOOLEAN | NOT NULL, DEFAULT FALSE | Manual curation flag |
| `created_at` | TIMESTAMP | NOT NULL, DEFAULT UTC NOW | Record creation timestamp |
| `updated_at` | TIMESTAMP | NOT NULL, DEFAULT UTC NOW | Record update timestamp |

### Indexes

- `path` (UNIQUE) - Fast path lookups for deduplication

### Enums

#### AssetType
- `image` - PNG, JPG, GIF, BMP, TIFF, WebP
- `audio` - WAV, MP3, FLAC, OGG, M4A, AAC
- `video` - MP4, MOV, AVI, MKV, WebM, FLV

#### AssetProvenance
- `unknown` - Default for new assets
- `ai_generated` - Created by AI tools
- `user_provided` - User-uploaded originals
- `enhanced` - AI-upscaled or processed

---

## Table: `pack`

Stores asset pack metadata for export.

### Columns

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `id` | INTEGER | PRIMARY KEY | Auto-incrementing pack ID |
| `name` | TEXT | NOT NULL | Pack display name |
| `theme` | TEXT | NULLABLE | Pack theme (e.g., "fantasy", "sci-fi") |
| `description` | TEXT | NULLABLE | Pack description (optional) |
| `license_type` | TEXT | NOT NULL | License: `royalty_free`, `attribution`, `commercial`, `personal` |
| `asset_count` | INTEGER | NOT NULL, DEFAULT 0 | Number of assets in pack |
| `total_size_mb` | REAL | NOT NULL, DEFAULT 0.0 | Total pack size in MB |
| `export_path` | TEXT | NULLABLE | Path to exported pack ZIP |
| `exported_at` | TIMESTAMP | NULLABLE | Export completion timestamp |
| `created_at` | TIMESTAMP | NOT NULL, DEFAULT UTC NOW | Record creation timestamp |
| `updated_at` | TIMESTAMP | NOT NULL, DEFAULT UTC NOW | Record update timestamp |

### Enums

#### LicenseType
- `royalty_free` - No attribution required
- `attribution` - Attribution required
- `commercial` - Commercial use allowed
- `personal` - Personal use only

---

## Table: `job`

Stores background job metadata for async operations (upscaling, denoising, exporting).

### Columns

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `id` | INTEGER | PRIMARY KEY | Auto-incrementing job ID |
| `kind` | TEXT | NOT NULL | Job type (see JobKind enum) |
| `asset_id` | INTEGER | NULLABLE, FOREIGN KEY | Related asset ID (if applicable) |
| `pack_id` | INTEGER | NULLABLE, FOREIGN KEY | Related pack ID (if applicable) |
| `params_json` | TEXT | NULLABLE | JSON-encoded job parameters |
| `status` | TEXT | NOT NULL | Job status: `pending`, `running`, `completed`, `failed`, `cancelled` |
| `progress` | REAL | NOT NULL, DEFAULT 0.0 | Progress percentage (0.0 - 100.0) |
| `result_path` | TEXT | NULLABLE | Path to result file (if applicable) |
| `error_message` | TEXT | NULLABLE | Error message if failed |
| `created_at` | TIMESTAMP | NOT NULL, DEFAULT UTC NOW | Job creation timestamp |
| `started_at` | TIMESTAMP | NULLABLE | Job start timestamp |
| `completed_at` | TIMESTAMP | NULLABLE | Job completion timestamp |

### Enums

#### JobKind
- `upscale` - AI image upscaling
- `denoise_audio` - Audio noise removal
- `denoise_video` - Video noise removal
- `enhance` - General enhancement
- `export_pack` - Pack export to ZIP
- `metadata_extract` - Extract FFmpeg metadata

#### JobStatus
- `pending` - Queued but not started
- `running` - Currently executing
- `completed` - Finished successfully
- `failed` - Finished with error
- `cancelled` - User cancelled

---

## Relationships

### Future (STEP 5+)
- `pack_asset` - Many-to-many junction table for Pack ↔ Asset
- Foreign keys for `job.asset_id` → `asset.id` and `job.pack_id` → `pack.id`

---

## Migrations

**STEP 4**: No migration system yet - database recreated on schema changes.

**STEP 5+**: Alembic migrations for production schema updates.

---

## Query Examples

### Get all unapproved assets
```python
from sqlmodel import Session, select
from app.backend.models.entities import Asset

with Session(engine) as session:
    assets = session.exec(
        select(Asset).where(Asset.approved == False)
    ).all()
```

### Get all assets by theme
```python
assets = session.exec(
    select(Asset).where(Asset.theme == "nature")
).all()
```

### Get active jobs
```python
from app.backend.models.entities import Job, JobStatus

jobs = session.exec(
    select(Job).where(Job.status == JobStatus.RUNNING)
).all()
```

---

## File Watcher Behavior

When the file watcher detects a new supported file:

1. **Extension Check**: File must have supported extension (`.png`, `.wav`, `.mp4`, etc.)
2. **Hash Calculation**: SHA-256 hash computed for deduplication
3. **Deduplication**: Check if `path` already exists in `asset` table
4. **Insert Asset**: Create row with:
   - `type` = Inferred from extension
   - `approved` = `False` (requires manual approval)
   - `provenance` = `unknown` (requires curation)
   - `theme` = `None` (user must set)
   - Metadata fields (`width`, `height`, etc.) = `None` (stubs for STEP 5+)

---

## Notes

- **Timestamps**: All timestamps use timezone-aware UTC (`datetime.now(timezone.utc)`)
- **File Paths**: Stored as absolute paths (OS-specific)
- **Hashes**: SHA-256 in hexadecimal format
- **Metadata Stubs**: `width`, `height`, `duration_sec`, `samplerate_hz` are placeholders for STEP 5 FFmpeg integration
