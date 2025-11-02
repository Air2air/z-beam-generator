# Voice Module Reusability Guide

**Date**: November 1, 2025  
**Status**: ✅ Production Ready  
**Purpose**: Standalone voice post-processing for frontmatter content

---

## 🎯 Overview

The voice module is now a **fully reusable** post-processor that can:
- Read existing frontmatter files
- Apply author voice to text content
- Validate voice markers
- Save enhanced content back to frontmatter

This enables **voice reprocessing** of content that was generated without voice enhancement or needs voice updates.

---

## 🏗️ Architecture

### Voice Module Location
- **Core**: `shared/voice/post_processor.py` - VoicePostProcessor class
- **Profiles**: `shared/voice/profiles/*.yaml` - Country-specific voice profiles
- **Orchestrator**: `shared/voice/orchestrator.py` - Profile management
- **CLI Tool**: `scripts/voice/reprocess_frontmatter_voice.py` - Standalone reprocessing

### Design Philosophy
```
Discrete Post-Processor Pattern:
  Input: text + author → Output: enhanced_text
  
  - Single Responsibility: Only voice enhancement
  - No Dependencies: Works with any text from any component
  - Reusable: Can be called at any stage
  - Configurable: Intensity, markers, length control
```

---

## 📋 Usage Patterns

### Pattern 1: During Generation (Inline)
Voice is applied during content generation:

```python
from shared.voice.post_processor import VoicePostProcessor

# Generate base content
caption = generate_caption(material_name)

# Apply voice inline
processor = VoicePostProcessor(api_client)
enhanced_caption = processor.enhance(
    text=caption,
    author={'name': 'Todd Dunning', 'country': 'United States'},
    voice_intensity=3
)

# Save to Materials.yaml with voice markers
```

**Used by**: Caption, Subtitle, FAQ generators

### Pattern 2: Post-Generation (Reprocessing)
Voice applied to existing frontmatter:

```bash
# Single file
python3 scripts/voice/reprocess_frontmatter_voice.py \
  --file materials/aluminum-laser-cleaning.yaml

# All materials
python3 scripts/voice/reprocess_frontmatter_voice.py --all-materials

# Specific material
python3 scripts/voice/reprocess_frontmatter_voice.py \
  --content-type material --identifier "Aluminum"

# Dry run (preview changes)
python3 scripts/voice/reprocess_frontmatter_voice.py \
  --file materials/aluminum-laser-cleaning.yaml --dry-run

# Validate only (check voice markers)
python3 scripts/voice/reprocess_frontmatter_voice.py --validate-only
```

### Pattern 3: Voice Validation
Check voice authenticity without enhancement:

```python
from shared/voice.post_processor import VoicePostProcessor

processor = VoicePostProcessor(api_client)

# Get voice score
score = processor.get_voice_score(
    text=caption_text,
    author=author_data
)

print(f"Authenticity: {score['authenticity_score']}/100")
print(f"Markers found: {score['marker_count']}")
print(f"Quality: {score['authenticity']}")  # excellent, good, fair, poor
```

---

## 🔧 CLI Tool: reprocess_frontmatter_voice.py

### Purpose
Standalone tool for applying voice to existing frontmatter files.

### Features
- ✅ Processes caption (before/after sections)
- ✅ Processes subtitle
- ✅ Processes FAQ answers (batch enhancement)
- ✅ Validates voice markers (authenticity scoring)
- ✅ Atomic file writes (no data loss)
- ✅ Dry-run mode (preview changes)
- ✅ Batch processing (all materials/regions)

### Command Reference

```bash
# Process single file
python3 scripts/voice/reprocess_frontmatter_voice.py \
  --file materials/aluminum-laser-cleaning.yaml

# Process by identifier
python3 scripts/voice/reprocess_frontmatter_voice.py \
  --content-type material --identifier "Aluminum"

# Process all materials
python3 scripts/voice/reprocess_frontmatter_voice.py --all-materials

# Process all regions
python3 scripts/voice/reprocess_frontmatter_voice.py --all-regions

# Dry run (no changes)
python3 scripts/voice/reprocess_frontmatter_voice.py \
  --file materials/aluminum-laser-cleaning.yaml --dry-run

# Validate voice markers
python3 scripts/voice/reprocess_frontmatter_voice.py --validate-only

# Custom voice intensity
python3 scripts/voice/reprocess_frontmatter_voice.py \
  --file materials/aluminum-laser-cleaning.yaml \
  --voice-intensity 4  # 1-5, default: 3
```

