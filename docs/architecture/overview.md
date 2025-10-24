# Architecture Overview — Reference

**Version**: 0.1.0  
**Last Updated**: October 22, 2025

---

## Note

This file is a **placeholder** for Step 1. The complete architecture documentation already exists in:

**📄 [/docs/architecture.md](/docs/architecture.md)** (from Step 0 design phase)

That document includes:
- Complete component diagram
- Startup/shutdown sequences
- 3 detailed data flow diagrams (auto-ingest, bg-removal, pack export)
- Job lifecycle state machine
- Directory structure specification

---

## Quick Reference

### System Architecture (Updated STEP 7)

```
┌─────────────────┐
│   PySide6 UI    │ ← User interaction (Qt widgets)
└────────┬────────┘
         │ HTTP
┌────────▼────────┐
│  FastAPI        │ ← Async backend (localhost:8971)
│  Backend        │
└───┬─────────┬───┘
    │         │
    │         └──────────────┐
    │                        │
┌───▼────────┐     ┌────────▼────────────┐
│  Worker    │     │  Offline LLM Agents │ ← STEP 7: llama.cpp
│  Queue     │     │  (CPU-only)         │    (ports 9091-9094)
│  (Jobs)    │     ├─────────────────────┤
└───┬────────┘     │ Agent Vision (9091) │
    │              │ Agent Dialog (9092) │
    │              │ Agent Logic  (9093) │
    │              │ Agent Fast   (9094) │
    │              └─────────────────────┘
    │
┌───▼────────┐
│  SQLite +  │ ← Data persistence + assets
│  Files     │
└────────────┘
```

### Tech Stack (Updated)

- **UI**: PySide6 (Qt 6)
- **Backend**: FastAPI + Uvicorn
- **Database**: SQLite + SQLModel
- **Workers**: ThreadPoolExecutor (default) or RQ (optional)
- **Media**: Pillow, OpenCV, rembg, FFmpeg, pydub
- **LLM Agents**: llama.cpp servers (4 concurrent GGUF models, CPU-only)

### LLM Agent Layer (STEP 7)

**Purpose**: Offline prompt generation and light reasoning

**Architecture**:
- 4 independent llama-server instances (HTTP)
- Each agent bound to specific GGUF model and port
- CPU-only execution (no GPU required)
- Health monitoring via `/api/llm/health`

**Agents**:
1. **Vision** (Port 9091): gemma-3-12b — Image analysis, captions
2. **Dialog** (Port 9092): discopop-zephyr-7b — Fluency, polish
3. **Logic** (Port 9093): gemma-3n-e4b — Reasoning, planning
4. **Fast** (Port 9094): lfm2-1.2b — Quick tasks, fallback

**Communication**:
- Backend → Agents: HTTP POST to `http://127.0.0.1:909X/v1/chat/completions`
- Retry logic with exponential backoff
- Fallback routing if primary agent unavailable

**Routing Logic**:
```
Prompt Draft → Logic Agent
Prompt Polish → Dialog Agent  
Image Caption → Vision Agent
Quick Summary → Fast Agent
```

---

**For full architecture, see**: [/docs/architecture.md](/docs/architecture.md)
