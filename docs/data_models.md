# PODStudio — Data Models Specification

**Version:** 1.0.0  
**Date:** October 22, 2025  
**Status:** Design Specification

---

## Table of Contents

1. [Overview](#overview)
2. [Entity Relationship Diagram](#entity-relationship-diagram)
3. [Asset Model](#asset-model)
4. [Job Model](#job-model)
5. [Pack Model](#pack-model)
6. [Settings Model](#settings-model)
7. [Manifest Schema](#manifest-schema)
8. [Database Indexes](#database-indexes)
9. [Validation Rules](#validation-rules)

---

## Overview

PODStudio uses **SQLite** as the embedded database with **SQLModel** (or peewee) as the ORM layer. All models use:
- **UUIDs** for primary keys (collision-free, opaque)
- **Timestamps** in ISO 8601 format (UTC)
- **JSON fields** for flexible metadata and params
- **Enums** for constrained string values (enforced at application layer)

### Design Principles
- **Immutability:** Asset records never deleted; only marked rejected
- **Auditability:** All jobs logged; status transitions timestamped
- **Extensibility:** JSON fields for metadata allow schema evolution
- **Type Safety:** Python type hints + Pydantic validation

---

## Entity Relationship Diagram

```
┌─────────────────────────────────────────────────────────────────────────┐
│                                                                         │
│                          ┌──────────────┐                               │
│                          │   Settings   │                               │
│                          └──────────────┘                               │
│                                                                         │
│   ┌──────────────┐                        ┌──────────────┐             │
│   │    Asset     │◄────────────┬──────────│     Job      │             │
│   └──────┬───────┘             │          └──────┬───────┘             │
│          │                     │                 │                     │
│          │ many                │ many            │ many                │
│          │                     │                 │                     │
│          ▼                     │                 ▼                     │
│   ┌──────────────┐             │          ┌──────────────┐             │
│   │  PackAsset   │◄────────────┘          │  JobInput    │             │
│   │ (join table) │                        │ (optional)   │             │
│   └──────┬───────┘                        └──────────────┘             │
│          │                                                              │
│          │ many                                                         │
│          │                                                              │
│          ▼                                                              │
│   ┌──────────────┐                                                     │
│   │     Pack     │                                                     │
│   └──────────────┘                                                     │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

### Relationships
- **Asset ↔ Job:** Many-to-many (via job inputs/outputs)
- **Pack ↔ Asset:** Many-to-many (via PackAsset join table)
- **Job:** Standalone entity; references assets by ID

---

## Asset Model

Represents a single digital asset (image, audio, or video file).

### Fields

| Field Name          | Type             | Constraints            | Description                                                   |
|---------------------|------------------|------------------------|---------------------------------------------------------------|
| `id`                | UUID             | PK, NOT NULL           | Unique identifier                                             |
| `path`              | TEXT             | NOT NULL, UNIQUE       | Absolute file path on disk                                    |
| `filename`          | TEXT             | NOT NULL               | Original filename (without path)                              |
| `hash`              | TEXT             | NOT NULL, INDEXED      | SHA-256 hash for deduplication                                |
| `type`              | ENUM(TEXT)       | NOT NULL               | `image`, `audio`, `video`                                     |
| `mime_type`         | TEXT             | NULL                   | MIME type (e.g., `image/png`, `audio/mpeg`)                   |
| `size_bytes`        | INTEGER          | NOT NULL               | File size in bytes                                            |
| `created_at`        | TIMESTAMP        | NOT NULL               | Record creation time (ISO 8601 UTC)                           |
| `file_modified_at`  | TIMESTAMP        | NULL                   | File's last modified timestamp                                |
| `source`            | ENUM(TEXT)       | NOT NULL               | `watched`, `imported`, `generated` (derived from job)         |
| `source_path`       | TEXT             | NULL                   | Original watched folder or import source                      |
| `generator_meta`    | JSON             | NULL                   | Extracted metadata (platform, model, seed, etc.)              |
| `width`             | INTEGER          | NULL                   | Image/video width in pixels                                   |
| `height`            | INTEGER          | NULL                   | Image/video height in pixels                                  |
| `duration`          | FLOAT            | NULL                   | Audio/video duration in seconds                               |
| `fps`               | FLOAT            | NULL                   | Video frames per second                                       |
| `sample_rate`       | INTEGER          | NULL                   | Audio sample rate in Hz (e.g., 44100, 48000)                  |
| `channels`          | INTEGER          | NULL                   | Audio channels (1=mono, 2=stereo)                             |
| `codec`             | TEXT             | NULL                   | General codec (e.g., `h264`, `aac`, `png`)                    |
| `video_codec`       | TEXT             | NULL                   | Video-specific codec                                          |
| `audio_codec`       | TEXT             | NULL                   | Audio-specific codec                                          |
| `tags`              | JSON (array)     | DEFAULT `[]`           | User-applied tags (e.g., `["dragon", "fantasy", "fire"]`)     |
| `theme`             | TEXT             | NULL, INDEXED          | Primary theme/category (e.g., `fantasy`, `scifi`)             |
| `approved`          | BOOLEAN          | DEFAULT FALSE          | User approval status                                          |
| `rejected`          | BOOLEAN          | DEFAULT FALSE          | User rejection (soft delete)                                  |
| `rating`            | INTEGER          | NULL, CHECK (1-5)      | User rating (1-5 stars)                                       |
| `notes`             | TEXT             | NULL                   | User freeform notes                                           |
| `prompt_ref`        | TEXT             | NULL                   | Path to linked prompt file or FK to Prompt table (future)     |
| `thumbnail_path`    | TEXT             | NULL                   | Path to cached thumbnail (relative to project Cache/)         |
| `parent_asset_id`   | UUID (FK)        | NULL                   | If derived from another asset (e.g., upscaled version)        |
| `metadata_extracted`| BOOLEAN          | DEFAULT FALSE          | Whether metadata extraction ran successfully                  |

### Enums

**Type:**
- `image`
- `audio`
- `video`

**Source:**
- `watched` — Auto-detected by file watcher
- `imported` — Manually imported by user
- `generated` — Created by job (e.g., upscale, bg-removal)

### Example Record (JSON representation)

```json
{
  "id": "a3f7e912-4b5c-4d3e-8f2a-1c9d8e7f6a5b",
  "path": "C:\\Users\\Alice\\Documents\\PODStudio\\Projects\\MyProject\\Library\\images\\fantasy\\20251022\\dragon_fire.png",
  "filename": "dragon_fire.png",
  "hash": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
  "type": "image",
  "mime_type": "image/png",
  "size_bytes": 8589934,
  "created_at": "2025-10-22T14:23:01.234Z",
  "file_modified_at": "2025-10-22T14:20:00.000Z",
  "source": "watched",
  "source_path": "C:\\Users\\Alice\\Downloads",
  "generator_meta": {
    "platform": "midjourney",
    "model": "v6",
    "prompt": "dark fantasy dragon breathing fire...",
    "seed": 123456
  },
  "width": 2048,
  "height": 2048,
  "duration": null,
  "fps": null,
  "sample_rate": null,
  "channels": null,
  "codec": "png",
  "video_codec": null,
  "audio_codec": null,
  "tags": ["dragon", "fire", "fantasy"],
  "theme": "fantasy",
  "approved": true,
  "rejected": false,
  "rating": 5,
  "notes": "Perfect for hero banner",
  "prompt_ref": "/prompts/dragon_fire_20251022.txt",
  "thumbnail_path": "Cache/thumbnails/a3f7e912-4b5c-4d3e-8f2a-1c9d8e7f6a5b.jpg",
  "parent_asset_id": null,
  "metadata_extracted": true
}
```

---

## Job Model

Represents a background processing task (e.g., upscale, bg-removal, pack export).

### Fields

| Field Name          | Type             | Constraints            | Description                                                   |
|---------------------|------------------|------------------------|---------------------------------------------------------------|
| `id`                | UUID             | PK, NOT NULL           | Unique identifier                                             |
| `kind`              | ENUM(TEXT)       | NOT NULL               | Job type (see below)                                          |
| `status`            | ENUM(TEXT)       | NOT NULL               | `queued`, `running`, `success`, `failed`, `canceled`          |
| `progress`          | INTEGER          | DEFAULT 0, CHECK (0-100)| Completion percentage                                        |
| `params`            | JSON             | NOT NULL               | Job-specific parameters (e.g., scale factor, model choice)    |
| `input_asset_ids`   | JSON (array)     | DEFAULT `[]`           | UUIDs of input assets                                         |
| `output_asset_ids`  | JSON (array)     | DEFAULT `[]`           | UUIDs of generated assets (populated on success)              |
| `created_at`        | TIMESTAMP        | NOT NULL               | Job creation time                                             |
| `started_at`        | TIMESTAMP        | NULL                   | Worker start time                                             |
| `finished_at`       | TIMESTAMP        | NULL                   | Completion time                                               |
| `error_message`     | TEXT             | NULL                   | Error description if failed                                   |
| `logs_path`         | TEXT             | NULL                   | Path to detailed log file                                     |
| `hardware_mode`     | ENUM(TEXT)       | NULL                   | `gpu`, `cpu`, `cpu+mem` (used mode)                           |
| `estimated_duration`| INTEGER          | NULL                   | Estimated duration in seconds (calculated pre-run)            |

### Enums

**Kind:**
- `bg_remove` — Background removal
- `upscale` — Image/video upscaling
- `transcode` — Video format conversion
- `normalize` — Audio loudness normalization
- `trim` — Audio/video trimming
- `crop` — Image cropping
- `thumbnail` — Thumbnail generation
- `pack_export` — Pack building and ZIP creation
- `metadata_extract` — Deep metadata extraction

**Status:**
- `queued` — Waiting in queue
- `running` — Currently executing
- `success` — Completed successfully
- `failed` — Error occurred
- `canceled` — User canceled

**Hardware Mode:**
- `gpu` — Used GPU acceleration
- `cpu` — CPU-only (no GPU)
- `cpu+mem` — CPU with high memory usage (e.g., large images)

### Example Record

```json
{
  "id": "b7c2d5e8-3a4f-4c5e-9b2a-8d7c6e5f4a3b",
  "kind": "upscale",
  "status": "success",
  "progress": 100,
  "params": {
    "scale_factor": 2,
    "model": "RealESRGAN_x2plus",
    "output_format": "png",
    "use_gpu": true
  },
  "input_asset_ids": ["a3f7e912-4b5c-4d3e-8f2a-1c9d8e7f6a5b"],
  "output_asset_ids": ["c9e1f3a5-7b8d-4e2f-9c3a-1d5e6f7a8b9c"],
  "created_at": "2025-10-22T14:30:00.000Z",
  "started_at": "2025-10-22T14:30:05.123Z",
  "finished_at": "2025-10-22T14:32:19.456Z",
  "error_message": null,
  "logs_path": "Logs/jobs/b7c2d5e8-3a4f-4c5e-9b2a-8d7c6e5f4a3b.log",
  "hardware_mode": "gpu",
  "estimated_duration": 120
}
```

---

## Pack Model

Represents an exported asset pack ready for distribution.

### Fields

| Field Name          | Type             | Constraints            | Description                                                   |
|---------------------|------------------|------------------------|---------------------------------------------------------------|
| `id`                | UUID             | PK, NOT NULL           | Unique identifier                                             |
| `name`              | TEXT             | NOT NULL               | Pack display name (e.g., "Fantasy Dragon Collection")         |
| `slug`              | TEXT             | NOT NULL, UNIQUE       | URL-safe slug (e.g., "fantasy-dragon-collection")             |
| `theme`             | TEXT             | NULL                   | Primary theme/category                                        |
| `description`       | TEXT             | NULL                   | Long-form description for README                              |
| `license_type`      | ENUM(TEXT)       | NOT NULL               | `personal`, `commercial`, `extended`                          |
| `export_dir`        | TEXT             | NOT NULL               | Directory path for pack files                                 |
| `zip_path`          | TEXT             | NULL                   | Path to final ZIP archive (null if not yet built)             |
| `version`           | TEXT             | DEFAULT "1.0.0"        | Semantic version                                              |
| `manifest_version`  | TEXT             | DEFAULT "1.0"          | Manifest schema version                                       |
| `created_at`        | TIMESTAMP        | NOT NULL               | Pack creation time                                            |
| `exported_at`       | TIMESTAMP        | NULL                   | Export completion time                                        |
| `status`            | ENUM(TEXT)       | NOT NULL               | `draft`, `building`, `completed`, `failed`                    |
| `export_options`    | JSON             | NOT NULL               | Export config (see below)                                     |
| `hardware_profile`  | JSON             | NULL                   | Snapshot of hardware used for processing                      |
| `asset_count`       | INTEGER          | DEFAULT 0              | Cached count of included assets                               |
| `total_size_bytes`  | INTEGER          | DEFAULT 0              | Total uncompressed size of assets                             |

### Enums

**License Type:**
- `personal` — Personal/non-commercial use
- `commercial` — Standard commercial use
- `extended` — Extended commercial (higher sales limits, multi-seat)

**Status:**
- `draft` — Pack created but not yet exported
- `building` — Export in progress
- `completed` — Successfully exported
- `failed` — Export failed

### Export Options (JSON)

```json
{
  "include_prompts": true,
  "generate_readme": true,
  "generate_store_copy": true,
  "generate_manifest": true,
  "include_checksums": true,
  "platform_variants": ["gumroad", "etsy"],
  "readme_template": "default",
  "store_copy_template": "default"
}
```

### Hardware Profile (JSON)

Snapshot captured during pack export:

```json
{
  "gpu_vendor": "NVIDIA",
  "gpu_model": "GeForce RTX 3060",
  "vram_mb": 8192,
  "cpu_threads": 12,
  "ram_gb": 32,
  "mode": "gpu",
  "os": "Windows 11",
  "app_version": "1.0.0"
}
```

### Example Record

```json
{
  "id": "d1e2f3a4-5b6c-7d8e-9f0a-1b2c3d4e5f6a",
  "name": "Fantasy Dragon Collection",
  "slug": "fantasy-dragon-collection",
  "theme": "fantasy",
  "description": "50 high-resolution fantasy dragon images...",
  "license_type": "commercial",
  "export_dir": "C:\\...\\Packs\\Fantasy_Dragon_Collection_20251022",
  "zip_path": "C:\\...\\Packs\\Fantasy_Dragon_Collection_20251022.zip",
  "version": "1.0.0",
  "manifest_version": "1.0",
  "created_at": "2025-10-22T15:00:00.000Z",
  "exported_at": "2025-10-22T15:05:32.123Z",
  "status": "completed",
  "export_options": { /* as above */ },
  "hardware_profile": { /* as above */ },
  "asset_count": 20,
  "total_size_bytes": 157286400
}
```

### PackAsset Join Table

Links packs to assets (many-to-many).

| Field Name    | Type       | Constraints       | Description                        |
|---------------|------------|-------------------|------------------------------------|
| `id`          | UUID       | PK, NOT NULL      | Join record ID                     |
| `pack_id`     | UUID       | FK → Pack, NOT NULL| Pack reference                    |
| `asset_id`    | UUID       | FK → Asset, NOT NULL| Asset reference                  |
| `order_index` | INTEGER    | DEFAULT 0         | Display order within pack          |
| `notes`       | TEXT       | NULL              | Asset-specific notes for this pack |

---

## Settings Model

Stores user preferences and application configuration.

### Fields

| Field Name          | Type             | Constraints            | Description                                                   |
|---------------------|------------------|------------------------|---------------------------------------------------------------|
| `id`                | UUID             | PK, NOT NULL           | Unique identifier                                             |
| `key`               | TEXT             | UNIQUE, NOT NULL       | Setting key (e.g., `watch_folders`, `ui_density`)             |
| `value`             | JSON             | NOT NULL               | Setting value (flexible type)                                 |
| `updated_at`        | TIMESTAMP        | NOT NULL               | Last update time                                              |

### Example Records

```json
[
  {
    "id": "...",
    "key": "watch_folders",
    "value": [
      {"path": "C:\\Users\\Alice\\Downloads", "enabled": true},
      {"path": "C:\\Generations", "enabled": true}
    ],
    "updated_at": "2025-10-22T10:00:00.000Z"
  },
  {
    "id": "...",
    "key": "ui_density",
    "value": "normal",
    "updated_at": "2025-10-22T09:00:00.000Z"
  },
  {
    "id": "...",
    "key": "default_license_type",
    "value": "commercial",
    "updated_at": "2025-10-22T08:00:00.000Z"
  },
  {
    "id": "...",
    "key": "auto_approve_threshold",
    "value": 4,
    "updated_at": "2025-10-22T07:00:00.000Z"
  }
]
```

---

## Manifest Schema

The `manifest.json` file exported with each pack. Versioned for forward compatibility.

### Version 1.0 Schema

```json
{
  "manifest_version": "1.0",
  "app_version": "1.0.0",
  "exported_at": "2025-10-22T15:05:32.123Z",
  "pack": {
    "id": "d1e2f3a4-5b6c-7d8e-9f0a-1b2c3d4e5f6a",
    "name": "Fantasy Dragon Collection",
    "slug": "fantasy-dragon-collection",
    "theme": "fantasy",
    "description": "50 high-resolution fantasy dragon images for game assets, book covers...",
    "license_type": "commercial",
    "version": "1.0.0",
    "asset_count": 20,
    "total_size_bytes": 157286400
  },
  "assets": [
    {
      "asset_id": "a3f7e912-4b5c-4d3e-8f2a-1c9d8e7f6a5b",
      "filename": "dragon_fire.png",
      "rel_path": "assets/dragon_fire.png",
      "type": "image",
      "mime_type": "image/png",
      "width": 2048,
      "height": 2048,
      "size_bytes": 8589934,
      "hash": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
      "tags": ["dragon", "fire", "fantasy"],
      "generator_meta": {
        "platform": "midjourney",
        "model": "v6",
        "prompt": "dark fantasy dragon breathing fire...",
        "seed": 123456
      },
      "prompts": [
        {
          "platform": "midjourney",
          "text": "dark fantasy dragon breathing fire over medieval castle at sunset --ar 1:1 --v 6 --style raw",
          "negatives": null
        },
        {
          "platform": "sdxl",
          "text": "majestic dragon, fire breath, medieval castle, sunset sky, dramatic lighting, highly detailed",
          "negatives": "blurry, low quality, cartoon, anime"
        }
      ],
      "edits": [
        {
          "kind": "upscale",
          "params": {"scale_factor": 2, "model": "RealESRGAN_x2plus"},
          "timestamp": "2025-10-22T14:32:19.456Z"
        }
      ]
    },
    {
      "asset_id": "...",
      "filename": "castle_wall.jpg",
      "rel_path": "assets/castle_wall.jpg",
      "type": "image",
      "mime_type": "image/jpeg",
      "width": 1920,
      "height": 1080,
      "size_bytes": 2048576,
      "hash": "...",
      "tags": ["castle", "medieval", "wall"],
      "generator_meta": null,
      "prompts": [],
      "edits": []
    }
  ],
  "checksums": {
    "assets/dragon_fire.png": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
    "assets/castle_wall.jpg": "...",
    "README.md": "...",
    "LICENSE.txt": "...",
    "store_copy.txt": "...",
    "manifest.json": "self"
  },
  "hardware_profile": {
    "gpu_vendor": "NVIDIA",
    "gpu_model": "GeForce RTX 3060",
    "vram_mb": 8192,
    "cpu_threads": 12,
    "ram_gb": 32,
    "mode": "gpu",
    "os": "Windows 11"
  }
}
```

### Manifest Schema Definition (JSON Schema)

Formal validation schema (for reference; not code):

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "object",
  "required": ["manifest_version", "app_version", "exported_at", "pack", "assets"],
  "properties": {
    "manifest_version": {"type": "string"},
    "app_version": {"type": "string"},
    "exported_at": {"type": "string", "format": "date-time"},
    "pack": {
      "type": "object",
      "required": ["id", "name", "license_type"],
      "properties": {
        "id": {"type": "string", "format": "uuid"},
        "name": {"type": "string"},
        "slug": {"type": "string"},
        "theme": {"type": "string"},
        "description": {"type": "string"},
        "license_type": {"enum": ["personal", "commercial", "extended"]},
        "version": {"type": "string"},
        "asset_count": {"type": "integer"},
        "total_size_bytes": {"type": "integer"}
      }
    },
    "assets": {
      "type": "array",
      "items": {
        "type": "object",
        "required": ["asset_id", "filename", "rel_path", "type"],
        "properties": {
          "asset_id": {"type": "string", "format": "uuid"},
          "filename": {"type": "string"},
          "rel_path": {"type": "string"},
          "type": {"enum": ["image", "audio", "video"]},
          "mime_type": {"type": "string"},
          "width": {"type": "integer"},
          "height": {"type": "integer"},
          "duration": {"type": "number"},
          "size_bytes": {"type": "integer"},
          "hash": {"type": "string"},
          "tags": {"type": "array", "items": {"type": "string"}},
          "generator_meta": {"type": ["object", "null"]},
          "prompts": {"type": "array"},
          "edits": {"type": "array"}
        }
      }
    },
    "checksums": {
      "type": "object",
      "additionalProperties": {"type": "string"}
    },
    "hardware_profile": {"type": "object"}
  }
}
```

---

## Database Indexes

For performance optimization on common queries.

### Asset Table
```sql
CREATE INDEX idx_assets_type ON assets(type);
CREATE INDEX idx_assets_theme ON assets(theme);
CREATE INDEX idx_assets_approved ON assets(approved);
CREATE INDEX idx_assets_rejected ON assets(rejected);
CREATE INDEX idx_assets_created_at ON assets(created_at);
CREATE INDEX idx_assets_hash ON assets(hash);
CREATE UNIQUE INDEX idx_assets_path ON assets(path);
```

### Job Table
```sql
CREATE INDEX idx_jobs_status ON jobs(status);
CREATE INDEX idx_jobs_kind ON jobs(kind);
CREATE INDEX idx_jobs_created_at ON jobs(created_at);
```

### Pack Table
```sql
CREATE INDEX idx_packs_status ON packs(status);
CREATE INDEX idx_packs_created_at ON packs(created_at);
CREATE UNIQUE INDEX idx_packs_slug ON packs(slug);
```

### PackAsset Table
```sql
CREATE INDEX idx_packassets_pack_id ON pack_assets(pack_id);
CREATE INDEX idx_packassets_asset_id ON pack_assets(asset_id);
CREATE UNIQUE INDEX idx_packassets_unique ON pack_assets(pack_id, asset_id);
```

### Settings Table
```sql
CREATE UNIQUE INDEX idx_settings_key ON settings(key);
```

---

## Validation Rules

### Asset Validation

- **Path:** Must be absolute; must exist on disk (checked on create)
- **Type:** Must be one of `image`, `audio`, `video`
- **Hash:** Must be 64-character SHA-256 hex string
- **Dimensions:** If type=image/video, width and height must be > 0
- **Duration:** If type=audio/video, duration must be > 0
- **Rating:** If set, must be 1-5
- **Approved/Rejected:** Cannot both be true

### Job Validation

- **Progress:** Must be 0-100
- **Input Asset IDs:** Must reference existing assets (FK validation)
- **Status Transitions:** Enforce valid state machine:
  - `queued` → `running` or `canceled`
  - `running` → `success` or `failed` or `canceled`
  - Terminal states (`success`, `failed`, `canceled`) cannot transition

### Pack Validation

- **Name:** Non-empty, max 255 chars
- **Slug:** Lowercase alphanumeric + hyphens, unique
- **License Type:** Must be `personal`, `commercial`, or `extended`
- **Asset Count:** Must match number of linked PackAsset records

### Settings Validation

- **Key:** Non-empty, unique
- **Value:** Must be valid JSON

---

## Data Migration Strategy

### Initial Setup (v1.0)
- Use simple `CREATE TABLE IF NOT EXISTS` statements
- No formal migration tool required

### Future Migrations (v1.1+)
- Use **Alembic** or simple versioned SQL scripts
- Store schema version in Settings table: `{"key": "schema_version", "value": "1"}`
- On app start, check version and run migrations if needed

---

## Backup & Recovery

### Automatic Backups
- On app shutdown, copy `podstudio.db` to `podstudio.db.backup`
- Keep last 7 backups: `podstudio.db.backup.{yyyymmdd}`

### User-Initiated Backups
- Settings → Backup → Creates timestamped ZIP of:
  - `podstudio.db`
  - `config.json`
  - `/Logs/` (last 7 days)

### Recovery
- Settings → Restore → Select backup ZIP
- Restore files, restart app

---

**End of Data Models Specification**  
**Next Steps:** Review schemas, validate field types, approve before implementation.
