# Hardware Policy Architecture

**Version**: 2.0.0  
**Last Updated**: October 23, 2025

---

## Overview

The Hardware Policy Engine enforces intelligent resource guardrails for:
- **LLM Agent Routing**: CPU-based inference workloads (NEW in v2.0)
- **Media Processing**: GPU/CPU-intensive operations
- **Resource Allocation**: RAM, CPU, and thermal budgeting

This document focuses on **LLM-specific policies** introduced in STEP 10.

---

## Hardware Probing (v2.0)

### Metrics Collected

```python
{
    "gpu_name": str,
    "vram_gb": float,
    "cpu_cores_logical": int,
    "cpu_cores_physical": int,
    "cpu_load_percent": float,
    "ram_total_gb": float,
    "ram_available_gb": float,
    "ram_percent_used": float,
    "llm_budget": "LOW" | "MEDIUM" | "HIGH",
    "llm_tokens_per_sec_estimate": int,
    "tier": "GREEN" | "YELLOW" | "RED"
}
```

### LLM Budget Estimation

**Base Formula:** `cpu_cores_physical × 2 tokens/sec`

**Penalties:** RAM < 8GB (-50%), CPU > 75% (-50%)  
**Bonuses:** 16+ cores (+25%)

**Classification:**
- `LOW`: < 5 tok/s
- `MEDIUM`: 5-15 tok/s
- `HIGH`: > 15 tok/s

---

## LLM Policy Rules

### Rule 1: Vision Agent (A1) Restrictions
**BLOCK if:** No vision workload OR RAM < 12GB OR CPU > 75%

### Rule 2: Resource-Constrained Downgrade
**DOWNGRADE to Fast if:** (RAM < 12GB OR CPU > 75%) AND agent is logic/dialog

### Rule 3: Context Size Truncation
**Threshold:** 8192 tokens (max for Q5_K_M models)

### Rule 4: Global Agent Call Cap
**Max:** 3 agents per "Generate" action

### Rule 5: Single-Call Limit Under Pressure
**Limit to 1 agent if:** RAM < 12GB OR CPU > 75%

---

## Tier Assignment

### GREEN Tier
- CUDA GPU 8GB+ VRAM, OR 32GB+ RAM with 12+ cores
- **Capabilities:** All agents, multi-agent pipelines

### YELLOW Tier
- CUDA GPU 4-8GB VRAM, OR 16GB+ RAM with 8+ cores
- **Capabilities:** All agents with warnings, pipeline limits

### RED Tier
- < 16GB RAM, < 8 cores, no GPU
- **Capabilities:** Fast agent only, strict limits

---

## UI Integration

### LLM Budget Display
- **Pill badge**: LOW (red), MEDIUM (orange), HIGH (green)
- **Location**: Prompts panel, top-right

### Policy Notices
- Inline warnings above "Generate" button
- Examples:
  - ⚠️ `Reduced to FAST agent due to system load`
  - ⚠️ `Vision agent unavailable: Low RAM (8.2GB < 12.0GB)`

---

## Testing

```bash
pytest tests/unit/test_llm_policy.py -v
```

Coverage: BLOCK, ALLOW_WITH_WARNING, DOWNGRADE_AGENT decisions

---

## References

- **Original Policy**: `/docs/hardware_policy.md` (Step 0 media ops)
- **GGUF Docs**: [llama.cpp wiki](https://github.com/ggerganov/llama.cpp/wiki)
- **psutil**: [psutil.readthedocs.io](https://psutil.readthedocs.io/)
