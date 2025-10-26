# Archived Unused Code

**Date**: October 25, 2025  
**Reason**: Radical simplification - removing unused complexity

## What was archived

### Total Impact (Phase 1 + Phase 2)
- **29 files archived**
- **8,383 lines of code removed from active codebase**
- **5.9% reduction** from 141,453 lines
- Focus on production-critical code only

## Categories

### Phase 1: Initial Cleanup (669 + 925 + 1,208 + 53 = 2,855 lines)

#### 1. Deprecated Scripts (669 lines)
Scripts that have been replaced by better implementations:
- `repopulate_ai_text_fields.py` - Replaced by CaptionComponentGenerator
- `REPOPULATE_AI_TEXT_FIELDS_DEPRECATION.md` - Documentation for above
- `ai_text_fields_demo.py` - Demo script, not needed

#### 2. Unused Systems (925 lines)
Systems built but never used in production:
- `universal_text_enhancer.py` - Over-engineered, never activated
- `demonstrate_field_separation.py` - Academic exercise

#### 3. Over-Documentation (1,208 lines)
Documentation for unused features:
- `TEXT_VS_NON_TEXT_FIELDS.md` - Complex field separation system (unused)
- `MATERIALS_FRONTMATTER_ANALYSIS.md` - Analysis leading to unused features
- `FIELD_NORMALIZATION_ACTION_PLAN.md` - Plan for unused features

#### 4. Unused Pipeline (53 lines)
Pipeline modes that were never completed:
- `text_generator.py` - Placeholder, never implemented

### Phase 2: Aggressive Cleanup (2,061 + 1,902 + 1,565 = 5,528 lines)

#### 5. Development Test Scripts (2,061 lines)
Test, demo, and analysis scripts never used in production:
- `advanced_blind_test.py` (117 lines)
- `analyze_linguistic_technicalities.py` (225 lines)
- `analyze_technical_gaps.py` (234 lines)
- `blind_author_test.py` (171 lines)
- `demonstrate_enhanced_generation.py` (168 lines)
- `show_complete_fields.py` (62 lines)
- `test_author_linguistics.py` (129 lines)
- `test_author_voice_simple.py` (83 lines)
- `test_author_voices.py` (76 lines)
- `test_differentiation_prompts.py` (153 lines)
- `test_enhanced_text_system.py` (108 lines)
- `test_full_author_analysis.py` (68 lines)
- `test_hybrid_enhancement.py` (75 lines)
- `test_linguistic_integration.py` (91 lines)
- `test_linguistic_technicalities.py` (162 lines)
- `test_sentence_structures.py` (109 lines)
- `test_unified_pipeline.py` (30 lines)

#### 6. Legacy Utilities (1,902 lines)
Deprecated utility scripts:
- `run_legacy.py` - 1,902 lines of legacy code replaced by current system

#### 7. Redundant Documentation (1,565 lines)
Documentation that's redundant or for unused features:
- `UNUSED_FILE_DETECTION_STRATEGY.md` (679 lines)
- `DEPLOYMENT_CHECKLIST.md` (886 lines) - Replaced by `--deploy` command

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
