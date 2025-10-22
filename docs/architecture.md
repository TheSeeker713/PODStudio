# PODStudio — Architecture Specification

**Version:** 1.0.0  
**Date:** October 22, 2025  
**Status:** Design Specification

---

## Table of Contents

1. [System Overview](#system-overview)
2. [Component Architecture](#component-architecture)
3. [Process Model](#process-model)
4. [Data Flow](#data-flow)
5. [Job Lifecycle](#job-lifecycle)
6. [Technology Stack](#technology-stack)
7. [Directory Structure](#directory-structure)
8. [Security & Privacy](#security--privacy)
9. [Deployment Modes](#deployment-modes)

---

## System Overview

PODStudio is a **hybrid desktop application** with:
- **Frontend:** PySide6 (Qt) GUI running as the main process
- **Backend:** FastAPI local HTTP service for async/heavy tasks
- **Workers:** ThreadPoolExecutor for concurrent job execution
- **Storage:** SQLite database + file system for assets
- **External Tools:** ffmpeg, ffprobe, exiftool (bundled or PATH-detected)

### Design Principles
- **Single-user, local-first:** No cloud dependency by default
- **Event-driven:** File watcher triggers ingestion; UI subscribes to job events
- **Non-blocking:** Long operations run in background; UI remains responsive
- **Fail-safe:** Graceful degradation; never crash on bad input or missing tools
- **Reproducible:** Deterministic outputs; version-stamped manifests

---

## Component Architecture

```
┌─────────────────────────────────────────────────────────────────────────┐
│                          PODStudio Application                          │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  ┌──────────────────────────────────────────────────────────────────┐  │
│  │                      UI Layer (PySide6/Qt)                       │  │
│  ├──────────────────────────────────────────────────────────────────┤  │
│  │ - Main Window (QMainWindow)                                      │  │
│  │ - Dock Widgets (Prompts, Listener, Filters, Inspector, Actions) │  │
│  │ - Central Tabbed View (Images/Audio/Video grids)                 │  │
│  │ - Dialogs (Pack Builder, Settings, Jobs Panel)                   │  │
│  │ - Models (QAbstractItemModel for asset grids)                    │  │
│  └───────────────────────┬──────────────────────────────────────────┘  │
│                          │ Qt Signals/Slots                            │
│  ┌───────────────────────▼──────────────────────────────────────────┐  │
│  │              Application Controller (Python)                     │  │
│  ├──────────────────────────────────────────────────────────────────┤  │
│  │ - Asset Manager (CRUD operations)                                │  │
│  │ - Job Manager (queue, monitor, cancel jobs)                      │  │
│  │ - Pack Builder (orchestrate export)                              │  │
│  │ - Prompt Generator (template engine or LLM client)               │  │
│  │ - Hardware Profiler (detect GPU/CPU/RAM)                         │  │
│  │ - Settings Manager (load/save config)                            │  │
│  └───────────────────────┬──────────────────────────────────────────┘  │
│                          │ HTTP/IPC                                     │
│  ┌───────────────────────▼──────────────────────────────────────────┐  │
│  │             Backend Service (FastAPI, Uvicorn)                   │  │
│  ├──────────────────────────────────────────────────────────────────┤  │
│  │ Endpoints:                                                        │  │
│  │ - POST /jobs/bg-remove                                           │  │
│  │ - POST /jobs/upscale                                             │  │
│  │ - POST /jobs/transcode                                           │  │
│  │ - POST /jobs/normalize                                           │  │
│  │ - GET /jobs/{id}/status                                          │  │
│  │ - POST /jobs/{id}/cancel                                         │  │
│  │ - GET /assets (query with filters)                               │  │
│  │ - POST /assets (create record)                                   │  │
│  │ - POST /packs/build                                              │  │
│  └───────────────────────┬──────────────────────────────────────────┘  │
│                          │ Thread Pool                                 │
│  ┌───────────────────────▼──────────────────────────────────────────┐  │
│  │                Worker Pool (ThreadPoolExecutor)                  │  │
│  ├──────────────────────────────────────────────────────────────────┤  │
│  │ - Background Removal Worker (rembg)                              │  │
│  │ - Upscale Worker (Real-ESRGAN)                                   │  │
│  │ - Transcode Worker (ffmpeg subprocess)                           │  │
│  │ - Audio Normalize Worker (pydub + ffmpeg)                        │  │
│  │ - Thumbnail Generator (Pillow / ffmpeg)                          │  │
│  │ - Pack Export Worker (file copy + ZIP)                           │  │
│  └───────────────────────┬──────────────────────────────────────────┘  │
│                          │ File I/O, DB writes                         │
│  ┌───────────────────────▼──────────────────────────────────────────┐  │
│  │                  Storage & Data Layer                            │  │
│  ├──────────────────────────────────────────────────────────────────┤  │
│  │ - SQLite Database (SQLModel ORM)                                 │  │
│  │   Tables: assets, jobs, packs, settings                          │  │
│  │ - File System:                                                   │  │
│  │   /Library/{type}/{theme}/{date}/                                │  │
│  │   /Work/edits|upscales|masks/                                    │  │
│  │   /Packs/{pack_name}/                                            │  │
│  │   /Cache/thumbnails/                                             │  │
│  │   /Logs/                                                         │  │
│  └──────────────────────────────────────────────────────────────────┘  │
│                                                                         │
│  ┌──────────────────────────────────────────────────────────────────┐  │
│  │             External Services (Sidecar Processes)                │  │
│  ├──────────────────────────────────────────────────────────────────┤  │
│  │ - File Watcher (watchdog) — separate thread                      │  │
│  │ - ffmpeg/ffprobe — subprocesses spawned as needed                │  │
│  │ - exiftool — subprocess for metadata extraction                  │  │
│  │ - Optional: Local LLM server (Ollama/etc.) for prompts           │  │
│  └──────────────────────────────────────────────────────────────────┘  │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

### Component Responsibilities

#### UI Layer (PySide6)
- Render windows, docks, dialogs
- Handle user input (clicks, keyboard, drag-drop)
- Display asset grids (thumbnails from cache)
- Emit signals for controller actions
- Subscribe to job/asset update events

#### Application Controller
- Business logic layer between UI and backend
- Orchestrates multi-step workflows (e.g., pack export)
- Manages application state (current project, selected assets)
- Proxies requests to backend service via HTTP
- Handles hardware profiling and capability checks

#### Backend Service (FastAPI)
- RESTful API for async operations
- Job queue management (create, monitor, cancel)
- Database queries (complex filters, aggregations)
- Exposes worker pool for heavy tasks
- Runs on localhost (127.0.0.1:8765 by default)

#### Worker Pool
- Executes CPU/GPU-intensive operations
- Isolated from UI thread
- Reports progress via callbacks
- Handles errors and retries
- Writes logs to `/Logs/jobs/{job_id}.log`

#### Storage Layer
- **SQLite:** Transactional metadata store
- **File System:** Asset files, derived files, caches
- **Checksums:** SHA-256 for integrity verification

#### External Services
- **watchdog:** File system event monitoring
- **ffmpeg/ffprobe:** Video/audio analysis and transcoding
- **exiftool:** EXIF/metadata extraction
- **rembg:** Background removal (U2Net model)
- **Real-ESRGAN:** Image upscaling

---

## Process Model

### Startup Sequence

1. **Launch Main Process**
   - Parse CLI args (project path, config path)
   - Initialize logging (console + file)
   - Load settings from `~/.podstudio/config.json`

2. **Hardware Profiling**
   - Detect GPU vendor (NVIDIA/AMD/Intel/None)
   - Query VRAM (via pynvml for NVIDIA, default estimates for others)
   - Query CPU threads (`os.cpu_count()`)
   - Query RAM (`psutil.virtual_memory()`)
   - Check ffmpeg/ffprobe/exiftool availability
   - Write profile to `~/.podstudio/hardware_profile.json`
   - Determine capability tier (GREEN/YELLOW/RED)

3. **Start Backend Service**
   - Spawn FastAPI/Uvicorn in subprocess (or thread for simplicity)
   - Wait for health check (`GET /health` returns 200)
   - On failure: Display error dialog and exit gracefully

4. **Initialize Database**
   - Connect to SQLite at `{project_path}/podstudio.db`
   - Run migrations (create tables if missing)
   - Load settings from DB

5. **Start File Watcher**
   - If any watched folders configured and enabled:
     - Start watchdog observer in background thread
     - Register event handlers for create/move events

6. **Show Main Window**
   - Render UI with saved layout (dock positions, sizes)
   - Load last-opened project or show empty state
   - Display hardware indicator in top bar
   - App is ready for user interaction

### Shutdown Sequence

1. **User Initiates Quit**
   - `Ctrl+Q` or clicks [×] button

2. **Check for Active Jobs**
   - Query backend: `GET /jobs?status=running`
   - If any: Show confirmation dialog
     - "3 jobs are still running. Cancel them and quit?"
     - [Cancel Jobs & Quit] [Continue Working]

3. **Stop File Watcher**
   - Stop watchdog observer
   - Wait for thread to join (max 2s timeout)

4. **Stop Backend Service**
   - Send shutdown signal to FastAPI process
   - Wait for graceful shutdown (max 5s timeout)
   - Force kill if timeout exceeded

5. **Save State**
   - Save window geometry and dock layout
   - Save current filters/view settings
   - Flush DB transactions

6. **Exit**
   - Close main window
   - Terminate process

---

## Data Flow

### Flow 1: Auto-Ingest New Asset

```
[User drops file in Downloads]
          ↓
[watchdog detects create event]
          ↓
[File Watcher Handler runs]
    • Check file extension and MIME type
    • Wait for write completion (file size stable)
    • Extract metadata (ffprobe/exiftool)
          ↓
[POST /assets to Backend]
    • Calculate SHA-256 hash
    • Detect asset type (image/audio/video)
    • Parse generator metadata if present
    • Determine theme from filename/metadata
    • Route to /Library/{type}/{theme}/{yyyymmdd}/
    • Copy/move file to destination
          ↓
[Backend creates DB record]
    • Insert into `assets` table
    • Generate thumbnail (async job)
          ↓
[Backend emits asset-created event]
          ↓
[UI receives event via polling or WebSocket]
    • Refresh asset grid
    • Show toast notification
    • Thumbnail appears when ready
```

### Flow 2: User Requests Background Removal

```
[User selects asset, clicks "Remove Background"]
          ↓
[UI → Controller: bg_remove(asset_id)]
          ↓
[Controller checks hardware capability]
    • Requires: 4GB RAM, 2GB VRAM (GPU) or 8GB RAM (CPU)
    • If insufficient: Show error dialog, abort
    • If borderline: Show warning, user confirms
          ↓
[Controller → Backend: POST /jobs/bg-remove]
    Request body:
    {
      "asset_id": "uuid",
      "output_format": "png",
      "model": "u2net",
      "use_gpu": true
    }
          ↓
[Backend creates Job record in DB]
    • status = "queued"
    • params = request body
          ↓
[Backend submits task to Worker Pool]
    • ThreadPoolExecutor.submit(bg_remove_worker, job_id, params)
          ↓
[Worker executes]
    1. Load asset file
    2. Initialize rembg session (loads U2Net model)
    3. Process image (remove background)
    4. Update job progress in DB (0% → 100%)
    5. Save output to /Work/edits/{asset_id}_nobg.png
    6. Create new Asset record for output
    7. Update job status = "success"
          ↓
[Backend emits job-completed event]
          ↓
[UI polls job status or receives event]
    • Update Jobs panel (move to Completed)
    • Show success notification
    • Refresh asset grid (new asset appears)
```

### Flow 3: Build Pack

```
[User selects 20 assets, clicks "Build Pack"]
          ↓
[UI opens Pack Builder modal]
    • Pre-fills name, theme from selection
          ↓
[User fills details, clicks "Build Pack"]
          ↓
[UI → Controller: build_pack(pack_config, asset_ids)]
          ↓
[Controller → Backend: POST /packs/build]
    Request body:
    {
      "name": "Fantasy Dragons",
      "theme": "fantasy",
      "description": "...",
      "license_type": "commercial",
      "asset_ids": ["uuid1", "uuid2", ...],
      "export_options": {
        "include_prompts": true,
        "generate_readme": true,
        ...
      }
    }
          ↓
[Backend creates Pack record in DB]
          ↓
[Backend submits task to Worker Pool]
    • ThreadPoolExecutor.submit(pack_export_worker, pack_id)
          ↓
[Worker executes]
    1. Create directory: /Packs/{name}_{date}/
    2. Create subdirs: assets/, prompts/
    3. Copy assets to assets/ (progress 0-50%)
    4. Generate README.md (template + data)
    5. Generate LICENSE.txt (from license_type)
    6. Generate store_copy.txt (marketing blurb)
    7. Generate manifest.json (full metadata)
    8. Copy prompts to prompts/ if available
    9. Calculate SHA-256 checksums (progress 50-80%)
    10. Write checksums.txt
    11. Create ZIP archive (progress 80-100%)
    12. Update Pack record: zip_path, status = "completed"
          ↓
[Backend emits pack-completed event]
          ↓
[UI receives event]
    • Close progress spinner
    • Show success dialog with [Open Folder] button
```

---

## Job Lifecycle

### States

```
┌──────────┐
│  queued  │  Initial state when job created
└────┬─────┘
     │
     ▼
┌──────────┐
│ running  │  Worker picked up job from queue
└────┬─────┘
     │
     ├──────► (success) ──────┐
     │                        │
     ├──────► (failed) ────┐  │
     │                     │  │
     └──────► (canceled) ──┤  │
                           │  │
                           ▼  ▼
                      ┌────────────┐
                      │  terminal  │  (success/failed/canceled)
                      └────────────┘
```

### Transitions

- **queued → running:** Worker starts execution
- **running → success:** Task completes without error
- **running → failed:** Exception raised or validation failed
- **running → canceled:** User cancels or system stops
- **queued → canceled:** Canceled before execution starts

### Persistence

Jobs table schema (subset):
```
id (uuid PK)
kind (enum: bg_remove, upscale, transcode, normalize, pack_export, ...)
status (enum: queued, running, success, failed, canceled)
progress (int 0-100)
params (json)
input_asset_ids (json array)
output_asset_ids (json array, populated on success)
started_at (timestamp, null if queued)
finished_at (timestamp, null if not finished)
error_message (text, null if success)
logs_path (text, path to job log file)
```

### Monitoring

- **UI Polling:** Every 1s, `GET /jobs?status=running,queued` to update Jobs panel
- **Alternative (WebSocket):** Backend can push job updates to UI via WebSocket for real-time updates (future enhancement)

### Cancellation

- **User Action:** Click [Cancel] in Jobs panel
- **Process:**
  1. UI → Backend: `POST /jobs/{id}/cancel`
  2. Backend sets job.status = "canceled"
  3. Worker checks `job.status` periodically during execution
  4. If "canceled", worker stops gracefully, cleans up temp files
  5. Backend emits job-canceled event

### Retry

- **Manual Retry:** User clicks [Retry] on failed job
- **Process:**
  1. UI → Backend: `POST /jobs/{id}/retry`
  2. Backend creates new Job with same params
  3. New job queued, old job remains in "failed" state for audit

---

## Technology Stack

### Core Language
- **Python 3.11+** (type hints, performance)

### UI Framework
- **PySide6 (Qt 6.x):** Cross-platform GUI
  - QMainWindow, QDockWidget, QTreeView, QGridView
  - QAbstractItemModel for asset grids
  - QThreadPool for background tasks in UI layer

### Backend Service
- **FastAPI:** Modern async web framework
- **Uvicorn:** ASGI server (runs on localhost:8765)
- **pydantic:** Request/response validation

### Database
- **SQLite:** Embedded, serverless, transactional
- **SQLModel:** ORM with Pydantic integration (or peewee as alternative)
- **Alembic:** Schema migrations (optional; simple CREATE IF NOT EXISTS for v1)

### File System
- **watchdog:** Cross-platform file watcher
- **pathlib:** Modern path handling (Python stdlib)

### Media Processing
- **Images:**
  - Pillow (PIL fork): Read, write, resize, crop
  - OpenCV (cv2): Advanced ops (optional)
  - rembg: Background removal (U2Net model)
  - Real-ESRGAN: Upscaling (ncnn or PyTorch backend)
  - CodeFormer: Face restoration (optional)

- **Video:**
  - ffmpeg: Transcode, trim, thumbnails (subprocess)
  - ffprobe: Metadata extraction (subprocess)
  - ESRGAN-ncnn-vulkan: Upscaling (optional, if Vulkan available)

- **Audio:**
  - pydub: High-level audio ops (wraps ffmpeg)
  - ffmpeg: Normalization, format conversion
  - audiowaveform: PNG waveform generation (optional; fallback to matplotlib)

### Utilities
- **exiftool:** Metadata extraction (subprocess; optional)
- **psutil:** System info (CPU, RAM)
- **pynvml:** NVIDIA GPU info (VRAM, driver)
- **GPUtil:** GPU detection (fallback)

### Prompt System
- **Jinja2:** Template engine for prompt generation
- **Optional:** httpx for LLM API calls (OpenAI, local Ollama)

### Packaging
- **PyInstaller** or **cx_Freeze:** Bundle to .exe for Windows
- **NSIS:** Installer generator (optional)

---

## Directory Structure

### Application Root (User's Project)
```
C:\Users\{name}\Documents\PODStudio\Projects\{project_name}\

├── podstudio.db              # SQLite database
├── config.json               # Project-specific settings
│
├── Library\                  # Organized asset storage
│   ├── images\
│   │   ├── fantasy\
│   │   │   ├── 20251022\
│   │   │   │   ├── dragon_fire.png
│   │   │   │   ├── castle_wall.jpg
│   │   │   └── 20251023\
│   │   └── scifi\
│   ├── audio\
│   │   └── epic\
│   │       └── 20251022\
│   │           ├── battle_theme.mp3
│   │           └── ambient_wind.wav
│   └── video\
│       └── fantasy\
│           └── 20251022\
│               └── dragon_flight.mp4
│
├── Work\                     # Derived/intermediate files
│   ├── edits\
│   │   ├── dragon_fire_nobg.png
│   │   └── castle_wall_crop.png
│   ├── upscales\
│   │   └── dragon_fire_2x.png
│   └── masks\
│       └── dragon_fire_mask.png
│
├── Packs\                    # Exported packs
│   ├── Fantasy_Dragons_20251022\
│   │   ├── assets\
│   │   │   ├── dragon_fire.png
│   │   │   └── castle_wall.jpg
│   │   ├── prompts\
│   │   │   └── dragon_fire.txt
│   │   ├── manifest.json
│   │   ├── README.md
│   │   ├── LICENSE.txt
│   │   ├── store_copy.txt
│   │   └── checksums.txt
│   └── Fantasy_Dragons_20251022.zip
│
├── Cache\                    # Temporary/regenerable data
│   ├── thumbnails\           # Asset thumbnails
│   │   ├── {asset_id}.jpg
│   │   └── ...
│   └── models\               # Downloaded ML models
│       ├── u2net.onnx
│       └── RealESRGAN_x2plus.pth
│
└── Logs\                     # Application logs
    ├── app.log               # Main app log (rotating)
    ├── watcher.log           # File watcher log
    └── jobs\
        ├── {job_id}.log
        └── ...
```

### User Config Directory (Shared Across Projects)
```
C:\Users\{name}\.podstudio\

├── config.json               # Global settings
├── hardware_profile.json     # Latest hardware probe results
├── recent_projects.json      # MRU list
└── templates\
    └── prompts\
        ├── image_sdxl.j2
        ├── image_midjourney.j2
        ├── audio_suno.j2
        └── video_kling.j2
```

---

## Security & Privacy

### Principles
- **Local by default:** No data leaves machine without explicit user opt-in
- **No telemetry:** No crash reports, usage stats, or PII collected remotely
- **Sandboxed ML models:** Loaded from local cache; no internet fetch after initial download

### Threat Model (Out of Scope for v1)
- Multi-user access control (single-user app)
- Network security (no external network exposure)
- Malicious asset files (basic MIME validation only; not a security scanner)

### Safe Practices
- **Input Validation:** All user inputs sanitized (file paths, SQL queries via ORM)
- **Subprocess Safety:** Use `subprocess.run()` with explicit args (no shell injection)
- **File Permissions:** Assets stored with user-only read/write (Windows default)
- **Secrets Management:** API keys stored in OS keyring (future; manual entry for now)

---

## Deployment Modes

### Mode 1: Windows Desktop (Primary)

**Target:** Windows 10/11, x64

**Distribution:**
- Installer: `.exe` via NSIS or Inno Setup
- Portable: ZIP with pre-bundled Python runtime (embedded Python)
- PyPI: `pip install podstudio` for advanced users

**Dependencies Bundling:**
- Python runtime (embedded or installer)
- ffmpeg/ffprobe binaries (bundled in `bin/`)
- exiftool (optional; download helper if missing)
- ML models: Downloaded on first use to `~/.podstudio/models/`

**First Launch:**
1. Check for bundled ffmpeg; if missing, show download prompt
2. Run hardware profiler
3. Show welcome wizard: set watch folders, choose theme
4. Create default project in `Documents\PODStudio\My First Project\`

### Mode 2: Cloud-Friendly (Secondary, Future)

**Target:** Colab, Azure VM, AWS EC2 (headless)

**Architecture:**
- Backend service runs standalone (no PySide6 GUI)
- Thin web UI (React or Vue SPA) served by FastAPI
- User connects via browser: `http://localhost:8765`

**Use Case:**
- Heavy processing on cloud GPU (e.g., 4K video upscaling)
- Access from tablet/phone for monitoring
- Shared processing server (multi-user via simple auth)

**Deployment:**
```bash
# On cloud VM
$ pip install podstudio[server]
$ podstudio-server --host 0.0.0.0 --port 8765 --no-auth
# User accesses via browser or desktop app in remote mode
```

**Status:** Design placeholder; not implemented in v1.

---

## Extension Points (Future)

### Plugin System
- **Processor Plugins:** Register new enhancement operations
  - Interface: `class Processor(name, input_types, output_type, process_fn)`
  - Example: Custom AI model, noise reduction, watermarking

- **Exporter Plugins:** Custom pack formats
  - Interface: `class Exporter(name, export_fn)`
  - Example: Shopify-specific export, Unity asset bundle

- **Prompt Templates:** User-installable templates
  - Stored in `~/.podstudio/templates/prompts/`
  - Auto-discovered on app start

### API Extensibility
- Backend REST API can be used by external tools
- Example: CLI script to bulk-import assets without GUI

---

## Performance Considerations

### UI Responsiveness
- **Target:** <16ms frame time (60fps) for grid scrolling
- **Strategy:** Virtual scrolling (only render visible thumbnails)
- **Thumbnail Cache:** Pre-generate 200×200px JPEG thumbnails; lazy-load on demand

### Job Throughput
- **ThreadPoolExecutor Size:** `min(32, cpu_count() + 4)` (balanced)
- **GPU Serialization:** Only 1 GPU job at a time to avoid VRAM contention
- **CPU Jobs:** Parallel up to thread pool limit

### Database Scaling
- **Indexes:** On `assets.type`, `assets.theme`, `assets.created_at`, `assets.approved`
- **Expected Load:** 10k-100k assets; SQLite handles easily
- **Vacuum:** Periodic `VACUUM` to reclaim space (weekly background task)

### File System
- **Thumbnails:** Store separately from originals (faster access)
- **Cleanup:** Periodic orphan check (thumbnails with no DB record)

---

## Observability

### Logging
- **Levels:** DEBUG, INFO, WARNING, ERROR, CRITICAL
- **Destinations:**
  - Console (stdout): INFO+ during development
  - File (`Logs/app.log`): INFO+ with daily rotation (keep 7 days)
  - Job logs (`Logs/jobs/{job_id}.log`): DEBUG for troubleshooting

### Monitoring
- **Metrics (Future):**
  - Jobs completed/failed per hour
  - Average job duration by type
  - Cache hit rate (thumbnails)
- **Health Check:** `GET /health` returns 200 with system status

---

## Error Handling Strategy

### Levels

1. **Recoverable (Log & Continue):**
   - Thumbnail generation fails → skip, show placeholder
   - Metadata extraction fails → use defaults

2. **Actionable (Show Dialog, User Chooses):**
   - Insufficient hardware → explain, offer alternatives
   - File not found → locate or remove from library

3. **Fatal (Crash Prevention):**
   - Database corrupted → backup + recreate
   - Backend startup fails → fallback to read-only mode or exit with clear error

### User-Facing Messages
- **Never show stack traces to end users**
- **Always provide:**
  - What happened
  - Why it happened (if known)
  - What user can do next (actionable steps)

---

**End of Architecture Specification**  
**Next Steps:** Review component boundaries, validate technology choices, approve before implementation.
