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

## STEP 7: LLM Agent Roles and Routing (New)

### Agent Overview

PODStudio uses **4 offline LLM agents** (via llama.cpp) to assist with prompt generation:

| Agent | Model | Purpose | Tasks |
|-------|-------|---------|-------|
| **Vision** | gemma-3-12b | Multimodal analysis | Image captions, visual descriptions, scene analysis |
| **Dialog** | discopop-zephyr-7b-gemma | Fluency & polish | Prompt refinement, natural language, creative writing |
| **Logic** | gemma-3n-e4b | Reasoning & structure | Prompt drafting, planning, logical reasoning |
| **Fast** | lfm2-1.2b | Quick tasks | Summaries, keywords, tags, fallback |

### Task Routing Logic

PODStudio routes prompt-related tasks to agents based on task type:

```
Prompt Drafting → agent_logic (structured planning)
Prompt Polishing → agent_dialog (fluency improvements)
Image Analysis → agent_vision (multimodal understanding)
Quick Summaries → agent_fast (fast responses)
```

### Agent Capabilities

**Vision Agent (gemma-3-12b)**
- Input: Text + Image
- Use cases:
  - Generate captions from existing images
  - Analyze composition for prompt ideas
  - Describe visual elements for reverse-engineering prompts
- Example: Upload artwork → agent describes "cyberpunk cityscape, neon lights, rain-soaked streets"

**Dialog Agent (discopop-zephyr-7b-gemma)**
- Input: Text only
- Use cases:
  - Polish rough prompt drafts
  - Improve fluency and grammar
  - Expand terse prompts with natural language
- Example: "dark forest" → "An ancient dark forest shrouded in mist, moonlight filtering through gnarled trees, atmospheric and mysterious"

**Logic Agent (gemma-3n-e4b)**
- Input: Text only
- Use cases:
  - Draft initial prompts from keywords
  - Structure complex multi-element prompts
  - Plan prompt variations
- Example: Keywords "cyberpunk, rain, neon" → Structured prompt with theme, style, mood, technical details

**Fast Agent (lfm2-1.2b)**
- Input: Text only
- Use cases:
  - Extract keywords from long descriptions
  - Quick summaries of reference text
  - Fallback when primary agents unavailable
- Example: Long article → "futuristic, urban, technology, night"

### Orchestration Flow (Conceptual)

1. **User requests prompt draft**
   - System routes to `agent_logic`
   - Logic agent generates structured draft
   - (Optional) Route to `agent_dialog` for fluency pass

2. **User uploads reference image**
   - System routes to `agent_vision` with image
   - Vision agent describes visual elements
   - Description used as prompt seed

3. **Agent unavailable fallback**
   - If primary agent offline → use `agent_fast`
   - Fast agent provides simpler response
   - UI notifies user of degraded mode

### Integration Points

- **Backend**: `/api/llm/health` — Check agent availability
- **Routing**: `app.core.agents.py` — Task-to-agent mapping
- **Client**: `app.core.llm_client.py` — HTTP communication with llama-servers
- **UI**: (Future) Prompt editor with "Draft" and "Polish" buttons

---

**For full specification and templates, see**: [/docs/prompt_templates/](/docs/prompt_templates/)