### Output
```
📝 Processing: aluminum-laser-cleaning.yaml
✅ Enhanced caption 'before' section
✅ Enhanced caption 'after' section
✅ Enhanced FAQ (8 answers)
💾 Saved enhanced frontmatter: aluminum-laser-cleaning.yaml

📊 VOICE REPROCESSING STATISTICS
================================================================================
Processed:  1
Enhanced:   1
Skipped:    0
Errors:     0
================================================================================
```

---

## 🧪 E2E Pipeline Test

### Purpose
Validates the complete generation pipeline:
1. Generate content → Materials.yaml
2. Export to frontmatter
3. Validate voice markers
4. Check data integrity

### Usage
```bash
# Test all components for a material
python3 tests/e2e_pipeline_test.py "Aluminum"

# Test specific component
python3 tests/e2e_pipeline_test.py "Aluminum" --component caption
python3 tests/e2e_pipeline_test.py "Aluminum" --component subtitle
python3 tests/e2e_pipeline_test.py "Aluminum" --component faq
```

### Output
```
🧪 TEST: Caption Generation Pipeline - Aluminum
================================================================================

📝 Step 1: Generating caption...
✅ Caption generated successfully

🔍 Step 2: Verifying Materials.yaml...
✅ Caption in Materials.yaml:
   - Before: 48 words
   - After: 52 words
   - Generated: 2025-11-01T12:34:56.789Z

🎤 Step 3: Validating voice markers...
   Before authenticity: 85.0/100
   Before markers: 3
   After authenticity: 90.0/100
   After markers: 3
✅ Voice markers validated

📊 E2E PIPELINE TEST SUMMARY
================================================================================
GENERATION:
  ✅ caption

MATERIALS_YAML:
  ✅ caption

VOICE_VALIDATION:
  ✅ caption
================================================================================
```

---

## 🔍 Voice Validation Criteria

### Authenticity Scoring (0-100)

**Excellent (85-100)**
- 3-4 voice markers
- Natural distribution
- No translation artifacts
- No excessive repetition

**Good (70-84)**
- 2-3 voice markers
- Reasonable distribution
- Minimal artifacts

**Fair (50-69)**
- 1-2 voice markers
- Some clustering
- Minor artifacts

**Poor (0-49)**
- 0-1 voice markers
- Wrong language detected
- Heavy translation artifacts
- Excessive marker repetition

### Recommendation Actions
- **keep**: Authenticity >= 70, no changes needed
- **enhance**: Authenticity 40-69, add more markers
- **reprocess**: Authenticity < 40 or artifacts detected
- **translate**: Wrong language detected

---

## 📊 Data Flow

### Generation Flow (Inline Voice)
```
AI Generation → VoicePostProcessor.enhance() → Materials.yaml
     ↓
Materials.yaml → Export → Frontmatter (with voice markers)
```

### Reprocessing Flow (Post-Generation Voice)
```
Frontmatter (no voice) → reprocess_frontmatter_voice.py → Frontmatter (with voice)
                              ↓
                       VoicePostProcessor.enhance()
```

### Validation Flow
```
Frontmatter → VoicePostProcessor.get_voice_score() → Validation Report
     ↓
  Caption, Subtitle, FAQ → Authenticity Score (0-100)
```

---

## 🎛️ Voice Configuration

### Voice Intensity Levels (1-5)

**Level 1: Minimal**
- Very subtle markers
- 1-2 markers per text
- Natural, barely noticeable

**Level 2: Light**
- Light voice presence
- 2 markers per text
- Natural integration

**Level 3: Moderate (DEFAULT)**
- Balanced authenticity
- 2-3 markers per text
- Clear but not excessive

**Level 4: Strong**
- Distinctive character
- 3-4 markers per text
- Notable voice presence

**Level 5: Maximum**
- Highly characteristic
- 4+ markers per text
- Very strong voice

### Author Profiles

**Available Countries:**
- United States (California)
- Taiwan
- Italy
- Indonesia

Each profile includes:
- Signature phrases (linguistic markers)
- Formality level
- Technical terminology preferences
- Cultural communication patterns

---

## 🚀 Use Cases

### Use Case 1: Bulk Voice Enhancement
You have 132 materials with frontmatter but no voice markers:

