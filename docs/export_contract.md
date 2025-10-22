# PODStudio — Export Contract Specification

**Version:** 1.0.0  
**Date:** October 22, 2025  
**Status:** Design Specification

---

## Table of Contents

1. [Overview](#overview)
2. [Pack Directory Structure](#pack-directory-structure)
3. [Required Files](#required-files)
4. [Optional Files](#optional-files)
5. [File Naming Conventions](#file-naming-conventions)
6. [README Format](#readme-format)
7. [LICENSE Variants](#license-variants)
8. [Store Copy Format](#store-copy-format)
9. [Manifest Contract](#manifest-contract)
10. [Platform-Specific Exports](#platform-specific-exports)
11. [Validation Checklist](#validation-checklist)

---

## Overview

This document defines the **exact structure and contents** of exported PODStudio asset packs. All exports must conform to this contract to ensure:
- Professional presentation
- Legal compliance
- Customer clarity
- Marketplace compatibility

### Design Goals
- **Self-documenting**: Every pack explains itself
- **Legal safety**: Clear licensing and usage terms
- **Technical transparency**: Manifest provides full provenance
- **Marketplace-ready**: Works with Gumroad, Etsy, Creative Market without modification

---

## Pack Directory Structure

### Standard Export (Default)

```
{pack_name}_{yyyymmdd_hhmmss}/
│
├── assets/                      # All included assets
│   ├── dragon_fire.png
│   ├── castle_wall.jpg
│   ├── epic_battle.mp3
│   └── dragon_flight.mp4
│
├── prompts/                     # Generation prompts (optional)
│   ├── dragon_fire.txt
│   ├── castle_wall.txt
│   └── dragon_flight.txt
│
├── README.md                    # Pack documentation (REQUIRED)
├── LICENSE.txt                  # Usage terms (REQUIRED)
├── manifest.json                # Technical metadata (REQUIRED)
├── store_copy.txt               # Marketing copy (OPTIONAL)
├── checksums.txt                # File integrity (OPTIONAL but recommended)
│
└── previews/                    # Thumbnails/previews (OPTIONAL)
    ├── preview_1.jpg
    ├── preview_2.jpg
    └── preview_grid.jpg
```

### Compressed Export

```
{pack_name}_{yyyymmdd_hhmmss}.zip
  └── (contains all files from above structure)
```

---

## Required Files

### 1. README.md

**Purpose:** Human-readable documentation

**Sections (Mandatory):**
1. **Title & Description**
2. **Contents List** (file count by type)
3. **Usage Guidelines**
4. **License Summary**
5. **Technical Specifications**
6. **Credits/Attribution** (if applicable)
7. **Support Contact**

**Format:** Markdown (CommonMark spec)

**Max Size:** 50 KB

---

### 2. LICENSE.txt

**Purpose:** Legal usage terms

**Format:** Plain text

**Variants:** Personal | Commercial | Extended (see below)

**Requirements:**
- Include copyright year and holder
- Specify allowed uses
- Specify prohibited uses
- State attribution requirements (if any)
- Include warranty disclaimer

**Max Size:** 20 KB

---

### 3. manifest.json

**Purpose:** Machine-readable metadata and provenance

**Format:** JSON (UTF-8, pretty-printed)

**Schema Version:** 1.0 (see Data Models spec)

**Required Top-Level Keys:**
- `manifest_version`
- `app_version`
- `exported_at`
- `pack` (object)
- `assets` (array)

**Optional Top-Level Keys:**
- `checksums` (object)
- `hardware_profile` (object)
- `export_options` (object)

**Max Size:** 10 MB (for packs with 1000+ assets)

---

## Optional Files

### 1. store_copy.txt

**Purpose:** Pre-written marketing description for marketplace listings

**Format:** Plain text with section headers

**Sections:**
- **Title** (one-line, 60 chars max)
- **Short Description** (160 chars, for previews)
- **Long Description** (500-2000 words)
- **Key Features** (bullet list)
- **What's Included** (file counts)
- **Suggested Tags** (comma-separated)
- **Suggested Price Range** (informational)

---

### 2. prompts/

**Purpose:** Preserve generation prompts for customer reference/reproduction

**Contents:** One `.txt` file per asset (matched by filename)

**Format:**
```
Platform: MidJourney v6
Prompt: majestic dragon breathing fire over medieval castle at sunset --ar 16:9 --v 6 --style raw
Negative Prompt: N/A
Seed: 123456
Generated: 2025-10-22T14:23:01Z
Model: midjourney-v6
```

---

### 3. checksums.txt

**Purpose:** File integrity verification

**Format:**
```
SHA256 (assets/dragon_fire.png) = e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855
SHA256 (assets/castle_wall.jpg) = a1b2c3d4e5f6789012345678901234567890123456789012345678901234
...
```

**Alternative:** Include in `manifest.json` under `checksums` key

---

### 4. previews/

**Purpose:** Quick visual reference for customers

**Contents:**
- `preview_grid.jpg` — Grid of all assets (recommended)
- `preview_{n}.jpg` — Individual hero shots (up to 5)

**Specs:**
- Format: JPEG, quality 90
- Dimensions: 1920×1080 or 1200×1200 (grid)
- Max file size: 2 MB per image

---

## File Naming Conventions

### Pack Name (Slug)

**Format:** `{descriptive_name}_{yyyymmdd_hhmmss}`

**Rules:**
- Lowercase
- Alphanumeric + underscores only
- No spaces (use underscores)
- Max 50 chars (excluding timestamp)

**Examples:**
- `fantasy_dragon_collection_20251022_153045`
- `scifi_ui_sounds_20251023_094512`

### Asset Filenames

**Preserve Original Names:** Yes (unless duplicates)

**Duplicate Handling:** Append `_001`, `_002`, etc.

**Forbidden Characters:** `< > : " / \ | ? *`

**Max Length:** 255 characters (Windows limit)

---

## README Format

### Template Structure

```markdown
# {Pack Name}

**Version:** {version}  
**Release Date:** {date}  
**License:** {license_type}

---

## Description

{Long-form description of pack, use cases, style, themes}

---

## Contents

- **Images:** {count} files ({formats})
- **Audio:** {count} files ({formats})
- **Video:** {count} files ({formats})
- **Total Size:** {uncompressed size}

---

## What's Included

- `/assets/` — All asset files
- `/prompts/` — Generation prompts (if applicable)
- `manifest.json` — Technical metadata
- `LICENSE.txt` — Usage terms

---

## Usage Guidelines

### Allowed Uses
{List of permitted uses based on license}

### Prohibited Uses
{List of restricted uses}

### Attribution
{Attribution requirements, if any}

---

## Technical Specifications

### Images
- **Formats:** PNG, JPEG
- **Resolutions:** 1024×1024 to 4096×4096
- **Color Space:** sRGB
- **Bit Depth:** 8-bit

### Audio
- **Formats:** MP3, WAV
- **Sample Rate:** 44.1 kHz, 48 kHz
- **Bit Depth:** 16-bit, 24-bit
- **Loudness:** Normalized to -14 LUFS

### Video
- **Formats:** MP4 (H.264)
- **Resolutions:** 1080p, 4K
- **Frame Rate:** 24 fps, 30 fps
- **Codec:** H.264 (Main Profile)

---

## Support

For questions or issues:
- **Email:** {support_email}
- **Website:** {website_url}
- **Discord:** {discord_invite} (optional)

---

## Credits

{If using third-party models, tools, or inspirations, credit here}

Generated with PODStudio v{app_version}

---

## Version History

- **{version}** ({date}): Initial release

---

© {year} {author/company}. All rights reserved.
```

---

## LICENSE Variants

### Personal Use License

```
PERSONAL USE LICENSE

Copyright (c) {year} {author}

Permission is granted to use these assets for personal, non-commercial projects only.

ALLOWED:
- Personal art projects
- Portfolio pieces
- Educational use
- Non-profit projects

NOT ALLOWED:
- Commercial use (including client work)
- Resale or redistribution of assets
- Use in products for sale
- Claiming assets as your own creation

ATTRIBUTION:
Optional but appreciated. Credit "{author} — {pack_name}"

WARRANTY DISCLAIMER:
These assets are provided "as is" without warranty of any kind.

For commercial use, please purchase a Commercial License.
```

### Commercial License

```
COMMERCIAL LICENSE (Standard)

Copyright (c) {year} {author}

Permission is granted to use these assets in commercial projects, subject to the following terms:

ALLOWED:
- Use in client projects (unlimited clients)
- Use in products for sale (physical or digital)
- Use in commercial media (ads, videos, games, apps)
- Modification and derivation

NOT ALLOWED:
- Resale or redistribution of raw assets
- Use in competing asset packs or marketplaces
- Sublicensing to third parties
- Use in AI training datasets

LIMITATIONS:
- Single user/organization license
- Unlimited projects, no revenue cap

ATTRIBUTION:
Not required, but appreciated.

WARRANTY DISCLAIMER:
These assets are provided "as is" without warranty of any kind.
```

### Extended Commercial License

```
EXTENDED COMMERCIAL LICENSE

Copyright (c) {year} {author}

This license grants all rights of the Standard Commercial License, plus:

ADDITIONAL ALLOWED USES:
- Multi-user/team use (up to 10 seats)
- On-demand products (print-on-demand services)
- Resale in end products (e.g., templates, apps) where assets are integrated
- Revenue over $1M USD per project

STILL NOT ALLOWED:
- Resale or redistribution of raw, unmodified assets
- Use in competing asset marketplaces
- AI training datasets

ATTRIBUTION:
Not required.

WARRANTY DISCLAIMER:
These assets are provided "as is" without warranty of any kind.

For custom licensing, contact {support_email}.
```

---

## Store Copy Format

### Template

```
=== TITLE ===
{Pack Name} — {Short Hook} ({Asset Count} Assets)

=== SHORT DESCRIPTION (160 chars) ===
{One-sentence value proposition}

=== LONG DESCRIPTION ===

{Compelling opening paragraph}

🎨 What's Included:
• {Asset count} high-quality {asset types}
• {Key feature 1}
• {Key feature 2}
• {Key feature 3}

✨ Perfect For:
• {Use case 1}
• {Use case 2}
• {Use case 3}

📋 Technical Details:
• Formats: {formats}
• Resolutions: {resolutions}
• Total Size: {size}
• License: {license type}

🚀 Why This Pack?
{Unique selling points, quality guarantees, etc.}

📦 Instant Download:
All files delivered immediately after purchase in a convenient ZIP file.

=== KEY FEATURES (bullets) ===
✓ Commercial license included
✓ High-resolution files
✓ Easy to use
✓ Instant download
✓ Regular updates

=== SUGGESTED TAGS ===
{tag1}, {tag2}, {tag3}, {tag4}, {tag5}

=== SUGGESTED PRICE ===
${X} - ${Y} USD
(Based on asset count, quality, and market research)

=== PREVIEW IMAGES ===
1. Hero shot (main asset showcase)
2. Grid view (all assets)
3. Detail shot (zoom on quality)
4. Use case example (in context)
5. License/support info graphic
```

---

## Manifest Contract

### Schema (Subset — See data_models.md for full spec)

```json
{
  "manifest_version": "1.0",
  "app_version": "1.0.0",
  "exported_at": "ISO 8601 timestamp",
  "pack": {
    "id": "UUID",
    "name": "string",
    "slug": "string",
    "theme": "string | null",
    "description": "string",
    "license_type": "personal | commercial | extended",
    "version": "semver string",
    "asset_count": "integer",
    "total_size_bytes": "integer"
  },
  "assets": [
    {
      "asset_id": "UUID",
      "filename": "string",
      "rel_path": "string (relative to pack root)",
      "type": "image | audio | video",
      "width": "integer | null",
      "height": "integer | null",
      "duration": "float | null",
      "size_bytes": "integer",
      "hash": "SHA-256 hex string",
      "tags": ["array of strings"],
      "generator_meta": {"object | null"},
      "prompts": [{"platform": "string", "text": "string"}],
      "edits": [{"kind": "string", "params": {}}]
    }
  ],
  "checksums": {
    "rel_path": "SHA-256 hex"
  },
  "hardware_profile": {
    "gpu_vendor": "string | null",
    "vram_mb": "integer | null",
    "cpu_threads": "integer",
    "ram_gb": "integer",
    "mode": "gpu | cpu | cpu+mem"
  }
}
```

---

## Platform-Specific Exports

### Gumroad

**Adjustments:**
- Flatten directory structure (no nested folders)
- Separate ZIP per asset type if >100 files total
- Include `INSTALL.txt` with simple instructions

**File Naming:**
```
{pack_name}_images.zip
{pack_name}_audio.zip
{pack_name}_video.zip
{pack_name}_docs.zip (README, LICENSE, manifest)
```

### Etsy (Digital Downloads)

**Limitations:**
- Max 5 files per listing
- Max 20 MB per file (workaround: external link in PDF)

**Adjustments:**
- Create single master ZIP (<20 MB if possible)
- If too large: Provide download link in `DOWNLOAD_LINK.pdf`
- Include thumbnail collage as separate JPG for listing images

### Creative Market

**Requirements:**
- Preview images (minimum 3)
- Detailed description in `DESCRIPTION.txt`
- Clear license terms in `LICENSE.txt`

**Adjustments:**
- Add `/previews/` folder with high-quality showcase images
- Include `CM_README.txt` with platform-specific instructions

---

## Validation Checklist

Before marking a pack export as "completed", verify:

### File Presence
- ✅ `README.md` exists and >500 bytes
- ✅ `LICENSE.txt` exists and contains license type
- ✅ `manifest.json` exists and is valid JSON
- ✅ `/assets/` directory exists and contains files
- ✅ All assets listed in manifest exist on disk

### File Integrity
- ✅ All checksums match (if checksums.txt present)
- ✅ No corrupted images (can be opened by Pillow)
- ✅ No corrupted audio/video (ffprobe succeeds)

### Metadata Accuracy
- ✅ Asset count in manifest matches actual file count
- ✅ Total size in manifest matches actual size (±1%)
- ✅ All asset dimensions correct (width, height)
- ✅ All asset durations correct (audio/video)

### Legal Compliance
- ✅ LICENSE.txt matches selected license type
- ✅ Copyright year is current
- ✅ Author/company name is filled
- ✅ No TODOs or placeholders remain

### Professional Presentation
- ✅ README has all required sections
- ✅ No typos in README or store_copy.txt
- ✅ Pack name is descriptive and professional
- ✅ All filenames are valid (no forbidden chars)

### ZIP Archive (if applicable)
- ✅ ZIP file created successfully
- ✅ ZIP can be extracted without errors
- ✅ ZIP size <2 GB (Windows compatibility)
- ✅ ZIP preserves directory structure

---

## Error Recovery

### Missing Required File

**Action:** Block export; show error dialog

**Message:**
```
Export Failed: Missing Required File

The following required file could not be generated:
• {filename}

Reason: {error_message}

[Retry] [View Log] [Cancel]
```

### Corrupted Asset

**Action:** Skip asset; log warning; continue export

**Message:**
```
Warning: Corrupted Asset Skipped

{filename} could not be validated and was excluded from the pack.

Error: {error_message}

Remaining assets ({count}) will be exported.

[Continue] [Cancel Export]
```

### Disk Full

**Action:** Abort export; clean up partial files

**Message:**
```
Export Failed: Insufficient Disk Space

Requires: {required_gb} GB
Available: {available_gb} GB

Free up disk space and try again.

[Open Disk Cleanup] [Cancel]
```

---

## Future Enhancements (Not v1.0)

- **Multi-language README:** Generate in multiple languages
- **Video Previews:** Auto-generate preview videos for video packs
- **Auto-updater Manifest:** Include update check URL for versioned packs
- **Blockchain Provenance:** Optional NFT/blockchain metadata
- **Platform Auto-Upload:** Direct upload to Gumroad/Etsy via API

---

**End of Export Contract Specification**  
**Next Steps:** Review all required elements, validate against real marketplace requirements, approve before implementation.
