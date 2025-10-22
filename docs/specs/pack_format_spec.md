# Pack Format Specification — Reference

**Version**: 0.1.0  
**Last Updated**: October 22, 2025

---

## Note

This file is a **placeholder** for Step 1. The complete pack format specification already exists in:

**📄 [/docs/export_contract.md](/docs/export_contract.md)** (from Step 0 design phase)

That document includes:
- Complete pack directory structure
- README.md template (8 sections)
- LICENSE.txt variants (Personal, Commercial, Extended)
- manifest.json schema v1.0
- Platform-specific adaptations (Gumroad, Etsy, Creative Market)
- 25-item validation checklist

---

## Quick Reference

### ZIP Structure

```
MyPackName_2025-10-22.zip
├── README.md          (8-section template)
├── LICENSE.txt        (variant: Personal/Commercial/Extended)
├── store_copy.txt     (marketing description)
├── manifest.json      (asset list, checksums, metadata)
├── assets/
│   ├── image_001.png
│   ├── image_002.png
│   └── ...
└── prompts/           (optional)
    └── prompts.txt
```

### Required Files

1. **README.md**: Product description, usage rights, support
2. **LICENSE.txt**: Legal terms based on pack license type
3. **manifest.json**: Asset inventory with SHA-256 checksums

---

**For full specification, see**: [/docs/export_contract.md](/docs/export_contract.md)
