# Pack Format Specification

**Version**: 0.2.0
**Last Updated**: Today

---

This document outlines the structure and contents of a POD Studio Asset Pack.

## 1. Root Directory

The pack is a standard `.zip` archive. The filename should follow the convention: `[PackSlug]_v[Version].zip`.

Example: `my-awesome-pack_v1.0.0.zip`

## 2. File Structure

```
/
├── manifest.json
├── README.md
├── store_copy.txt
├── LICENSE.txt
├── assets/
│   ├── image_001.png
│   ├── sound_effect_001.wav
│   └── ...
└── prompts/
    ├── final_prompts.json
    └── agent_lineage.json
```

### 2.1. `manifest.json`

The machine-readable heart of the pack. It contains metadata and a file inventory.

**Schema:**

```json
{
  "pack_id": "string",
  "title": "string",
  "author": "string",
  "description": "string",
  "version": "string (semver)",
  "export_date": "string (ISO 8601)",
  "prompt_session_id": "string | null",
  "prompt_source": "'template-only' | 'agent-assisted' | null",
  "files": [
    {
      "path": "string (relative to zip root)",
      "checksum": "string (SHA-256)"
    }
  ]
}
```

### 2.2. `/prompts` Directory (Optional)

This directory exists if the assets were generated with the assistance of the Prompt Engine. It provides transparency and reproducibility.

- **`final_prompts.json`**: A key-value map where keys are asset filenames and values are the final, executed prompts used to generate them.
- **`agent_lineage.json`**: An array of objects detailing the sequence of AI agent calls, including the model used, the prompt sent, and the response received. This creates a full audit trail of the creative process.

### 2.3. Disclosure Notes

If the user opts in, AI assistance disclosures are added:

- **`README.md`**: Appended with a note: "*This pack contains content generated with offline AI assistance.*"
- **`store_copy.txt`**: Appended with a detailed model disclosure section, listing each agent and the specific model file used (e.g., `llava-v1.6-34b.Q5_K_M.gguf`). This provides full transparency to the end-user.
