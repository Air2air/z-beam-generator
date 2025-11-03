# Voice Workflow - Complete Guide

**Quick Reference for Voice Enhancement System**  
**Last Updated**: November 2, 2025

---

## 🎯 Three-Step Workflow

```
Step 1: GENERATE → Materials.yaml
Step 2: VOICE ENHANCE → OVERWRITES fields in Materials.yaml  
Step 3: MANUAL EXPORT → combines Materials.yaml + Categories.yaml → frontmatter
```

---

## 📋 Step-by-Step Commands

### Step 1: Generate Content (Saves to Materials.yaml)

```bash
# Generate individual components
python3 run.py --caption "Aluminum"     # Caption → Materials.yaml
python3 run.py --subtitle "Aluminum"    # Subtitle → Materials.yaml
python3 run.py --faq "Aluminum"         # FAQ → Materials.yaml

# Or generate all content for a material at once
python3 run.py --material "Aluminum"    # All components → Materials.yaml
```

**What this does**:
- AI generates raw content (no voice markers)
- Saves directly to `materials/data/Materials.yaml`
- Content is technical and neutral

### Step 2: Apply Voice Enhancement (OVERWRITES fields in Materials.yaml)

```bash
# Single material
python3 scripts/voice/enhance_materials_voice.py --material "Aluminum"

# All materials
python3 scripts/voice/enhance_materials_voice.py --all

# Dry run (preview changes without saving)
python3 scripts/voice/enhance_materials_voice.py --material "Aluminum" --dry-run

# Validate voice quality
python3 scripts/voice/enhance_materials_voice.py --validate-only
```

**What this does**:
- Reads material entry from `materials/data/Materials.yaml`
- Applies voice markers to qualifying text fields:
  - `caption.before`
  - `caption.after`
  - `subtitle`
  - `faq[].answer`
- **OVERWRITES original text** with voice-enhanced version
- Uses atomic writes (temp files) for safe overwriting
- Only overwrites if authenticity score ≥70/100
- Adds `voice_enhanced` timestamp

### Step 3: Manual Export (Combines Materials.yaml + Categories.yaml → frontmatter)

```bash
# Single material
python3 run.py --material "Aluminum" --data-only

# All materials
python3 run.py --all --data-only
```

**What this does**:
- Reads voice-enhanced content from `materials/data/Materials.yaml`
- Reads category metadata from `materials/data/Categories.yaml`
- Combines both sources into complete frontmatter structure
- Exports to `frontmatter/materials/aluminum-laser-cleaning.yaml`
- NO API calls (content already generated and enhanced)
- NO validation (already validated in Materials.yaml)
- Fast: seconds for all 132 materials

---

## 🔄 Complete Example: Aluminum

```bash
# 1. Generate content
echo "Step 1: Generate content → Materials.yaml"
python3 run.py --caption "Aluminum"
python3 run.py --subtitle "Aluminum"
python3 run.py --faq "Aluminum"

# 2. Apply voice enhancement
echo "Step 2: Apply voice → OVERWRITES fields in Materials.yaml"
python3 scripts/voice/enhance_materials_voice.py --material "Aluminum"

# 3. Export to frontmatter
echo "Step 3: Export → combines Materials.yaml + Categories.yaml → frontmatter"
python3 run.py --material "Aluminum" --data-only

echo "✅ Complete! Check: frontmatter/materials/aluminum-laser-cleaning.yaml"
```

---

## 🚀 Batch Processing (All Materials)

```bash
# Generate all content
python3 run.py --all

# Apply voice to all materials
python3 scripts/voice/enhance_materials_voice.py --all

# Export all to frontmatter
python3 run.py --all --data-only
```

---

## 📊 Voice Quality Scoring

Voice authenticity is measured 0-100:

| Score | Quality | Action |
|-------|---------|--------|
| 85-100 | Excellent | No action needed |
| 70-84 | Good | Production ready |
| 50-69 | Fair | Enhancement recommended |
| 0-49 | Poor | Re-enhancement required |

The voice enhancement script **only overwrites** if enhanced version scores ≥70/100.

---

## 🔍 Verification Commands

