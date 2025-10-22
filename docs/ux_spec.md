# PODStudio — UX Specification

**Version:** 1.0.0  
**Date:** October 22, 2025  
**Status:** Design Specification

---

## Table of Contents

1. [Design Philosophy](#design-philosophy)
2. [Application Layout](#application-layout)
3. [Wireframes (ASCII)](#wireframes-ascii)
4. [User Flows](#user-flows)
5. [UI States & Feedback](#ui-states--feedback)
6. [Interaction Patterns](#interaction-patterns)
7. [Accessibility](#accessibility)
8. [Keyboard Shortcuts](#keyboard-shortcuts)

---

## Design Philosophy

### Video Editor Paradigm
PODStudio adopts a video editor-style interface with:
- **Dock-based panels** (collapsible, resizable)
- **Timeline metaphor** for asset browsing (chronological + filterable)
- **Inspector panel** for detailed item view
- **Non-modal operations** (progress in status bar, not blocking dialogs)

### Core Principles
- **Clarity over density:** Breathing room; clear visual hierarchy
- **Keyboard-first for power users:** Every action has a shortcut
- **Progressive disclosure:** Advanced options hidden by default
- **Fail-visible:** Errors shown inline with actionable next steps
- **Undo-friendly:** Non-destructive by default; originals never overwritten

---

## Application Layout

```
┌─────────────────────────────────────────────────────────────────────────────┐
│  PODStudio                                            [─] [□] [×]            │
├─────────────────────────────────────────────────────────────────────────────┤
│  [Project ▼] [Search...                     ] [🟢 GPU·8GB] [Jobs ⊙ 3] [⚙]  │
├──────────────┬────────────────────────────────────────────────┬─────────────┤
│              │                                                │             │
│  LEFT DOCK   │          CENTER PANE (Main Workspace)         │ RIGHT DOCK  │
│  (Panels)    │                                                │  (Cards)    │
│              │                                                │             │
│  250-400px   │                  Flexible                      │   300-400px │
│              │                                                │             │
│              │                                                │             │
│              │                                                │             │
│              │                                                │             │
│              │                                                │             │
│              │                                                │             │
│              │                                                │             │
├──────────────┴────────────────────────────────────────────────┴─────────────┤
│  [✓ 12 selected]  [Clear Selection]          [Build Pack...]               │
│  Selection Tray (80px height)                                               │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Top Bar (60px height)
- **Project Selector:** Dropdown for recent projects/workspaces
- **Global Search:** Full-text search across assets (tags, notes, prompts)
- **Hardware Indicator:** Pill showing current capability (GPU/CPU mode + VRAM/RAM)
- **Jobs Badge:** Click to open jobs panel overlay; badge shows active count
- **Settings Gear:** Opens settings panel

### Left Dock (Collapsible Panels)
1. **Prompt Generator**
2. **Smart Listener** (watch folders)
3. **Filters** (type, theme, approval state, date range)
4. **Tags & Collections** (custom groupings)

### Center Pane (Tabbed Views)
- **Images Tab:** Grid view with thumbnails
- **Audio Tab:** Waveform tile grid
- **Video Tab:** Thumbnail grid with duration overlay
- **All Assets Tab:** Mixed view with type icons

### Right Dock (Stacked Cards)
1. **Inspector** (metadata, tags, notes)
2. **Actions** (approve, reject, rename, move)
3. **Enhance** (bg remove, upscale, normalize, etc.)
4. **Prompt History** (shows linked prompt if available)

### Bottom Tray (Selection Context)
- Appears when 1+ assets selected
- Shows count, bulk actions, "Build Pack" CTA

---

## Wireframes (ASCII)

### Main Window — Initial State (No Assets)

```
┌─────────────────────────────────────────────────────────────────────────────┐
│  PODStudio                                            [─] [□] [×]            │
├─────────────────────────────────────────────────────────────────────────────┤
│  [New Project ▼] [Search...               ] [🟡 CPU·16GB] [Jobs] [⚙]       │
├──────────────┬────────────────────────────────────────────────┬─────────────┤
│ ▼ Prompts    │                                                │ Inspector   │
│ ┌──────────┐ │             No Assets Yet                      │ ┌─────────┐ │
│ │Brief:    │ │                                                │ │ Select  │ │
│ │          │ │    Welcome to PODStudio!                       │ │ an asset│ │
│ │          │ │                                                │ │ to view │ │
│ │          │ │    1. Enable Smart Listener below             │ │ details │ │
│ └──────────┘ │       to auto-import from Downloads            │ └─────────┘ │
│ [Gen Prompt] │                                                │             │
│              │    2. Or drag-and-drop files here              │             │
│ ▼ Listener   │                                                │             │
│ ○ OFF        │    [Enable Listener] [Import Files...]         │             │
│ [+ Folder]   │                                                │             │
│              │                                                │             │
│ ▼ Filters    │                                                │             │
│ □ Images     │                                                │             │
│ □ Audio      │                                                │             │
│ □ Video      │                                                │             │
├──────────────┴────────────────────────────────────────────────┴─────────────┤
│  No selection                                                                │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Main Window — Assets Loaded

```
┌─────────────────────────────────────────────────────────────────────────────┐
│  PODStudio — Fantasy Assets                           [─] [□] [×]           │
├─────────────────────────────────────────────────────────────────────────────┤
│  [Fantasy Assets ▼] [Search...            ] [🟢 GPU·8GB] [Jobs ⊙ 2] [⚙]    │
├──────────────┬────────────────────────────────────────────────┬─────────────┤
│ ▼ Prompts    │ [Images] [Audio] [Video] [All (284)]           │ Inspector   │
│ ┌──────────┐ │ ┌───────────────────────────────────────────┐  │ ┌─────────┐ │
│ │Dark fant-│ │ │Sort: Newest ▼  View: Grid [≡][▦][▦▦]      │  │ │ dragon_ │ │
│ │asy drago-│ │ └───────────────────────────────────────────┘  │ │ fire.png│ │
│ │n breathg │ │ ┌────┐ ┌────┐ ┌────┐ ┌────┐ ┌────┐ ┌────┐    │ │ 2048x2048│
│ └──────────┘ │ │[✓] │ │    │ │    │ │[✓] │ │    │ │    │    │ │ PNG·8MB  │
│ [Gen Prompt] │ │ 🔥 │ │ 🏰 │ │ 🌙 │ │ ⚔️ │ │ 🐉 │ │ 🗡️ │    │ │ ✓Approved│
│              │ │img │ │img │ │img │ │img │ │img │ │img │    │ │          │
│ ▼ Listener   │ └────┘ └────┘ └────┘ └────┘ └────┘ └────┘    │ │ Tags:    │
│ ● ON         │ ┌────┐ ┌────┐ ┌────┐ ┌────┐ ┌────┐ ┌────┐    │ │ • dragon │
│ Downloads/   │ │    │ │    │ │    │ │    │ │    │ │    │    │ │ • fire   │
│ C:/Gens/     │ │ 🏛️ │ │ ⭐ │ │ 🌲 │ │ 🔮 │ │ 👑 │ │ 🛡️ │    │ │ • fantasy│
│              │ │img │ │img │ │img │ │img │ │img │ │img │    │ │          │
│ ▼ Filters    │ └────┘ └────┘ └────┘ └────┘ └────┘ └────┘    │ │ Prompt:  │
│ ☑ Images(280)│ ... (12 rows of 6) ...                        │ │ [View]   │
│ ☑ Audio (3)  │                                                │ └─────────┘ │
│ □ Video (1)  │                                                │             │
│              │                                                │ ▼ Actions   │
│ ☑ Approved   │                                                │ [Approve]   │
│ □ Pending    │                                                │ [Reject]    │
│              │                                                │ [Rename...] │
│ Theme:       │                                                │             │
│ • fantasy    │                                                │ ▼ Enhance   │
│ • medieval   │                                                │ [BG Remove] │
│              │                                                │ [Upscale]   │
├──────────────┴────────────────────────────────────────────────┴─────────────┤
│  [✓ 2 selected] [Clear] [Tag...] [Move...] [Delete]    [Build Pack...]     │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Prompt Generator Panel (Expanded)

```
┌────────────────────────────────────────┐
│ ▼ Prompt Generator                     │
├────────────────────────────────────────┤
│ Brief:                                 │
│ ┌────────────────────────────────────┐ │
│ │ Dark fantasy dragon breathing fire │ │
│ │ over a medieval castle at sunset   │ │
│ │                                    │ │
│ └────────────────────────────────────┘ │
│                                        │
│ Asset Type:                            │
│ ● Image  ○ Audio  ○ Video             │
│                                        │
│ Style/Theme Chips (multi-select):      │
│ [✓ Fantasy] [✓ Epic] [ Realistic]     │
│ [ Anime] [ Low-Poly] [ Watercolor]    │
│                                        │
│ [Generate Prompts]                     │
│                                        │
│ Output (after generation):             │
│ ┌────────────────────────────────────┐ │
│ │ SDXL:                              │ │
│ │ "majestic dragon, fire breath,     │ │
│ │  medieval castle, sunset sky..."   │ │
│ │                                    │ │
│ │ MidJourney:                        │ │
│ │ "dark fantasy dragon breathing...  │ │
│ │  --ar 16:9 --v 6 --style raw"      │ │
│ │                                    │ │
│ │ [Copy SDXL] [Copy MJ] [Save All]   │ │
│ └────────────────────────────────────┘ │
└────────────────────────────────────────┘
```

### Smart Listener Panel

```
┌────────────────────────────────────────┐
│ ▼ Smart Listener                       │
├────────────────────────────────────────┤
│ Status: ● ACTIVE                       │
│                                        │
│ Watched Folders:                       │
│ ┌────────────────────────────────────┐ │
│ │ 📁 C:\Users\...\Downloads      [×] │ │
│ │ 📁 C:\Generations              [×] │ │
│ └────────────────────────────────────┘ │
│ [+ Add Folder]                         │
│                                        │
│ Auto-Sort Rules: [Configure]           │
│ ☑ Detect file type (MIME + signature) │
│ ☑ Extract generation metadata         │
│ ☑ Route to /Library/{type}/{theme}/   │
│ ☑ Create DB record                    │
│                                        │
│ Recent Ingests (last 10):              │
│ • dragon_fire.png → /Library/images/   │
│   fantasy/20251022/                    │
│ • castle_wall.png → /Library/images/   │
│   fantasy/20251022/                    │
│                                        │
│ [View Log] [Pause] [Clear History]    │
└────────────────────────────────────────┘
```

### Inspector Panel (Asset Selected)

```
┌────────────────────────────────────────┐
│ ▼ Inspector                            │
├────────────────────────────────────────┤
│ dragon_fire.png                        │
│ ┌────────────────────────────────────┐ │
│ │         [THUMBNAIL PREVIEW]        │ │
│ │                                    │ │
│ │                                    │ │
│ └────────────────────────────────────┘ │
│                                        │
│ Dimensions: 2048 × 2048 px             │
│ Size: 8.2 MB                           │
│ Format: PNG (RGBA)                     │
│ Created: Oct 22, 2025 14:23           │
│ Source: Watched (Downloads)            │
│                                        │
│ Status: ✓ Approved                     │
│ Rating: ★★★★☆                          │
│                                        │
│ Tags:                                  │
│ [dragon] [fire] [fantasy] [+ Add]     │
│                                        │
│ Notes:                                 │
│ ┌────────────────────────────────────┐ │
│ │ Perfect for hero banner            │ │
│ │                                    │ │
│ └────────────────────────────────────┘ │
│                                        │
│ Generator: MidJourney v6               │
│ Prompt: [View Full Prompt]             │
│                                        │
│ Hash: a3f7e9...                        │
│ Library Path: /Library/images/fantasy/ │
│               20251022/dragon_fire.png │
└────────────────────────────────────────┘
```

### Actions Panel

```
┌────────────────────────────────────────┐
│ ▼ Actions                              │
├────────────────────────────────────────┤
│ Quick Actions:                         │
│ ┌────────────┐ ┌────────────┐         │
│ │  ✓ Approve │ │  ✗ Reject  │         │
│ └────────────┘ └────────────┘         │
│                                        │
│ Organize:                              │
│ [✏️ Rename...]                         │
│ [📁 Move to...]                        │
│ [🏷️ Add Tags...]                       │
│ [📝 Edit Notes]                        │
│                                        │
│ Rating:                                │
│ ☆☆☆☆☆ (click to rate)                  │
│                                        │
│ Danger Zone:                           │
│ [🗑️ Delete] (non-reversible)          │
└────────────────────────────────────────┘
```

### Enhance Panel

```
┌────────────────────────────────────────┐
│ ▼ Enhance                              │
├────────────────────────────────────────┤
│ Image Operations:                      │
│ ┌────────────────────────────────────┐ │
│ │ Background Removal                 │ │
│ │ Remove bg, save with alpha         │ │
│ │ [Remove Background]                │ │
│ └────────────────────────────────────┘ │
│                                        │
│ ┌────────────────────────────────────┐ │
│ │ Upscale (ESRGAN)                   │ │
│ │ Scale: [2x▼] Model: [RealESRGAN+▼] │ │
│ │ [Upscale Image]                    │ │
│ └────────────────────────────────────┘ │
│                                        │
│ ┌────────────────────────────────────┐ │
│ │ Crop & Resize                      │ │
│ │ Preset: [Square 1:1▼]              │ │
│ │ [Open Crop Tool]                   │ │
│ └────────────────────────────────────┘ │
│                                        │
│ Audio Operations:                      │
│ ┌────────────────────────────────────┐ │
│ │ Normalize Loudness                 │ │
│ │ Target: [-14 LUFS (streaming)▼]    │ │
│ │ [Normalize]                        │ │
│ └────────────────────────────────────┘ │
│                                        │
│ Video Operations:                      │
│ ┌────────────────────────────────────┐ │
│ │ Transcode                          │ │
│ │ Format: [MP4 (H.264)▼]             │ │
│ │ [Transcode]                        │ │
│ └────────────────────────────────────┘ │
│                                        │
│ ⚠️ Operations create new files;        │
│    originals preserved.                │
└────────────────────────────────────────┘
```

### Jobs Panel (Overlay)

```
┌─────────────────────────────────────────────────────┐
│ Background Jobs                          [×]        │
├─────────────────────────────────────────────────────┤
│ ▶ Active (2)                                        │
│ ┌─────────────────────────────────────────────────┐ │
│ │ Upscaling dragon_fire.png (2x ESRGAN)           │ │
│ │ [████████████░░░░░░░░] 65%  [Cancel]            │ │
│ │ Elapsed: 1m 23s  Est. remaining: 47s            │ │
│ └─────────────────────────────────────────────────┘ │
│                                                     │
│ ┌─────────────────────────────────────────────────┐ │
│ │ Removing background from castle_wall.png        │ │
│ │ [████████████████████░░] 85%  [Cancel]          │ │
│ │ Elapsed: 34s  Est. remaining: 6s                │ │
│ └─────────────────────────────────────────────────┘ │
│                                                     │
│ ▶ Queued (1)                                        │
│ • Normalize audio_epic_battle.mp3                  │
│                                                     │
│ ▼ Completed (12)                                    │
│ ✓ Upscaled hero_banner.png — 2m 14s                │
│ ✓ Removed bg from knight.png — 1m 03s              │
│ ... (show all / collapse)                          │
│                                                     │
│ ▼ Failed (1)                                        │
│ ✗ Upscale video_clip.mp4                           │
│   Error: Insufficient VRAM (requires 6GB, have 4GB)│
│   [Retry with CPU] [View Log] [Dismiss]            │
└─────────────────────────────────────────────────────┘
```

### Pack Builder Modal

```
┌─────────────────────────────────────────────────────────────┐
│ Build Asset Pack                                 [×]        │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│ Pack Name:                                                   │
│ ┌──────────────────────────────────────────────────────────┐│
│ │ Fantasy Dragon Collection                                ││
│ └──────────────────────────────────────────────────────────┘│
│                                                              │
│ Theme/Category:                                              │
│ ┌──────────────────────────────────────────────────────────┐│
│ │ fantasy                                                  ││
│ └──────────────────────────────────────────────────────────┘│
│                                                              │
│ Description:                                                 │
│ ┌──────────────────────────────────────────────────────────┐│
│ │ 50 high-resolution fantasy dragon images, perfect for    ││
│ │ game assets, book covers, and digital art projects.      ││
│ │                                                           ││
│ └──────────────────────────────────────────────────────────┘│
│                                                              │
│ License Type:                                                │
│ ● Personal Use Only                                          │
│ ○ Commercial (standard)                                      │
│ ○ Extended Commercial                                        │
│ [Preview License Text]                                       │
│                                                              │
│ Assets Included: 12 selected                                 │
│ [Review Selection]                                           │
│                                                              │
│ Export Options:                                              │
│ ☑ Include prompts folder                                    │
│ ☑ Generate README.md                                         │
│ ☑ Generate store_copy.txt (marketing)                       │
│ ☑ Create manifest.json (metadata)                           │
│ ☑ Add SHA-256 checksums                                     │
│ □ Create platform-specific variants (Gumroad/Etsy)          │
│                                                              │
│ Export Location:                                             │
│ [C:\Users\...\PODStudio\Packs\           ] [Browse...]      │
│                                                              │
│                   [Cancel]  [Build Pack]                     │
└─────────────────────────────────────────────────────────────┘
```

---

## User Flows

### Flow 1: First-Time Setup

1. **Launch PODStudio**
   - Splash screen (logo, version, "Initializing...")
   - Hardware detection runs (2-3 seconds)
   - Main window opens in "empty state"

2. **Welcome Screen (Center Pane)**
   - "No Assets Yet"
   - Two CTAs: "Enable Listener" or "Import Files"
   - Help tooltip: "Start by adding a watched folder"

3. **User Clicks "Enable Listener"**
   - Left panel expands if collapsed
   - Smart Listener panel highlights
   - "Add Folder" button pulsates (subtle animation)

4. **User Clicks "+ Add Folder"**
   - Native folder picker opens
   - User selects `C:\Users\{name}\Downloads`
   - Folder added to watch list
   - Status changes to "● ACTIVE"

5. **First Asset Detected**
   - Toast notification: "New asset detected: dragon_fire.png"
   - Asset auto-sorted to `/Library/images/fantasy/20251022/`
   - Thumbnail appears in center grid
   - Celebrate with subtle confetti animation (first asset only)

6. **User Selects Asset**
   - Inspector panel populates
   - Actions and Enhance panels become active
   - Bottom tray shows "1 selected"

### Flow 2: Curate & Enhance 50 Assets

**Context:** User has 50 new images in library; wants to approve best 20, enhance 10, reject rest.

1. **Filter to Unapproved**
   - Left panel: Filters → uncheck "Approved", check "Pending"
   - Grid shows 50 thumbnails

2. **Quick Approve (Keyboard)**
   - Click first image
   - Press `A` to approve (shortcut)
   - Press `→` (right arrow) to move to next
   - Repeat 19 more times
   - Approved items get ✓ badge overlay

3. **Bulk Reject Rest**
   - Press `Ctrl+A` to select all visible
   - Press `Ctrl+Shift+A` to deselect approved (keep only unapproved selected)
   - Right-click → "Reject Selected" (or press `R`)
   - Confirmation: "Reject 30 assets? (Can undo)"
   - Confirm → items moved to "Rejected" collection (hidden by default)

4. **Filter to Approved**
   - Left panel: Filters → check "Approved" only
   - Grid now shows 20 thumbnails

5. **Bulk Enhance (Background Removal)**
   - Select 10 assets (Ctrl+Click or Shift+Click)
   - Right Dock → Enhance → "Remove Background"
   - Batch job dialog: "Queue 10 background removal jobs?"
   - Confirm → Jobs panel badge updates to "⊙ 10"

6. **Monitor Progress**
   - Click "Jobs ⊙ 10" badge in top bar
   - Jobs panel opens
   - Watch progress bars; first job completes in ~30s
   - New files created: `{original}_nobg.png` in `/Work/edits/`

7. **Review Enhanced Assets**
   - New assets auto-added to library
   - Filter: "Edited" tag shows enhanced versions
   - User approves enhanced versions

### Flow 3: Build & Export Pack

**Context:** User has 20 approved assets ready to package.

1. **Select Assets**
   - Grid view: Ctrl+A selects all visible (approved)
   - Bottom tray: "✓ 20 selected"

2. **Click "Build Pack"**
   - Pack Builder modal opens (center screen)

3. **Fill Pack Details**
   - Name: "Fantasy Dragon Collection"
   - Theme: "fantasy" (auto-suggested from tags)
   - Description: (textarea with character count)
   - License: Select "Commercial (standard)"
   - Preview license text (opens in new modal)

4. **Configure Export Options**
   - All checkboxes pre-checked (sensible defaults)
   - Export location pre-filled: `C:\...\PODStudio\Packs\`

5. **Click "Build Pack"**
   - Modal shows progress spinner
   - Steps shown:
     - ✓ Creating directory structure
     - ✓ Copying assets (1/20... 20/20)
     - ✓ Generating README.md
     - ✓ Generating LICENSE.txt
     - ✓ Generating store_copy.txt
     - ✓ Creating manifest.json
     - ✓ Calculating checksums
     - ✓ Creating ZIP archive
   - Success message: "Pack created! [Open Folder] [Build Another]"

6. **Review Export**
   - User clicks "Open Folder"
   - Windows Explorer opens to `/Packs/Fantasy_Dragon_Collection_20251022/`
   - Shows ZIP file and unzipped folder structure

### Flow 4: Generate Prompts from Brief

1. **Left Dock → Prompt Generator Panel**
   - Click to expand if collapsed

2. **Enter Brief**
   - Type: "Dark fantasy dragon breathing fire over medieval castle at sunset"
   - Select Asset Type: "Image"
   - Select Style Chips: "Fantasy", "Epic"

3. **Click "Generate Prompts"**
   - If online LLM configured: Sends to API
   - If Zero-AI mode: Uses templates with variable substitution
   - Spinner shows "Generating..."

4. **View Results**
   - Output box populates with platform-specific prompts:
     - SDXL variant
     - MidJourney variant with parameters
     - Negative prompts listed
   - Each has [Copy] button

5. **Copy & Use**
   - User clicks [Copy MJ]
   - Opens MidJourney Discord
   - Pastes prompt and generates
   - Downloads result to watched folder
   - PODStudio auto-ingests and links prompt via filename matching or manual association

6. **Save Prompts**
   - User clicks [Save All]
   - Prompts saved to `/prompts/fantasy_dragon_20251022.txt`
   - Future pack exports include this file

---

## UI States & Feedback

### Empty States

#### No Assets in Library
```
┌───────────────────────────────────────┐
│                                       │
│         📦                            │
│    No Assets Yet                      │
│                                       │
│  Import files or enable Smart         │
│  Listener to start building your      │
│  library.                             │
│                                       │
│  [Enable Listener] [Import Files]     │
│                                       │
└───────────────────────────────────────┘
```

#### No Jobs Running
```
┌───────────────────────────────────────┐
│  Background Jobs                      │
├───────────────────────────────────────┤
│                                       │
│         ✓                             │
│    All Caught Up!                     │
│                                       │
│  No active or queued jobs.            │
│                                       │
└───────────────────────────────────────┘
```

#### No Search Results
```
┌───────────────────────────────────────┐
│         🔍                            │
│    No Results for "unicorn"           │
│                                       │
│  Try different keywords or check      │
│  your filters.                        │
│                                       │
│  [Clear Filters] [Clear Search]       │
└───────────────────────────────────────┘
```

### Loading States

#### Asset Grid Loading
```
┌────┐ ┌────┐ ┌────┐
│░░░░│ │░░░░│ │░░░░│  (Skeleton screens)
│░░░░│ │░░░░│ │░░░░│
└────┘ └────┘ └────┘
```

#### Thumbnail Generating
```
┌────┐
│    │
│ ⏳ │  (Spinner while thumbnail renders)
│    │
└────┘
```

#### Job Progress
```
[████████████░░░░░░░░] 65%
Elapsed: 1m 23s  Est. remaining: 47s
```

### Error States

#### Hardware Insufficient (Red Zone)
```
┌──────────────────────────────────────────────────┐
│ ⚠️ Cannot Run This Operation                     │
├──────────────────────────────────────────────────┤
│ Upscaling 4K video requires at least 6GB VRAM.   │
│ Your system has 4GB.                             │
│                                                  │
│ Suggestions:                                     │
│ • Try a smaller resolution video                │
│ • Use cloud processing (coming soon)            │
│ • Upgrade GPU (recommended: RTX 3060+)          │
│                                                  │
│ [Learn More] [Cancel]                            │
└──────────────────────────────────────────────────┘
```

#### Job Failed
```
┌──────────────────────────────────────────────────┐
│ ✗ Job Failed: Background Removal                 │
├──────────────────────────────────────────────────┤
│ File: castle_wall.png                            │
│ Error: Corrupted image file (PNG header invalid) │
│                                                  │
│ [Retry] [View Log] [Dismiss]                     │
└──────────────────────────────────────────────────┘
```

#### File Not Found
```
┌──────────────────────────────────────────────────┐
│ ⚠️ Asset Missing                                  │
├──────────────────────────────────────────────────┤
│ dragon_fire.png                                  │
│ Expected location:                               │
│ C:\...\Library\images\fantasy\20251022\...       │
│                                                  │
│ The file may have been moved or deleted.         │
│                                                  │
│ [Locate File] [Remove from Library] [Cancel]     │
└──────────────────────────────────────────────────┘
```

### Warning States

#### Hardware Caution (Yellow Zone)
```
┌──────────────────────────────────────────────────┐
│ ⚠️ Performance Warning                            │
├──────────────────────────────────────────────────┤
│ This operation may be slow on your hardware.     │
│                                                  │
│ Estimated time: 15-20 minutes                    │
│ VRAM usage: ~5.5GB (you have 6GB)               │
│                                                  │
│ ☑ Run in background (won't block UI)             │
│                                                  │
│ [Continue] [Cancel]                              │
└──────────────────────────────────────────────────┘
```

#### Unsaved Changes
```
┌──────────────────────────────────────────────────┐
│ Unsaved Pack Configuration                       │
├──────────────────────────────────────────────────┤
│ You have unsaved changes in the Pack Builder.    │
│                                                  │
│ [Save Draft] [Discard] [Cancel]                  │
└──────────────────────────────────────────────────┘
```

### Success States

#### Job Complete
```
┌──────────────────────────────────────────────────┐
│ ✓ Upscale Complete                                │
├──────────────────────────────────────────────────┤
│ dragon_fire_2x.png created                       │
│ Output: 4096 × 4096 px, 24.3 MB                  │
│                                                  │
│ [View Result] [Dismiss]                          │
└──────────────────────────────────────────────────┘
```

#### Pack Exported
```
┌──────────────────────────────────────────────────┐
│ ✓ Pack Built Successfully!                        │
├──────────────────────────────────────────────────┤
│ Fantasy_Dragon_Collection_20251022.zip           │
│ 20 assets · 156 MB · Ready to upload             │
│                                                  │
│ [Open Folder] [Build Another] [Done]             │
└──────────────────────────────────────────────────┘
```

---

## Interaction Patterns

### Selection Model
- **Single Select:** Click thumbnail
- **Multi-Select:** Ctrl+Click (toggle) or Shift+Click (range)
- **Select All (filtered):** Ctrl+A
- **Deselect All:** Esc or click empty space
- **Select None (when items selected):** Ctrl+Shift+A

### Context Menus
- **Right-click on asset:** Quick actions (Approve, Reject, Enhance, etc.)
- **Right-click on selection tray:** Bulk operations menu
- **Right-click on dock title:** Show/hide, move to other side

### Drag & Drop
- **Drag files from Explorer to center pane:** Import
- **Drag selected assets to "Rejected" in left panel:** Bulk reject
- **Drag assets between grid and selection tray:** Add/remove from selection

### Keyboard Navigation
- **Arrow keys:** Navigate grid
- **Space:** Toggle selection
- **Enter:** Open inspector / edit mode
- **Delete:** Move to rejected
- **Ctrl+F:** Focus search box
- **Ctrl+,:** Open settings
- **F5:** Refresh library

### Progress Indicators
- **Determinate:** Progress bar with percentage (when total known)
- **Indeterminate:** Spinner (when duration unknown)
- **Status Text:** Always show elapsed time; show ETA when >50% complete

### Notifications
- **Toast (bottom-right, 4s auto-dismiss):** Non-critical info ("Asset imported")
- **Persistent badge:** Jobs count on top bar
- **Modal dialog:** Critical errors or confirmations requiring user action

---

## Accessibility

### Keyboard Access
- All panels, buttons, and controls reachable via Tab
- Focus indicators (2px blue outline)
- Logical tab order (top-to-bottom, left-to-right)

### Screen Reader Support
- All images have alt text (thumbnails: filename + dimensions)
- Buttons have ARIA labels
- Progress bars announce percentage at 25%, 50%, 75%, 100%
- Live regions for status updates

### Visual
- **Contrast:** All text meets WCAG AA (4.5:1 for normal, 3:1 for large)
- **High Contrast Mode:** Detect Windows high-contrast theme and adapt
- **UI Density:** Settings option for Compact/Normal/Comfortable
- **Font Scaling:** Respect system font size settings

### Motor
- **Large Click Targets:** Minimum 44×44px for touch-friendly operation
- **No Rapid Actions:** Nothing requires fast double-click or drag
- **Sticky Keys Friendly:** No multi-key chords required for core functions

---

## Keyboard Shortcuts

### Global
- `Ctrl+N` — New project
- `Ctrl+O` — Open project
- `Ctrl+S` — Save project
- `Ctrl+,` — Settings
- `Ctrl+Q` — Quit
- `Ctrl+F` — Search
- `Ctrl+/` — Show keyboard shortcuts

### Navigation
- `Ctrl+1` — Images tab
- `Ctrl+2` — Audio tab
- `Ctrl+3` — Video tab
- `Ctrl+4` — All assets tab
- `Ctrl+J` — Toggle jobs panel
- `Ctrl+B` — Toggle left dock
- `Ctrl+I` — Toggle right dock

### Selection
- `Ctrl+A` — Select all (filtered)
- `Ctrl+Shift+A` — Deselect all
- `Esc` — Clear selection
- `Space` — Toggle selection on focused item
- `Arrow Keys` — Navigate grid
- `Enter` — Open inspector for selected

### Asset Actions
- `A` — Approve selected
- `R` — Reject selected
- `Delete` — Move to rejected
- `Ctrl+E` — Open enhance menu
- `Ctrl+T` — Edit tags
- `Ctrl+R` — Rename

### Pack Builder
- `Ctrl+P` — Build pack from selection

### Jobs
- `Ctrl+Shift+C` — Cancel all jobs
- `Ctrl+Shift+R` — Retry failed jobs

---

## Responsive Behavior

### Minimum Window Size
- **Width:** 1280px
- **Height:** 720px
- Below minimum: Show warning overlay "Please resize window for best experience"

### Dock Behavior
- **Collapsible:** Click panel title to collapse/expand
- **Resizable:** Drag divider to resize (min 200px, max 600px)
- **Detachable (future):** Right-click title → "Detach to floating window"

### Grid Density
- Automatically adjusts columns based on center pane width
- Maintains ~180px thumbnail size with 12px gutters
- Settings override: Force 4/6/8 columns

---

**End of UX Specification**  
**Next Steps:** Review flows, validate wireframes, approve before implementation.
