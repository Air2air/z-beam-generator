# Universal Text Generation Architecture

**Status**: ✅ Production Ready  
**Date**: November 13, 2025  
**Test Results**: 100% success rate (10/10 materials)

---

## Overview

All text generation (subtitles, captions, FAQs, descriptions) now follows a unified 3-step pipeline:

```
Context Prompt → API Generation → Voice Postprocessor → Materials.yaml
```

This replaces multiple legacy prompt systems with a single, consistent approach.

---

## Core Components

### 1. **Prompt Builder** (`shared/prompts/`)

**File**: `text_prompt_builder.py`

**Purpose**: Generate context-only prompts without voice markers

**Features**:
- Universal for all text components
- Component-specific configurations (length, tone, examples)
- Plain language anti-jargon rules
- Focus area variation support
- Sibling material comparison

**Example**:
```python
from shared.prompts.text_prompt_builder import TextPromptBuilder

builder = TextPromptBuilder()
prompt = builder.build_prompt(
    component_type='subtitle',  # or 'caption', 'faq_answer', etc.
    material_name='Bronze',
    category='Metals',
    subcategory='Non-Ferrous',
    focus_area=focus_area_obj
)
```

**Output**: Neutral professional prompt with no voice markers

---

### 2. **Voice Postprocessor** (`shared/voice/`)

**File**: `post_processor.py`

**Purpose**: Add author-specific voice markers AFTER generation

**Features**:
- 4 author profiles (USA, Taiwan, Italy, Indonesia)
- 5 intensity levels (1=minimal, 5=maximum)
- Voice authentication scoring (≥70/100)
- Language detection (prevents voice on non-English)

**Example**:
```python
from shared.voice.post_processor import VoicePostProcessor
from components.frontmatter.utils.author_manager import get_author_by_id

voice_processor = VoicePostProcessor(api_client)
author = get_author_by_id(author_id)

enhanced_text = voice_processor.enhance(
    text=neutral_content,
    author=author,
    intensity=2  # 2=light for subtitles, 3=moderate for captions, 4=strong for FAQs
)
```

**Intensity Levels**:
| Level | Use Case | Markers |
|-------|----------|---------|
| 1 | Technical docs | Minimal/none |
| 2 | Subtitles | "helps", "ensures", "offers", "maintains" |
| 3 | Captions | "pretty", "basically" (occasional) |
| 4 | FAQs | "pretty", "basically", "fairly" (frequent) |
| 5 | Conversational | Heavy marker usage |

---

### 3. **Voice Policy Configuration** (`components/text/config/`)

**File**: `voice_application.yaml`

**Purpose**: Define which fields receive voice and at what intensity

**Key Settings**:
```yaml
version: 1.1.0
updated: 2025-11-13

materials_page:
  subtitle: true        # Intensity 2 (light)
  caption_before: true  # Intensity 3 (moderate)
  caption_after: true   # Intensity 3 (moderate)
  faq_answers: true     # Intensity 4 (strong)
  title: false          # No voice
  description: false    # No voice
```

**Universal Text Approach Notes**:
- All text generated with context-only prompts
- Voice added via postprocessor
- Clean separation: prompt = context, voice = postprocessing

---

### 4. **Reference Implementation** (`scripts/`)

**File**: `regenerate_subtitles.py`

**Purpose**: Complete working example of the 3-step pipeline

**Pipeline**:
```python
# Step 1: Generate context-only prompt
prompt = generate_subtitle_prompt(material_name, category, subcategory, 
                                   focus_area, siblings, author_id=None)

# Step 2: Generate neutral content from API
response = api_client.generate_simple(
    prompt=prompt,
    system_prompt="Write in neutral professional tone.",
    temperature=0.7
)
neutral_text = response.content

# Step 3: Apply voice postprocessor
author = get_author_by_id(author_id)
enhanced_text = voice_processor.enhance(
    text=neutral_text,
    author=author,
    intensity=2  # Light voice for subtitles
)

# Step 4: Save to Materials.yaml
material_data['subtitle'] = enhanced_text
material_data['subtitle_metadata'] = {
    'generation_method': 'context_prompt_plus_voice_postprocessor',
    'voice_enhanced': True,
    'author_id': author_id
}
```

**Test Results**: 100% success rate on 10 diverse materials

---

## Component Directory Structure

```
shared/
├── prompts/
│   ├── __init__.py
│   ├── text_prompt_builder.py    # Universal prompt builder
│   └── README.md                  # Complete usage guide
└── voice/
    ├── post_processor.py          # Voice enhancement
    └── orchestrator.py            # Legacy (contains _legacy methods)

components/text/config/
└── voice_application.yaml         # Voice policy per component

scripts/
└── regenerate_subtitles.py        # Reference implementation

components/frontmatter/
├── core/
│   ├── base_generator.py
│   ├── hybrid_generation_manager.py  # Contains _legacy methods
│   └── streamlined_generator.py      # Contains _legacy methods
└── utils/
    └── author_manager.py          # get_author_by_id()
```

