# Contaminants Domain Documentation
**Version**: 2.0.0  
**Last Updated**: December 14, 2025  
**Status**: Production Ready

---

## Overview

The Contaminants domain manages all contamination pattern data, categorization, and frontmatter generation for the Z-Beam laser cleaning system. This documentation covers the complete categorization system, data structure, and implementation guidelines.

---

## Quick Reference

| Resource | Path | Purpose |
|----------|------|---------|
| **Source Data** | `data/contaminants/Contaminants.yaml` | Single source of truth for all contaminant patterns |
| **Schema** | `domains/contaminants/schema.yaml` | Data structure and validation rules |
| **Exporter** | `export/contaminants/trivial_exporter.py` | Generates frontmatter from source data |
| **Frontmatter** | `frontmatter/contaminants/*.yaml` | Generated files for website |
| **Tests** | `tests/test_contaminant_categories.py` | Category validation tests |
| **Policy** | `docs/05-data/CONTAMINANT_SLUG_POLICY.md` | Mandatory slug and category requirements |

---

## Categorization System

### 8 Main Categories

The contaminant categorization system uses **8 main categories** and **27 subcategories** for comprehensive organization:

#### 1. **oxidation** - Corrosion and Oxidation
Metal degradation through oxidation reactions.

**Subcategories** (3):
- `ferrous` - Iron and steel rust, red/brown oxidation
- `non-ferrous` - Copper patina, aluminum oxidation, bronze tarnish
- `general` - Mixed metal corrosion, unspecified oxidation

**Example Patterns**:
- `rust-oxidation` (ferrous)
- `copper-patina` (non-ferrous)
- `aluminum-oxidation` (non-ferrous)

---

#### 2. **organic_residue** - Oils, Greases, and Organic Materials
Carbon-based contaminants from biological or petroleum sources.

**Subcategories** (6):
- `hydrocarbons` - Motor oil, diesel, petroleum products
- `greases` - Lubricating grease, bearing grease
- `waxes` - Protective waxes, paraffin coatings
- `adhesives` - Glue residue, tape residue, bonding agents
- `polymers` - Plastic residues, rubber compounds
- `foodstuffs` - Food processing residues, organic matter

**Example Patterns**:
- `industrial-oil` (hydrocarbons)
- `grease-buildup` (greases)
- `adhesive-residue` (adhesives)

**Distribution**: Largest category (30 patterns, 31% of total)

---

#### 3. **inorganic_coating** - Mineral and Construction Materials
Non-metallic, non-organic coatings and deposits.

**Subcategories** (5):
- `mineral_deposits` - Limescale, calcium deposits, mineral buildup
- `concrete` - Concrete splatter, cement residue, mortar
- `paint` - Non-metallic paints, latex, acrylics
- `dust` - Industrial dust, powder coatings, particulates
- `silicates` - Glass residue, silica deposits

**Example Patterns**:
- `concrete-splatter` (concrete)
- `limestone-deposits` (mineral_deposits)
- `paint-coating` (paint)

**Distribution**: Second largest (17 patterns, 17% of total)

---

#### 4. **metallic_coating** - Metallic Layers and Plating
Applied metallic finishes and metal deposits.

**Subcategories** (4):
- `plating` - Electroplating (chrome, nickel, zinc)
- `paint` - Metallic paints, metal-flake finishes
- `coating` - Thermal spray coatings, metal deposits
- `general` - Unspecified metallic layers

**Example Patterns**:
- `brass-plating` (plating)
- `metallic-paint` (paint)
- `zinc-coating` (coating)

**Distribution**: 10 patterns (10% of total)

---

#### 5. **thermal_damage** - Heat-Related Degradation
Damage from high temperature exposure.

**Subcategories** (3):
- `discoloration` - Heat tints, temper colors, thermal oxidation
- `burn_marks` - Scorch marks, welding spatter, fire damage
- `charring` - Carbon deposits from combustion, char

**Example Patterns**:
- `heat-discoloration` (discoloration)
- `weld-spatter` (burn_marks)
- `fire-damage` (charring)

**Distribution**: 12 patterns (12% of total)

---

#### 6. **biological** - Organic Growth and Biofilms
Living organisms and biological contamination.

**Subcategories** (3):
- `mold` - Fungal growth, mildew, spores
- `algae` - Algae films, green growth
- `biofilm` - Bacterial films, slime layers

**Example Patterns**:
- `mold-growth` (mold)
- `algae-film` (algae)
- `bacterial-biofilm` (biofilm)

**Distribution**: 7 patterns (7% of total)

---

#### 7. **chemical_residue** - Chemical Process Contaminants
Residues from chemical treatments and industrial processes.

