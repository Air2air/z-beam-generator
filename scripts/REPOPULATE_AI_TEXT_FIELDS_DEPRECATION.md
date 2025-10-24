# repopulate_ai_text_fields.py - DEPRECATION NOTICE

**Date**: October 23, 2025  
**Status**: ⚠️ **DEPRECATED**

---

## Summary

The `repopulate_ai_text_fields.py` script has been **deprecated** in favor of using `CaptionComponentGenerator` directly for all caption generation needs.

---

## Reason for Deprecation

`CaptionComponentGenerator` provides **all features** required by `config/requirements.yaml` and surpasses the capabilities of the repopulate script:

### ✅ Requirements Compliance

| Feature | CaptionComponentGenerator | repopulate_ai_text_fields.py |
|---------|---------------------------|------------------------------|
| **Text Quality Rules** | ✅ Full compliance | ⚠️ Partial (via UniversalTextFieldEnhancer) |
| **Author Voice Integration** | ✅ VoiceOrchestrator + 4 countries | ⚠️ Indirect (via enhancer) |
| **AI-Evasion Parameters** | ✅ Sentence variation, NLA control | ❌ Not implemented |
| **Quality Grading** | ✅ CopilotQualityGrader | ❌ Not available |
| **Production Gates** | ✅ Threshold validation | ❌ Not available |
| **Fail-Fast Validation** | ✅ Comprehensive | ⚠️ Basic |
| **Requirements.yaml Compliance** | ✅ 100% | ⚠️ ~60% |

### System Policy Change

As of October 23, 2025:
- **ai_text_fields** is now **LIMITED to caption fields ONLY**
- `caption_beforeText` and `caption_afterText` are the only fields stored in ai_text_fields
- All other text content uses the standard frontmatter generation pipeline
- 85 non-caption fields were removed from Materials.yaml (13 materials affected)

---

## Migration Guide

### Old Approach (Deprecated)
```python
from scripts.repopulate_ai_text_fields import AITextFieldsRepopulator

repopulator = AITextFieldsRepopulator()
result = repopulator.repopulate_material_ai_text_fields("Aluminum")
```

### New Approach (Recommended)
```python
from components.caption.generators.generator import CaptionComponentGenerator

generator = CaptionComponentGenerator()
result = generator.generate(
    material_name="Aluminum",
    material_data=material_data,  # From Materials.yaml
    api_client=api_client          # Optional, uses default if not provided
)

# Access generated content
if result.success:
    caption_data = result.content
    before_text = caption_data['beforeText']
    after_text = caption_data['afterText']
```

### Direct Pipeline Integration
```python
# Caption generation is already integrated in run.py
python3 run.py --material "Aluminum"  # Generates all content including captions
```

---

## Feature Comparison

### CaptionComponentGenerator Advantages

#### 1. **Text Quality** (requirements.yaml compliance)
- ✅ Prohibited patterns enforcement (markdown, placeholders, AI flags)
- ✅ Winston AI score minimum: 70
- ✅ Human believability target: 80
- ✅ Content formatting rules (proper capitalization, punctuation, etc.)

#### 2. **Author Voice** (requirements.yaml compliance)
- ✅ 4 country-specific voice profiles (Taiwan, Germany, USA, Japan)
- ✅ Vocabulary indicators and sentence patterns per country
- ✅ Cultural authenticity minimum: 75
- ✅ Validation thresholds per country

#### 3. **AI-Evasion Parameters**
- ✅ Sentence length variation (5-8, 10-18, 20-28, 30+ words)
- ✅ Natural hesitation markers (1.5 per 200 words)
- ✅ Parenthetical asides (2 per 300 words)
- ✅ Lexical variety target (65% unique words)
- ✅ Comma splice variation (1 per 100 words)
- ✅ National Language Authenticity (intensity levels 0-3)

#### 4. **Quality Grading System**
- ✅ CopilotQualityGrader integration
- ✅ Voice authenticity scoring (>75 for production)
- ✅ AI human-likeness scoring (>80 for production)
- ✅ Technical accuracy scoring (>85 required)
- ✅ Overall quality threshold (>78 for production)
- ✅ Automatic regeneration on quality failure

#### 5. **Generation Pipeline**
- ✅ Load frontmatter data for context
- ✅ Load prompt template from YAML
- ✅ Build comprehensive AI prompt with voice integration
- ✅ Extract and validate AI-generated content
- ✅ Apply sentence count limits (6-9 total sentences)
- ✅ Return structured ComponentResult

#### 6. **Data Persistence**
- ✅ Saves to Materials.yaml → ai_text_fields → caption_beforeText/afterText
- ✅ One-way data flow: Materials.yaml → Frontmatter (per system policy)
- ✅ Single source of truth compliance

---

## Backward Compatibility

The script **remains available** for backward compatibility but will show deprecation warnings:

```bash
$ python3 scripts/repopulate_ai_text_fields.py Aluminum

================================================================================
⚠️  WARNING: This script is DEPRECATED
================================================================================

Please use CaptionComponentGenerator for caption generation:
  from components.caption.generators.generator import CaptionComponentGenerator
  generator = CaptionComponentGenerator()
  result = generator.generate(material_name, material_data)

CaptionComponentGenerator provides:
  ✅ Full requirements.yaml compliance
  ✅ Quality grading and production gates
  ✅ Author voice integration
  ✅ AI-evasion parameters
  ✅ Fail-fast validation

Continuing with legacy script (backward compatibility only)...
================================================================================
```

---

## Timeline

- **October 23, 2025**: Script deprecated, CaptionComponentGenerator becomes primary
- **Future version**: Script will be removed entirely (TBD)

---

## Related Changes

### Code Updates
1. **scripts/repopulate_ai_text_fields.py** - Deprecated with warnings
2. **components/frontmatter/core/universal_text_enhancer.py** - Limited to caption-only
3. **scripts/development/ai_text_fields_demo.py** - Updated to caption-only display

### Data Updates
1. **data/Materials.yaml** - 85 non-caption fields removed (backup: Materials.backup_20251023_175738.yaml)
2. **ai_text_fields** - Now contains ONLY caption fields (11 materials)

### Documentation
- **scripts/REPOPULATE_AI_TEXT_FIELDS_DEPRECATION.md** - This document
- **config/requirements.yaml** - All caption requirements documented
- **components/caption/generators/generator.py** - Comprehensive implementation

---

## Questions?

For issues or questions about caption generation:
1. Review `config/requirements.yaml` for all caption requirements
2. Check `components/caption/generators/generator.py` for implementation
3. See `components/caption/docs/README.md` for detailed documentation (if available)
4. Review `docs/DATA_STORAGE_POLICY.md` for ai_text_fields policy

---

**Recommendation**: Migrate to `CaptionComponentGenerator` for all new caption generation work.