```bash
# Process all at once
python3 scripts/voice/reprocess_frontmatter_voice.py --all-materials

# Or incrementally
for material in $(ls frontmatter/materials/*.yaml); do
  python3 scripts/voice/reprocess_frontmatter_voice.py --file "$material"
done
```

### Use Case 2: Voice Update After Profile Changes
Voice profiles updated with new markers:

```bash
# Reprocess all materials to apply new markers
python3 scripts/voice/reprocess_frontmatter_voice.py \
  --all-materials \
  --voice-intensity 3
```

### Use Case 3: Quality Audit
Check voice marker coverage across all content:

```bash
# Validate all materials
python3 scripts/voice/reprocess_frontmatter_voice.py \
  --validate-only \
  --all-materials > voice_audit_report.txt
```

### Use Case 4: A/B Testing Voice Intensity
Test different voice intensities:

```bash
# Test with low intensity
python3 scripts/voice/reprocess_frontmatter_voice.py \
  --file materials/aluminum-laser-cleaning.yaml \
  --voice-intensity 2 \
  --dry-run

# Test with high intensity
python3 scripts/voice/reprocess_frontmatter_voice.py \
  --file materials/aluminum-laser-cleaning.yaml \
  --voice-intensity 4 \
  --dry-run
```

---

## 🔒 Safety Features

### Atomic Writes
All file operations use atomic writes:
1. Write to temporary file
2. Verify write succeeded
3. Atomic rename (replaces original)
4. Cleanup temp file on error

### Dry Run Mode
Preview changes without modifying files:
```bash
python3 scripts/voice/reprocess_frontmatter_voice.py \
  --all-materials \
  --dry-run
```

### Validation Before Enhancement
VoicePostProcessor validates text before enhancement:
- ✅ Detects wrong language (Indonesian, Italian)
- ✅ Identifies translation artifacts
- ✅ Checks existing voice markers
- ✅ Skips if already authentic (>70 score)

---

## 📈 Performance

### Processing Speed
- **Single file**: ~3-5 seconds
- **Caption + Subtitle + FAQ**: ~8-12 seconds
- **All materials (132)**: ~15-20 minutes

### API Usage
- **Caption**: 1 API call (before + after in one request)
- **Subtitle**: 1 API call
- **FAQ**: 1 API call (batch enhancement)

**Total per material**: 3 API calls

---

## 🛠️ Troubleshooting

### Issue: No voice markers detected
**Solution**: Check author data in frontmatter:
```yaml
author:
  name: "Todd Dunning"
  country: "United States"  # Must match profile name
```

### Issue: Validation shows low authenticity
**Solution**: Reprocess with higher intensity:
```bash
python3 scripts/voice/reprocess_frontmatter_voice.py \
  --file materials/aluminum-laser-cleaning.yaml \
  --voice-intensity 4
```

### Issue: Wrong language detected
**Solution**: Content is in non-English language, needs translation first.
Check `docs/voice/TRANSLATION_WORKFLOW.md`.

### Issue: Translation artifacts detected
**Solution**: Reprocess to clean up artifacts:
```bash
python3 scripts/voice/reprocess_frontmatter_voice.py \
  --file materials/aluminum-laser-cleaning.yaml \
  --voice-intensity 3
```

---

## 📚 Related Documentation

- **Voice System**: `shared/voice/README.md`
- **Voice Profiles**: `shared/voice/profiles/README.md`
- **Post Processor API**: `shared/voice/post_processor.py` (docstrings)
- **E2E Testing**: `tests/e2e_pipeline_test.py`
- **Generation Commands**: `shared/commands/generation.py`

---

## 🎓 Best Practices

1. **Always use author data**: Voice enhancement requires proper author information
2. **Start with default intensity**: Level 3 works for most content
3. **Validate before bulk processing**: Test on single file first
4. **Use dry-run for experiments**: Preview changes before applying
5. **Monitor authenticity scores**: Aim for 70+ for production content
6. **Reprocess after profile updates**: Keep voice markers current
7. **Batch FAQ enhancement**: Better marker distribution than individual answers

---

## ✅ Summary

The voice module is now **fully reusable** with:
- ✅ Standalone CLI tool for post-processing
- ✅ E2E pipeline test validation
- ✅ Voice authenticity scoring
- ✅ Atomic file operations
- ✅ Dry-run and validation modes
- ✅ Batch processing support
- ✅ Comprehensive documentation

**Result**: Content can be generated first, then voice-enhanced later, or voice can be updated anytime without regenerating content.