**Subcategories** (2):
- `industrial` - Etchants, solvents, process chemicals
- `treatment` - Anodizing residues, phosphate coatings, conversion coatings

**Example Patterns**:
- `chemical-stains` (industrial)
- `phosphate-coating` (treatment)
- `anodizing-residue` (treatment)

**Distribution**: 12 patterns (12% of total)

---

#### 8. **aging** - General Weathering and Degradation
Time-based degradation without specific contamination source.

**Subcategories** (1):
- `general` - Generic aging, weathering, surface degradation

**Example Patterns**:
- `weathered-surface` (general)

**Distribution**: 1 pattern (1% of total)

---

## Category Distribution

| Category | Count | Percentage | Top Subcategories |
|----------|-------|------------|-------------------|
| **organic_residue** | 30 | 31% | hydrocarbons (12), greases (8), adhesives (5) |
| **inorganic_coating** | 17 | 17% | mineral_deposits (7), concrete (5), paint (3) |
| **thermal_damage** | 12 | 12% | discoloration (6), burn_marks (4), charring (2) |
| **chemical_residue** | 12 | 12% | industrial (8), treatment (4) |
| **metallic_coating** | 10 | 10% | plating (5), paint (3), coating (2) |
| **oxidation** | 9 | 9% | ferrous (5), non-ferrous (3), general (1) |
| **biological** | 7 | 7% | mold (4), algae (2), biofilm (1) |
| **aging** | 1 | 1% | general (1) |
| **TOTAL** | **98** | **100%** | 27 subcategories |

---

## Data Structure

### Source Data Format
**File**: `data/contaminants/Contaminants.yaml`

```yaml
rust-oxidation:
  pattern_id: rust-oxidation
  name: Rust Oxidation
  category: oxidation              # REQUIRED: Main category
  subcategory: ferrous             # REQUIRED: Subcategory
  description: "Ferrous oxide formation..."
  visual_appearance:
    colors: ["reddish-brown", "orange-brown"]
    texture: "rough, flaky"
    thickness: "thin to moderate layers"
    # ... 16 appearance fields total
  laser_properties:
    removal_difficulty: "moderate"
    fluence_range: [2.5, 4.0]
  # ... other fields
```

### Required Fields

**Categorization** (MANDATORY):
- `category` - Must be one of 8 allowed categories
- `subcategory` - Must be valid for the specified category

**Identification**:
- `pattern_id` - Unique identifier (kebab-case)
- `name` - Human-readable name

**Content** (varies by pattern):
- `description` - Text description of contamination
- `visual_appearance` - Appearance characteristics
- `laser_properties` - Removal parameters
- `contexts` - Where contamination occurs

### Frontmatter Output Format
**Path**: `frontmatter/contaminants/{slug}-contamination.yaml`

```yaml
name: Rust Oxidation
slug: rust-oxidation-contamination    # Note: -contamination suffix
category: oxidation
subcategory: ferrous
description: "Ferrous oxide formation..."
visual_appearance: { ... }
laser_properties: { ... }
# ... other fields
```

---

## Implementation Guidelines

### Adding a New Contaminant

**Step 1**: Add to `data/contaminants/Contaminants.yaml`
```yaml
new-pattern-id:
  pattern_id: new-pattern-id
  name: New Pattern Name
  category: organic_residue        # Choose from 8 categories
  subcategory: hydrocarbons        # Choose valid subcategory
  description: "..."
  # ... other fields
```

**Step 2**: Validate category/subcategory
```bash
# Check schema for allowed values
cat domains/contaminants/schema.yaml | grep -A 30 "allowed_categories"
```

**Step 3**: Run exporter
```bash
python3 run.py --deploy contaminants
```

**Step 4**: Verify output
```bash
# Check frontmatter was created
ls frontmatter/contaminants/new-pattern-id-contamination.yaml

# Verify category/subcategory present
grep -E "(category|subcategory)" frontmatter/contaminants/new-pattern-id-contamination.yaml
```

**Step 5**: Run tests
```bash
pytest tests/test_contaminant_categories.py -v
```

### Fail-Fast Validation

The exporter enforces category requirements with **fail-fast validation**:

**File**: `export/contaminants/trivial_exporter.py` (lines 198-213)

```python
# Validate required categorization fields
if 'category' not in pattern or not pattern['category']:
    raise ValueError(
        f"Contamination pattern '{pattern_id}' missing required 'category' field. "
        f"All contaminants must have a category."
    )

if 'subcategory' not in pattern or not pattern['subcategory']:
    raise ValueError(
        f"Contamination pattern '{pattern_id}' missing required 'subcategory' field. "
        f"All contaminants must have a subcategory."
    )
```

**Result**: System will NOT export contaminants with missing categories. Export fails immediately with clear error message.

