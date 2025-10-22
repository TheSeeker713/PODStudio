# Manifest Schema — Reference

**Version**: 0.1.0  
**Last Updated**: October 22, 2025

---

## Note

This file is a **placeholder** for Step 1. The complete manifest schema already exists in:

**📄 [/docs/data_models.md](/docs/data_models.md)** (from Step 0 design phase)

That document includes:
- Complete manifest.json schema v1.0
- Asset model (40+ fields)
- Pack model (14+ fields)
- Validation rules

---

## Quick Reference

### Manifest v1.0 Schema

```json
{
  "schema_version": "1.0",
  "pack": {
    "id": "pack_abc123",
    "name": "Fantasy Character Pack Vol. 1",
    "version": "1.0.0",
    "created_at": "2025-10-22T14:30:00Z",
    "license_type": "commercial",
    "theme": "fantasy_characters"
  },
  "assets": [
    {
      "id": "asset_001",
      "filename": "character_001.png",
      "path": "assets/character_001.png",
      "type": "image",
      "hash_sha256": "abc123...",
      "size_bytes": 1024000,
      "dimensions": {"width": 1024, "height": 1024}
    }
  ],
  "checksums": {
    "README.md": "def456...",
    "LICENSE.txt": "ghi789..."
  }
}
```

---

**For full specification, see**: [/docs/data_models.md](/docs/data_models.md)
