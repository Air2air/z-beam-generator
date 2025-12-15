# Contaminant Category & Subcategory Proposal - December 14, 2025

## Current State

### Materials Domain (GOOD ✅)
- **Consistent structure**: All materials have `category` and `subcategory`
- **Example**: Aluminum → `category: metal`, `subcategory: non-ferrous`
- **Coverage**: 159/159 materials properly categorized

### Contaminants Domain (INCOMPLETE ⚠️)
- **88/99 patterns** have NO category (marked as MISSING)
- **11/99 patterns** have category but NO subcategory
- **Current categories** (inconsistent):
  - oxidation: 2 patterns
  - contamination: 6 patterns  
  - aging: 1 pattern
  - biodegradation: 1 pattern
  - photodegradation: 1 pattern
  - MISSING: 88 patterns

---

## Proposed Structure

Mirror the materials domain structure with domain-appropriate categories:

```yaml
# MATERIALS PATTERN (current):
name: Aluminum
slug: aluminum
category: metal              # Primary classification
subcategory: non-ferrous     # Secondary classification

# CONTAMINANTS PATTERN (proposed):
name: Adhesive Residue / Tape Marks
slug: adhesive-residue-contamination
category: organic_residue    # Primary classification
subcategory: adhesive        # Secondary classification
```

---

## Proposed Categories (8 main categories)

### 1. **oxidation** (8 patterns)
Corrosion, tarnish, rust, oxidation layers

**Subcategories:**
- `ferrous` - Iron/steel rust and corrosion (3)
- `non-ferrous` - Aluminum, copper, bronze oxidation/patina (4)
- `battery` - Battery leakage corrosion (1)

**Examples:**
- rust-oxidation → `category: oxidation`, `subcategory: ferrous`
- aluminum-oxidation → `category: oxidation`, `subcategory: non-ferrous`
- copper-patina → `category: oxidation`, `subcategory: non-ferrous`

### 2. **organic_residue** (49 patterns)
Oils, greases, adhesives, polymers, organic compounds

**Subcategories:**
- `petroleum` - Oil, grease, fuel, tar (15)
- `adhesive` - Glue, tape, sealant residues (8)
- `polymer` - Plastic, rubber, Teflon (6)
- `biological_fluid` - Coolant, hydraulic fluid, cutting fluid (7)
- `wax` - Wax, polish, coating compounds (4)
- `marking` - Ink, graphite, marking compounds (3)
- `other` - Miscellaneous organic residues (6)

**Examples:**
- adhesive-residue → `category: organic_residue`, `subcategory: adhesive`
- industrial-oil → `category: organic_residue`, `subcategory: petroleum`
- plastic-residue → `category: organic_residue`, `subcategory: polymer`

### 3. **inorganic_coating** (10 patterns)
Paint, ceramic coatings, mineral deposits

**Subcategories:**
- `paint` - Paint, graffiti, powder coating (4)
- `ceramic` - Ceramic glazes and coatings (2)
- `mineral` - Scale, lime, efflorescence (3)
- `hazardous` - Asbestos, lead paint (1)

**Examples:**
- paint-residue → `category: inorganic_coating`, `subcategory: paint`
- ceramic-glaze → `category: inorganic_coating`, `subcategory: ceramic`
- lime-scale → `category: inorganic_coating`, `subcategory: mineral`

### 4. **metallic_coating** (9 patterns)
Electroplating, anodizing, metallic layers

**Subcategories:**
- `plating` - Electroplating (gold, silver, nickel, etc) (7)
- `anodizing` - Anodizing defects (1)
- `galvanizing` - Zinc galvanizing (1)

**Examples:**
- gold-plating → `category: metallic_coating`, `subcategory: plating`
- anodizing-defects → `category: metallic_coating`, `subcategory: anodizing`

### 5. **thermal_damage** (10 patterns)
Heat treatment scale, fire damage, thermal coatings

**Subcategories:**
- `scale` - Heat treatment, forging, annealing scale (4)
- `fire` - Fire damage, smoke damage, exhaust residue (3)
- `coating` - Thermal barrier coatings, heat-resistant coatings (3)

**Examples:**
- annealing-scale → `category: thermal_damage`, `subcategory: scale`
- fire-damage → `category: thermal_damage`, `subcategory: fire`

### 6. **biological** (6 patterns)
Mold, algae, biological growth, organic deposits

**Subcategories:**
- `growth` - Mold, mildew, algae, lichen (3)
- `deposit` - Pollen, insect residue, biological stains (3)

**Examples:**
- algae-growth → `category: biological`, `subcategory: growth`
- mold-mildew → `category: biological`, `subcategory: growth`
- pollen-deposit → `category: biological`, `subcategory: deposit`

