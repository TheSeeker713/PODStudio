"""
Hardware Profiler
Detect GPU, CPU, RAM capabilities and assign tier (GREEN/YELLOW/RED)
Includes LLM budget estimation for CPU-based inference workloads
"""

from typing import Literal

import psutil

try:
    import pynvml

    PYNVML_AVAILABLE = True
except ImportError:
    PYNVML_AVAILABLE = False


def probe_hardware() -> dict:
    """
    Probe system hardware capabilities including LLM inference budget.

    Returns:
        dict with keys:
            - gpu_name: str
            - vram_gb: float
            - cpu_cores_logical: int
            - cpu_cores_physical: int
            - cpu_load_percent: float (current 1-minute average)
            - ram_total_gb: float
            - ram_available_gb: float
            - ram_percent_used: float
            - llm_budget: Literal["LOW", "MEDIUM", "HIGH"]
            - llm_tokens_per_sec_estimate: int
            - tier: Literal["GREEN", "YELLOW", "RED"]
    """
    # CPU detection
    cpu_cores_logical = psutil.cpu_count(logical=True) or 1
    cpu_cores_physical = psutil.cpu_count(logical=False) or 1
    cpu_load_percent = psutil.cpu_percent(interval=1)

    # RAM detection
    ram = psutil.virtual_memory()
    ram_total_gb = ram.total / (1024**3)
    ram_available_gb = ram.available / (1024**3)
    ram_percent_used = ram.percent

    # GPU detection
    gpu_name = "None"
    vram_gb = 0.0
    has_cuda = False

    if PYNVML_AVAILABLE:
        try:
            pynvml.nvmlInit()
            device_count = pynvml.nvmlDeviceGetCount()
            if device_count > 0:
                handle = pynvml.nvmlDeviceGetHandleByIndex(0)
                gpu_name = pynvml.nvmlDeviceGetName(handle)
                if isinstance(gpu_name, bytes):
                    gpu_name = gpu_name.decode("utf-8")
                mem_info = pynvml.nvmlDeviceGetMemoryInfo(handle)
                vram_gb = mem_info.total / (1024**3)
                has_cuda = True
            pynvml.nvmlShutdown()
        except Exception:
            pass

    # LLM Budget Estimation (tokens/sec for CPU inference)
    # Based on: RAM available, CPU cores, and current load
    llm_tokens_per_sec_estimate = _estimate_llm_throughput(ram_available_gb, cpu_cores_logical, cpu_load_percent)
    llm_budget = _classify_llm_budget(llm_tokens_per_sec_estimate)

    # Tier assignment
    tier = _assign_tier(has_cuda, vram_gb, ram_total_gb, cpu_cores_physical)

    return {
        "gpu_name": gpu_name,
        "vram_gb": round(vram_gb, 2),
        "cpu_cores_logical": cpu_cores_logical,
        "cpu_cores_physical": cpu_cores_physical,
        "cpu_load_percent": round(cpu_load_percent, 1),
        "ram_total_gb": round(ram_total_gb, 2),
        "ram_available_gb": round(ram_available_gb, 2),
        "ram_percent_used": round(ram_percent_used, 1),
        "llm_budget": llm_budget,
        "llm_tokens_per_sec_estimate": llm_tokens_per_sec_estimate,
        "tier": tier,
    }


def _estimate_llm_throughput(ram_available_gb: float, cpu_cores: int, cpu_load: float) -> int:
    """
    Estimate tokens/sec for CPU-based LLM inference.

    Rough heuristics:
    - Base: ~2 tokens/sec per physical core on modern CPUs (Q5_K_M quants)
    - Penalty: -50% if RAM < 8GB available
    - Penalty: -50% if CPU load > 75%
    - Bonus: +25% if 16+ cores
    """
    base_throughput = cpu_cores * 2

    # RAM penalty
    if ram_available_gb < 8:
        base_throughput = int(base_throughput * 0.5)

    # CPU load penalty
    if cpu_load > 75:
        base_throughput = int(base_throughput * 0.5)

    # Multi-core bonus
    if cpu_cores >= 16:
        base_throughput = int(base_throughput * 1.25)

    return max(1, base_throughput)


def _classify_llm_budget(tokens_per_sec: int) -> Literal["LOW", "MEDIUM", "HIGH"]:
    """Classify LLM budget based on estimated throughput."""
    if tokens_per_sec < 5:
        return "LOW"
    elif tokens_per_sec < 15:
        return "MEDIUM"
    else:
        return "HIGH"


def _assign_tier(
    has_cuda: bool, vram_gb: float, ram_total_gb: float, cpu_cores: int
) -> Literal["GREEN", "YELLOW", "RED"]:
    """
    Assign hardware tier based on capabilities.

    GREEN: CUDA GPU with 8GB+ VRAM, or 32GB+ RAM with 12+ cores
    YELLOW: CUDA GPU with 4-8GB VRAM, or 16GB+ RAM with 8+ cores
    RED: Everything else
    """
    if has_cuda and vram_gb >= 8:
        return "GREEN"
    elif has_cuda and vram_gb >= 4:
        return "YELLOW"
    elif ram_total_gb >= 32 and cpu_cores >= 12:
        return "GREEN"
    elif ram_total_gb >= 16 and cpu_cores >= 8:
        return "YELLOW"
    else:
        return "RED"
