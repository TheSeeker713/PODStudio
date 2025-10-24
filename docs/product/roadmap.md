# PODStudio — Development Roadmap

**Version**: 0.3.0
**Last Updated**: Today

---

## Milestone 1: Foundational Setup (M1)
**Status**: ✅ Complete (Steps 0-1)
- **Deliverables**: Project structure, Git repo, CI, design docs, Python environment.

---

## Milestone 2: UI & Database Core (M2)
**Status**: ✅ Complete (Steps 2-3)
- **Deliverables**: PySide6 UI shell, SQLite schema, database migrations, hardware probe.

---

## Milestone 3: Curation & File Management (M3)
**Status**: ✅ Complete (Steps 4-5)
- **Deliverables**: File watcher, thumbnail generation, asset grid, multi-select, full suite of curation actions (approve, reject, tag, move, rename), DB sync.

---

## Milestone 4: Offline AI Agent Layer (M4)
**Status**: ✅ Complete (Steps 6-7)
- **Deliverables**: Llama.cpp server management, multi-agent abstraction (`llm_client.py`), health checks, model registry, GGUF model support.

---

## Milestone 5: Prompt Engine v2 (M5)
**Status**: ✅ Complete (Step 8)
- **Deliverables**: Dual-mode prompt engine (`TEMPLATE_ONLY`, `AGENT_ASSISTED`), Jinja2 integration, FastAPI endpoints for prompt generation, agent-based pipeline (vision->logic->dialog->fast).

---

## Milestone 6: Pack Builder v2 (M6)
**Status**: ✅ Complete (Step 9)
- **Deliverables**:
    - Pack exporter embeds prompt generation artifacts (`/prompts` directory).
    - `final_prompts.json` and `agent_lineage.json` for reproducibility.
    - `manifest.json` updated with `prompt_session_id` and `prompt_source`.
    - Optional AI disclosure notes in `README.md` and `store_copy.txt`.
    - UI checkbox to control disclosure.

---

## Milestone 7: Full-Featured Image Generation (M7)
**Status**: **In Progress** (Step 10+)
**Goal**: A full-window, offline-first image generation module.
- **Key Features**:
    - **Hardware**: AMD/DirectML and robust CPU-only support.
    - **Models**: SDXL, SD3, FLUX, and community models.
    - **No Limits**: Overcome the 75-token prompt limit for complex prompts.
    - **UI**: Dedicated image generation window accessible from the top menu.
    - **Integration**: Generated images feed directly into the curation grid.

---

## Milestone 8: Advanced Curation & Filters (M8)
**Status**: Planned
- **Deliverables**: Drag-and-drop, keyboard shortcuts, filters, search, batch operations, undo/redo.

---

## Milestone 9: Media Processing Pipelines (M9)
**Status**: Planned
- **Deliverables**: Background removal (rembg), image upscaling (ESRGAN), video transcoding, audio normalization.

---

## Milestone 10: Polish, Release & Beyond (M10)
**Status**: Planned
- **Deliverables**: Unit/integration tests, manual QA, PyInstaller build, user docs, v1.0 release.
- **Post-v1.0**: Marketplace integrations, cross-platform support.
