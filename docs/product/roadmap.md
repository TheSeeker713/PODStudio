# PODStudio — Development Roadmap

**Version**: 0.1.0  
**Timeline**: Oct 2025 - Q2 2026  
**Last Updated**: October 22, 2025

---

## Milestone 1 (M1): Project Bootstrap ✅
**Status**: Complete  
**Duration**: Step 1 (1 week)  
**Goal**: Clean workspace, tooling, docs

### Deliverables
- [x] Python venv with all dependencies
- [x] Project structure (/app, /docs, /tests)
- [x] Git repo with CI placeholder
- [x] Design docs (vision, north_star, specs)
- [x] External tool documentation

---

## Milestone 2 (M2): UI Skeleton & Database
**Status**: ✅ Complete  
**Duration**: Step 2-3 (2 weeks)  
**Goal**: Empty UI shell + SQLite schema

### Deliverables
- [x] PySide6 main window with dock layout
- [x] Empty grid view (no thumbnails yet)
- [x] SQLModel schemas (Asset, Job, Pack)
- [x] Database migrations
- [x] Hardware probe (GPU/CPU/RAM detection)

---

## Milestone 3 (M3): File Ingestion & Curation
**Status**: ✅ Complete (STEP 4-5)  
**Duration**: Step 4-5 (2 weeks)  
**Goal**: Auto-detect, organize, and curate assets

### Deliverables
- [x] File watcher (watchdog integration)
- [x] MIME + ffprobe file type detection
- [x] Auto-organization to /Workspace/{theme}/{type}
- [x] Thumbnail generation (Pillow for images, ffmpeg for video, placeholders for audio)
- [x] Asset grid displays thumbnails with metadata
- [x] Multi-select support (Ctrl+Click, Shift+Click)
- [x] Right dock curation controls (Approve, Reject/Delete, Tag, Move, Rename)
- [x] File operations with collision handling
- [x] Database synchronization on all operations
- [x] Automatic grid refresh after curation actions

### Acceptance Criteria
- ✅ File watcher detects new files in monitored directories
- ✅ Assets automatically added to database with type detection
- ✅ Thumbnails generated and cached (Cache/thumbs/)
- ✅ Grid view shows asset cards with thumbnails and status
- ✅ User can select single or multiple assets
- ✅ Context menu provides curation actions
- ✅ Right dock shows selected asset metadata
- ✅ Approve button marks assets as approved in DB
- ✅ Reject/Delete removes assets from DB and disk
- ✅ Rename changes filename with collision handling
- ✅ Move relocates files to theme folders
- ✅ Tag assigns theme metadata without moving files
- ✅ Grid refreshes automatically after operations
- ✅ File operations update database paths correctly

---

## Milestone 4 (M4): Advanced Curation & Filters
**Status**: Planned  
**Duration**: Step 6-7 (2 weeks)  
**Goal**: Enhanced curation workflows

### Deliverables
- [ ] Drag-and-drop file support
- [ ] Keyboard shortcuts (A=Approve, R=Reject, Space=Preview, Del=Delete, F2=Rename)
- [ ] Filters (type, status, tags, date)
- [ ] Search functionality
- [ ] Batch operations UI
- [ ] Undo/Redo for curation actions
- [ ] Preview panel for selected assets
- [ ] Metadata editing (custom fields)

---

## Milestone 5 (M5): First Processing Pipeline
**Status**: Planned  
**Duration**: Step 8-9 (2 weeks)  
**Goal**: Background removal working

### Deliverables
- [ ] Worker queue (ThreadPoolExecutor)
- [ ] Job status tracking (DB + UI)
- [ ] rembg integration (GPU/CPU fallback)
- [ ] Progress bar with ETA
- [ ] Output to /Work folder
- [ ] Grid toggle: [Original] [BG-Removed]

---

## Milestone 6 (M6): Pack Builder
**Status**: Planned  
**Duration**: Step 10-11 (2 weeks)  
**Goal**: Export first pack

### Deliverables
- [ ] Pack creation dialog
- [ ] README.md template (Gumroad/Etsy/etc.)
- [ ] LICENSE.txt variants (Personal/Commercial/Extended)
- [ ] manifest.json with SHA-256 checksums
- [ ] ZIP export
- [ ] Validation (required files, integrity)

---

## Milestone 7 (M7): Hardware Guardrails
**Status**: Planned  
**Duration**: Step 12 (1 week)  
**Goal**: Tier-based operation gating

### Deliverables
- [ ] GREEN/YELLOW/RED tier assignment
- [ ] Pre-flight checks before jobs
- [ ] Block dialogs with upgrade guidance
- [ ] Fallback to CPU (with warnings)

---

## Milestone 8 (M8): Full Media Pipelines
**Status**: Planned  
**Duration**: Step 13-14 (3 weeks)  
**Goal**: All enhancement ops working

### Deliverables
- [ ] Image upscaling (Real-ESRGAN 2x/4x)
- [ ] Video transcoding (FFmpeg)
- [ ] Audio normalization (LUFS)
- [ ] Video upscaling (FFmpeg + model)
- [ ] Trim/crop operations

---

## Milestone 9 (M9): Prompt Templates
**Status**: Planned  
**Duration**: Step 15 (1 week)  
**Goal**: Zero-AI prompt generation

### Deliverables
- [ ] Jinja2 template engine
- [ ] 6 platform templates (SDXL, MidJourney, Suno, etc.)
- [ ] Variable substitution UI
- [ ] Batch generation (10+ prompts)
- [ ] Export to TXT

---

## Milestone 10 (M10): Polish & Testing
**Status**: Planned  
**Duration**: Step 16-17 (2 weeks)  
**Goal**: Beta-ready release

### Deliverables
- [ ] Unit tests (>80% coverage)
- [ ] Integration tests (with mocks)
- [ ] Manual QA (test plan)
- [ ] Bug fixes
- [ ] Dark mode theme
- [ ] Performance profiling

---

## Milestone 11 (M11): Packaging & Release
**Status**: Planned  
**Duration**: Step 18 (1 week)  
**Goal**: v1.0 release

### Deliverables
- [ ] PyInstaller build (single .exe)
- [ ] Installer (NSIS or similar)
- [ ] User documentation (end-user README)
- [ ] GitHub release with binaries
- [ ] Announcement (Twitter, Reddit, Discord)

---

## Post-v1.0 Roadmap

### v1.1 (Q2 2026): Usability Improvements
- Enhanced keyboard shortcuts
- Batch tagging
- Custom themes
- Export presets

### v1.2 (Q3 2026): Cloud Mode (Optional)
- Headless backend
- Web UI for remote access
- Team sync (shared packs)

### v2.0 (Q4 2026): Marketplace Integrations
- Auto-upload to Gumroad
- Etsy API integration
- Revenue tracking

### v3.0 (2027): MacOS/Linux Support
- Qt cross-platform port
- Linux package (AppImage/Flatpak)
- MacOS dmg

---

## Success Criteria (v1.0)

- [ ] <30 minutes from ingest to pack export
- [ ] Zero crashes on GREEN-tier systems
- [ ] 100 active users in first 3 months
- [ ] 50+ GitHub stars
- [ ] 20+ community contributions (issues/PRs)

---

**Current Status**: M1 Complete, M2 Starting  
**Next Milestone**: UI Skeleton (PySide6 main window)