---

## Adding New Text Components

### 1. Add Component Config

Edit `shared/prompts/text_prompt_builder.py`:

```python
COMPONENT_CONFIGS = {
    "your_new_component": {
        "length": "20-30 words",
        "tone": "Descriptive and informative",
        "examples": {
            "excellent": ["Example with good structure"],
            "avoid": ["Example with problems"]
        }
    }
}
```

### 2. Set Voice Policy

Edit `components/text/config/voice_application.yaml`:

```yaml
materials_page:
  your_new_component: true  # Enable voice
  # Intensity set in code (1-5)
```

### 3. Implement Generation

```python
# 1. Build prompt
prompt = builder.build_prompt('your_new_component', material_name, category)

# 2. Generate neutral
neutral = api_client.generate_simple(prompt, temperature=0.7).content

# 3. Add voice
enhanced = voice_processor.enhance(neutral, author, intensity=3)

# 4. Save
material_data['your_field'] = enhanced
```

---

## Migration Guide

### From Legacy Systems

**Old Approach** (❌ Deprecated):
- Voice markers embedded in prompts
- Author-specific prompt construction
- Multiple prompt templates per component
- Files: `orchestrator.py`, `hybrid_generation_manager.py`, `streamlined_generator.py`

**New Approach** (✅ Current):
- Context-only prompts (universal)
- Voice added via postprocessor
- Single prompt builder for all components
- Files: `text_prompt_builder.py`, `post_processor.py`

### Legacy Code

The following methods are DEPRECATED (kept for backwards compatibility only):

- `shared/voice/orchestrator.py::_build_subtitle_prompt_legacy()`
- `components/frontmatter/core/hybrid_generation_manager.py::_build_subtitle_prompt_legacy()`
- `components/frontmatter/core/streamlined_generator.py::_generate_subtitle_legacy()`

**Do NOT use these for new development.**

---

## Benefits

1. **Clean Separation**: Prompts focus on context, voice is postprocessing
2. **Consistency**: Same postprocessor for all text types
3. **Flexibility**: Easy to adjust voice intensity per component
4. **Reusability**: One prompt builder for all components
5. **Maintainability**: Single source of voice logic
6. **Testability**: Each step can be tested independently

---

## Testing

Run the test suite:

```bash
# Test subtitle generation with 10 diverse materials
python3 scripts/regenerate_subtitles.py --test

# Expected output:
# ✅ Successfully regenerated: 10
# ❌ Failed: 0
# Success rate: 100.0%
```

---

## Data Flow

```
┌─────────────────────────────────────────────────────────────┐
│ 1. PROMPT GENERATION (text_prompt_builder.py)              │
│    - Material context (name, category, properties)          │
│    - Component requirements (length, tone)                   │
│    - Focus area (optional variation)                         │
│    → Output: Neutral professional prompt                     │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│ 2. API GENERATION (Grok/GPT via api_client)                 │
│    - Receives context-only prompt                            │
│    - Generates neutral professional content                  │
│    - No voice markers                                        │
│    → Output: Neutral text (e.g., "Laser cleaning removes    │
│              rust from Copper while preserving conductivity")│
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│ 3. VOICE POSTPROCESSING (post_processor.py)                 │
│    - Receives neutral text + author profile                  │
│    - Adds author-specific markers (intensity 1-5)            │
│    - Validates authenticity score (≥70/100)                  │
│    → Output: Voice-enhanced text (e.g., "Laser cleaning     │
│              helps remove rust from Copper while keeping     │
│              its conductivity intact")                       │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│ 4. SAVE TO MATERIALS.YAML (source of truth)                 │
│    - material_data['subtitle'] = enhanced_text              │
│    - material_data['subtitle_metadata'] = {...}             │
│    - Frontmatter export uses Materials.yaml                  │
└─────────────────────────────────────────────────────────────┘
```

---

## Quick Reference

| Component | Intensity | Example Markers |
|-----------|-----------|----------------|
| Subtitle | 2 (light) | "helps", "ensures", "offers", "maintains" |
| Caption | 3 (moderate) | "pretty", "basically" (occasional) |
| FAQ Answer | 4 (strong) | "pretty", "basically", "fairly" (frequent) |
| Technical | 1 (minimal) | None or very rare |

**Key Files**:
- 🔧 `shared/prompts/text_prompt_builder.py` - Universal prompts
- 🎭 `shared/voice/post_processor.py` - Voice enhancement
- 📋 `components/text/config/voice_application.yaml` - Policy
- 📝 `scripts/regenerate_subtitles.py` - Reference implementation

**Documentation**:
- 📖 `shared/prompts/README.md` - Complete usage guide

---

## Status

✅ **Production Ready**  
✅ **100% Test Success Rate**  
✅ **All 132 Materials Supported**  
✅ **Documentation Complete**