### 7. **chemical_residue** (5 patterns)
Industrial chemicals, hazardous substances, process residues

**Subcategories:**
- `hazardous` - Radioactive, mercury, beryllium, uranium (4)
- `industrial` - Semiconductor, pharmaceutical, pesticide (1)

**Examples:**
- mercury-contamination → `category: chemical_residue`, `subcategory: hazardous`
- semiconductor-residue → `category: chemical_residue`, `subcategory: industrial`

### 8. **aging** (2 patterns)
Natural weathering, photodegradation, time-based degradation

**Subcategories:**
- `weathering` - Natural outdoor aging (1)
- `photodegradation` - UV damage, chalking (1)

**Examples:**
- natural-weathering → `category: aging`, `subcategory: weathering`
- uv-chalking → `category: aging`, `subcategory: photodegradation`

---

## Implementation Plan

### Phase 1: Update Source Data
File: `data/contaminants/Contaminants.yaml`

Add `category` and `subcategory` fields to all 99 patterns:

```yaml
contamination_patterns:
  adhesive-residue:
    name: "Adhesive Residue / Tape Marks"
    category: organic_residue
    subcategory: adhesive
    description: "..."
    # ... rest of fields
```

### Phase 2: Update Exporter
File: `export/contaminants/trivial_exporter.py`

Already exports these fields correctly:
```python
# Line 198-199 (already implemented)
frontmatter['category'] = pattern_data.get('category', 'contamination')
frontmatter['subcategory'] = pattern_data.get('subcategory', 'contamination')
```

**Current issue**: Falls back to `'contamination'` when missing
**Fix needed**: Fail-fast if category/subcategory missing (require explicit values)

### Phase 3: Re-export All Frontmatter
After updating source data, regenerate all 99 frontmatter files:
```bash
python3 -c "from export.contaminants.trivial_exporter import export_all_contaminants_frontmatter; export_all_contaminants_frontmatter()"
```

### Phase 4: Update Documentation
- Update schema.yaml with category definitions
- Update CONTAMINANT_SLUG_POLICY.md with category examples
- Update crosslinking tests if needed

---

## Benefits

### 1. **Consistency with Materials Domain**
- Same structural pattern across all domains
- Easier navigation and filtering
- Predictable data structure

### 2. **Better SEO & Navigation**
- Category-based URLs: `/contaminants/oxidation/rust-oxidation-contamination`
- Breadcrumbs: Home > Contaminants > Oxidation > Rust Oxidation
- Category landing pages

### 3. **Improved Filtering**
- Filter by category: "Show all oxidation-related contaminants"
- Filter by subcategory: "Show all petroleum-based residues"
- Material-contaminant compatibility rules

### 4. **Better User Experience**
- Logical groupings make finding contaminants easier
- Related contaminants appear together
- Category pages can explain removal strategies

---

## Example Before/After

### BEFORE (Current - Inconsistent)
```yaml
# adhesive-residue - HAS category but generic subcategory
category: contamination
subcategory: contamination

# rust-oxidation - HAS proper category, NO subcategory  
category: oxidation
subcategory: contamination

# industrial-oil - NO category, NO subcategory
category: contamination
subcategory: contamination
```

### AFTER (Proposed - Consistent)
```yaml
# adhesive-residue
category: organic_residue
subcategory: adhesive

# rust-oxidation
category: oxidation
subcategory: ferrous

# industrial-oil
category: organic_residue
subcategory: petroleum
```

---

## Next Steps

1. **Review & Approve** this categorization scheme
2. **Update source data** with categories/subcategories (bulk operation)
3. **Update exporter** to fail-fast on missing categories
4. **Re-export frontmatter** for all 99 patterns
5. **Update tests** to verify category structure
6. **Update documentation** with new category system

---

## Questions for User

1. **Approve category structure?** Are the 8 main categories appropriate?
2. **Subcategory granularity?** Too detailed or not detailed enough?
3. **URL structure?** Should category appear in URL? `/contaminants/{category}/{slug}`?
4. **Fallback strategy?** Fail-fast or use generic `contamination` category?
5. **Timeline?** Update all 99 patterns now or incrementally?

---

## Appendix: Full Pattern Mapping

See attached spreadsheet for complete mapping of all 99 patterns to proposed categories/subcategories.

**Category Distribution:**
- organic_residue: 49 patterns (49%)
- thermal_damage: 10 patterns (10%)
- inorganic_coating: 10 patterns (10%)
- metallic_coating: 9 patterns (9%)
- oxidation: 8 patterns (8%)
- biological: 6 patterns (6%)
- chemical_residue: 5 patterns (5%)
- aging: 2 patterns (2%)

**Total**: 99 patterns (100%)
