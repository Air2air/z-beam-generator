# Frontmatter Cleanup Required - January 7, 2026

## 🚨 Action Required

The `presentation_type` field has been removed from **source data** but still exists in **frontmatter files** (separate repository).

---

## Current Status

### ✅ Complete: Source Data (z-beam-generator)
- [x] Removed from data/materials/Materials.yaml (2 occurrences)
- [x] Removed from data/compounds/Compounds.yaml (5 occurrences)
- [x] Removed from data/settings/Settings.yaml (3 occurrences)
- [x] Schema updated (export/config/schema.yaml)
- [x] Tests created and passing
- [x] Documentation complete

### ⚠️ Incomplete: Frontmatter Files (z-beam repository)
- [ ] Frontmatter files NOT updated yet
- [ ] Located in: `../z-beam/frontmatter/`
- [ ] Estimated files affected: 20+ frontmatter YAML files

---

## Why Frontmatter Still Has presentation_type

**This is correct behavior per architecture**:
1. Frontmatter files are **generated output** (not source data)
2. Source data has been cleaned (presentation_type removed)
3. Frontmatter files need **regeneration** to pick up changes
4. Per "Frontmatter Source of Truth" policy: frontmatter = output only

**Analogy**: We fixed the source code, but the "compiled binaries" (frontmatter) need rebuilding.

---

## Required Actions

### Step 1: Navigate to z-beam Repository
```bash
cd /Users/todddunning/Desktop/Z-Beam/z-beam-generator
# Make sure you're in the generator repo first
```

### Step 2: Regenerate All Domain Frontmatter
```bash
# This will regenerate frontmatter from cleaned source data
python3 run.py --export --domain materials
python3 run.py --export --domain compounds
python3 run.py --export --domain settings
python3 run.py --export --domain contaminants
```

**Expected output**: 438 frontmatter files regenerated (153 materials + 98 contaminants + 34 compounds + 153 settings)

### Step 3: Verify Cleanup (In z-beam Repository)
```bash
# Navigate to z-beam repository
cd ../z-beam

# Check for presentation_type in frontmatter
grep -r "presentation_type:" frontmatter/ | wc -l
# Expected: 0 matches

# If matches found, list them
grep -r "presentation_type:" frontmatter/
```

### Step 4: Run Tests (In z-beam-generator)
```bash
cd ../z-beam-generator
pytest tests/test_presentation_type_removal.py -v
# Expected: 5/5 tests passing
```

---

## Affected Frontmatter Files (Known)

Based on frontend analysis, at minimum these files need regeneration:
- `acrylic-pmma-laser-cleaning.yaml` (lines 199, 222)
- `pahs-compound.yaml` (line 182)
- Likely 20+ additional files (full grep required)

---

## Technical Details

### Why Export Fixes This
```
Source Flow:
  data/materials/Materials.yaml (✅ cleaned)
    ↓ (export process)
  ../z-beam/frontmatter/materials/*.yaml (⚠️ needs regeneration)

Export reads from:
  1. data/materials/Materials.yaml (no presentation_type)
  2. export/config/schema.yaml (no presentation_type definition)
  3. Generates frontmatter using presentation field only

Result:
  ✅ Regenerated frontmatter will NOT have presentation_type
```

### What Gets Updated
```yaml
# BEFORE (old frontmatter - incorrect)
relationships:
  safety:
    regulatory_standards:
      presentation: card
      _section:
        sectionMetadata:
          presentation_type: card  # ← Will be removed

# AFTER (regenerated frontmatter - correct)
relationships:
  safety:
    regulatory_standards:
      presentation: card
      _section:
        sectionMetadata:
          notes: "Compliance requirements"
          # No presentation_type
```

---

## Verification Checklist

After regeneration:
- [ ] No `presentation_type` in frontmatter files (grep returns 0 matches)
- [ ] All tests passing (5/5 in test_presentation_type_removal.py)
- [ ] Frontend validation passes
- [ ] No visual regressions on website

---

## Time Estimate

- **Export regeneration**: ~2-5 minutes (438 files)
- **Verification**: ~1 minute
- **Total**: ~5-10 minutes

---

## Related Documents

- **Resolution analysis**: [COMPONENT_VS_PRESENTATION_TYPE_RESOLUTION_JAN7_2026.md](COMPONENT_VS_PRESENTATION_TYPE_RESOLUTION_JAN7_2026.md)
- **Status summary**: [OVERLAP_RESOLUTION_COMPLETE_JAN7_2026.md](OVERLAP_RESOLUTION_COMPLETE_JAN7_2026.md)
- **Terminology guide**: [docs/09-reference/GENERATION_VS_DISPLAY_TERMINOLOGY.md](docs/09-reference/GENERATION_VS_DISPLAY_TERMINOLOGY.md)
- **Tests**: [tests/test_presentation_type_removal.py](tests/test_presentation_type_removal.py)

---

**Created**: January 7, 2026  
**Status**: ⚠️ ACTION REQUIRED  
**Priority**: High (blocks frontend validation)
