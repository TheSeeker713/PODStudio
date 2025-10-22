# Hardware Policy — Reference

**Version**: 0.1.0  
**Last Updated**: October 22, 2025

---

## Note

This file is a **placeholder** for Step 1. The complete hardware policy already exists in:

**📄 [/docs/hardware_policy.md](/docs/hardware_policy.md)** (from Step 0 design phase)

That document includes:
- 5-phase hardware probe sequence
- Capability tier definitions (GREEN/YELLOW/RED)
- Operation requirement matrices (15+ operations with VRAM/RAM/time estimates)
- Decision logic pseudocode
- 8 user-facing message templates (block/warn dialogs)
- Fallback strategies (GPU→CPU)

---

## Quick Reference

### Capability Tiers

| Tier | GPU | VRAM | Restrictions |
|------|-----|------|--------------|
| **GREEN** | NVIDIA/AMD | 6GB+ | All operations enabled |
| **YELLOW** | iGPU or old GPU | 2-6GB | Warn on heavy ops (4K upscale) |
| **RED** | None or <2GB | <2GB | Block GPU ops, CPU-only mode |

### Gating Rules

- **BG Removal**: GREEN/YELLOW OK, RED → CPU fallback (slow)
- **Upscale 2x**: GREEN OK, YELLOW warn, RED block if >2K input
- **Upscale 4x**: GREEN only (block on YELLOW/RED)
- **Video Upscale**: GREEN only (requires 8GB+ VRAM)

---

**For full policy, see**: [/docs/hardware_policy.md](/docs/hardware_policy.md)
