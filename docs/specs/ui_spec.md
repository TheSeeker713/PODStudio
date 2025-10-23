# UI Specification — Reference

**Version**: 0.2.0  
**Last Updated**: October 22, 2025  
**Status**: STEP 2 - UI shell implemented

---

## Implementation Status

✅ **STEP 2 Complete**: PySide6 UI shell scaffolded with:
- Main window with dock layout
- Top bar placeholder (hardware pill, job queue)
- Left dock (Instructions, Listener, Filters)
- Right dock (Inspector, Actions, History)
- Center tabs (Images, Audio, Video grids)
- Bottom tray (Selection counter, Build Pack button)
- Theme tokens defined (tokens.json)

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
| RightDock | `dock_right.py` | ✅ Placeholder | Inspector, Actions, History cards |
| AssetGrid | `asset_grid.py` | ✅ Placeholder | Empty grid with placeholder text |
| SelectionTray | `selection_tray.py` | ✅ Placeholder | Selection count, Build Pack button |

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
