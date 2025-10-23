# PODStudio

[![CI Pipeline](https://github.com/TheSeeker713/PODStudio/actions/workflows/ci.yml/badge.svg)](https://github.com/TheSeeker713/PODStudio/actions/workflows/ci.yml)

**Windows-first desktop app for building store-ready print-on-demand AI asset packs**

## Overview

PODStudio is a minimalist, video-editor-style desktop application that helps POD (Print-on-Demand) creators organize, curate, enhance, and package AI-generated assets (images, audio, video) into professional, marketplace-ready packs.

### Key Features

- **Smart Asset Ingestion**: Auto-detect, sort, and organize AI-generated files
- **Non-Destructive Curation**: Approve/reject workflow with keyboard-first UX
- **AI Enhancement Pipelines**: Background removal, upscaling, transcoding, normalization
- **Hardware-Aware Processing**: GPU/CPU capability detection with safe fallbacks
- **Professional Pack Builder**: Auto-generate README, LICENSE, manifest, store copy
- **Zero/Minimal-AI Mode**: Template-based prompt generation (no LLM calls)
- **Offline-First**: No network calls; optional cloud mode for future

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    PySide6 Desktop UI                       │
│   (Top Bar, Docks: Instructions/Grid/Inspector, Tray)      │
└─────────────────┬───────────────────────────────────────────┘
                  │
┌─────────────────▼───────────────────────────────────────────┐
│              FastAPI Backend Service                        │
│           (localhost:8765, async routes)                    │
└─────────────────┬───────────────────────────────────────────┘
                  │
┌─────────────────▼───────────────────────────────────────────┐
│          Worker Queue (ThreadPool / RQ)                     │
│  Jobs: bg-remove, upscale, transcode, normalize, export     │
└─────────────────┬───────────────────────────────────────────┘
                  │
┌─────────────────▼───────────────────────────────────────────┐
│     SQLite DB (Assets, Jobs, Packs) + File Watcher         │
└─────────────────┬───────────────────────────────────────────┘
                  │
┌─────────────────▼───────────────────────────────────────────┐
│   External Tools: FFmpeg, ExifTool, Real-ESRGAN, rembg     │
└─────────────────────────────────────────────────────────────┘
```

## Tech Stack

- **UI**: PySide6 (Qt 6)
- **Backend**: FastAPI + Uvicorn
- **Database**: SQLite + SQLModel
- **Workers**: ThreadPoolExecutor (RQ optional)
- **Media**: Pillow, OpenCV, rembg, FFmpeg, pydub
- **Quality**: Ruff, Black, isort, pytest, pre-commit

## Project Status

✅ **Milestone 3 Complete** — File Ingestion & Curation UX  
🚧 **Currently**: Asset grid with thumbnails, multi-select, and curation actions functional

**Completed Milestones**:
- ✅ M1: Project Bootstrap
- ✅ M2: UI Skeleton & Database  
- ✅ M3: File Ingestion & Curation (File watcher, thumbnails, grid, curation controls)

**Next Up**: M4 - Advanced Curation & Filters

See [docs/product/roadmap.md](docs/product/roadmap.md) for detailed milestones.

## Documentation

All documentation lives under `/docs`:

- **Product**: [vision.md](docs/product/vision.md), [north_star.md](docs/product/north_star.md), [roadmap.md](docs/product/roadmap.md)
- **Specs**: [ui_spec.md](docs/specs/ui_spec.md), [pack_format_spec.md](docs/specs/pack_format_spec.md), [manifest_schema.md](docs/specs/manifest_schema.md)
- **Architecture**: [overview.md](docs/architecture/overview.md), [data_model.md](docs/architecture/data_model.md), [hardware_policy.md](docs/architecture/hardware_policy.md)
- **UX**: [ux_spec.md](docs/ux_spec.md) - Complete UI/UX specification with wireframes
- **Operations**: [install_windows.md](docs/ops/install_windows.md), [external_tools.md](docs/ops/external_tools.md)

## Installation (Windows)

See [docs/ops/install_windows.md](docs/ops/install_windows.md) for full setup instructions.

### Quick Start

```powershell
# Clone repo
git clone https://github.com/TheSeeker713/PODStudio.git
cd PODStudio

# Create venv
python -m venv .venv
.\.venv\Scripts\activate

# Install dependencies
python -m pip install --upgrade pip wheel setuptools pip-tools
pip-compile requirements.in -o requirements.txt
pip install -r requirements.txt

# Copy environment template
copy .env.example .env

# Run app
python -m app.ui.app
```

## Development

### Running the Application

**Option 1: Desktop UI Only** (Current - M3 Complete)
```powershell
python -m app.ui.app
```
The UI now includes:
- Asset grid with thumbnails (images, audio, video)
- File watcher for auto-ingestion
- Curation controls (Approve, Reject, Tag, Move, Rename)
- Multi-select support (Ctrl+Click, Shift+Click)
- Database-backed asset management

**Option 2: Backend + UI Together** (Optional - for API testing)

Open **two terminal windows**:

**Terminal 1 - Backend API**:
```powershell
python -m uvicorn app.backend.server:app --reload --port 8971
```

**Terminal 2 - Desktop UI**:
```powershell
python -m app.ui.app
```

**Backend API docs** (when backend is running): http://127.0.0.1:8971/docs  
**Available endpoints**: `/api/health`, `/api/probe`, `/api/jobs`

---

### Prerequisites

- Python 3.11+ (tested on 3.13)
- FFmpeg (optional - for video thumbnails)
- Git for version control

### Development Setup

```powershell
# Install dev dependencies
pip install -r dev-requirements.txt

# Install pre-commit hooks
pre-commit install

# Run quality checks
ruff check .
black --check .

# Run tests
pytest
```

## Current Features (M3 Complete)

✅ **Asset Management**
- File watcher automatically detects new assets
- MIME type detection and organization
- SQLite database with Asset, Job, Pack models

✅ **Thumbnail System**
- Image thumbnails via Pillow (128x128, cached)
- Video thumbnails via ffmpeg (1-second frame)
- Colored placeholders for audio files

✅ **Curation UX**
- Grid view with asset cards showing thumbnails and status
- Multi-select with Ctrl+Click (toggle) and Shift+Click (range)
- Context menu: Approve, Reject/Delete, Tag, Move, Rename
- Right dock inspector showing asset metadata
- File operations with collision handling (_1, _2 suffixes)
- Database synchronization on all operations

✅ **UI Shell**
- PySide6 desktop app with dock layout
- Top bar, left dock (controls), right dock (inspector)
- Bottom selection tray
- Theme system with color tokens

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for branch model, commit conventions, and PR process.

## License

Apache-2.0 — See [LICENSE](LICENSE)

---

**Built for POD Creators** | Windows-First | Offline-Capable | Hardware-Aware
