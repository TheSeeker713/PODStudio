"""
Backend Server - FastAPI Service
Runs on localhost:8765 for async/heavy operations

TODO (Step 2+): Implement FastAPI app with:
- /health endpoint
- /probe endpoint (hardware detection)
- /jobs endpoints (CRUD for processing jobs)
- WebSocket for progress updates
"""

from fastapi import FastAPI

app = FastAPI(
    title="PODStudio Backend",
    description="Local backend service for PODStudio desktop app",
    version="0.1.0",
)


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "ok", "service": "PODStudio Backend", "version": "0.1.0"}


# TODO: Add routes for /probe, /jobs, /assets, /packs
