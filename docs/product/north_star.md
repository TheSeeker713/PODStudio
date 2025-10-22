# PODStudio — North Star User Journey

**Version**: 0.1.0  
**Last Updated**: October 22, 2025

---

## The Complete Workflow

This document defines the **ideal end-to-end user experience** for a POD creator using PODStudio.

---

## Phase 1: Initial Setup (First Launch)

### User Intent
New user wants to set up PODStudio for the first time.

### Steps
1. **Launch PODStudio** (double-click executable or Start Menu shortcut)
2. **Hardware Probe** (automatic, ~5 seconds):
   - Detects GPU (NVIDIA RTX 3060, 12GB VRAM)
   - Detects CPU (Intel i7, 12 cores)
   - Detects RAM (32GB)
   - Detects FFmpeg, ExifTool (PATH scan)
   - Assigns **GREEN tier** (all operations enabled)
3. **Welcome Dialog**:
   - "Welcome to PODStudio! We detected:"
   - ✅ NVIDIA RTX 3060 (12GB VRAM) — All AI operations enabled
   - ✅ FFmpeg found — Video/audio processing ready
   - ✅ ExifTool found — Metadata extraction ready
   - ⚠️ Real-ESRGAN not found — [Install Guide]
   - [Continue to App]
4. **First-Time Tour** (skippable):
   - "This is the Library Grid — your organized assets appear here"
   - "Use Left Panel to start File Listener or write instructions"
   - "Select assets and click 'Build Pack' to export"
   - [Skip Tour] [Next] buttons

### Outcome
- User understands hardware capabilities
- User knows which features work (and which need additional tools)
- User sees empty UI, ready to ingest assets

---

## Phase 2: Asset Ingestion

### Scenario A: Manual Drag-and-Drop

1. User has 50 AI-generated images in `C:\Users\Alex\Downloads\StableDiffusion\`
2. User drags folder into PODStudio center grid
3. **Auto-Ingest Pipeline** (10-15 seconds):
   - Scan 50 files
   - Detect MIME types (49 PNG, 1 corrupted file)
   - Extract dimensions, EXIF metadata, AI params (if embedded)
   - Compute SHA-256 hashes
   - Move files to `/Library/images/fantasy_characters/2025-10-22/`
   - Create DB records (Asset table)
   - Generate thumbnails (256px) in `/Cache/thumbnails/`
4. **Grid Updates**:
   - Shows 49 thumbnails (1 skipped with error icon)
   - Status bar: "Imported 49 images, 1 error"
   - User clicks error icon: "Corrupted file: invalid PNG signature"

### Scenario B: Auto-Watch Folder

1. User enables "File Listener" in Left Panel
2. Configures watch folder: `C:\Users\Alex\Downloads`
3. User generates 10 new images with SDXL (saves to Downloads)
4. **Watcher detects** new files within 2 seconds:
   - Auto-runs same ingest pipeline
   - Notification: "10 new images added to Library"
   - Grid auto-refreshes

### Outcome
- All AI assets are in `/Library/`, organized by type/theme/date
- Database has full metadata (path, hash, dims, tags)
- Thumbnails are cached for instant grid display

---

## Phase 3: Curation (Approve/Reject)

### User Intent
Review 200 AI-generated images and approve the best 30 for a pack.

### Steps
1. **Filter** (Left Panel):
   - Type: Images
   - Date: Last 7 days
   - Theme: "fantasy_characters"
   - Approval Status: All (not yet curated)
2. **Grid View** (Center):
   - Shows 200 thumbnails in 6-column grid
   - Hover = show filename, dimensions, file size
   - Click = show in Right Panel Inspector
3. **Keyboard Workflow** (power user):
   - `↓` = next asset
   - `↑` = previous asset
   - `A` = approve (green checkmark overlay)
   - `R` = reject (red X overlay, fades out)
   - `Space` = toggle full preview
   - `1-5` = star rating
   - `T` = add tag (inline text input)
4. **Visual Feedback**:
   - Approved assets have green border
   - Rejected assets fade to 30% opacity or hide (user pref)
   - Counter updates: "30 approved, 150 rejected, 20 pending"
5. **Undo**: `Ctrl+Z` to undo last action

### Outcome
- 30 assets marked "approved"
- Database updated (`approved = true` for 30 rows)
- User ready to enhance or export

---

## Phase 4: Enhancement (Background Removal + Upscaling)

### User Intent
Remove backgrounds from 30 approved character images and upscale 10 to 4K.

### Steps: Background Removal

1. User selects 30 approved images (Shift+Click or `Ctrl+A` in filtered view)
2. Right-click → "Remove Background (rembg)"
3. **Pre-Flight Check**:
   - Hardware: GREEN tier, 12GB VRAM → OK
   - Batch size: 30 images × ~500KB = 15MB → OK
   - Estimated time: ~60 seconds (GPU mode)
   - [Start Job] [Cancel]
4. **Job Processing**:
   - Bottom tray shows progress bar: "Removing backgrounds... 10/30 (30s elapsed, ~40s remaining)"
   - Real-time thumbnail updates as each completes
   - Outputs saved to `/Work/bg_removed/{date}/`
5. **Completion**:
   - Notification: "Background removal complete: 30/30 succeeded"
   - Grid shows toggle: [Original] [BG-Removed] side-by-side
   - User can approve/reject BG-removed versions

### Steps: Upscaling

1. User selects 10 best images from BG-removed set
2. Right-click → "Upscale 4x (Real-ESRGAN)"
3. **Pre-Flight Check**:
   - Hardware: GREEN tier, Real-ESRGAN binary found → OK
   - Input: 10 × 1024×1024 → Output: 10 × 4096×4096
   - Estimated time: ~120 seconds (GPU mode)
   - Estimated disk: ~200MB
   - [Start Job] [Cancel]
4. **Job Processing** (same as above)
5. **Completion**:
   - 10 4K images saved to `/Work/upscaled_4x/{date}/`
   - Grid shows toggle: [Original] [BG-Removed] [Upscaled]

### Outcome
- 30 BG-removed PNGs ready for pack
- 10 4K upscaled versions (optional premium tier)
- All originals untouched (non-destructive)

---

## Phase 5: Pack Building

### User Intent
Export 30 BG-removed images as a store-ready pack for Gumroad.

### Steps

1. **Create New Pack** (Bottom Tray):
   - Click "Build Pack" button
   - Dialog: "New Pack"
     - Name: "Fantasy Character Pack Vol. 1"
     - Theme: "fantasy_characters"
     - License: Commercial (dropdown: Personal/Commercial/Extended)
     - Platform: Gumroad (dropdown: Gumroad/Etsy/Creative Market/Generic)
     - Description: "30 high-quality AI-generated fantasy characters with transparent backgrounds"
   - [Create Pack]

2. **Asset Selection**:
   - Pre-selected: 30 approved BG-removed images
   - User can add/remove from Bottom Tray selection
   - Preview: Thumbnails with checkboxes

3. **Pack Builder Execution** (10-phase pipeline, ~30 seconds):
   - Phase 1: Validate selections (30 assets, all PNG, total 45MB)
   - Phase 2: Generate README.md (template: Gumroad Commercial)
   - Phase 3: Generate LICENSE.txt (Commercial Rights template)
   - Phase 4: Generate store_copy.txt (marketing description)
   - Phase 5: Generate manifest.json (asset list, SHA-256 checksums, pack metadata)
   - Phase 6: Copy assets to temp folder `/Packs/.temp/fantasy_pack_v1/`
   - Phase 7: Copy prompts (if applicable; N/A for this pack)
   - Phase 8: Create ZIP `/Packs/Fantasy_Character_Pack_Vol1_2025-10-22.zip`
   - Phase 9: Validate ZIP (integrity, size, required files)
   - Phase 10: Clean up temp folder
   - Progress bar shows each phase

4. **Completion**:
   - Success notification: "Pack exported successfully!"
   - File location: `C:\Users\Alex\PODStudio\Packs\Fantasy_Character_Pack_Vol1_2025-10-22.zip`
   - Quick actions:
     - [Open Folder]
     - [Upload to Gumroad] (future feature; N/A for v1.0)
     - [Create Another Pack]

### Pack Contents (User opens ZIP to verify)

```
Fantasy_Character_Pack_Vol1/
  README.md               (Gumroad-formatted, 8 sections)
  LICENSE.txt             (Commercial Rights with usage terms)
  store_copy.txt          (marketing description for listing)
  manifest.json           (asset list, checksums, pack metadata)
  assets/
    character_001.png
    character_002.png
    ...
    character_030.png
