# PODStudio — Product Vision

**Version**: 0.1.0  
**Last Updated**: October 22, 2025

---

## Problem Statement

POD (Print-on-Demand) creators using AI tools face a critical workflow gap:

**The Chaos**: AI generation tools (Stable Diffusion, MidJourney, Suno, ElevenLabs, Kling, Sora) produce hundreds of assets scattered across folders, with inconsistent naming, missing metadata, and no organization system.

**The Pain**: To create a store-ready asset pack (for Gumroad, Etsy, Creative Market), creators manually:
1. Hunt through folders to find related files
2. Rename and organize by hand
3. Open each file in Photoshop/GIMP to remove backgrounds or upscale
4. Write README/LICENSE files from scratch
5. Manually ZIP and upload

**Time Cost**: 4-8 hours per pack for manual curation and packaging.

**Revenue Impact**: Missed deadlines, inconsistent quality, burnout.

---

## Solution: PODStudio

**Tagline**: *From AI chaos to store-ready packs in minutes.*

PODStudio is a **Windows-first desktop app** that automates the entire post-generation workflow:

1. **Smart Ingestion**: Auto-detect new AI files, sort by type/theme/date, extract metadata
2. **Visual Curation**: Approve/reject workflow with keyboard shortcuts (video editor UX)
3. **AI Enhancement**: One-click background removal, upscaling, transcoding, normalization
4. **Pack Building**: Auto-generate README, LICENSE, manifest, store copy, and export to ZIP

**Key Differentiator**: Hardware-aware processing with safe fallbacks. No cloud dependency. No LLM calls (zero-AI mode for prompts).

---

## Target Audience (Personas)

### Primary: **Solo POD Creator**
- Age: 25-45
- Role: Freelance designer, side hustler, digital entrepreneur
- Platform: Windows 10/11 desktop (gaming PC or workstation)
- Hardware: Mid-tier GPU (RTX 3060, 8GB VRAM) or CPU-only laptop
- Pain: Overwhelmed by 100s of AI-generated files; needs fast, professional packaging
- Goal: Publish 2-4 packs/month on Gumroad/Etsy with minimal manual work

### Secondary: **Small POD Studio**
- Team: 2-3 creators collaborating
- Need: Consistent pack quality, shared templates, batch processing
- Future: Cloud mode for team sync (out of scope for v1.0)

### Anti-Persona: **Large Agencies**
- PODStudio is NOT for enterprise teams needing multi-user collaboration, cloud rendering, or advanced video editing

---

## Value Proposition

**For POD creators who generate assets with AI tools,**  
PODStudio is a **Windows-first desktop app**  
that **organizes, enhances, and packages** AI assets into **store-ready packs in minutes**,  
unlike **manual workflows or generic file managers**,  
PODStudio **understands AI metadata, hardware limits, and POD marketplace requirements**.

### Key Benefits
1. **Time Savings**: 4-8 hours → 30 minutes per pack
2. **Professional Output**: Consistent README/LICENSE/manifest; checksums for integrity
3. **Hardware Safety**: Auto-detect GPU/CPU limits; block crash-prone operations; fallback to CPU
4. **Offline-First**: No network calls; works without internet (optional cloud mode later)
5. **Zero-AI Mode**: Template-based prompts (no LLM API costs)

---

## Core Capabilities (v1.0)

### 1. Smart Asset Ingestion
- **Auto-Detection**: Watch Downloads folder; detect image/audio/video
- **Metadata Extraction**: EXIF, AI generation params (if embedded)
- **Auto-Organization**: Move to `/Library/{type}/{theme}/{date}/`
- **Database**: SQLite record with path, hash, tags, approval status

### 2. Visual Curation Interface
- **Layout**: Video editor-style docks (collapsible left/right panels, center grid)
- **Grid View**: Thumbnails (images), waveforms (audio), first frames (video)
- **Keyboard-First**: `A` = approve, `R` = reject, `Space` = toggle, `1-5` = star rating
- **Filters**: By type, approval status, tags, date

### 3. AI Enhancement Pipelines
- **Background Removal**: rembg (U2Net) with GPU/CPU fallback
- **Upscaling**: Real-ESRGAN 2x/4x (GPU) or fallback (CPU)
- **Transcoding**: FFmpeg for video/audio conversion
- **Normalization**: Loudness normalization (LUFS) for audio

### 4. Pack Builder & Exporter
- **10-Phase Export Pipeline**:
  1. Validate selections
  2. Generate README.md (template-based)
  3. Generate LICENSE.txt (Personal/Commercial/Extended)
  4. Generate store_copy.txt (marketing copy)
  5. Generate manifest.json (with checksums)
  6. Copy assets to temp folder
  7. Copy prompts (if applicable)
  8. Create ZIP
  9. Validate ZIP
  10. Move to `/Packs/`

