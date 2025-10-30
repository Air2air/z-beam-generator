# Voice Architecture - YAML-Only Prompting System

**Status**: Fully implemented (October 24, 2025)  
**Design Principle**: ALL voice prompting comes exclusively from YAML configuration files

---

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                    YAML-ONLY VOICE SYSTEM                       │
└─────────────────────────────────────────────────────────────────┘
                              ▼
        ┌─────────────────────────────────────────┐
        │   voice/base/voice_base.yaml            │
        │   • Core principles                     │
        │   • Technical standards                 │
        │   • Forbidden patterns                  │
        │   • Section-specific rules              │
        └─────────────────────────────────────────┘
                              +
        ┌─────────────────────────────────────────┐
        │   voice/profiles/{country}.yaml         │
        │   • taiwan.yaml                         │
        │   • italy.yaml                          │
        │   • indonesia.yaml                      │
        │   • united_states.yaml                  │
        │   • Linguistic patterns                 │
        │   • Grammar characteristics             │
        │   • Vocabulary patterns                 │
        └─────────────────────────────────────────┘
                              ▼
        ┌─────────────────────────────────────────┐
        │   VoiceOrchestrator (Python)            │
        │   • Loads YAML files                    │
        │   • Formats sections                    │
        │   • NO hardcoded prompts                │
        └─────────────────────────────────────────┘
                              ▼
        ┌─────────────────────────────────────────┐
        │   Complete Prompt → Grok API            │
        └─────────────────────────────────────────┘
```

---

## File Structure

### 1. Base Voice (Universal Rules)
**File**: `voice/base/voice_base.yaml`

**Contains**:
- `core_principles` - Technical authority, analytical precision
- `technical_writing_standards` - Terminology, measurements, direct observations
- `forbidden_patterns` - Marketing language, vague results, emotional descriptors
- `laser_cleaning_context`:
  - `before_state_focus` - Contamination analysis requirements
  - `after_state_focus` - Post-cleaning analysis requirements

**Extracted by**: `_format_base_guidance()`

### 2. Country Profiles (Linguistic Patterns)
**Files**: `voice/profiles/{country}.yaml`

**Contains**:
- `linguistic_characteristics`:
  - `sentence_structure` - Patterns, tendencies, natural variations
  - `vocabulary_patterns` - Formality level, technical density
  - `grammar_characteristics` - Common patterns, markers

**Extracted by**: `_format_country_voice()`

### 3. Orchestrator (YAML Assembly Only)
**File**: `voice/orchestrator.py`

**Role**: 
- Load YAML files (base + country profile)
- Extract relevant sections
- Format into prompt structure
- **NO hardcoded prompt text**

**Key Methods**:
```python
get_unified_prompt()           # Entry point
_build_microscopy_prompt()     # Assemble sections
_format_base_guidance()        # Extract from voice_base.yaml
_format_country_voice()        # Extract from profiles/*.yaml
```

---

## Prompt Structure (Generated)

```
You are {author_name}, a {author_expertise} expert from {author_country}, 
writing for a general audience.

{SECTION FROM voice_base.yaml - before_state_focus OR after_state_focus}
  - Title
  - Primary focus
  - Required content (list)
  - Technical authority (list)
  - Strictly forbidden (list)

{SECTION FROM voice/profiles/{country}.yaml}
  - Linguistic patterns (top 3)
  - Tendencies (top 2)
  - Formality level

MATERIAL CONTEXT:
- Material: {material_name}
- Category: {category}
- Properties: {properties}
- Applications: {applications}

ANALYSIS FOCUS:
- Section focus: {section_focus}
- Task: {section_instruction}

LENGTH TARGET:
- Target: {target_words} words
- Style: {style_guidance}
- Structure: {paragraph_count}

Generate {section_focus} description now.
```

---

## Verification Checklist

✅ **NO hardcoded prompts in Python code**  
✅ **ALL rules come from voice_base.yaml**  
✅ **ALL linguistic patterns come from country profiles**  
✅ **Orchestrator only formats/assembles YAML content**  
✅ **Material context comes from parameters only**  

---

## How to Modify Voice Behavior

### Change Technical Requirements
**Edit**: `voice/base/voice_base.yaml`  
**Section**: `laser_cleaning_context.before_state_focus` or `after_state_focus`  
**Examples**:
- Add required content items
- Modify technical authority guidelines
- Update forbidden patterns

### Change Country Voice
**Edit**: `voice/profiles/{country}.yaml`  
**Section**: `linguistic_characteristics`  
**Examples**:
- Add sentence structure patterns
- Update grammar characteristics
- Modify vocabulary patterns

### ❌ NEVER Edit
- `voice/orchestrator.py` for prompt content
- `components/caption/generators/generator.py` for voice rules
- Any Python file for voice characteristics

---

## Testing

```bash
# Verify YAML-only prompting
cd /Users/todddunning/Desktop/Z-Beam/z-beam-generator
python3 run.py --caption "MaterialName"

# Check generated prompt structure
python3 -c "
from voice.orchestrator import VoiceOrchestrator
voice = VoiceOrchestrator('Taiwan')
prompt = voice.get_unified_prompt(...)
print(prompt)
"
```

---

## Migration Complete

**Old System**: `voice/prompts/unified_voice_system.yaml` (deprecated)  
**New System**: `voice/base/voice_base.yaml` + `voice/profiles/*.yaml`  

**Benefits**:
- ✅ Separation of concerns (base rules vs. country voice)
- ✅ Easier to maintain (edit YAML, not Python)
- ✅ Better modularity (base + layered profiles)
- ✅ No code changes needed for voice modifications
- ✅ Clear source of truth for all voice behavior

---

**Last Updated**: October 24, 2025  
**Status**: Production Ready ✅
