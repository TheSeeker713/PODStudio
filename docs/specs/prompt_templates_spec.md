# Prompt Templates Specification — Reference

**Version**: 0.1.0  
**Last Updated**: October 22, 2025

---

## Note

This file is a **placeholder** for Step 1. The complete prompt templates specification and actual templates already exist in:

**📄 Specification**: [/docs/export_contract.md](/docs/export_contract.md) (Section: Prompt Generation)  
**📁 Templates**: [/docs/prompt_templates/](/docs/prompt_templates/) (6 template files)

Templates available:
- `image_sdxl.txt` — Stable Diffusion XL
- `image_midjourney.txt` — MidJourney with parameters
- `audio_suno.txt` — Suno music generation
- `audio_elevenlabs.txt` — ElevenLabs voice synthesis
- `video_kling.txt` — Kling AI video
- `video_sora.txt` — Sora-style video

---

## Quick Reference

### Template Grammar

Templates use **Jinja2** syntax with slot variables:

```jinja2
A {theme} in {style} style, {quality_tags}, {lighting},
trending on ArtStation, highly detailed, 8k
```

### Platform Support

| Platform | Type | Variables |
|----------|------|-----------|
| SDXL | Image | theme, style, quality_tags, negative_prompt |
| MidJourney | Image | theme, style, --ar, --v |
| Suno | Audio | genre, mood, BPM, instruments |
| ElevenLabs | Audio | voice_type, emotion, SSML |
| Kling | Video | scene, camera_movement, duration |
| Sora | Video | shot_type, cinematography, style |

---

**For full specification and templates, see**: [/docs/prompt_templates/](/docs/prompt_templates/)