---

## Testing

### Comprehensive Test Suite
**File**: `tests/test_contaminant_categories.py`

**Test Classes** (6 total):

1. **TestSourceDataCategories** (4 tests)
   - Verifies all patterns have category/subcategory
   - Validates values against allowed lists
   - Checks category/subcategory combinations

2. **TestCategoryDistribution** (2 tests)
   - Validates expected pattern counts per category
   - Ensures all 8 categories are present

3. **TestQuestionablePatterns** (3 tests)
   - Verifies brass-plating → metallic_coating/plating
   - Verifies chrome-pitting → oxidation/non-ferrous
   - Verifies chemical-stains → chemical_residue/industrial

4. **TestFrontmatterCategories** (4 tests)
   - Validates frontmatter files have categories
   - Ensures frontmatter matches source data
   - Checks all 98 files present

5. **TestRemovedPatterns** (2 tests)
   - Verifies natural-weathering removed from source
   - Verifies natural-weathering removed from frontmatter

6. **TestFlatStructure** (2 tests)
   - Confirms no category subdirectories
   - Validates all files in root directory

### Running Tests

```bash
# Run all contaminant category tests
pytest tests/test_contaminant_categories.py -v

# Run specific test class
pytest tests/test_contaminant_categories.py::TestSourceDataCategories -v

# Run with coverage
pytest tests/test_contaminant_categories.py --cov=export.contaminants --cov-report=html
```

### Integration Tests
**File**: `tests/test_normalized_exports.py`

Validates category/subcategory presence in exported frontmatter:
```python
def test_contaminants_export():
    # ... load frontmatter ...
    has_category = 'category' in data
    has_subcategory = 'subcategory' in data
    
    assert has_category, "Contaminant missing category field"
    assert has_subcategory, "Contaminant missing subcategory field"
```

---

## URL Structure

### Slug Format
**All contaminant slugs MUST end with `-contamination` suffix.**

**Pattern**: `{pattern-id}-contamination`

**Examples**:
- `rust-oxidation` → `rust-oxidation-contamination`
- `industrial-oil` → `industrial-oil-contamination`
- `copper-patina` → `copper-patina-contamination`

### URL Path
**Flat structure** (no category subdirectories):

```
/contaminants/{slug}
```

**Examples**:
```
/contaminants/rust-oxidation-contamination
/contaminants/industrial-oil-contamination
/contaminants/adhesive-residue-contamination
```

### Rationale
- **SEO Clarity**: URLs explicitly indicate contamination content
- **Domain Separation**: Prevents slug conflicts with materials/settings
- **URL Semantics**: Self-documenting URL structure
- **Namespace**: Clear boundaries for future content types

---

## Schema Reference

### Schema Version
**Current**: 2.0.0 (December 14, 2025)

### Allowed Values

**Categories** (8):
```yaml
allowed_categories:
  - oxidation
  - organic_residue
  - inorganic_coating
  - metallic_coating
  - thermal_damage
  - biological
  - chemical_residue
  - aging
```

**Subcategories by Category** (27 total):
```yaml
allowed_subcategories:
  oxidation:
    - ferrous
    - non-ferrous
    - general
  organic_residue:
    - hydrocarbons
    - greases
    - waxes
    - adhesives
    - polymers
    - foodstuffs
  inorganic_coating:
    - mineral_deposits
    - concrete
    - paint
    - dust
    - silicates
  metallic_coating:
    - plating
    - paint
    - coating
    - general
  thermal_damage:
    - discoloration
    - burn_marks
    - charring
  biological:
    - mold
    - algae
    - biofilm
  chemical_residue:
    - industrial
    - treatment
  aging:
    - general
```

**Full schema**: `domains/contaminants/schema.yaml`

---

## Migration History

### Phase 1: Normalization (Dec 14, 2025)
- Fixed double suffix bug (`-contamination-contamination`)
- Fixed 3 edge cases with existing `-contamination` in pattern_id
- Enforced mandatory `-contamination` suffix
- 100% compliance achieved (98/98 patterns)

### Phase 2: Categorization (Dec 14, 2025)
- Implemented 8-category/27-subcategory system
- Moved 3 questionable patterns to correct categories:
  * brass-plating → metallic_coating/plating
  * chrome-pitting → oxidation/non-ferrous
  * chemical-stains → chemical_residue/industrial
- Removed natural-weathering pattern (ambiguous categorization)
- Added fail-fast validation to exporter
- Updated schema to version 2.0.0
- Created comprehensive test suite (17 tests)

### Phase 3: Flat Structure (Dec 14, 2025)
- Removed category subdirectories from URL structure
- All frontmatter files in flat `/contaminants/` directory
- Simplified navigation and SEO

---

## Related Documentation

