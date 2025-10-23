"""
Backend Server - FastAPI Service
Runs on localhost:8971 for async/heavy operations

STEP 3: FastAPI skeleton with health/probe/jobs stubs.
No heavy logic yet - just API scaffolding.

To run:
    uvicorn app.backend.server:app --reload --port 8971
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.backend.routes import health, jobs, probe

app = FastAPI(
    title="PODStudio Backend",
    description="Local backend service for PODStudio desktop app",
    version="0.1.0",
)

# CORS - allow localhost UI to communicate with backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:*",
        "http://127.0.0.1:*",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include route modules with /api prefix
app.include_router(health.router, prefix="/api", tags=["health"])
app.include_router(probe.router, prefix="/api", tags=["probe"])
app.include_router(jobs.router, prefix="/api", tags=["jobs"])


@app.get("/")
async def root():
    """Root endpoint - redirects to /docs"""
    return {
        "message": "PODStudio Backend API",
        "version": "0.1.0",
        "docs": "/docs",
        "health": "/api/health",
    }
