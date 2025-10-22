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

### System Architecture

```
┌─────────────────┐
│   PySide6 UI    │ ← User interaction (Qt widgets)
└────────┬────────┘
         │ HTTP
┌────────▼────────┐
│  FastAPI        │ ← Async backend (localhost:8765)
│  Backend        │
└────────┬────────┘
         │
┌────────▼────────┐
│  Worker Queue   │ ← ThreadPoolExecutor / RQ
│  (Jobs)         │
└────────┬────────┘
         │
┌────────▼────────┐
│  SQLite + Files │ ← Data persistence + assets
└─────────────────┘
```

### Tech Stack

- **UI**: PySide6 (Qt 6)
- **Backend**: FastAPI + Uvicorn
- **Database**: SQLite + SQLModel
- **Workers**: ThreadPoolExecutor (default) or RQ (optional)
- **Media**: Pillow, OpenCV, rembg, FFmpeg, pydub

---

**For full architecture, see**: [/docs/architecture.md](/docs/architecture.md)
