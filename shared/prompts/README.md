# Universal Text Prompt System

## Overview

Simplified, universal approach for all text generation (subtitles, captions, FAQs, etc.):

```
Context Prompt → API Generation → Voice Postprocessor → Materials.yaml
```

## Architecture

### 1. **Context-Only Prompts** (`text_prompt_builder.py`)
- Generates prompts with ONLY context and requirements
- NO voice markers in the prompt
- Plain professional language instructions
- Component-specific: length, tone, examples

### 2. **API Generation**
- Receives neutral professional prompt
- Generates content without voice markers
- Uses standard API client (Grok, GPT, etc.)

### 3. **Voice Postprocessor** (`/shared/voice/post_processor.py`)
- Adds author-specific voice markers AFTER generation
- Intensity levels: 1-5 (light to strong)
- Author profiles: USA, Taiwan, Italy, Indonesia
- Validates voice authenticity (score ≥70/100)

### 4. **Save to Materials.yaml**
- Voice-enhanced content saved to source of truth
- Frontmatter export uses Materials.yaml data
- All text generation happens on Materials.yaml first

## Usage

### For Subtitles

```python
from shared.prompts.text_prompt_builder import TextPromptBuilder
from shared.voice.post_processor import VoicePostProcessor
from components.frontmatter.utils.author_manager import get_author_by_id

# 1. Build context-only prompt
builder = TextPromptBuilder()
prompt = builder.build_prompt(
    component_type='subtitle',
    material_name='Bronze',
    category='Metals',
    subcategory='Non-Ferrous',
    focus_area=focus_area_obj,
    siblings=['Copper', 'Brass']
)

# 2. Generate neutral content
response = api_client.generate_simple(
    prompt=prompt,
    system_prompt="Write in neutral professional tone.",
    temperature=0.7
)
neutral_text = response.content

# 3. Apply voice postprocessor
author = get_author_by_id(author_id)
voice_processor = VoicePostProcessor(api_client)
enhanced_text = voice_processor.enhance(
    text=neutral_text,
    author=author,
    intensity=2  # Light voice for subtitles
)

# 4. Save to Materials.yaml
material_data['subtitle'] = enhanced_text
```

### For Captions

```python
enhanced_caption = voice_processor.enhance(
    text=neutral_caption,
    author=author,
    intensity=3  # Moderate voice for captions
)
```

### For FAQ Answers

```python
enhanced_faq = voice_processor.enhance(
    text=neutral_faq,
    author=author,
    intensity=4  # Strong voice for FAQs
)
```

## Voice Intensity Levels

| Level | Type | Use Case | Example Markers |
|-------|------|----------|----------------|
| 1 | Minimal | Technical docs | None or very rare |
| 2 | Light | Subtitles | "helps", "ensures", "offers" |
| 3 | Moderate | Captions | "pretty", "basically" (occasional) |
| 4 | Strong | FAQs | "pretty", "basically", "fairly" |
| 5 | Maximum | Conversational | Heavy marker usage |

## Component Configuration

Add new components to `COMPONENT_CONFIGS` in `text_prompt_builder.py`:

```python
COMPONENT_CONFIGS = {
    "your_component": {
        "length": "20-30 words",
        "tone": "Descriptive and informative",
        "examples": {
            "excellent": ["Example 1", "Example 2"],
            "avoid": ["Bad example"]
        }
    }
}
```

Then set voice intensity in `components/text/config/voice_application.yaml`:

```yaml
materials_page:
  your_component: true  # Enable voice
  # Intensity: 3 (moderate) - set in code when calling voice_processor.enhance()
```

## Benefits

1. **Clean Separation**: Prompts focus on context, voice is postprocessing
2. **Consistency**: Same postprocessor for all text types
3. **Flexibility**: Easy to adjust voice intensity per component
4. **Reusability**: One prompt builder for all components
5. **Maintainability**: Single source of voice logic

## Migration from Legacy Systems

### Old Approach (❌ Deprecated)
- Voice markers embedded in prompts
- Author-specific prompt construction
- Complex prompt templates with voice instructions

### New Approach (✅ Current)
- Context-only prompts
- Universal postprocessor
- Simple, consistent pipeline

## Files

- **`text_prompt_builder.py`** - Universal prompt builder (context only)
- **`/shared/voice/post_processor.py`** - Voice enhancement postprocessor
- **`/components/text/config/voice_application.yaml`** - Voice policy per component
- **`/scripts/regenerate_subtitles.py`** - Example implementation

## Legacy Code

The following methods are DEPRECATED and kept only for backwards compatibility:
- `shared/voice/orchestrator.py:_build_subtitle_prompt_legacy()`
- `components/frontmatter/core/hybrid_generation_manager.py:_build_subtitle_prompt_legacy()`
- `components/frontmatter/core/streamlined_generator.py:_generate_subtitle_legacy()`

DO NOT use these for new development. Use the universal text approach instead.
