# UI Specification — Reference

**Version**: 0.1.0  
**Last Updated**: October 22, 2025

---

## Note

This file is a **placeholder** for Step 1. The complete UI specification with wireframes, flows, and component details already exists in:

**📄 [/docs/ux_spec.md](/docs/ux_spec.md)** (from Step 0 design phase)

That document includes:
- Complete ASCII wireframes (12 diagrams)
- 3 detailed user flows
- Keyboard shortcuts (40+ commands)
- UI states (empty, loading, error, success)
- Accessibility guidelines

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

**For full specification, see**: [/docs/ux_spec.md](/docs/ux_spec.md)