### 5. Hardware Guardrails
- **Startup Probe**: GPU (VRAM), CPU (cores), RAM, disk space, external tools
- **Capability Tiers**:
  - **GREEN**: 6GB+ VRAM, all operations safe
  - **YELLOW**: 4-6GB VRAM or CPU-only, warn on heavy ops
  - **RED**: <2GB VRAM or missing tools, block unsafe ops
- **User Messaging**: Clear dialogs with upgrade/workaround guidance

### 6. Prompt Generation (Zero-AI Mode)
- **Template Engine**: Jinja2-based templates
- **Platform Support**: SDXL, MidJourney, Suno, ElevenLabs, Kling, Sora
- **Variable Substitution**: Theme, style, mood, BPM, camera angles
- **No LLM Calls**: Fully offline, no API costs

---

## Success Metrics (v1.0)

### User Adoption
- **Target**: 100 active users in first 3 months
- **Measure**: GitHub stars, downloads, Discord members

### Time Savings
- **Target**: <30 minutes per pack (vs. 4-8 hours manual)
- **Measure**: User surveys, in-app telemetry (opt-in)

### Pack Quality
- **Target**: 100% of exports pass marketplace validation
- **Measure**: User feedback, no LICENSE/README errors

### Stability
- **Target**: Zero crashes on GREEN-tier systems
- **Measure**: Crash reports, GPU fallback usage rates

### Community
- **Target**: 20+ GitHub issues/PRs in first 6 months
- **Measure**: Issue activity, contributor count

---

## Out of Scope (v1.0)

### Not Included
- **Real-time AI generation** (users generate externally)
- **Cloud sync or multi-user collaboration** (local-only)
- **Marketplace auto-upload** (manual upload for v1.0)
- **Advanced video editing** (beyond trim/transcode/upscale)
- **Audio mixing** (only normalization)
- **LLM-based prompt refinement** (zero-AI mode only)

### Future Roadmap (Post-v1.0)
- **Cloud Mode**: Optional backend for team sync (v1.2)
- **Batch Prompt Gen**: LLM-powered prompt refinement (v1.3)
- **Marketplace Integrations**: Auto-upload to Gumroad/Etsy (v2.0)
- **MacOS Port**: Qt cross-platform support (v2.0)

---

## Windows-First Strategy

**Why Windows?**
1. **POD Creator Hardware**: 70% use Windows desktops (gaming PCs, workstations)
2. **GPU Ecosystem**: NVIDIA CUDA/Vulkan better on Windows
3. **Toolchain Maturity**: FFmpeg, Real-ESRGAN, rembg all well-supported
4. **Faster MVP**: Single platform = faster iteration

**Future Cross-Platform**: Qt/PySide6 supports MacOS/Linux; can port later with minimal UI changes.

---

## Design Principles

1. **Local-First**: No cloud dependency; works offline
2. **Fail-Safe**: Hardware guardrails prevent crashes
3. **Professional Output**: Marketplace-ready by default
4. **Hardware-Aware**: Adapt to user's GPU/CPU/RAM
5. **Non-Destructive**: Never modify originals
6. **Keyboard-First**: Power users love shortcuts
7. **Minimalist UI**: Video editor aesthetic (docks, grids, cards)
8. **Zero Surprises**: Clear progress, ETA, cancel options

---

## Competitive Landscape

| Tool | Strength | Weakness vs. PODStudio |
|------|----------|------------------------|
| **Adobe Bridge** | Pro-grade DAM | No AI metadata, no pack building, expensive |
| **XnView MP** | Fast image browsing | No video/audio, no AI enhancements |
| **Bulk Rename Utility** | Powerful renaming | File-focused, no curation workflow |
| **Generic File Managers** | Universal | No AI context, no marketplace templates |

**PODStudio's Moat**: Deep integration with AI asset workflows + POD marketplace requirements.

---

## Open Questions (To Resolve)

1. **Redis Requirement**: RQ (task queue) needs Redis. Ship local Redis with installer, or use ThreadPoolExecutor only?
   - **Decision (Step 1)**: ThreadPoolExecutor default; RQ optional for power users.

2. **Real-ESRGAN Binary**: Bundle with installer or require manual download?
   - **Decision**: Document manual download; provide PATH guidance in `/docs/ops/external_tools.md`.

3. **Telemetry**: Opt-in anonymous usage stats for improvement?
   - **Decision**: Post-v1.0 feature; no telemetry in initial release.

---

**Status**: Vision approved. Ready for detailed specs (UX, architecture, data models).
