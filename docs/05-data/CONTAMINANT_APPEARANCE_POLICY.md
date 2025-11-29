# Contaminant Visual Appearance Data Policy

**Status**: MANDATORY  
**Effective**: November 29, 2025 (Simplified Architecture)  
**Enforcement**: Automated tests in `tests/domains/materials/image/test_contamination_pattern_selector.py`

---

## Policy Statement

**All contaminant visual appearance data MUST be pre-populated in `Contaminants.yaml`.**

Image generation operations MUST NOT require live API calls to research how contamination appears on materials. All visual appearance data must be available locally in the database.

---

## Architecture (SIMPLIFIED - Nov 29, 2025)

### Single Source of Truth
**`ContaminationPatternSelector`** is the ONLY class for contamination data:
- Reads from `Contaminants.yaml` 
- **ZERO API calls** for contamination data
- Pattern selection based on `valid_materials` field
- Priority scoring for patterns with rich appearance data

```python
# Location: domains/materials/image/research/contamination_pattern_selector.py

from domains.materials.image.research.contamination_pattern_selector import (
    ContaminationPatternSelector,
    select_contamination_patterns  # Convenience function
)

# Usage
selector = ContaminationPatternSelector()
result = selector.get_patterns_for_image_gen("Aluminum", num_patterns=3)
# result['api_calls_made'] == 0  # ALWAYS zero
```

### Deprecated Components
The following are NO LONGER USED:
- ❌ `CategoryContaminationResearcher` (made API calls)
- ❌ `MaterialContaminationResearcher` (made API calls)  
- ❌ `ContaminantAppearanceLoader` (separate loader, unnecessary)

### Only Remaining API Call
**Shape Research** (optional):
- `MaterialShapeResearcher` - researches most common form of a material
- This is the ONLY external API call in image generation
- Can be disabled by not providing `GEMINI_API_KEY`

---

## Rationale

1. **Consistency**: Pre-populated data ensures consistent, reproducible image generation
2. **Reliability**: No runtime API dependencies for visual data (API failures won't block generation)
3. **Quality**: All appearance data can be reviewed and validated before use
4. **Speed**: No research delays during image generation
5. **Cost**: Eliminates API costs during image generation workflow
6. **Simplicity**: Single class, single data source, zero complexity

---

## Data Structure

Each contamination pattern in `Contaminants.yaml`:

```yaml
contamination_patterns:
  industrial-oil:
    name: "Industrial Oil & Grease"
    category: "organic-residue"
    valid_materials:  # Used for pattern selection
      - "metal"
      - "aluminum"
      - "stainless steel"
    visual_characteristics:
      appearance_on_materials:
        aluminum:
          # 7 Visual Fields
          description: "Full description of how oil appears on aluminum..."
          color_variations:
            - "#F5DEB3 'Wheat' (fresh, thin layer)"
            - "#D2B48C 'Tan' (aged, thicker)"
          texture_details: "Initially glossy and slick..."
          common_patterns: "Streaks, drips, pooling in low areas..."
          aged_appearance: "Fresh vs aged progression..."
          lighting_effects: "Glossy reflection, rainbow sheen..."
          thickness_range: "10-200 micrometers typically..."
          
          # 9 Distribution Fields (for realism)
          distribution_patterns: "Where contamination forms..."
          uniformity_assessment: "How even the coverage is..."
          concentration_variations: "Heavier in corners, edges..."
          typical_formations: "Pools, drips, films..."
          geometry_effects: "How surface shape affects distribution..."
          gravity_influence: "Dripping, pooling behavior..."
          coverage_ranges: "Sparse (<10%) to Heavy (60-85%)..."
          edge_center_behavior: "Accumulation at boundaries..."
          buildup_progression: "Time-based accumulation..."
```

---

## Pattern Selection Logic

`ContaminationPatternSelector.select_patterns()` uses:

1. **valid_materials filter** - Only patterns valid for the material
2. **Rich data bonus (+100 score)** - Patterns with appearance_on_materials data for this specific material
3. **Category priority bonus** - Patterns in CATEGORY_PRIORITIES for the material's category
4. **Top N selection** - Highest scoring patterns selected

```python
# Selection priority
scored_patterns.sort(reverse=True, key=lambda x: x[0])
selected = scored_patterns[:num_patterns]
```

---

## Coverage Status (Nov 29, 2025)

| Metric | Value |
|--------|-------|
| Total patterns | 100 |
| Patterns with material-specific data | 11 |
| Materials in database | 159 |
| Expected combinations | 15,900 |
| Current coverage | ~4% (652/15,900) |

### To Populate Missing Data
```bash
python3 scripts/research/batch_visual_appearance_research.py --all
```

---

## Enforcement

### Automated Tests (16 tests)
```bash
python3 -m pytest tests/domains/materials/image/test_contamination_pattern_selector.py -v
```

| Test | Purpose |
|------|---------|
| `test_zero_api_calls_made` | **CRITICAL**: Verifies no HTTP calls |
| `test_load_data_succeeds` | Data loads from YAML |
| `test_get_patterns_for_image_gen_format` | Output format correct |
| `test_visual_characteristics_content` | Required fields present |
| `test_data_format_compatibility` | Works with MaterialImageGenerator |

### CI Integration
Tests run on every PR to ensure:
- Zero API calls for contamination data
- Data loads correctly from YAML
- No breaking changes to output format

---

## Migration Path

If you encounter missing appearance data during image generation:

1. **DO NOT** add fallback API research to the generator
2. **DO** run the batch research script to populate missing data
3. **DO** commit the updated `Contaminants.yaml`
4. **DO** verify with tests before proceeding

```bash
# Example: Material "NewMaterial" missing appearance data
python3 scripts/research/batch_visual_appearance_research.py --material NewMaterial

# Verify
python3 -m pytest tests/domains/materials/image/test_contamination_pattern_selector.py -v

# Commit
git add data/contaminants/Contaminants.yaml
git commit -m "Add visual appearance data for NewMaterial"
```

---

## Exceptions

**None.** This policy has no exceptions. All visual appearance data must be pre-populated.

If you believe an exception is needed, open a discussion issue first.

---

## Related Documents

- `docs/08-development/HARDCODED_VALUE_POLICY.md` - No hardcoded defaults
- `docs/05-data/DATA_STORAGE_POLICY.md` - Data storage architecture
- `scripts/research/batch_visual_appearance_research.py` - Research tool
- `domains/materials/image/research/contamination_pattern_selector.py` - Pattern selector (single source)
