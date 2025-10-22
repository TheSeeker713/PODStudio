# PODStudio — Hardware Policy Specification

**Version:** 1.0.0  
**Date:** October 22, 2025  
**Status:** Design Specification

---

## Table of Contents

1. [Overview](#overview)
2. [Hardware Profiling](#hardware-profiling)
3. [Capability Tiers](#capability-tiers)
4. [Operation Requirements](#operation-requirements)
5. [Decision Logic](#decision-logic)
6. [User Messages](#user-messages)
7. [Fallback Strategies](#fallback-strategies)
8. [Testing Hardware Scenarios](#testing-hardware-scenarios)

---

## Overview

PODStudio ensures **safe and predictable operation** across diverse Windows hardware by:
- Probing system capabilities at startup
- Classifying hardware into capability tiers (GREEN/YELLOW/RED)
- Blocking or warning before running operations that may crash or take excessive time
- Providing actionable upgrade guidance when operations are infeasible

### Design Philosophy
- **Fail-safe over fail-fast:** Never crash; degrade gracefully
- **Transparent decisions:** Always explain *why* something is blocked or slow
- **User agency:** Warnings allow users to proceed at their own risk; hard blocks only for guaranteed failures
- **Evolutionary:** Profiles are cached but re-checked on driver updates or hardware changes

---

## Hardware Profiling

### Probe Sequence (Startup)

Runs on application launch; takes ~2-3 seconds.

#### 1. GPU Detection

**Methods (fallback chain):**
1. **NVIDIA GPUs:** Use `pynvml` (NVIDIA Management Library)
   - Detects: Model, VRAM, driver version, CUDA capability
2. **AMD GPUs:** Use `wmi` (Windows Management Instrumentation)
   - Detects: Model, VRAM estimate (less reliable)
3. **Intel iGPUs:** Use `wmi` or fallback to generic detection
   - Detects: Model, shared memory estimate
4. **Fallback:** If all fail, assume CPU-only mode

**Data Collected:**
```python
{
  "gpu_vendor": "NVIDIA" | "AMD" | "Intel" | "Unknown" | None,
  "gpu_model": "GeForce RTX 3060" | "Radeon RX 6700" | "Intel UHD 630" | None,
  "vram_mb": 8192 | None,  # Dedicated VRAM in MB
  "driver_version": "531.68" | None,
  "cuda_version": "12.1" | None,  # NVIDIA only
  "vulkan_supported": True | False,  # Check for Vulkan runtime
  "directml_supported": True | False  # Windows DirectML for AMD/Intel
}
```

#### 2. CPU Detection

**Method:** Use `os.cpu_count()` and `platform` module

**Data Collected:**
```python
{
  "cpu_model": "Intel Core i7-10700K" | "AMD Ryzen 7 5800X" | "Unknown",
  "cpu_threads": 12,  # Logical cores (includes hyperthreading)
  "cpu_architecture": "x86_64"
}
```

#### 3. RAM Detection

**Method:** Use `psutil.virtual_memory()`

**Data Collected:**
```python
{
  "ram_total_gb": 32,
  "ram_available_gb": 24  # Current available (may fluctuate)
}
```

#### 4. Disk Detection

**Method:** Use `psutil.disk_usage()` on project path

**Data Collected:**
```python
{
  "disk_total_gb": 1000,
  "disk_free_gb": 450,
  "disk_type": "SSD" | "HDD" | "Unknown"  # Heuristic: check read speed
}
```

#### 5. External Tools Check

**Method:** Try executing with `--version` or `--help`

**Data Collected:**
```python
{
  "ffmpeg_available": True,
  "ffmpeg_version": "5.1.2",
  "ffprobe_available": True,
  "exiftool_available": False,  # Optional
  "vulkan_runtime": True  # Check for vulkan-1.dll
}
```

### Profile Storage

**Location:** `~/.podstudio/hardware_profile.json`

**Lifecycle:**
- Generated on first launch
- Re-generated if file missing or `--force-probe` flag used
- Re-checked on major driver updates (user-initiated via Settings)

**Example Profile:**
```json
{
  "version": "1.0",
  "probed_at": "2025-10-22T10:00:00.000Z",
  "gpu": {
    "vendor": "NVIDIA",
    "model": "GeForce RTX 3060",
    "vram_mb": 8192,
    "driver_version": "531.68",
    "cuda_version": "12.1",
    "vulkan_supported": true,
    "directml_supported": true
  },
  "cpu": {
    "model": "Intel Core i7-10700K",
    "threads": 12,
    "architecture": "x86_64"
  },
  "ram": {
    "total_gb": 32,
    "available_gb": 24
  },
  "disk": {
    "total_gb": 1000,
    "free_gb": 450,
    "type": "SSD"
  },
  "tools": {
    "ffmpeg_available": true,
    "ffmpeg_version": "5.1.2",
    "ffprobe_available": true,
    "exiftool_available": false,
    "vulkan_runtime": true
  }
}
```

---

## Capability Tiers

### GREEN (Safe for All Operations)

**Criteria:**
- **GPU:** Dedicated GPU with ≥ 6 GB VRAM (NVIDIA/AMD)
- **CPU:** ≥ 8 threads
- **RAM:** ≥ 16 GB
- **Tools:** ffmpeg and ffprobe available

**Allowed Operations:**
- ✅ All image operations (bg-remove, upscale 2x/4x, crop, resize)
- ✅ Video transcode up to 4K
- ✅ Video upscale up to 1080p (with GPU)
- ✅ Audio normalization, trim, format conversion
- ✅ Batch operations (limited by queue size)
- ✅ Pack exports with 100+ assets

**UI Indicator:**
```
[🟢 GPU · 8GB]
```

### YELLOW (Caution — Slow but Feasible)

**Scenarios:**

#### Scenario A: Low VRAM
- **GPU:** 4-6 GB VRAM
- **CPU:** ≥ 8 threads
- **RAM:** ≥ 16 GB

**Limitations:**
- ⚠️ Image upscale 4x may OOM (warn user)
- ⚠️ Video upscale limited to 720p (block higher resolutions)
- ⚠️ Background removal on large images (>4K) may be slow
- ✅ All other operations safe

#### Scenario B: CPU-Only (No Dedicated GPU)
- **GPU:** Integrated GPU or none
- **CPU:** ≥ 8 threads
- **RAM:** ≥ 16 GB

**Limitations:**
- ⚠️ All GPU ops run on CPU (5-10x slower)
- ⚠️ Upscale 4x may take 10+ minutes per image
- ⚠️ Video upscale not recommended (block or show severe warning)
- ✅ Background removal works (rembg has CPU fallback)
- ✅ Audio ops unaffected

#### Scenario C: Low RAM
- **GPU:** Any
- **CPU:** ≥ 8 threads
- **RAM:** 8-12 GB

**Limitations:**
- ⚠️ Large video files (>1GB) may crash (warn before processing)
- ⚠️ Batch ops limited to 5 concurrent jobs
- ✅ Image and audio ops mostly safe

**UI Indicator:**
```
[🟡 CPU · 16GB]  (CPU-only)
[🟡 GPU · 4GB]   (Low VRAM)
[🟡 GPU · 8GB · Low RAM]
```

### RED (Unsafe — Block Operations)

**Scenarios:**

#### Scenario A: Very Low VRAM
- **GPU:** < 2 GB VRAM
- **Limitations:** Block all GPU-accelerated ops; CPU fallback only

#### Scenario B: Very Low RAM
- **RAM:** < 8 GB
- **Limitations:** Block video processing; limit image upscale to 2x max

#### Scenario C: Missing Critical Tools
- **ffmpeg:** Missing
- **Limitations:** Block all video/audio operations

#### Scenario D: Insufficient CPU
- **CPU:** < 4 threads
- **Limitations:** Warn on all batch operations; suggest upgrading

**UI Indicator:**
```
[🔴 CPU-Only · 4GB RAM]
[🔴 No ffmpeg]
```

---

## Operation Requirements

Detailed hardware requirements per operation type.

### Image Operations

#### Background Removal (rembg U2Net)
| Tier   | GPU VRAM | RAM   | CPU Threads | Time (2048x2048) | Notes                          |
|--------|----------|-------|-------------|------------------|--------------------------------|
| GREEN  | ≥ 4 GB   | ≥ 8 GB| ≥ 4         | 15-30s           | GPU-accelerated                |
| YELLOW | < 4 GB   | ≥ 8 GB| ≥ 4         | 30-60s           | GPU or CPU fallback            |
| YELLOW | N/A      | ≥ 8 GB| ≥ 8         | 60-120s          | CPU-only (slow)                |
| RED    | N/A      | < 6 GB| Any         | N/A              | **BLOCK** (likely OOM)         |

#### Upscale 2x (Real-ESRGAN)
| Tier   | GPU VRAM | RAM   | CPU Threads | Time (2048x2048) | Notes                          |
|--------|----------|-------|-------------|------------------|--------------------------------|
| GREEN  | ≥ 6 GB   | ≥ 8 GB| ≥ 4         | 20-40s           | GPU-accelerated                |
| YELLOW | 4-6 GB   | ≥ 8 GB| ≥ 4         | 30-60s           | GPU (may be tight)             |
| YELLOW | N/A      | ≥ 16 GB| ≥ 8        | 3-5 min          | CPU-only (very slow)           |
| RED    | < 2 GB   | Any   | Any         | N/A              | **BLOCK** (GPU OOM)            |
| RED    | N/A      | < 8 GB| Any         | N/A              | **BLOCK** (RAM OOM)            |

#### Upscale 4x (Real-ESRGAN)
| Tier   | GPU VRAM | RAM   | CPU Threads | Time (2048x2048) | Notes                          |
|--------|----------|-------|-------------|------------------|--------------------------------|
| GREEN  | ≥ 8 GB   | ≥ 16 GB| ≥ 8        | 60-120s          | GPU-accelerated                |
| YELLOW | 6-8 GB   | ≥ 16 GB| ≥ 8        | 90-180s          | **WARN** (may OOM on large images) |
| RED    | < 6 GB   | Any   | Any         | N/A              | **BLOCK** (GPU OOM)            |
| RED    | Any      | < 12 GB| Any        | N/A              | **BLOCK** (RAM OOM)            |

### Video Operations

#### Transcode (H.264, 1080p)
| Tier   | GPU      | RAM   | CPU Threads | Time (1min video) | Notes                          |
|--------|----------|-------|-------------|-------------------|--------------------------------|
| GREEN  | Any      | ≥ 8 GB| ≥ 8         | 30-60s            | ffmpeg hardware-accelerated    |
| YELLOW | Any      | ≥ 8 GB| 4-8         | 60-120s           | CPU encoding (slower)          |
| RED    | Any      | < 6 GB| Any         | N/A               | **BLOCK** (RAM OOM)            |

#### Upscale 720p → 1080p (ESRGAN-ncnn-vulkan)
| Tier   | GPU VRAM | RAM   | Vulkan | Time (1min video) | Notes                          |
|--------|----------|-------|--------|-------------------|--------------------------------|
| GREEN  | ≥ 6 GB   | ≥ 16 GB| ✅     | 15-30 min         | Vulkan GPU-accelerated         |
| YELLOW | 4-6 GB   | ≥ 16 GB| ✅     | 20-40 min         | **WARN** (slower, may drop frames)|
| RED    | < 4 GB   | Any   | Any    | N/A               | **BLOCK** (GPU OOM)            |
| RED    | Any      | Any   | ❌     | N/A               | **BLOCK** (no Vulkan runtime)  |

#### Upscale 1080p → 4K
| Tier   | GPU VRAM | RAM   | Vulkan | Time (1min video) | Notes                          |
|--------|----------|-------|--------|-------------------|--------------------------------|
| GREEN  | ≥ 8 GB   | ≥ 24 GB| ✅     | 30-60 min         | Vulkan GPU-accelerated         |
| YELLOW | 6-8 GB   | ≥ 24 GB| ✅     | 45-90 min         | **WARN** (very slow, may OOM)  |
| RED    | < 6 GB   | Any   | Any    | N/A               | **BLOCK** (GPU OOM)            |
| RED    | Any      | < 20 GB| Any   | N/A               | **BLOCK** (RAM OOM)            |

### Audio Operations

#### Normalize Loudness (ffmpeg)
| Tier   | Requirements     | Time (5min audio) | Notes                          |
|--------|------------------|-------------------|--------------------------------|
| GREEN  | ffmpeg, ≥ 4 GB RAM| 10-20s            | Fast, minimal resources        |
| YELLOW | ffmpeg, ≥ 2 GB RAM| 15-30s            | Safe on low-end systems        |
| RED    | No ffmpeg        | N/A               | **BLOCK** (tool missing)       |

#### Trim/Format Conversion
| Tier   | Requirements     | Time (5min audio) | Notes                          |
|--------|------------------|-------------------|--------------------------------|
| GREEN  | ffmpeg, ≥ 4 GB RAM| 5-10s             | Instant operation              |
| YELLOW | ffmpeg, ≥ 2 GB RAM| 10-20s            | Safe                           |
| RED    | No ffmpeg        | N/A               | **BLOCK** (tool missing)       |

---

## Decision Logic

### Pre-Flight Check Algorithm

Before starting a job, run this check:

```
FUNCTION can_run_job(job_kind, params, hardware_profile):
    requirements = get_requirements(job_kind, params)
    
    # Check VRAM
    IF requirements.min_vram > hardware_profile.gpu.vram_mb:
        RETURN BLOCK("Insufficient VRAM", fallback=cpu_fallback_available)
    
    # Check RAM
    IF requirements.min_ram_gb > hardware_profile.ram.available_gb:
        RETURN BLOCK("Insufficient RAM")
    
    # Check tools
    IF job_kind IN [transcode, normalize, video_upscale]:
        IF NOT hardware_profile.tools.ffmpeg_available:
            RETURN BLOCK("ffmpeg missing", action="install_ffmpeg")
    
    # Check disk space (estimated output size)
    estimated_output_size = calculate_output_size(job_kind, params)
    IF estimated_output_size > hardware_profile.disk.free_gb * 0.9:
        RETURN BLOCK("Insufficient disk space", required=estimated_output_size)
    
    # Warnings (YELLOW tier)
    warnings = []
    
    IF requirements.min_vram <= hardware_profile.gpu.vram_mb < requirements.rec_vram:
        warnings.append("Low VRAM — operation may be slow or fail on large files")
    
    IF cpu_only AND job_kind IN [upscale, bg_remove]:
        estimate = estimate_duration_cpu(job_kind, params)
        warnings.append(f"CPU-only mode: estimated time {estimate} min")
    
    IF warnings:
        RETURN WARN(warnings, user_can_proceed=True)
    
    # All checks passed
    RETURN ALLOW
```

### Fallback Selection

```
FUNCTION select_hardware_mode(job_kind, hardware_profile):
    IF hardware_profile.gpu.vram_mb >= get_requirements(job_kind).min_vram:
        IF hardware_profile.gpu.vendor == "NVIDIA":
            RETURN "cuda"
        ELIF hardware_profile.gpu.vendor == "AMD" AND directml_supported:
            RETURN "directml"
        ELIF vulkan_supported:
            RETURN "vulkan"
    
    # Fallback to CPU
    IF hardware_profile.cpu.threads >= 8 AND hardware_profile.ram.total_gb >= 16:
        RETURN "cpu"
    
    # Last resort
    RETURN "cpu_minimal"
```

---

## User Messages

### Block Messages (RED Tier)

#### Insufficient VRAM
```
┌────────────────────────────────────────────────────────────┐
│ ⚠️ Cannot Run This Operation                               │
├────────────────────────────────────────────────────────────┤
│ Upscaling this image (4096×4096) to 4x requires at least  │
│ 8 GB VRAM. Your system has 4 GB.                           │
│                                                            │
│ Suggestions:                                               │
│ • Reduce scale factor to 2x (requires 4 GB)               │
│ • Try on a smaller image (<2048px)                        │
│ • Use cloud processing (coming soon)                      │
│ • Upgrade GPU (recommended: RTX 3060 or better)           │
│                                                            │
│ [Try 2x Instead] [Cancel]                                 │
└────────────────────────────────────────────────────────────┘
```

#### Insufficient RAM
```
┌────────────────────────────────────────────────────────────┐
│ ⚠️ Cannot Run This Operation                               │
├────────────────────────────────────────────────────────────┤
│ Processing this 4K video requires at least 20 GB RAM.      │
│ Your system has 12 GB.                                     │
│                                                            │
│ Suggestions:                                               │
│ • Close other applications to free RAM                    │
│ • Downscale video to 1080p first                          │
│ • Split video into shorter clips                          │
│ • Upgrade RAM (recommended: 32 GB for 4K workflows)       │
│                                                            │
│ [Downscale First] [Cancel]                                │
└────────────────────────────────────────────────────────────┘
```

#### Missing Tools
```
┌────────────────────────────────────────────────────────────┐
│ ⚠️ Required Tool Missing: ffmpeg                           │
├────────────────────────────────────────────────────────────┤
│ Video and audio operations require ffmpeg.                 │
│                                                            │
│ PODStudio can download and install ffmpeg automatically.   │
│ (60 MB download, 2 minutes)                                │
│                                                            │
│ [Download & Install] [Manual Install Guide] [Cancel]      │
└────────────────────────────────────────────────────────────┘
```

### Warning Messages (YELLOW Tier)

#### Slow CPU Operation
```
┌────────────────────────────────────────────────────────────┐
│ ⚠️ Performance Warning                                      │
├────────────────────────────────────────────────────────────┤
│ This operation will run in CPU-only mode (no GPU).         │
│                                                            │
│ Estimated time: 8-12 minutes                               │
│ (vs. 30-60 seconds with GPU)                               │
│                                                            │
│ The operation will run in the background; you can continue │
│ working while it processes.                                │
│                                                            │
│ ☑ Don't warn me again for CPU operations                   │
│                                                            │
│ [Continue] [Cancel]                                        │
└────────────────────────────────────────────────────────────┘
```

#### Borderline VRAM
```
┌────────────────────────────────────────────────────────────┐
│ ⚠️ Low VRAM Warning                                         │
├────────────────────────────────────────────────────────────┤
│ This operation will use ~5.5 GB VRAM. You have 6 GB.       │
│                                                            │
│ If the operation fails (out of memory):                    │
│ • Close other GPU applications (browsers, games)           │
│ • Try a smaller image or lower scale factor               │
│                                                            │
│ [Continue Anyway] [Cancel]                                │
└────────────────────────────────────────────────────────────┘
```

### Success Messages (GREEN Tier)

#### Operation Safe
No dialog shown; operation starts immediately with progress in Jobs panel.

**UI Feedback:**
- Toast notification: "Background removal started"
- Jobs panel badge updates: `[Jobs ⊙ 1]`
- Hardware indicator remains green: `[🟢 GPU · 8GB]`

---

## Fallback Strategies

### GPU → CPU Fallback

**Trigger:** VRAM insufficient or GPU driver error

**Implementation:**
1. Detect failure (CUDA OOM, DirectML error)
2. Re-queue job with `use_gpu=False` flag
3. Show notification: "GPU failed; retrying on CPU (will be slower)"
4. Job continues with CPU backend

**Supported Operations:**
- ✅ Background removal (rembg has CPU mode)
- ✅ Image upscale 2x (slower but works)
- ❌ Video upscale (no reliable CPU fallback; block instead)

### Large File Splitting

**Trigger:** Video file >1 GB on systems with <16 GB RAM

**Implementation:**
1. Detect large file pre-flight
2. Offer to split into chunks: "This file is large. Split into 3 parts?"
3. Process each chunk separately
4. Stitch results (ffmpeg concat)

**Overhead:** +15% time for splitting/stitching

### Batch Size Limiting

**Trigger:** Queue exceeds safe concurrency for hardware

**Implementation:**
- GREEN tier: Max 10 concurrent jobs
- YELLOW tier: Max 5 concurrent jobs
- RED tier: Max 2 concurrent jobs (or block batch ops)

**UI:** Show message "Queue full — will start after current jobs finish"

---

## Testing Hardware Scenarios

### Test Matrix

| Scenario                     | GPU        | VRAM  | CPU Threads | RAM   | Expected Tier |
|------------------------------|------------|-------|-------------|-------|---------------|
| High-end desktop             | RTX 3080   | 10 GB | 16          | 32 GB | GREEN         |
| Mid-range laptop             | RTX 3060   | 6 GB  | 8           | 16 GB | GREEN         |
| Budget laptop                | GTX 1650   | 4 GB  | 6           | 8 GB  | YELLOW        |
| Integrated GPU laptop        | Intel UHD  | 0 GB  | 8           | 16 GB | YELLOW        |
| Old desktop                  | None       | 0 GB  | 4           | 8 GB  | RED           |
| Cloud VM (CPU-only)          | None       | 0 GB  | 16          | 64 GB | YELLOW        |
| Cloud VM (GPU)               | Tesla T4   | 16 GB | 8           | 32 GB | GREEN         |

### Manual Test Cases

1. **Block Test (RED):**
   - Remove ffmpeg from PATH
   - Try to transcode video → Should show "Tool Missing" dialog
   - Install ffmpeg → Retry should succeed

2. **Warning Test (YELLOW):**
   - Simulate 4 GB VRAM system
   - Try 4x upscale on 2048px image → Should warn "Low VRAM"
   - Proceed → Should work but slower

3. **Fallback Test:**
   - Start GPU upscale
   - Simulate CUDA OOM error (inject failure)
   - Should auto-retry on CPU with notification

4. **Batch Limit Test:**
   - Queue 20 upscale jobs on YELLOW tier
   - First 5 start immediately
   - Rest show "Queued" status
   - As jobs complete, next ones start

---

## Hardware Upgrade Recommendations

### Tier-Based Suggestions

**RED → YELLOW:**
- Add 8 GB RAM (total 16 GB)
- Upgrade to 6-thread CPU minimum
- Install ffmpeg

**YELLOW → GREEN:**
- Add dedicated GPU with 6+ GB VRAM (RTX 3060, RX 6600 XT)
- Upgrade to 8+ CPU threads
- Upgrade to 16 GB RAM minimum

**GREEN → PRO:**
- Upgrade to 8+ GB VRAM GPU (RTX 3070, RX 6800)
- 32 GB RAM for 4K workflows
- NVMe SSD for temp files

### Budget-Friendly Options

- **Used GPUs:** GTX 1660 Super (6 GB) often available <$200
- **RAM:** 16 GB DDR4 kits <$50
- **Cloud Burst:** Rent GPU VM for heavy batch jobs ($1-2/hour)

---

**End of Hardware Policy Specification**  
**Next Steps:** Review thresholds, validate warning messages, approve before implementation.