```bash
# Check if voice enhancement was applied
python3 -c "
import yaml
with open('materials/data/Materials.yaml') as f:
    data = yaml.safe_load(f)
    material = data['materials']['Aluminum']
    print('voice_enhanced:', material.get('voice_enhanced', 'Not yet enhanced'))
"

# Validate voice markers in frontmatter
python3 scripts/voice/enhance_materials_voice.py --validate-only

# Check frontmatter file exists
ls -lh frontmatter/materials/aluminum-laser-cleaning.yaml
```

---

## 🎭 Author Voice Profiles

Voice markers are country-specific:

| Country | Author | Style | Word Limit |
|---------|--------|-------|------------|
| United States | Todd Dunning | Conversational expertise | 320 |
| Taiwan | Yi-Chun Lin | Academic precision | 380 |
| Italy | Alessandro Moretti | Technical elegance | 450 |
| Indonesia | Ikmanda Roswati | Practical accessible | 250 |

Author assignment is automatic based on material data.

---

## 🔑 Key Principles

1. ✅ **Voice enhancement OVERWRITES fields** in Materials.yaml
2. ✅ **Materials.yaml is the single source of truth** for all content
3. ✅ **Export is a separate manual step** - combines Materials.yaml + Categories.yaml
4. ✅ **Categories.yaml provides metadata only** (NO fallback ranges)
5. ✅ **All complex operations happen on Materials.yaml** (generation, voice, validation)
6. ✅ **Frontmatter export is trivial** (simple copy + combine operation)

---

## 🛠️ Advanced Options

### Voice Intensity Adjustment

```bash
# Light voice (intensity 1-2)
python3 scripts/voice/enhance_materials_voice.py --material "Aluminum" --voice-intensity 2

# Heavy voice (intensity 4-5)
python3 scripts/voice/enhance_materials_voice.py --material "Aluminum" --voice-intensity 4

# Default is 3 (moderate)
```

### Dry Run (Preview Changes)

```bash
# See what would change without saving
python3 scripts/voice/enhance_materials_voice.py --material "Aluminum" --dry-run
```

### Voice Validation Only

```bash
# Check voice quality across all materials without making changes
python3 scripts/voice/enhance_materials_voice.py --validate-only
```

---

## 📁 File Locations

- **Source Data**: `materials/data/Materials.yaml` (single source of truth)
- **Category Data**: `materials/data/Categories.yaml` (metadata only)
- **Voice Script**: `scripts/voice/enhance_materials_voice.py`
- **Export Output**: `frontmatter/materials/*.yaml`
- **Voice Profiles**: `shared/voice/profiles/*.yaml`

---

## 🐛 Troubleshooting

### Voice enhancement not working?
```bash
# Check if material exists in Materials.yaml
python3 -c "
import yaml
with open('materials/data/Materials.yaml') as f:
    materials = yaml.safe_load(f)['materials']
    print('Aluminum' in materials)
"

# Verify API client is available
python3 -c "from shared.api.client_factory import create_api_client; print(create_api_client('grok'))"
```

### Frontmatter export failing?
```bash
# Verify Materials.yaml is valid YAML
python3 -c "import yaml; yaml.safe_load(open('materials/data/Materials.yaml'))"

# Check if voice enhancement was applied
python3 scripts/voice/enhance_materials_voice.py --validate-only
```

### Voice markers not present?
```bash
# Re-run voice enhancement
python3 scripts/voice/enhance_materials_voice.py --material "Aluminum"

# Check authenticity score
python3 scripts/voice/enhance_materials_voice.py --validate-only
```

---

## 📚 Additional Documentation

- **Complete Voice System**: `shared/voice/README.md`
- **Implementation Details**: `docs/updates/VOICE_POST_PROCESSING_COMPLETE.md`
- **Data Storage Policy**: `docs/data/DATA_STORAGE_POLICY.md`
- **Component Architecture**: `docs/COMPONENT_ARCHITECTURE.md`
- **Quick Reference**: `docs/QUICK_REFERENCE.md`

---

## ✅ Summary

The voice workflow is a clean 3-step process:

1. **Generate** → Save raw content to Materials.yaml
2. **Enhance** → Apply voice, OVERWRITE fields in Materials.yaml
3. **Export** → Combine Materials.yaml + Categories.yaml → frontmatter

Each step is independent, can be run separately, and maintains Materials.yaml as the single source of truth.
