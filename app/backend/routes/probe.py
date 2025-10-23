"""
Probe Routes - Hardware Detection
STEP 3: Stub endpoint returning placeholder hardware info
"""

from fastapi import APIRouter

from app.backend.models.schemas import HardwareMode, ProbeResponse

router = APIRouter()


@router.get("/probe", response_model=ProbeResponse)
async def probe_hardware():
    """
    Hardware detection endpoint (STUB)

    Returns placeholder hardware info. Real GPU/CPU/RAM detection
    will be implemented in future steps.

    TODO (Step 4+): Implement actual hardware detection using:
    - GPUtil or nvidia-ml-py for GPU info
    - psutil for CPU/RAM info
    - Categorize into GREEN/YELLOW/RED tiers
    """
    return ProbeResponse(
        gpu="unknown",
        vram_gb=None,
        cpu_threads=None,
        ram_gb=None,
        mode=HardwareMode.UNKNOWN,
    )
