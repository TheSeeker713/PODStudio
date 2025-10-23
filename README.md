# PODStudio

[![CI Pipeline](https://github.com/<youruser>/PODStudio/actions/workflows/ci.yml/badge.svg)](https://github.com/<youruser>/PODStudio/actions/workflows/ci.yml)

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

🚧 **In Development** — Currently in Step 1 (Bootstrap)

See [docs/product/roadmap.md](docs/product/roadmap.md) for milestones.

## Documentation

All documentation lives under `/docs`:

- **Product**: [vision.md](docs/product/vision.md), [north_star.md](docs/product/north_star.md), [roadmap.md](docs/product/roadmap.md)
- **Specs**: [ui_spec.md](docs/specs/ui_spec.md), [pack_format_spec.md](docs/specs/pack_format_spec.md), [manifest_schema.md](docs/specs/manifest_schema.md)
- **Architecture**: [overview.md](docs/architecture/overview.md), [hardware_policy.md](docs/architecture/hardware_policy.md)
- **Operations**: [install_windows.md](docs/ops/install_windows.md), [external_tools.md](docs/ops/external_tools.md)

## Installation (Windows)

See [docs/ops/install_windows.md](docs/ops/install_windows.md) for full setup instructions.

### Quick Start

```powershell
# Clone repo
git clone https://github.com/<youruser>/PODStudio.git
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

# Run app (STEP 2: UI only, backend offline)
python -m app.ui.app
```

## Development

### Running the Application (STEP 3+)

**Option 1: Desktop UI Only**
```powershell
python -m app.ui.app
```
(Top bar will show "API: OFFLINE" since backend is not running)

**Option 2: Backend + UI Together** (Recommended)

Open **two terminal windows**:

**Terminal 1 - Backend API**:
```powershell
uvicorn app.backend.server:app --reload --port 8971
```

**Terminal 2 - Desktop UI**:
```powershell
python -m app.ui.app
```

Backend API docs available at: http://127.0.0.1:8971/docs

---

### Prerequisites

- Python 3.11+
- FFmpeg (added to PATH)
- ExifTool (recommended)
- Real-ESRGAN binaries (optional, for GPU upscaling)

### Setup

```powershell
# Install dev dependencies
pip-compile dev-requirements.in -o dev-requirements.txt
pip install -r dev-requirements.txt

# Install pre-commit hooks
pre-commit install

# Run quality checks
ruff check .
black --check .
isort --check .

# Run tests
pytest
```

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for branch model, commit conventions, and PR process.

## License

Apache-2.0 — See [LICENSE](LICENSE)

---

**Built for POD Creators** | Windows-First | Offline-Capable | Hardware-Aware
