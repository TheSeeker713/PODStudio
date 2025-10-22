# PODStudio — Test Plan

**Version:** 1.0.0  
**Date:** October 22, 2025  
**Status:** Design Specification

---

## Table of Contents

1. [Overview](#overview)
2. [Test Strategy](#test-strategy)
3. [UX Smoke Tests](#ux-smoke-tests)
4. [Feature Tests](#feature-tests)
5. [Performance Tests](#performance-tests)
6. [Hardware Policy Tests](#hardware-policy-tests)
7. [Export Validation Tests](#export-validation-tests)
8. [Edge Cases & Error Handling](#edge-cases--error-handling)
9. [Manual Test Checklist](#manual-test-checklist)
10. [Acceptance Criteria](#acceptance-criteria)

---

## Overview

This test plan ensures PODStudio meets all design requirements before v1.0 release. Tests are **manual** (no automation required for v1), with clear pass/fail criteria.

### Test Goals
- Verify all core workflows function end-to-end
- Ensure UI is responsive and intuitive
- Validate hardware guardrails prevent crashes
- Confirm exported packs meet contract spec
- Identify blockers and edge cases

### Test Environment
- **OS:** Windows 10 & 11
- **Hardware Profiles:** Low-end, mid-range, high-end (see Hardware Policy doc)
- **Test Data:** Sample assets (images, audio, video) in various formats and sizes

---

## Test Strategy

### Phases

#### Phase 1: UX Smoke Tests
- First-time user experience (onboarding)
- Core workflows (import → curate → export)
- UI responsiveness and navigation

#### Phase 2: Feature Tests
- Each processing pipeline (bg-remove, upscale, transcode, etc.)
- Prompt generation
- Pack builder with all options

#### Phase 3: Performance Tests
- UI remains responsive during long jobs
- Batch operations complete without crashes
- Memory usage stays within bounds

#### Phase 4: Hardware Policy Tests
- GREEN/YELLOW/RED tier behavior
- Warning and block messages
- Fallback modes (GPU → CPU)

#### Phase 5: Export Validation Tests
- All required files present
- Checksums verify
- Manifest schema valid
- ZIP extraction works

#### Phase 6: Edge Cases
- Corrupted files
- Missing tools (ffmpeg)
- Disk full scenarios
- Network interruptions (if online LLM used)

---

## UX Smoke Tests

### Test 1.1: First Launch & Onboarding

**Objective:** New user can start using app within 5 minutes

**Steps:**
1. Launch PODStudio for the first time
2. Observe hardware detection (2-3 second wait)
3. Main window opens showing empty state
4. Read welcome message and CTAs

**Expected Results:**
- ✅ App starts without errors
- ✅ Hardware indicator shows correct tier (🟢/🟡/🔴)
- ✅ Empty state message is clear and actionable
- ✅ [Enable Listener] and [Import Files] buttons visible

**Pass Criteria:** User understands next steps without external help

---

### Test 1.2: Add Watch Folder

**Objective:** User can enable auto-ingest from Downloads

**Steps:**
1. Click "Enable Listener" or expand Smart Listener panel
2. Click [+ Add Folder]
3. Select `Downloads` folder
4. Observe status change to "● ACTIVE"

**Expected Results:**
- ✅ Folder picker opens
- ✅ Selected folder appears in watch list
- ✅ Status indicator turns green/active
- ✅ No errors or crashes

**Pass Criteria:** Folder is actively monitored (verify with next test)

---

### Test 1.3: First Asset Auto-Imported

**Objective:** File dropped in watched folder is auto-detected and sorted

**Steps:**
1. Copy a test image (e.g., `dragon.png`) to `Downloads`
2. Wait up to 5 seconds
3. Observe toast notification
4. Check center pane for new thumbnail

**Expected Results:**
- ✅ Toast notification: "New asset detected: dragon.png"
- ✅ Asset appears in grid within 5 seconds
- ✅ Asset routed to `/Library/images/{theme}/{date}/` (check file system)
- ✅ DB record created with correct metadata
- ✅ Thumbnail generated and displayed

**Pass Criteria:** Asset visible and clickable in UI

---

### Test 1.4: Select Asset & View Inspector

**Objective:** User can view asset details

**Steps:**
1. Click on asset thumbnail in grid
2. Observe right dock (Inspector panel)

**Expected Results:**
- ✅ Asset selected (checkmark or highlight)
- ✅ Inspector shows: filename, dimensions, size, format, tags
- ✅ Thumbnail preview displayed
- ✅ Actions and Enhance panels become active

**Pass Criteria:** All metadata visible and accurate

---

### Test 1.5: Approve Asset

**Objective:** User can approve an asset for later pack export

**Steps:**
1. Select asset
2. Click [Approve] button in Actions panel (or press `A`)
3. Observe visual feedback

**Expected Results:**
- ✅ Asset marked with ✓ badge
- ✅ DB record updated: `approved=true`
- ✅ Asset stays visible (not filtered out)

**Pass Criteria:** Approved state persists after app restart

---

### Test 1.6: Run Enhancement Job (Background Removal)

**Objective:** User can enhance an asset

**Steps:**
1. Select asset
2. Expand Enhance panel
3. Click [Remove Background]
4. If warning appears, click [Continue]
5. Observe Jobs panel badge update
6. Wait for job completion

**Expected Results:**
- ✅ Hardware check runs (no block on capable system)
- ✅ Job appears in Jobs panel with progress bar
- ✅ Progress updates in real-time (0% → 100%)
- ✅ UI remains responsive (can navigate during job)
- ✅ On completion: success notification + new asset in grid
- ✅ New asset has `_nobg` suffix and transparent background

**Pass Criteria:** Job completes without crash; output is correct

---

### Test 1.7: Build First Pack

**Objective:** User can export a simple pack

**Steps:**
1. Select 3 approved assets (Ctrl+Click)
2. Click [Build Pack] in bottom tray
3. Fill pack details:
   - Name: "Test Pack"
   - Theme: "test"
   - Description: "Test description"
   - License: Commercial
4. Click [Build Pack]
5. Wait for export to complete
6. Click [Open Folder]

**Expected Results:**
- ✅ Pack Builder modal opens with pre-filled fields
- ✅ Export runs with progress indicator
- ✅ No errors during export
- ✅ Success dialog appears
- ✅ Windows Explorer opens to pack folder
- ✅ All required files present: README.md, LICENSE.txt, manifest.json, assets/, ZIP file

**Pass Criteria:** Pack folder contains 3 assets + all required files; ZIP extracts correctly

---

## Feature Tests

### Test 2.1: Prompt Generation (Template Mode)

**Objective:** Generate prompts from natural language brief

**Steps:**
1. Expand Prompt Generator panel
2. Enter brief: "Dark fantasy dragon breathing fire"
3. Select Asset Type: Image
4. Select Style Chips: Fantasy, Epic
5. Click [Generate Prompts]
6. Observe output

**Expected Results:**
- ✅ Output box populates with SDXL and MidJourney prompts
- ✅ Prompts contain relevant keywords from brief
- ✅ MidJourney prompt includes parameters (--ar, --v)
- ✅ [Copy] buttons work (clipboard populated)

**Pass Criteria:** Generated prompts are coherent and usable

---

### Test 2.2: Upscale Image (2x)

**Objective:** Test image upscaling pipeline

**Preconditions:** Test image: 1024×1024 PNG

**Steps:**
1. Select test image
2. Enhance panel → Upscale
3. Set scale: 2x, model: RealESRGAN_x2plus
4. Click [Upscale Image]
5. Monitor job in Jobs panel
6. Verify output

**Expected Results:**
- ✅ Job starts (status: running)
- ✅ Progress updates (0-100%)
- ✅ Estimated time shown
- ✅ Job completes (status: success)
- ✅ New asset created: 2048×2048
- ✅ Output file in `/Work/upscales/`
- ✅ Visual quality improved (inspect manually)

**Pass Criteria:** Output is 2× resolution with no artifacts

---

### Test 2.3: Video Transcode

**Objective:** Convert video format

**Preconditions:** Test video: 5-second MP4, 1080p

**Steps:**
1. Select test video
2. Enhance panel → Transcode
3. Set format: MP4, codec: H.264, resolution: 720p
4. Click [Transcode]
5. Wait for completion

**Expected Results:**
- ✅ ffmpeg detected (or error if missing)
- ✅ Job runs with progress (based on frames processed)
- ✅ Output video: 720p, H.264, playable
- ✅ Audio preserved (if input had audio)

**Pass Criteria:** Output plays correctly in Windows Media Player

---

### Test 2.4: Audio Normalization

**Objective:** Normalize audio loudness to -14 LUFS

**Preconditions:** Test audio: 3-minute MP3, varied loudness

**Steps:**
1. Select test audio
2. Enhance panel → Normalize
3. Set target: -14 LUFS
4. Click [Normalize]
5. Verify output

**Expected Results:**
- ✅ Job completes in <30 seconds
- ✅ Output file has consistent loudness (verify with ffprobe or ears)
- ✅ No clipping or distortion

**Pass Criteria:** Output loudness within ±0.5 LUFS of target

---

### Test 2.5: Batch Operations (5 Assets)

**Objective:** Process multiple assets simultaneously

**Steps:**
1. Import 5 test images (1024×1024 each)
2. Select all 5 (Ctrl+A)
3. Right-click → Upscale → 2x
4. Confirm batch operation
5. Monitor Jobs panel

**Expected Results:**
- ✅ 5 jobs queued
- ✅ Jobs start based on hardware capability (max concurrent)
- ✅ Progress shown for each
- ✅ All complete successfully
- ✅ 5 new upscaled assets in library

**Pass Criteria:** All jobs succeed; UI responsive throughout

---

## Performance Tests

### Test 3.1: UI Responsiveness During Long Job

**Objective:** UI doesn't freeze during CPU-intensive task

**Preconditions:** Run on CPU-only system (or simulate)

**Steps:**
1. Start a 5-minute upscale job (large image, CPU mode)
2. While job running, navigate app:
   - Switch tabs
   - Scroll grid
   - Open inspector
   - Search assets

**Expected Results:**
- ✅ UI remains smooth (<16ms frame time target)
- ✅ No stuttering or freezing
- ✅ Job progress updates in real-time

**Pass Criteria:** User can work on other tasks while job runs

---

### Test 3.2: Memory Leak Check

**Objective:** Memory usage stable over time

**Steps:**
1. Launch app
2. Import 100 test assets
3. Run 20 background removal jobs in sequence
4. Monitor RAM usage (Task Manager)

**Expected Results:**
- ✅ RAM usage increases during jobs
- ✅ RAM returns to baseline after jobs complete
- ✅ No continuous growth (leak)
- ✅ Peak usage < 2 GB (on 16 GB system)

**Pass Criteria:** Memory usage stable after 1 hour

---

### Test 3.3: Large Pack Export (100 Assets)

**Objective:** Pack builder handles large asset count

**Steps:**
1. Select 100 assets
2. Build pack with all options enabled
3. Monitor export time and disk usage

**Expected Results:**
- ✅ Export completes in <5 minutes
- ✅ Progress indicator accurate
- ✅ No crashes or errors
- ✅ All 100 assets copied correctly
- ✅ Manifest.json valid and contains all assets

**Pass Criteria:** Pack exports successfully and is under 2 GB

---

## Hardware Policy Tests

### Test 4.1: GREEN Tier (High-End System)

**Hardware:** RTX 3060 (8 GB VRAM), 16 GB RAM, 8 threads

**Steps:**
1. Launch app
2. Verify hardware indicator: 🟢 GPU · 8GB
3. Try all operations (bg-remove, upscale 4x, video upscale)

**Expected Results:**
- ✅ All operations allowed (no blocks)
- ✅ No warnings shown
- ✅ GPU used for all ops

**Pass Criteria:** Full functionality, fast execution

---

### Test 4.2: YELLOW Tier (CPU-Only)

**Hardware:** No dedicated GPU, 16 GB RAM, 8 threads

**Steps:**
1. Launch app
2. Verify hardware indicator: 🟡 CPU · 16GB
3. Try upscale 2x on image
4. Observe warning dialog

**Expected Results:**
- ✅ Warning shown: "CPU-only mode; estimated time: X minutes"
- ✅ User can click [Continue] or [Cancel]
- ✅ If continued: Job runs on CPU (slower)
- ✅ Job completes successfully

**Pass Criteria:** Warning is clear; job succeeds (even if slow)

---

### Test 4.3: RED Tier (Insufficient VRAM)

**Hardware:** Integrated GPU (<1 GB VRAM)

**Steps:**
1. Launch app
2. Try video upscale (1080p → 4K)
3. Observe error dialog

**Expected Results:**
- ✅ Operation blocked
- ✅ Error dialog explains reason: "Insufficient VRAM"
- ✅ Dialog suggests alternatives (lower resolution, upgrade GPU)
- ✅ No crash or hang

**Pass Criteria:** User understands why blocked and what to do

---

### Test 4.4: Missing Tool (ffmpeg)

**Preconditions:** Remove ffmpeg from PATH

**Steps:**
1. Launch app
2. Try video transcode
3. Observe error dialog

**Expected Results:**
- ✅ Error: "ffmpeg missing"
- ✅ Dialog offers [Download & Install] button
- ✅ Or shows manual install instructions

**Pass Criteria:** User can resolve issue without external help

---

## Export Validation Tests

### Test 5.1: Required Files Present

**Objective:** All mandatory files in pack

**Steps:**
1. Build a pack with 5 assets
2. Extract ZIP to temp folder
3. Check file presence

**Expected Results:**
- ✅ `README.md` exists and >500 bytes
- ✅ `LICENSE.txt` exists and matches license type
- ✅ `manifest.json` exists and is valid JSON
- ✅ `/assets/` folder contains 5 files
- ✅ All 5 assets match selection

**Pass Criteria:** All required files present per Export Contract

---

### Test 5.2: Checksums Verify

**Objective:** File integrity validation

**Steps:**
1. Build pack with checksums enabled
2. Extract ZIP
3. Recalculate SHA-256 for each asset
4. Compare with `checksums.txt` or `manifest.json`

**Expected Results:**
- ✅ All checksums match
- ✅ No corrupted files

**Pass Criteria:** 100% checksum match

---

### Test 5.3: Manifest Schema Valid

**Objective:** Manifest conforms to schema

**Steps:**
1. Build pack
2. Open `manifest.json`
3. Validate against JSON schema (manual or tool)

**Expected Results:**
- ✅ All required keys present
- ✅ Data types correct (strings, integers, arrays)
- ✅ Asset count matches actual file count
- ✅ Total size matches actual size (±1%)

**Pass Criteria:** Manifest is valid JSON and semantically correct

---

### Test 5.4: Platform-Specific Export (Gumroad)

**Objective:** Gumroad-style export works

**Steps:**
1. Build pack with 50 assets
2. Select export option: "Platform: Gumroad"
3. Observe output structure

**Expected Results:**
- ✅ Separate ZIPs per asset type (images.zip, audio.zip, etc.)
- ✅ Each ZIP <100 MB (if possible)
- ✅ Docs ZIP contains README, LICENSE, manifest

**Pass Criteria:** Structure matches Gumroad best practices

---

## Edge Cases & Error Handling

### Test 6.1: Corrupted Image File

**Objective:** App handles bad file gracefully

**Steps:**
1. Create corrupted PNG (truncate file or edit header)
2. Import to library
3. Try to open/process

**Expected Results:**
- ✅ Import detects corruption, shows warning
- ✅ Asset marked as "corrupted" or skipped
- ✅ No crash
- ✅ Log entry created

**Pass Criteria:** App remains stable

---

### Test 6.2: Disk Full During Export

**Objective:** Handle disk space exhaustion

**Steps:**
1. Fill disk to <100 MB free
2. Try to build large pack (500 MB)
3. Observe error

**Expected Results:**
- ✅ Export fails gracefully
- ✅ Error dialog: "Insufficient disk space"
- ✅ Partial files cleaned up
- ✅ Disk space suggestions shown

**Pass Criteria:** No orphaned files; clear next steps

---

### Test 6.3: Cancel Job Mid-Execution

**Objective:** User can cancel long-running job

**Steps:**
1. Start 5-minute upscale job
2. After 1 minute, click [Cancel] in Jobs panel
3. Observe behavior

**Expected Results:**
- ✅ Job stops within 5 seconds
- ✅ Status changes to "canceled"
- ✅ Temp files cleaned up
- ✅ No output asset created

**Pass Criteria:** Clean cancellation, no orphaned data

---

### Test 6.4: Restart App with Active Jobs

**Objective:** Jobs don't corrupt DB after crash

**Steps:**
1. Start 3 jobs
2. Force-quit app (Task Manager → End Task)
3. Restart app
4. Check Jobs panel

**Expected Results:**
- ✅ Jobs marked as "failed" or "canceled"
- ✅ No stuck "running" jobs
- ✅ App starts normally
- ✅ User can retry jobs

**Pass Criteria:** DB remains consistent

---

## Manual Test Checklist

### Pre-Release Checklist

Run through this list before v1.0 release:

#### Installation
- [ ] Installer runs on clean Windows 10
- [ ] Installer runs on clean Windows 11
- [ ] Bundled ffmpeg detected and works
- [ ] First launch completes successfully

#### Core Workflows
- [ ] Import assets (drag-drop and watch folder)
- [ ] View asset inspector with all metadata
- [ ] Approve and reject assets
- [ ] Run background removal job
- [ ] Run upscale job (2x and 4x)
- [ ] Run video transcode
- [ ] Run audio normalization
- [ ] Build pack with 10 assets
- [ ] Extract and verify pack ZIP

#### UI/UX
- [ ] All panels collapsible and resizable
- [ ] Keyboard shortcuts work (A, R, Ctrl+A, etc.)
- [ ] Search finds assets by name/tags
- [ ] Filters work (type, theme, approval)
- [ ] Jobs panel updates in real-time
- [ ] Settings save and load correctly

#### Hardware Policy
- [ ] Correct tier detected (GREEN/YELLOW/RED)
- [ ] Warnings shown on YELLOW tier
- [ ] Blocks shown on RED tier
- [ ] CPU fallback works when GPU unavailable

#### Error Handling
- [ ] Corrupted file handled gracefully
- [ ] Missing ffmpeg detected and reported
- [ ] Disk full handled gracefully
- [ ] Job cancellation works
- [ ] App restart after crash recovers

#### Documentation
- [ ] README.md complete and accurate
- [ ] LICENSE.txt variants correct
- [ ] Manifest.json schema valid
- [ ] Store_copy.txt helpful

---

## Acceptance Criteria

### v1.0 Must-Haves

- ✅ **Core Workflow:** User can go from raw assets to exportable pack in <30 minutes
- ✅ **Stability:** Zero crashes during 2-hour test session on supported hardware
- ✅ **Performance:** UI <16ms frame time during background jobs
- ✅ **Hardware Safety:** RED tier ops blocked; YELLOW tier warns
- ✅ **Export Quality:** 100% of packs pass validation checklist
- ✅ **Documentation:** All 10 design docs approved and internally consistent

### Nice-to-Haves (Post-v1.0)

- Real-time job updates (WebSocket instead of polling)
- Cloud mode (headless backend + web UI)
- Batch prompt generation
- Auto-tagging with local AI model
- Marketplace auto-upload (Gumroad API)

---

**End of Test Plan**  
**Next Steps:** Execute tests on test hardware, document results, fix issues, re-test until all acceptance criteria met.
