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

## STEP 8: Agent-Assisted Prompt Engine v2 (New)

### Overview

PODStudio's Prompt Engine v2 provides **two modes** for generating prompts:

1. **TEMPLATE_ONLY** (Zero-AI): Pure Jinja2 template substitution — always works, no dependencies
2. **AGENT_ASSISTED** (Offline AI): Uses local LLM agents for enhancement — requires llama.cpp servers

The system **automatically falls back** to TEMPLATE_ONLY if agents are unavailable, ensuring prompts always work.

### Generation Modes

#### TEMPLATE_ONLY Mode

- **Input**: Template name + variables (e.g., `{subject: "dragon", style: "fantasy"}`)
- **Process**: Jinja2 template rendering with variable substitution
- **Output**: Rendered prompt string
- **Performance**: <10ms (instant)
- **Requirements**: None (always available)

**Example**:
```python
generate_prompt(
    template_name="image_sdxl",
    variables={"subject": "dragon", "style": "fantasy art"},
    mode=PromptMode.TEMPLATE_ONLY
)
# → "dragon, fantasy art, epic mood, wide angle, dramatic lighting, highly detailed"
```

#### AGENT_ASSISTED Mode

- **Input**: Template name + variables + optional reference image
- **Process**: Multi-agent pipeline (vision → logic → dialog)
- **Output**: AI-enhanced prompt with keywords and lineage tracking
- **Performance**: 12-20s (3-4 agent calls with 3-6s each)
- **Requirements**: llama.cpp servers running (ports 9091-9094)

**Example**:
```python
generate_prompt(
    template_name="image_sdxl",
    variables={
        "subject": "dragon",
        "style": "fantasy",
        "reference_image": "/path/to/ref.png"
    },
    mode=PromptMode.AGENT_ASSISTED
)
# → Enhanced prompt with visual details from reference image
# + agent_lineage: ["agent_vision", "agent_logic", "agent_dialog"]
```

### Agent-Assisted Pipeline Flow

```
┌─────────────────────────────────────────────────────────────┐
│                   AGENT-ASSISTED PIPELINE                    │
└─────────────────────────────────────────────────────────────┘

   User Input                    Optional Reference Image
       ↓                                  ↓
   Template Name              ┌──────────────────────┐
   + Variables                │   agent_vision       │
       ↓                      │   (gemma-3-12b)      │
       ↓                      │   → Image analysis   │
       ↓                      └──────────┬───────────┘
       ↓                                 ↓
       └─────────────────────────────────┘
                         ↓
              ┌──────────────────────┐
              │   agent_logic        │
              │   (gemma-3n-e4b)     │
              │   → Structured draft │
              └──────────┬───────────┘
                         ↓
              ┌──────────────────────┐
              │   agent_dialog       │
              │   (discopop-zephyr)  │
              │   → Fluency polish   │
              └──────────┬───────────┘
                         ↓
              ┌──────────────────────┐
              │   agent_fast         │
              │   (lfm2-1.2b)        │
              │   → Keywords/tags    │
              └──────────┬───────────┘
                         ↓
                  Final Prompt
                  + Keywords
                  + Negative Prompt
                  + Agent Lineage

    ╔════════════════════════════════════╗
    ║  FALLBACK POLICY                   ║
    ║  - Any agent timeout (>20s)        ║
    ║  - Any agent unavailable           ║
    ║  → Auto-switch to TEMPLATE_ONLY    ║
    ╚════════════════════════════════════╝
```

### Fallback Behavior

**Timeout Guards**: Each agent call has 20s timeout. If exceeded:
- System falls back to TEMPLATE_ONLY mode
- User receives notification: "Offline AI unavailable — using template-only mode"

**Partial Failures**:
- Vision agent fails → continue with empty vision context
- Logic agent fails → fallback to TEMPLATE_ONLY
- Dialog agent fails → return unpolished draft

**Health Monitoring**: `/api/prompts/health` endpoint checks agent availability:
- **4/4 agents online** → recommend AGENT_ASSISTED
- **<3 agents online** → recommend TEMPLATE_ONLY

### Multimodal Support (Reference Images)

When user provides a `reference_image`:

1. **agent_vision** analyzes the image (multimodal gemma-3-12b)
2. Extracts: subject, composition, style, lighting, mood
3. Feeds analysis into **agent_logic** as additional context
4. Result: Prompts informed by visual reference

**Use Cases**:
- Upload existing artwork → generate similar prompt
- Reverse-engineer prompts from images
- Style matching: "Generate prompt for this art style"

### API Endpoints (STEP 8)

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/api/prompts/generate` | POST | Generate prompt (TEMPLATE_ONLY or AGENT_ASSISTED) |
| `/api/prompts/polish` | POST | Polish draft with agent_dialog |
| `/api/prompts/variants` | POST | Generate 3 prompt variants |
| `/api/prompts/save` | POST | Save prompt artifact with lineage |
| `/api/prompts/health` | GET | Check agent availability + mode recommendation |

### Artifact Storage

Prompts are persisted to `Work/prompts/<session_id>.json`:

```json
{
  "session_id": "abc123",
  "timestamp": "2025-10-23T12:34:56Z",
  "mode": "agent_assisted",
  "template": "image_sdxl",
  "prompt": "...",
  "negative_prompt": "...",
  "variables": {...},
  "agent_lineage": ["agent_vision", "agent_logic", "agent_dialog"],
  "reference_image": "/path/to/ref.png",
  "reference_image_hash": "a1b2c3d4e5f6..."
}
```

### Performance Characteristics

| Mode | Latency | Offline | Quality |
|------|---------|---------|---------|
| TEMPLATE_ONLY | <10ms | ✅ Always | Good (deterministic) |
| AGENT_ASSISTED | 12-20s | ⚠️ Requires agents | Excellent (AI-enhanced) |

### Token Limits

Derived from agent context sizes:

- **agent_vision**: 32K tokens (multimodal)
- **agent_dialog**: 8K tokens (fluency)
- **agent_logic**: 16K tokens (reasoning)
- **agent_fast**: 4K tokens (quick tasks)

Input prompts are truncated to 512 tokens max to stay within limits.

---

## STEP 7: LLM Agent Roles and Routing

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