### Policies
- **Slug Policy**: `docs/05-data/CONTAMINANT_SLUG_POLICY.md`
- **Data Architecture**: `docs/DATA_ARCHITECTURE.md`
- **Schema Validation**: `domains/contaminants/schema.yaml`

### Implementation
- **Exporter Code**: `export/contaminants/trivial_exporter.py`
- **Test Suite**: `tests/test_contaminant_categories.py`
- **Integration Tests**: `tests/test_normalized_exports.py`

### Reports
- **Completeness**: `CONTAMINANTS_COMPLETENESS_REPORT_DEC14_2025.md`
- **Exporter Implementation**: `CONTAMINANTS_EXPORTER_COMPLETE_DEC14_2025.md`
- **Categorization Analysis**: `MATERIALS_VS_CONTAMINANTS_ANALYSIS_DEC14_2025.md`

---

## Troubleshooting

### Common Issues

**Issue**: Export fails with "missing required 'category' field"  
**Solution**: Add category field to pattern in Contaminants.yaml

**Issue**: Export fails with "missing required 'subcategory' field"  
**Solution**: Add subcategory field to pattern in Contaminants.yaml

**Issue**: Invalid category value  
**Solution**: Use one of 8 allowed categories (see schema.yaml)

**Issue**: Invalid subcategory value  
**Solution**: Ensure subcategory is valid for the specified category (see schema.yaml)

**Issue**: Slug doesn't have `-contamination` suffix  
**Solution**: Exporter automatically adds suffix - don't add manually to pattern_id

**Issue**: Frontmatter file not created  
**Solution**: Check pattern_id in Contaminants.yaml matches expected format (kebab-case)

### Validation Commands

```bash
# Check source data has all categories
python3 -c "import yaml; data = yaml.safe_load(open('data/contaminants/Contaminants.yaml')); missing = [k for k, v in data.items() if 'category' not in v or 'subcategory' not in v]; print(f'Missing categories: {len(missing)}'); print(missing if missing else 'All patterns have categories ✅')"

# Count patterns by category
python3 -c "import yaml; from collections import Counter; data = yaml.safe_load(open('data/contaminants/Contaminants.yaml')); counts = Counter(v.get('category') for v in data.values()); print('Distribution:'); [print(f'  {k}: {v}') for k, v in counts.most_common()]"

# Verify frontmatter files
ls frontmatter/contaminants/*.yaml | wc -l  # Should be 98

# Check for category subdirectories (should be empty)
find frontmatter/contaminants -type d -mindepth 1

# Run validation tests
pytest tests/test_contaminant_categories.py -v
```

---

## Future Enhancements

### Category Landing Pages
- Create `/contaminants/category/{category}` pages
- Show all contaminants in category
- Display subcategory breakdown

### Category Filtering
- Add category filters to contaminant list pages
- Enable multi-category selection
- Show distribution charts

### Related Contaminants
- Suggest related contaminants based on category
- Cross-reference similar patterns
- Display "Other {category} contaminants" sections

### Analytics
- Track category-based search patterns
- Monitor popular contamination types
- Identify content gaps by category

---

## Appendix: Complete Pattern List

### By Category

**oxidation** (9 patterns):
- rust-oxidation (ferrous)
- steel-rust (ferrous)
- iron-oxidation (ferrous)
- ... (see Contaminants.yaml for complete list)

**organic_residue** (30 patterns):
- industrial-oil (hydrocarbons)
- motor-oil (hydrocarbons)
- grease-buildup (greases)
- ... (see Contaminants.yaml for complete list)

**inorganic_coating** (17 patterns):
- concrete-splatter (concrete)
- limestone-deposits (mineral_deposits)
- paint-coating (paint)
- ... (see Contaminants.yaml for complete list)

**metallic_coating** (10 patterns):
- brass-plating (plating)
- chrome-plating (plating)
- metallic-paint (paint)
- ... (see Contaminants.yaml for complete list)

**thermal_damage** (12 patterns):
- heat-discoloration (discoloration)
- weld-spatter (burn_marks)
- fire-damage (charring)
- ... (see Contaminants.yaml for complete list)

**biological** (7 patterns):
- mold-growth (mold)
- algae-film (algae)
- bacterial-biofilm (biofilm)
- ... (see Contaminants.yaml for complete list)

**chemical_residue** (12 patterns):
- chemical-stains (industrial)
- phosphate-coating (treatment)
- anodizing-residue (treatment)
- ... (see Contaminants.yaml for complete list)

**aging** (1 pattern):
- weathered-surface (general)

---

**Document Version**: 2.0.0  
**System Status**: Production Ready  
**Coverage**: 98/98 patterns (100%)  
**Last Verified**: December 14, 2025
