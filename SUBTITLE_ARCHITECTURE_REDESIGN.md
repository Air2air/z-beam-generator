# Subtitle Generation Architecture Redesign
**Date**: November 13, 2025  
**Status**: Implementation in progress

---

## Problem

**Previous approach**: Try to teach AI via complex prompts with anti-AI rules
- ❌ Complex prompts with 30+ lines of instructions
- ❌ AI still generates uniform patterns despite rules
- ❌ No enforcement mechanism
- ❌ 100% AI detection failure

**Result**: All subtitles followed "Precision Laser [verb] [material]'s [property]" pattern

---

## New Architecture (Post-Processing Pipeline)

### Flow

```
1. SIMPLE PROMPT
   - Context + length only
   - No anti-AI rules
   - No voice instructions
   ↓
2. API GENERATES
   - Neutral subtitle
   - Basic professional tone
   ↓
3. STRUCTURAL TRANSFORMATION
   - VoicePostProcessor.transform_subtitle_structure()
   - 5 pattern templates
   - Programmatic variation
   ↓
4. AI DETECTION
   - AIDetector.detect_ai_patterns()
   - Score 0-100 (lower = better)
   ↓
5. RETRY LOOP
   - Max 3 attempts
   - Different pattern each attempt
   - Success if AI score < 40
   ↓
6. SAVE RESULT
```

### Changes Made

#### 1. Simplified Prompt (`shared/voice/orchestrator.py`)

**Before** (40+ lines):
```python
prompt = f"""You are {author_name} from {author_country}...

🚨 CRITICAL ANTI-AI REQUIREMENTS:
  NEVER use formula: 'Laser cleaning [verb] [material] while [benefit]'
  VARY sentence structure...
  [30+ lines of rules]
"""
```

**After** (10 lines):
```python
prompt = f"""Write a professional {target_words}-word subtitle for laser cleaning {material_name}.

MATERIAL CONTEXT:
- Material: {material_name}
- Category: {material_category}

REQUIREMENTS:
- {target_words} words (±2)
- Professional tone
- No period at end

Generate subtitle:"""
```

#### 2. Added Structural Transformation (`shared/voice/post_processor.py`)

New method: `transform_subtitle_structure()`

**Pattern Templates**:
1. `verb_material_connector`: "Preserve [material]'s [property] without [risk]"
2. `material_verb_property`: "[Material] maintains [property] during cleaning"
3. `property_preserved_via`: "[Property] preserved via precise laser control"
4. `connector_first`: "Without damage, restore [material]'s [property]"
5. `gerund_focus`: "Restoring [material] integrity through laser precision"

**Features**:
- Rotates through 5 patterns
- AI detection per attempt
- Word count preservation
- Retry loop (max 3)
- Success if AI score < 40

#### 3. Wired Up Script (`scripts/regenerate_subtitles.py`)

**Before**:
- Generated subtitle directly from API
- No post-processing
- No AI detection
- No retry

**After**:
- Simple generation → transformation → detection → retry
- Uses `VoicePostProcessor.transform_subtitle_structure()`
- Shows AI scores
- Reports transformation pattern used

---

## Status: Debugging

### Current Error

```python
AttributeError: 'AIDetector' object has no attribute 'is_ai_generated'
```

**Fix Applied**: Changed to `detect_ai_patterns()` which returns:
```python
{
    'ai_score': float,  # 0-100
    'is_ai_like': bool,
    'confidence': str,
    'issues': List[str],
    'recommendation': str
}
```

### Next Steps

1. ✅ Fix AIDetector method name → DONE
2. ⏳ Test transformation flow
3. ⏳ Verify structural variation
4. ⏳ Consolidate configuration files

---

## File Consolidation Plan

### Current Mess (Too Many Files)

```
shared/voice/
├── base/voice_base.yaml (295 lines - intensity levels, forbidden patterns)
├── component_config.yaml (anti-AI requirements)
├── ai_detection_patterns.txt (pattern definitions)
├── ai_detection.py (detector class)
├── post_processor.py (transformation logic)
├── orchestrator.py (prompt building)
└── profiles/*.yaml (4 country profiles)

components/text/config/
└── voice_application.yaml (voice marker rules)

shared/prompts/
└── text_prompt_builder.py (simplified builder - NOT USED)
```

### Consolidation Target

```
shared/voice/
├── config.yaml  # CONSOLIDATED: All voice/detection config
│   ├── subtitle_patterns (5 transformation templates)
│   ├── forbidden_phrases (from voice_base.yaml)
│   ├── ai_detection_rules (from ai_detection_patterns.txt)
│   ├── component_settings (from component_config.yaml)
│   └── intensity_levels (from voice_base.yaml)
│
├── detector.py  # RENAMED: ai_detection.py
├── transformer.py  # NEW: Extract from post_processor.py
├── processor.py  # RENAMED: post_processor.py (voice enhancement only)
└── profiles/*.yaml  # KEEP: Country-specific patterns

REMOVE:
❌ shared/voice/base/voice_base.yaml → Move to config.yaml
❌ shared/voice/component_config.yaml → Move to config.yaml
❌ shared/voice/ai_detection_patterns.txt → Move to config.yaml
❌ shared/voice/orchestrator.py → Functionality moved to transformer.py
❌ shared/prompts/text_prompt_builder.py → Not used
❌ components/text/config/voice_application.yaml → Merge into config.yaml
```

### Benefits

1. **Single source of truth**: One config file
2. **Clear separation**: detector.py, transformer.py, processor.py
3. **Easier maintenance**: All rules in one place
4. **Better testing**: Simpler to mock/test
5. **Less confusion**: Fewer files to navigate

---

## Next Actions

1. **Test current implementation** - verify transformation works
2. **Consolidate configs** - merge into single config.yaml
3. **Refactor code** - split into detector/transformer/processor
4. **Update documentation** - reflect new architecture
5. **Deploy** - test on all 132 materials

---

## Success Metrics

- ✅ Structural variation (5+ different patterns)
- ✅ AI detection score < 40
- ✅ Word count preserved (±2 words)
- ✅ Professional tone maintained
- ✅ Material-specific content
- ✅ < 5 configuration files total

---

**Current Status**: Debugging transformation flow  
**Next**: Test and verify structural variation working