```

### Outcome
- 1 ZIP file (45MB) ready for Gumroad upload
- Includes README, LICENSE, manifest with checksums
- User uploads manually to Gumroad (auto-upload is v2.0 feature)

---

## Phase 6: Prompt Generation (Bonus Workflow)

### User Intent
Generate 10 Stable Diffusion XL prompts for a "cyberpunk city" theme.

### Steps

1. **Left Panel → Instructions Tab**:
   - Theme: "cyberpunk city"
   - Style: "neon-lit, dystopian, rainy streets"
   - Platform: Stable Diffusion XL (dropdown)
   - Quantity: 10
   - [Generate Prompts]

2. **Template Engine**:
   - Loads `/docs/prompt_templates/image_sdxl.txt`
   - Variables: `{theme}`, `{style}`, `{quality_tags}`
   - Renders 10 unique prompts with variations

3. **Output**:
   - Prompts appear in Right Panel → Prompts Tab
   - Each prompt is editable text box
   - [Copy All] [Export to TXT]
   - Example:
     ```
     A cyberpunk city street at night, neon-lit signs, dystopian atmosphere,
     rainy reflections on pavement, high detail, 8k, cinematic lighting,
     trending on ArtStation
     ```

4. **User Copies** prompts to Stable Diffusion UI (external tool)
5. Generates 50 images, saves to Downloads
6. **File Listener** auto-detects, ingests to `/Library/images/cyberpunk_city/2025-10-22/`

### Outcome
- User has 10 high-quality prompts without LLM API calls
- Cycle repeats: generate → ingest → curate → enhance → pack

---

## North Star Metrics

### Time to First Pack
- **Goal**: <10 minutes from launch to exported ZIP (for returning user with pre-ingested assets)
- **Breakdown**:
  - Ingest 50 files: 15 seconds
  - Curate (approve 30): 3 minutes
  - Enhance (BG removal): 60 seconds
  - Build pack: 30 seconds
  - Total: ~5 minutes

### User Satisfaction
- **Goal**: "This saved me hours" feedback from 80%+ of users
- **Measure**: Post-export survey (optional)

### Feature Adoption
- **Goal**: 70% use enhancement pipelines (BG removal or upscaling)
- **Goal**: 50% use prompt templates
- **Measure**: Anonymous usage telemetry (opt-in, post-v1.0)

---

**Status**: North Star approved. Ready for detailed UX wireframes.
