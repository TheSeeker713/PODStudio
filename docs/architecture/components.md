# PODStudio Architecture — Components

**Version**: 0.3.0  
**Last Updated**: October 22, 2025  
**Status**: STEP 3 - Backend skeleton implemented

---

## System Components

PODStudio consists of three main layers:

### 1. **Desktop UI Layer** (PySide6)

**Technology**: PySide6 (Qt 6)  
**Process**: Main application process  
**Status**: STEP 2 - Scaffolded

**Components**:
- `app/ui/app.py` - QApplication entry point
- `app/ui/main_window.py` - Main window with dock layout
- `app/ui/widgets/` - UI widgets (top bar, docks, grids, tray)
- `app/ui/helpers/` - UI helpers (backend status checker)
- `app/ui/themes/` - Design tokens and stylesheets

**Responsibilities**:
- Present asset library, preview, and controls
- Handle user input (keyboard shortcuts, clicks)
- Communicate with backend API for heavy operations
- Display hardware status and job progress
- Manage window state and preferences

---

### 2. **Backend API Layer** (FastAPI)

**Technology**: FastAPI + Uvicorn  
**Process**: Separate process on `http://127.0.0.1:8971`  
**Status**: STEP 3 - Skeleton implemented

**Components**:
- `app/backend/server.py` - FastAPI application
- `app/backend/routes/health.py` - Health check endpoint
- `app/backend/routes/probe.py` - Hardware detection endpoint (stub)
- `app/backend/routes/jobs.py` - Job management endpoints (stub)
- `app/backend/models/schemas.py` - Pydantic models

**Endpoints**:

| Endpoint | Method | Description | Status |
|----------|--------|-------------|--------|
| `/` | GET | Root - API info | ✅ Implemented |
| `/api/health` | GET | Health check | ✅ Implemented |
| `/api/probe` | GET | Hardware detection | ✅ Stub (returns "unknown") |
| `/api/jobs` | POST | Create background job | ✅ Stub (in-memory) |
| `/api/jobs/{id}` | GET | Get job status | ✅ Stub |
| `/api/jobs/{id}` | DELETE | Cancel job | ✅ Stub |

**Responsibilities**:
- Expose REST API for heavy operations
- Run background jobs (upscale, bg removal, transcoding)
- Detect GPU/CPU/RAM capabilities
- Return hardware tier (GREEN/YELLOW/RED)
- Manage job queue and progress tracking

**Future Endpoints** (Step 4+):
- `/api/assets` - Asset CRUD operations
- `/api/packs` - Pack creation and export
- WebSocket for real-time job progress

---

### 3. **Core Logic Layer**

**Technology**: Python standard library + domain logic  
**Process**: Shared between UI and Backend  
**Status**: STEP 1-3 - Stubs and placeholders

**Components**:
- `app/core/config.py` - Settings from `.env` (Pydantic)
- `app/core/logging.py` - Logger factory (placeholder)
- `app/core/db.py` - Database connection (SQLModel, future)
- `app/core/filetypes.py` - File type detection (stub)
- `app/core/watcher.py` - File system watcher (stub)
- `app/core/thumbnails.py` - Thumbnail generation (stub)
- `app/core/probe.py` - Hardware probing (stub)
- `app/core/packer.py` - Pack builder (stub)
- `app/core/prompts.py` - Prompt templates (stub)
- `app/core/utils.py` - Utility functions (stub)

**Responsibilities**:
- Provide shared logic for UI and backend
- Manage configuration and settings
- Interface with external tools (FFmpeg, ExifTool, etc.)
- Database operations (SQLModel ORM)
- File system monitoring

---

## Component Interaction

