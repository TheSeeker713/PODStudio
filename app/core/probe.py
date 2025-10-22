"""
Hardware Profiler
Detect GPU, CPU, RAM capabilities and assign tier (GREEN/YELLOW/RED)

TODO (Step 2+): Implement with:
- pynvml for NVIDIA GPU detection
- psutil for CPU/RAM
- Capability matrix checking
- Tier assignment logic
"""


def probe_hardware() -> dict:
    """
    Probe system hardware capabilities

    Returns:
        dict with keys: gpu_name, vram_gb, cpu_cores, ram_gb, tier
    """
    # TODO: Implement GPU/CPU/RAM probing
    return {
        "gpu_name": "Unknown",
        "vram_gb": 0,
        "cpu_cores": 0,
        "ram_gb": 0,
        "tier": "YELLOW",
    }
