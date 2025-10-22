# PODStudio — Processing Pipelines Specification

**Version:** 1.0.0  
**Date:** October 22, 2025  
**Status:** Design Specification

---

## Table of Contents

1. [Overview](#overview)
2. [Image Pipelines](#image-pipelines)
3. [Video Pipelines](#video-pipelines)
4. [Audio Pipelines](#audio-pipelines)
5. [Thumbnail Generation](#thumbnail-generation)
6. [Pack Export Pipeline](#pack-export-pipeline)
7. [Common Utilities](#common-utilities)
8. [Error Handling](#error-handling)

---

## Overview

This document specifies the **exact inputs, outputs, parameters, and steps** for each processing operation. These are the blueprints for the worker functions (but **not implementation code**).

### Pipeline Design Principles
- **Idempotent:** Re-running same pipeline with same inputs produces identical output
- **Non-destructive:** Original files never modified; outputs saved to `/Work/` or new asset records
- **Progress Reporting:** All long-running ops report progress (0-100%)
- **Graceful Degradation:** If GPU fails, try CPU; if CPU fails, log and mark job failed
- **Deterministic Filenames:** Outputs named `{original}__{operation}__{timestamp}.ext`

---

## Image Pipelines

### 1. Background Removal

**Purpose:** Remove background, output transparent PNG

**Inputs:**
- `asset_id` (UUID) — Source image asset
- `model` (enum) — `u2net` | `u2netp` | `silueta` (default: `u2net`)
- `output_format` (enum) — `png` | `webp` (default: `png`)
- `use_gpu` (bool) — Try GPU acceleration (default: `true`)

**Outputs:**
- New Asset record (type=image, parent_asset_id=input)
- File: `/Work/edits/{asset_id}__nobg__{yyyymmdd_hhmmss}.png`
- Alpha mask (optional): `/Work/masks/{asset_id}__mask__{timestamp}.png`

**Steps:**
1. **Load Asset Record** from DB by `asset_id`
2. **Hardware Check:** Verify VRAM ≥ 2 GB or RAM ≥ 8 GB
3. **Load Image:** Pillow or OpenCV
4. **Initialize rembg Session:**
   - Model: U2Net (download to Cache/models/ if missing)
   - Backend: CUDA if `use_gpu=true` and available, else CPU
5. **Process Image:**
   - Call `rembg.remove(image, session=session)`
   - Update progress: 0% (loading) → 50% (processing) → 100% (saving)
6. **Save Output:**
   - Format: PNG with alpha channel
   - Compression: PNG optimize=True
7. **Create Mask (optional):**
   - Extract alpha channel as grayscale image
   - Save to `/Work/masks/`
8. **Create New Asset Record:**
   - Copy metadata from parent
   - Set `parent_asset_id`, `source="generated"`
   - Tags: inherit + add `["edited", "nobg"]`
9. **Update Job:** status=success, output_asset_ids=[new_id]

**Compute Cost:**
- GPU (6 GB VRAM): 15-30s per 2048×2048 image
- CPU (8 threads): 60-120s per 2048×2048 image
- RAM: ~2-4 GB peak

**Fallbacks:**
- If GPU OOM: Retry on CPU with notification
- If CPU OOM: Downscale image to 1024×1024, process, then upscale result
- If model download fails: Use fallback model (u2netp, smaller)

---

### 2. Image Upscale (Real-ESRGAN)

**Purpose:** Increase resolution using AI upscaling

**Inputs:**
- `asset_id` (UUID)
- `scale_factor` (int) — `2` | `4` (default: `2`)
- `model` (enum) — `RealESRGAN_x2plus` | `RealESRGAN_x4plus` | `realesr-animevideov3` (default: auto-select)
- `output_format` (enum) — `png` | `jpg` | `webp` (default: same as input)
- `use_gpu` (bool) — Default: `true`

**Outputs:**
- New Asset record
- File: `/Work/upscales/{asset_id}__x{scale}__{timestamp}.{ext}`

**Steps:**
1. **Load Asset Record**
2. **Hardware Check:**
   - 2x scale: VRAM ≥ 4 GB or RAM ≥ 8 GB
   - 4x scale: VRAM ≥ 6 GB or RAM ≥ 16 GB
3. **Model Selection:**
   - If scale=2 → RealESRGAN_x2plus
   - If scale=4 → RealESRGAN_x4plus
   - If anime/cartoon style detected → realesr-animevideov3
4. **Load Image:** Pillow (RGB or RGBA)
5. **Initialize Real-ESRGAN:**
   - Backend: CUDA/DirectML/CPU
   - Model: Load from Cache/models/ (download if missing)
6. **Process Image:**
   - Tile processing if image >2048px (to avoid VRAM overflow)
   - Tile size: 512×512 with 32px overlap
   - Stitch tiles with feathering to avoid seams
   - Progress: Per-tile completion (0-100%)
7. **Save Output:**
   - Format: PNG (lossless) or JPEG (quality=95)
   - Preserve EXIF if possible
8. **Create New Asset Record:**
   - Width/height = original × scale_factor
   - Tags: inherit + add `["upscaled", "x{scale}"]`
9. **Update Job:** status=success

**Compute Cost:**
- GPU (6 GB): 20-40s (2x), 60-120s (4x) per 2048×2048 image
- CPU (8 threads): 3-5 min (2x), 10-15 min (4x) per 2048×2048 image
- VRAM: 2-3 GB (2x), 4-6 GB (4x)
- RAM: 4-8 GB (2x), 8-16 GB (4x)

**Fallbacks:**
- If GPU OOM: Switch to CPU
- If CPU OOM: Process in smaller tiles (256×256)
- If extreme dimensions (>16K): Reject with error

---

### 3. Crop & Resize

**Purpose:** Non-AI geometric transforms

**Inputs:**
- `asset_id` (UUID)
- `crop_box` (optional) — `{x, y, width, height}` in pixels
- `resize_dimensions` (optional) — `{width, height}` in pixels or `{aspect_ratio}`
- `preset` (optional) — `square_1_1` | `portrait_4_5` | `landscape_16_9`
- `output_format` (enum) — Default: same as input

**Outputs:**
- New Asset record
- File: `/Work/edits/{asset_id}__cropped__{timestamp}.{ext}`

**Steps:**
1. **Load Asset & Image**
2. **Apply Crop:**
   - If `crop_box` provided: Pillow `image.crop((x, y, x+w, y+h))`
   - Validate: Box within image bounds
3. **Apply Resize:**
   - If `resize_dimensions`: Pillow `image.resize((w, h), Resampling.LANCZOS)`
   - If `preset`: Calculate dimensions from aspect ratio
4. **Save Output:** Preserve format or convert
5. **Create Asset Record:** Tags: `["edited", "cropped"]` or `["edited", "resized"]`
6. **Update Job:** status=success

**Compute Cost:**
- Instant (<1s for images <4K)
- RAM: <500 MB

**Fallbacks:** None needed (simple ops)

---

### 4. Face Restoration (Optional)

**Purpose:** Enhance faces in upscaled images using CodeFormer

**Inputs:**
- `asset_id` (UUID)
- `fidelity` (float 0-1) — Balance between quality and fidelity (default: 0.5)
- `use_gpu` (bool)

**Outputs:**
- New Asset record
- File: `/Work/edits/{asset_id}__face_restored__{timestamp}.png`

**Steps:**
1. **Detect Faces:** Use simple face detector (Haar cascades or dlib)
2. **If faces found:**
   - Initialize CodeFormer model (download to Cache/models/)
   - Process each face region
   - Blend restored faces back into original image
3. **If no faces:** Skip, return original with warning
4. **Save & Record**

**Compute Cost:**
- GPU: 30-60s per face
- CPU: 2-5 min per face
- VRAM: 2-4 GB

**Fallbacks:**
- If no faces detected: Skip, mark job success with note
- If CodeFormer unavailable: Fallback to simple sharpening filter

---

## Video Pipelines

### 5. Video Transcode

**Purpose:** Convert format, codec, or resolution

**Inputs:**
- `asset_id` (UUID)
- `output_format` (enum) — `mp4` | `webm` | `mov` (default: `mp4`)
- `video_codec` (enum) — `h264` | `h265` | `vp9` | `av1` (default: `h264`)
- `audio_codec` (enum) — `aac` | `opus` | `mp3` (default: `aac`)
- `resolution` (optional) — `{width, height}` or `preset` (e.g., `1080p`, `720p`)
- `bitrate` (optional) — Video bitrate in Mbps (default: auto)
- `fps` (optional) — Target framerate (default: preserve)
- `hardware_accel` (bool) — Use GPU encoder if available (default: `true`)

**Outputs:**
- New Asset record
- File: `/Work/edits/{asset_id}__transcoded__{timestamp}.{ext}`

**Steps:**
1. **Load Asset Record**
2. **Probe Input:** `ffprobe` to get current codec, resolution, bitrate, fps
3. **Hardware Check:**
   - If NVIDIA: Try `-c:v h264_nvenc` or `-c:v hevc_nvenc`
   - If AMD: Try `-c:v h264_amf`
   - If Intel: Try `-c:v h264_qsv`
   - Fallback: CPU software encoding (`libx264`)
4. **Build ffmpeg Command:**
   ```
   ffmpeg -i input.mp4 \
     -c:v h264_nvenc -preset fast -b:v 5M \
     -c:a aac -b:a 192k \
     -vf scale=1920:1080 \
     -progress pipe:1 \
     output.mp4
   ```
5. **Execute ffmpeg:** Subprocess with real-time progress parsing
   - Parse: `frame=X out_of Y` → calculate %
6. **Validate Output:**
   - Check file exists and size >0
   - Probe with ffprobe to confirm codec
7. **Create Asset Record:** Tags: `["transcoded", "{codec}"]`
8. **Update Job:** status=success

**Compute Cost:**
- GPU (NVENC): 0.2-0.5× realtime (5min video → 2-10min)
- CPU (libx264): 0.05-0.2× realtime (5min video → 25-100min)
- Disk: Output size ~= bitrate × duration

**Fallbacks:**
- If GPU encoder fails: Retry with CPU encoder
- If CPU too slow: Offer to reduce resolution or bitrate

---

### 6. Video Upscale (ESRGAN-ncnn-vulkan)

**Purpose:** Increase video resolution frame-by-frame

**Inputs:**
- `asset_id` (UUID)
- `scale_factor` (int) — `2` | `4` (default: `2`)
- `model` (enum) — Same as image upscale
- `denoise_strength` (float 0-1) — Reduce compression artifacts (default: 0.3)
- `output_format` (enum) — Default: same as input

**Outputs:**
- New Asset record
- File: `/Work/upscales/{asset_id}__x{scale}__{timestamp}.mp4`

**Steps:**
1. **Load Asset & Probe:**
   - Get fps, total_frames, resolution, codec
2. **Hardware Check:**
   - 720p→1080p (2x): VRAM ≥ 6 GB, Vulkan required
   - 1080p→4K (2x): VRAM ≥ 8 GB, RAM ≥ 20 GB
   - 4x: Block (too slow; suggest external tool)
3. **Extract Frames:**
   - Use ffmpeg: `ffmpeg -i input.mp4 frame_%06d.png`
   - Save to temp dir: `/Cache/video_frames/{job_id}/`
4. **Upscale Frames:**
   - Loop through frames
   - Call ESRGAN-ncnn-vulkan binary for each frame
   - Progress: frame_num / total_frames × 100%
   - Estimated time: ~0.5-2s per frame (depends on resolution)
5. **Reassemble Video:**
   - Use ffmpeg: `ffmpeg -framerate {fps} -i frame_%06d.png -c:v h264 output.mp4`
   - Copy audio stream from original: `-c:a copy`
6. **Cleanup Temp Frames:** Delete `/Cache/video_frames/{job_id}/`
7. **Create Asset Record**
8. **Update Job:** status=success

**Compute Cost:**
- 720p→1080p (1min video, 30fps): 15-30 min (GPU)
- 1080p→4K: 30-60 min (GPU)
- VRAM: 4-6 GB (1080p), 6-8 GB (4K)
- Disk: Temp frames ~= 500 MB per minute of video

**Fallbacks:**
- If Vulkan unavailable: Block with error (no CPU fallback for video)
- If VRAM OOM: Suggest shorter clips or lower resolution

---

### 7. Video Trim

**Purpose:** Cut video to specific start/end times

**Inputs:**
- `asset_id` (UUID)
- `start_time` (float) — Seconds from start (default: 0)
- `end_time` (float) — Seconds from start (default: full duration)
- `output_format` (enum) — Default: same as input

**Outputs:**
- New Asset record
- File: `/Work/edits/{asset_id}__trimmed__{timestamp}.mp4`

**Steps:**
1. **Load Asset & Probe**
2. **Validate Times:** 0 ≤ start < end ≤ duration
3. **Build ffmpeg Command:**
   ```
   ffmpeg -ss {start_time} -to {end_time} -i input.mp4 -c copy output.mp4
   ```
   (Stream copy mode: instant, no re-encoding)
4. **Execute ffmpeg**
5. **Create Asset Record:** Duration = end - start
6. **Update Job:** status=success

**Compute Cost:**
- Instant (<5s) if using `-c copy` (stream copy)
- If re-encode needed: ~1-5 min depending on length

**Fallbacks:** None needed

---

## Audio Pipelines

### 8. Audio Normalize (Loudness)

**Purpose:** Adjust loudness to target LUFS (Loudness Units Full Scale)

**Inputs:**
- `asset_id` (UUID)
- `target_lufs` (float) — Target loudness (default: `-14.0` for streaming, `-16.0` for podcasts)
- `limiter` (bool) — Apply limiter to prevent clipping (default: `true`)
- `output_format` (enum) — Default: same as input

**Outputs:**
- New Asset record
- File: `/Work/edits/{asset_id}__normalized__{timestamp}.{ext}`

**Steps:**
1. **Load Asset & Probe:** Get current loudness with ffmpeg EBU R128 filter
   ```
   ffmpeg -i input.mp3 -af ebur128 -f null -
   ```
   Parse output for current Integrated Loudness (LUFS)
2. **Calculate Gain:** `gain_db = target_lufs - current_lufs`
3. **Apply Normalization:**
   ```
   ffmpeg -i input.mp3 \
     -af "volume={gain_db}dB, alimiter=limit=0.95" \
     -c:a aac -b:a 192k \
     output.mp3
   ```
4. **Validate Output:** Re-probe to confirm loudness within ±0.5 LUFS
5. **Create Asset Record:** Tags: `["normalized", "{target_lufs}LUFS"]`
6. **Update Job:** status=success

**Compute Cost:**
- CPU: 0.5-2× realtime (5min audio → 2-10min)
- RAM: <500 MB

**Fallbacks:** None needed (ffmpeg is robust)

---

### 9. Audio Trim

**Purpose:** Cut audio to specific start/end times

**Inputs:**
- `asset_id` (UUID)
- `start_time` (float) — Seconds
- `end_time` (float) — Seconds
- `fade_in` (float) — Fade-in duration in seconds (default: 0)
- `fade_out` (float) — Fade-out duration in seconds (default: 0)
- `output_format` (enum)

**Outputs:**
- New Asset record
- File: `/Work/edits/{asset_id}__trimmed__{timestamp}.{ext}`

**Steps:**
1. **Load Asset**
2. **Build ffmpeg Command:**
   ```
   ffmpeg -ss {start} -to {end} -i input.mp3 \
     -af "afade=t=in:st={start}:d={fade_in}, afade=t=out:st={end-fade_out}:d={fade_out}" \
     -c:a aac output.mp3
   ```
3. **Execute ffmpeg**
4. **Create Asset Record**
5. **Update Job:** status=success

**Compute Cost:**
- Instant to fast (<30s for typical audio)
- RAM: <200 MB

---

### 10. Audio Format Conversion

**Purpose:** Convert between formats (MP3 ↔ WAV ↔ FLAC ↔ AAC ↔ OGG)

**Inputs:**
- `asset_id` (UUID)
- `output_format` (enum) — `mp3` | `wav` | `flac` | `aac` | `ogg`
- `bitrate` (optional) — For lossy formats (default: `192k` for MP3/AAC)
- `sample_rate` (optional) — Default: preserve

**Outputs:**
- New Asset record
- File: `/Work/edits/{asset_id}__converted__{timestamp}.{ext}`

**Steps:**
1. **Load Asset**
2. **Build ffmpeg Command:**
   ```
   ffmpeg -i input.mp3 -c:a libmp3lame -b:a 192k output.mp3
   ```
   Or for lossless:
   ```
   ffmpeg -i input.mp3 -c:a flac output.flac
   ```
3. **Execute ffmpeg**
4. **Create Asset Record**
5. **Update Job:** status=success

**Compute Cost:**
- CPU: 1-5× realtime (5min audio → 1-5min)
- Disk: WAV/FLAC larger; MP3/AAC smaller

---

## Thumbnail Generation

### 11. Image Thumbnail

**Purpose:** Generate small preview for grid display

**Inputs:**
- `asset_id` (UUID)
- `size` (int) — Max dimension (default: `200` for 200×200 max)
- `format` (enum) — `jpg` | `webp` (default: `jpg`)

**Outputs:**
- File: `/Cache/thumbnails/{asset_id}.jpg`
- No Asset record (ephemeral cache)

**Steps:**
1. **Load Asset**
2. **Load Image:** Pillow
3. **Resize:** Pillow `thumbnail((size, size))` (maintains aspect ratio)
4. **Save:** JPEG quality=85 or WebP quality=80
5. **Update Asset Record:** Set `thumbnail_path`

**Compute Cost:**
- Instant (<100ms per image)
- RAM: <100 MB

---

### 12. Video Thumbnail

**Purpose:** Extract frame as thumbnail

**Inputs:**
- `asset_id` (UUID)
- `timestamp` (float) — Time in seconds (default: 25% of duration, avoids black intros)
- `size` (int) — Default: `200`

**Outputs:**
- File: `/Cache/thumbnails/{asset_id}.jpg`

**Steps:**
1. **Load Asset & Probe**
2. **Extract Frame:**
   ```
   ffmpeg -ss {timestamp} -i input.mp4 -vframes 1 -vf scale={size}:-1 output.jpg
   ```
3. **Save to Cache**
4. **Update Asset Record:** Set `thumbnail_path`

**Compute Cost:**
- Fast (1-3s per video)

---

### 13. Audio Waveform Thumbnail

**Purpose:** Generate PNG waveform visualization

**Inputs:**
- `asset_id` (UUID)
- `width` (int) — Default: `400`
- `height` (int) — Default: `100`
- `color` (hex) — Waveform color (default: `#3b82f6`)

**Outputs:**
- File: `/Cache/thumbnails/{asset_id}.png`

**Steps:**
1. **Load Asset**
2. **Generate Waveform:**
   - **Option A (preferred):** Use `audiowaveform` binary (fast, accurate)
     ```
     audiowaveform -i input.mp3 -o waveform.png -w {width} -h {height} --colors {color}
     ```
   - **Option B (fallback):** Use matplotlib (slower)
     - Load audio with `pydub` or `librosa`
     - Downsample to match width
     - Plot with matplotlib
     - Save as PNG
3. **Save to Cache**
4. **Update Asset Record:** Set `thumbnail_path`

**Compute Cost:**
- audiowaveform: 1-5s
- matplotlib: 5-15s
- RAM: <500 MB

---

## Pack Export Pipeline

### 14. Build Pack

**Purpose:** Assemble selected assets into store-ready ZIP package

**Inputs:**
- `pack_id` (UUID) — Pack record with selected assets
- `export_options` (JSON) — Flags for what to include

**Outputs:**
- Directory: `/Packs/{pack_name}_{date}/`
- ZIP file: `/Packs/{pack_name}_{date}.zip`
- Updated Pack record with `status=completed`, `zip_path`

**Steps:**

#### Phase 1: Directory Setup (Progress 0-5%)
1. **Load Pack Record** from DB
2. **Create Export Directory:**
   ```
   /Packs/{slug}_{yyyymmdd_hhmmss}/
     ├── assets/
     ├── prompts/
     └── (files below)
   ```

#### Phase 2: Copy Assets (Progress 5-50%)
3. **Query PackAsset Join Table** for linked assets
4. **For each asset:**
   - Copy file to `assets/{filename}`
   - Update progress: `5 + (45 × current/total)`
   - Log any copy failures (skip, don't abort)

#### Phase 3: Generate README (Progress 50-60%)
5. **Load Template:** `/templates/README_default.md` or custom
6. **Populate Variables:**
   ```
   - {pack_name}
   - {description}
   - {license_type}
   - {asset_count}
   - {file_list} (generated from assets)
   - {date}
   ```
7. **Render with Jinja2 or simple string replacement**
8. **Save:** `README.md`

#### Phase 4: Generate LICENSE (Progress 60-70%)
9. **Load License Template:** Based on `license_type`
   - `/templates/LICENSE_personal.txt`
   - `/templates/LICENSE_commercial.txt`
   - `/templates/LICENSE_extended.txt`
10. **Populate Variables:** (year, author, pack_name)
11. **Save:** `LICENSE.txt`

#### Phase 5: Generate Store Copy (Progress 70-80%)
12. **Load Template:** `/templates/store_copy_default.txt`
13. **Populate Variables:**
    - {pack_name}
    - {description}
    - {asset_count}
    - {asset_types} (e.g., "20 images, 3 audio files")
    - {license_summary}
    - {suggested_price} (optional, heuristic)
14. **Save:** `store_copy.txt`

#### Phase 6: Generate Manifest (Progress 80-85%)
15. **Build Manifest JSON:**
    - Load all asset records
    - Extract metadata (width, height, hash, tags, prompts, edits)
    - Build schema per Data Models spec
16. **Save:** `manifest.json`

#### Phase 7: Copy Prompts (Progress 85-90%, optional)
17. **If `export_options.include_prompts`:**
    - For each asset with `prompt_ref`:
      - Copy prompt file to `prompts/{asset_id}.txt`
      - Or generate from asset.generator_meta if no file

#### Phase 8: Calculate Checksums (Progress 90-95%)
18. **For each file in pack directory:**
    - Calculate SHA-256 hash
    - Store in dict: `{rel_path: hash}`
19. **Save:** `checksums.txt` (or include in manifest)

#### Phase 9: Create ZIP (Progress 95-100%)
20. **Create ZIP Archive:**
    ```python
    shutil.make_archive(
        base_name=f"/Packs/{slug}_{date}",
        format="zip",
        root_dir=f"/Packs/{slug}_{date}"
    )
    ```
21. **Verify ZIP:** Check size >0, test extraction to temp dir
22. **Update Pack Record:**
    - `zip_path = ...`
    - `exported_at = now()`
    - `status = "completed"`

#### Phase 10: Cleanup (Optional)
23. **If `export_options.delete_unzipped`:**
    - Delete directory, keep only ZIP
    - (Default: keep both)

**Compute Cost:**
- Mostly disk I/O bound
- Time: ~5-30s for 20 assets (100 MB)
- Time: ~1-5 min for 100 assets (1 GB)
- Disk: Temp usage = 2× final pack size (unzipped + zipped)

**Fallbacks:**
- If single asset copy fails: Skip, log warning, continue
- If template missing: Use hardcoded fallback template
- If ZIP creation fails: Keep directory, mark job failed

---

## Common Utilities

### File Hash Calculation (SHA-256)

**Purpose:** Generate unique identifier for deduplication

**Steps:**
1. Open file in binary read mode
2. Hash in 64KB chunks (memory-efficient)
3. Return hex digest (64 chars)

**Compute Cost:** ~50-200 MB/s (depends on disk speed)

---

### Metadata Extraction

**Purpose:** Pull EXIF, AI generation metadata, codec info

**Tools:**
- **Images:** Pillow `image.info`, exiftool (optional)
- **Video:** ffprobe JSON output
- **Audio:** ffprobe, mutagen (ID3 tags)

**Steps:**
1. Run appropriate tool
2. Parse output (JSON or key-value)
3. Map to Asset model fields
4. Store unparsed metadata in `generator_meta` JSON

**Compute Cost:** 100-500ms per file

---

### Progress Reporting

**Implementation (pseudo-logic):**
```python
def report_progress(job_id, percent, message=None):
    # Update Job record in DB
    db.update(Job, id=job_id, progress=percent)
    
    # Emit event (for real-time UI updates)
    events.emit("job_progress", {"job_id": job_id, "progress": percent, "message": message})
    
    # Log
    logger.info(f"Job {job_id}: {percent}% — {message}")
```

---

## Error Handling

### Recoverable Errors
- **File not found:** Skip, log warning, continue processing other files
- **Corrupted image:** Log error, mark job failed, keep original
- **GPU OOM:** Retry on CPU (if supported)

### Fatal Errors
- **Disk full:** Abort job, show actionable error (free space)
- **Missing tool (ffmpeg):** Abort job, show install dialog
- **Invalid input:** Abort job, show validation error

### Retry Logic
- **Transient failures:** Retry up to 3 times with exponential backoff (1s, 2s, 4s)
- **Persistent failures:** Mark job failed, log stack trace

### User Notifications
- **Success:** Toast + Jobs panel update
- **Failure:** Persistent notification with [View Log] [Retry] buttons
- **Warning:** Non-blocking toast with [Dismiss] button

---

**End of Processing Pipelines Specification**  
**Next Steps:** Review pipelines, validate compute cost estimates, approve before implementation.
