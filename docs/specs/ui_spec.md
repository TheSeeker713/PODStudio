# UI Specification — Reference

**Version**: 0.5.0  
**Last Updated**: January 2025  
**Status**: STEP 5 - Curation UX implemented

---

## Implementation Status

✅ **STEP 2 Complete**: PySide6 UI shell scaffolded  
✅ **STEP 4 Complete**: Database models and file watcher  
✅ **STEP 5 Complete**: Asset grid with curation controls

**STEP 5 Features**:
- Asset grid with thumbnail display (128×128px cards)
- Multi-select support (Ctrl+Click toggle, Shift+Click range)
- Context menus for curation actions
- Right dock controls (Approve, Reject/Delete, Rename, Move, Tag)
- File operations with collision handling
- Database synchronization
- Automatic grid refresh after operations

---

## Note

The **complete UI specification** with wireframes, flows, and component details exists in:

**📄 [/docs/ux_spec.md](/docs/ux_spec.md)** (from Step 0 design phase)

That document includes:
- Complete ASCII wireframes (12 diagrams)
- 3 detailed user flows
- Keyboard shortcuts (40+ commands)
- UI states (empty, loading, error, success)
- Accessibility guidelines

---

## STEP 2: Implemented Components

### Main Window (`app/ui/main_window.py`)
- `QMainWindow` with dock-based layout
- Window state persistence stubs (QSettings)
- Close event handling

### Widgets (`app/ui/widgets/`)

| Widget | File | Status | Description |
|--------|------|--------|-------------|
| TopBar | `top_bar.py` | ✅ Placeholder | Hardware pill, job queue icon |
| LeftDock | `dock_left.py` | ✅ Placeholder | Instructions, Listener, Filters sections |
| RightDock | `dock_right.py` | ✅ **STEP 5** | Inspector, Quick Actions (Approve/Reject/Tag/Move/Rename), History |
| AssetGrid | `asset_grid.py` | ✅ **STEP 5** | Grid with thumbnails, multi-select, context menus |
| SelectionTray | `selection_tray.py` | ✅ Placeholder | Selection count, Build Pack button |

---

## STEP 5: Curation Workflows

### Asset Grid Features

**Card Layout** (138×190px per card):
- Thumbnail: 128×128px with 2px border
- Filename: Wrapped text below thumbnail
- Status indicator: `✓ Approved` (green) or `○ Pending` (orange)

**Selection Interactions**:
- **Single select**: Left-click → Clears previous, selects clicked
- **Multi-select (toggle)**: `Ctrl+Click` → Toggle selection state
- **Multi-select (range)**: `Shift+Click` → Add to selection
- **Context menu**: Right-click → Show Approve/Reject/Tag/Move/Rename

**Card States**:
- Default: `#1f2937` background, `#374151` border
- Hover: `#374151` background, `#10b981` border
- Selected: `#10b981` background, `#059669` border

### Right Dock Actions

**Inspector Card**:
- Single selection: Shows file, type, theme, status, size, hash
- Multi-selection: Shows "N assets selected"
- No selection: Shows "No selection"

**Quick Actions** (Enabled based on selection):
- **✓ Approve** (Green): Mark as approved in database
- **✗ Reject/Delete** (Red): Delete from DB and disk (with confirmation)
- **🏷 Rename**: Single asset only, shows input dialog, handles collisions
- **📁 Move**: Move to theme folder, creates dirs, updates DB
- **🏷 Tag Theme**: Assign theme without moving files

**History Card**: Shows last 5 operations (Approved N assets, Moved N assets, etc.)

### Signal Flow

```
Grid Selection Change → RightDock.update_selection()
  → Inspector updates with metadata
  → Action buttons enabled/disabled

Action Button Clicked → Database operation
  → File operation (move/rename/delete) if needed
  → Emit refresh_requested signal
  → All grids refresh from database
```

### Keyboard Shortcuts (Implemented)

- `Ctrl + Click` = Toggle selection
- `Shift + Click` = Range select (simplified)

---

### Theme System (`app/ui/themes/`)
- `tokens.json` - Color, spacing, typography tokens
- `style.md` - Theme design documentation

### Assets (`app/ui/assets/`)
- Empty directory with README (icons/images to be added in Step 3+)

---

## Quick Reference

### Layout (Video Editor Style)

```
┌────────────────────────────────────────────────────────────┐
│  Top Bar: Logo | Status | GPU Pill | Search | Settings    │
├─────────────┬──────────────────────────┬───────────────────┤
│             │                          │                   │
│  Left Dock  │    Center Grid           │   Right Dock      │
│             │    (Images/Audio/Video)  │   (Inspector)     │
│  - Instructions                        │                   │
│  - Listener │                          │   - Metadata      │
│  - Filters  │                          │   - Actions       │
│             │                          │   - History       │
├─────────────┴──────────────────────────┴───────────────────┤
│  Bottom Tray: Selection Counter | [Build Pack] Button     │
└────────────────────────────────────────────────────────────┘
```

### Key Shortcuts

- `A` = Approve
- `R` = Reject
- `Space` = Toggle preview
- `↑↓` = Navigate grid
- `Ctrl+A` = Select all
- `Ctrl+B` = Build pack

---

## Running the UI (Development Mode)

```powershell
# From project root
python -m app.ui.app
```

Expected output:
- Main window appears with placeholder widgets
- All docks visible and collapsible
- Empty grid states showing
- Build Pack button disabled (no selection)

---

## Next Steps (Step 3+)

- [ ] Implement asset database models
- [ ] Connect grids to database
- [ ] Add thumbnail generation
- [ ] Implement keyboard shortcuts
- [ ] Apply theme tokens via Qt stylesheets
- [ ] Add icons and assets

---

**For full specification, see**: [/docs/ux_spec.md](/docs/ux_spec.md)
