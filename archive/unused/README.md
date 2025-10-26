# Archived Unused Code

**Date**: October 25, 2025  
**Reason**: Radical simplification - removing unused complexity

## What was archived

### Total Impact
- **9 files archived**
- **2,855 lines of code removed from active codebase**
- Focus on production-critical code only

## Categories

### 1. Deprecated Scripts (669 lines)
Scripts that have been replaced by better implementations:
- `repopulate_ai_text_fields.py` - Replaced by CaptionComponentGenerator
- `REPOPULATE_AI_TEXT_FIELDS_DEPRECATION.md` - Documentation for above
- `ai_text_fields_demo.py` - Demo script, not needed

### 2. Unused Systems (925 lines)
Systems built but never used in production:
- `universal_text_enhancer.py` - Over-engineered, never activated
- `demonstrate_field_separation.py` - Academic exercise

### 3. Over-Documentation (1,208 lines)
Documentation for unused features:
- `TEXT_VS_NON_TEXT_FIELDS.md` - Complex field separation system (unused)
- `MATERIALS_FRONTMATTER_ANALYSIS.md` - Analysis leading to unused features
- `FIELD_NORMALIZATION_ACTION_PLAN.md` - Plan for unused features

### 4. Unused Pipeline (53 lines)
Pipeline modes that were never completed:
- `text_generator.py` - Placeholder, never implemented

## Production Stack (What Remains)

```
Materials.yaml (source of truth)
    ↓
CaptionComponentGenerator (845 lines) - WORKING
    ↓ uses
VoiceOrchestrator (762 lines) - WORKING
    ↓ writes to
Materials.yaml (captions saved)
    ↓
TrivialExporter (264 lines) - WORKING
    ↓
content/frontmatter/*.yaml (132 files)
    ↓
python3 run.py --deploy
    ↓
Production ✅
```

## Recovery

If you need any of this code back:
```bash
# Copy file back from archive
cp archive/unused/path/to/file.py original/path/file.py
```

## Philosophy

**Complexity is the enemy of reliability.**

We archived code that:
- Wasn't used in production
- Added maintenance burden
- Made onboarding harder
- Distracted from what actually works

The remaining codebase focuses on:
- ✅ What's tested
- ✅ What's deployed
- ✅ What generates value