```
┌──────────────────────────────────────────────────────────┐
│  Desktop UI (PySide6)                                    │
│  - Main Window                                           │
│  - Asset Grid                                            │
│  - Top Bar (API status, hardware pill)  ←───┐           │
│  - Selection Tray                            │           │
└──────────────────────────────────────────────┼───────────┘
                   │                           │
                   │ HTTP GET/POST             │
                   ↓                           │
┌──────────────────────────────────────────────┼───────────┐
│  Backend API (FastAPI)                       │           │
│  http://127.0.0.1:8971                       │           │
│                                              │           │
│  ┌──────────────┐   ┌────────────────────┐  │           │
│  │ /api/health  │   │  /api/probe        │  │           │
│  │ Status: OK   │   │  Mode: UNKNOWN     │──┘           │
│  └──────────────┘   └────────────────────┘              │
│                                                          │
│  ┌──────────────────────────────────────────┐           │
│  │ /api/jobs                                │           │
│  │ - POST: Create job                       │           │
│  │ - GET: Query status                      │           │
│  │ - DELETE: Cancel job                     │           │
│  └──────────────────────────────────────────┘           │
└──────────────────────────────────────────────────────────┘
                   │
                   │ Calls core logic
                   ↓
┌──────────────────────────────────────────────────────────┐
│  Core Logic Layer                                        │
│  - app/core/config.py (Settings)                         │
│  - app/core/logging.py (Logger)                          │
│  - app/core/db.py (Database)                             │
│  - app/core/probe.py (Hardware detection)                │
│  - app/workers/queue.py (Job queue)                      │
└──────────────────────────────────────────────────────────┘
```

---

## Communication Flow

### 1. **UI ↔ Backend API**

**Protocol**: HTTP REST  
**Format**: JSON  
**Connection**: Localhost only (127.0.0.1)  
**Auth**: None (local-only, trusted environment)

**STEP 3 Implementation**:
- UI pings backend on startup with `BackendStatusChecker`
- Sends HTTP GET to `/api/health` and `/api/probe`
- Updates top bar with connection status
- No error popups - just visual indicators

**Future (Step 4+)**:
- UI creates jobs via POST `/api/jobs`
- Polls job status via GET `/api/jobs/{id}`
- Displays progress in job queue widget
- WebSocket for real-time updates

---

### 2. **Backend → Core Logic**

**Protocol**: Direct function calls  
**Format**: Python objects  

**STEP 3 Status**: Stub implementations  
**Future**: Backend routes will call core modules for actual processing

---

### 3. **UI → Core Logic** (Direct)

**Protocol**: Direct imports  
**Format**: Python objects

**Used for**:
- Reading settings (`app.core.config.settings`)
- Logging (`app.core.logging.get_logger()`)
- Lightweight operations (file type detection, etc.)

---

## Security Model

### Local-Only Design

PODStudio is designed for **local desktop use only**:

- **No remote access**: Backend only listens on `127.0.0.1` (localhost)
- **No authentication**: Assumes single-user trusted environment
- **No encryption**: HTTP (not HTTPS) since it's localhost
- **CORS**: Allows localhost origins only

### Future Considerations (Optional)

If remote access is ever needed:
- Add API token authentication
- Implement HTTPS with self-signed certs
- Rate limiting for API endpoints
- Audit logging for sensitive operations

---

## Deployment Model

**STEP 3**: Developer runs two processes manually:

```powershell
# Terminal 1: Backend API
uvicorn app.backend.server:app --reload --port 8971

# Terminal 2: Desktop UI
python -m app.ui.app
```

**Future (Step 5+)**: Single launcher script:
- Start backend in background process
- Wait for health check to pass
- Launch UI
- On UI exit, terminate backend gracefully

---

## Technology Stack Summary

| Layer | Technology | Version | Purpose |
|-------|-----------|---------|---------|
| UI Framework | PySide6 | 6.x | Desktop application |
| Backend API | FastAPI | 0.x | REST API server |
| API Server | Uvicorn | 0.x | ASGI server |
| Validation | Pydantic | 2.x | Schema validation |
| Database | SQLite | 3.x | Local asset database |
| ORM | SQLModel | 0.x | Database models |
| Config | pydantic-settings | 2.x | .env configuration |
| Job Queue | ThreadPoolExecutor | stdlib | Background tasks |
| Logging | logging | stdlib | Application logs |

---

**Next Steps (Step 4+)**:
- Implement real hardware probing (GPU detection)
- Add database models for assets
- Connect job queue to actual processing workers
- Implement WebSocket for real-time progress
- Add asset CRUD endpoints

---

**Related Documentation**:
- `/docs/architecture/overview.md` - High-level architecture
- `/docs/architecture/hardware_policy.md` - Hardware detection details
- `/docs/specs/ui_spec.md` - UI component specification
