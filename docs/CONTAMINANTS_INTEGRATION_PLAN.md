# Contaminants Domain Integration Plan

**Date**: November 25, 2025  
**Status**: Domain Created, Integration Pending

---

## Overview

The Contaminants domain provides material-contamination compatibility validation to prevent physically impossible combinations (rust on plastics, wood rot on metals, etc.). This document outlines the integration strategy.

## Current Status

### ✅ Completed
- **Contaminants domain created**: `domains/contaminants/`
- **Schema populated**: 11 contamination patterns, 13 materials
- **Validation logic**: Elemental compatibility, context awareness
- **Library loader**: YAML parsing, pattern/material lookup
- **API ready**: `ContaminationValidator`, `ContaminationLibrary`

### 📊 Coverage Analysis
- **Materials.yaml**: 159 materials total
- **Contaminants DB**: 13 materials (8% coverage)
- **Missing**: 147 materials need contamination properties

---

## Integration Architecture

### Phase 1: Add Contamination Properties to Materials.yaml ⚡ **IMMEDIATE**

**Goal**: Associate each material with valid/prohibited contamination patterns

**Implementation**:

```yaml
# data/materials/Materials.yaml
materials:
  
  Aluminum:
    # ... existing properties ...
    
    # NEW: Contamination properties
    contamination:
      valid:
        - aluminum_oxidation
        - industrial_oil
        - environmental_dust
        - scale_buildup
        - paint_residue
        - chemical_stains
      prohibited:
        - rust_oxidation  # No iron
        - copper_patina   # No copper
        - wood_rot        # Not organic
        - uv_chalking     # Not polymer
      conditional:
        industrial_oil:
          context: "machinery_parts_only"
          note: "Only on machinery components"
```

**Benefits**:
- ✅ Single source of truth (Materials.yaml + Contaminants schema)
- ✅ Material-centric view (all properties in one place)
- ✅ Easy to maintain and extend
- ✅ Validation uses both sources

### Phase 2: Population Strategy

**Option A: Manual Population** (Recommended for accuracy)
- Add contamination properties material-by-material
- Verify chemistry/physics for each
- High accuracy, time-intensive
- **Estimate**: 2-3 hours for 159 materials

**Option B: Category-Based Auto-Population**
- Use material category to infer common patterns
- Generate initial contamination lists automatically
- Manual review for accuracy
- **Estimate**: 30 minutes + 1 hour review

**Option C: Hybrid Approach** (RECOMMENDED)
- Auto-populate based on categories
- Manual verification for common materials (top 50)
- Flag uncertain cases for review
- **Estimate**: 1 hour total

### Phase 3: Integration Points

#### 3.1 Image Generation Pre-Validation

**Location**: `domains/materials/image/generate.py`

**Hook Point**: After contamination research, before prompt building

```python
# Line ~160 in generate.py
from domains.contaminants import ContaminationValidator

validator = ContaminationValidator()

# Validate contamination patterns
result = validator.validate_generation_config(
    material_name=self.material_name,
    research_data=research_data,
    context=context
)

if not result.is_valid:
    # Log detailed errors
    for error in result.get_errors():
        logger.error(f"{error.message}\n{error.explanation}")
    
    # Option 1: Fail fast (recommended)
    raise GenerationError(f"Invalid contamination: {result.format_report()}")
    
    # Option 2: Filter and retry (graceful)
    research_data['contamination_patterns'] = [
        p for p in research_data['contamination_patterns']
        if validator.validate_patterns_for_material(
            self.material_name, [p['pattern_name']]
        ).is_valid
    ]
```

#### 3.2 Research Filtering

**Location**: `domains/materials/image/research.py`

**Hook Point**: After category research, before pattern selection

```python
# Filter patterns by material compatibility
from domains.contaminants import ContaminationValidator

validator = ContaminationValidator()
valid_patterns = []

for pattern in category_patterns:
    result = validator.validate_patterns_for_material(
        material_name=material_name,
        pattern_names=[pattern.name]
    )
    if result.is_valid:
        valid_patterns.append(pattern)

# Use only valid_patterns for selection
```

#### 3.3 Validation Enhancement

**Location**: `domains/materials/image/validator.py`

**Addition**: Check contamination appropriateness in validation prompt

```python
# Add to validation JSON schema
validation_schema = {
    "photorealism": "realistic/unrealistic",
    "material_accuracy": "correct/incorrect",
    "contamination_appropriate": "plausible/impossible",  # NEW
    "contamination_explanation": "Why is contamination valid/invalid"  # NEW
}
```

---

## Implementation Steps

### Step 1: Auto-Populate Materials.yaml (30 minutes)

Create script to add contamination properties based on categories:

```python
# scripts/tools/populate_contamination_properties.py

import yaml
from domains.contaminants import get_library

library = get_library()

with open('data/materials/Materials.yaml', 'r') as f:
    data = yaml.safe_load(f)

materials = data.get('materials', {})

for mat_name, mat_data in materials.items():
    # Check if already has contamination properties
    if 'contamination' in mat_data:
        continue
    
    # Try to get from contaminants DB
    mat_props = library.get_material(mat_name)
    if mat_props:
        mat_data['contamination'] = {
            'valid': mat_props.valid_contamination,
            'prohibited': mat_props.prohibited_contamination,
            'conditional': mat_props.conditional_contamination
        }
    else:
        # Infer from category
        category = mat_data.get('category', '')
        mat_data['contamination'] = infer_from_category(category, mat_name)
        mat_data['_contamination_needs_review'] = True

# Save updated Materials.yaml
with open('data/materials/Materials.yaml', 'w') as f:
    yaml.safe_dump(data, f, default_flow_style=False, sort_keys=False)
```

### Step 2: Review Top 50 Materials (30 minutes)

Manually verify contamination properties for most-used materials:
- Steel, Aluminum, Copper, Brass, Bronze, Titanium
- Acrylic, ABS, Polycarbonate, PEEK, Nylon
- Oak, Pine, Maple, Walnut
- Glass, Concrete, Granite, Marble

### Step 3: Integrate Validator into Image Generation (20 minutes)

Add validation hook in `generate.py`:
1. Import `ContaminationValidator`
2. Add validation after research
3. Filter or fail on incompatible patterns
4. Log detailed errors

### Step 4: Add Tests (15 minutes)

```python
# tests/test_contamination_integration.py

def test_steel_allows_rust():
    """Steel should allow rust oxidation"""
    validator = ContaminationValidator()
    result = validator.validate_patterns_for_material('Steel', ['rust_oxidation'])
    assert result.is_valid

def test_acrylic_rejects_rust():
    """Acrylic should reject rust oxidation"""
    validator = ContaminationValidator()
    result = validator.validate_patterns_for_material('Acrylic (PMMA)', ['rust_oxidation'])
    assert not result.is_valid
    assert any('iron' in e.explanation.lower() for e in result.get_errors())

def test_image_generation_validates_contamination():
    """Image generation should validate contamination patterns"""
    # Generate Acrylic image with rust contamination (should fail or filter)
    # ...
```

### Step 5: Regenerate Problem Materials (10 minutes)

Regenerate materials that had impossible contamination:
- Acrylic (PMMA) - had rust, should have UV chalking
- Other plastics that got rust/patina
- Woods that got metal oxidation

---

## Data Structure Decisions

### Should contamination properties be in Materials.yaml or Contaminants schema.yaml?

**RECOMMENDATION: Both** (dual-source architecture)

**Contaminants `schema.yaml`**:
- **Purpose**: Chemistry/physics knowledge base
- **Contains**: Pattern definitions, elemental requirements, general material categories
- **Scope**: Core contamination types, broad material classes
- **Maintenance**: Updated when adding new contamination types

**Materials.yaml**:
- **Purpose**: Material-specific overrides and context
- **Contains**: Per-material contamination lists, conditional rules, context notes
- **Scope**: All 159 materials with specific compatibility
- **Maintenance**: Updated when adding materials or refining compatibility

**Why Both?**:
1. **Flexibility**: Materials.yaml can override schema defaults
2. **Completeness**: Schema provides fallback for materials not in DB
3. **Maintainability**: Update one contamination pattern in schema, affects all materials
4. **Extensibility**: Add new materials to Materials.yaml without touching schema

**Lookup Priority**:
```python
# ContaminationValidator logic
def validate():
    # 1. Check Materials.yaml contamination properties (if exist)
    if material.has_contamination_properties():
        return validate_from_materials_yaml()
    
    # 2. Fall back to Contaminants schema.yaml
    return validate_from_schema()
```

---

## Migration Path

### Immediate (Today):
1. ✅ Contaminants domain created
2. ⏳ Auto-populate Materials.yaml with contamination properties
3. ⏳ Review top 50 materials for accuracy

### Short-term (This Week):
4. ⏳ Integrate validator into image generation
5. ⏳ Add pre-generation validation hook
6. ⏳ Add tests for integration
7. ⏳ Regenerate problem materials (Acrylic, etc.)

### Medium-term (Next Week):
8. ⏳ Enhance validation prompts (contamination appropriateness)
9. ⏳ Add contamination filtering to research system
10. ⏳ Complete review of all 159 materials

### Long-term (Future):
11. ⏳ Add contamination learning system (track success patterns)
12. ⏳ Extend schema with more contamination types
13. ⏳ Add context-aware validation (decorative vs industrial)

---

## Example: Acrylic (PMMA) Full Integration

**Before** (Current):
```yaml
# Materials.yaml
Aluminum:
  category: metals_non_ferrous
  # No contamination properties
```

**After** (Integrated):
```yaml
# Materials.yaml
Acrylic (PMMA):
  category: polymers_thermoplastic
  composition:
    elements: [C, H, O]
    compounds: [polymethyl_methacrylate]
  
  # NEW: Contamination properties
  contamination:
    valid:
      - uv_chalking           # Polymer photodegradation
      - chemical_stains       # Acid/solvent damage
      - environmental_dust    # Universal
      - adhesive_residue      # Label/tape marks
    
    prohibited:
      - rust_oxidation        # No iron content
      - copper_patina         # No copper content
      - aluminum_oxidation    # No aluminum
      - wood_rot              # Not organic wood
    
    conditional:
      industrial_oil:
        context: "machinery_parts_only"
        note: "Only if plastic is part of machinery (gears, housings, not decorative)"
```

**Image Generation**:
```python
# Research finds patterns: [rust_oxidation, uv_chalking, environmental_dust]

# Validator checks each:
validator.validate_patterns_for_material('Acrylic (PMMA)', ['rust_oxidation'])
# → ❌ ERROR: "Rust cannot form on Acrylic (PMMA) - requires iron content"

validator.validate_patterns_for_material('Acrylic (PMMA)', ['uv_chalking'])
# → ✅ VALID: "UV chalking is appropriate for polymers"

# Filter to valid patterns only: [uv_chalking, environmental_dust]
# Generate with validated patterns
```

---

## Success Metrics

### Coverage
- ✅ **Goal**: 100% of Materials.yaml (159/159 materials)
- 📊 **Current**: 8% (13/159 materials)
- 🎯 **Phase 1**: 75% (120/159 materials auto-populated)
- 🎯 **Phase 2**: 100% (159/159 materials reviewed)

### Accuracy
- 🎯 **Goal**: Zero impossible contamination patterns in generated images
- 📊 **Current**: Unknown (validation not integrated)
- 🎯 **Phase 1**: Validation active, logging errors
- 🎯 **Phase 2**: Zero validation errors

### Quality
- 🎯 **Goal**: 95%+ contamination appropriateness score in validation
- 📊 **Current**: Not measured
- 🎯 **Phase 1**: Add to validation schema
- 🎯 **Phase 2**: Track and optimize

---

## Questions for User

1. **Population approach**: Auto-populate all 159 materials, or manually add top 50 first?
2. **Validation strictness**: Fail fast (block generation), or filter and retry (graceful degradation)?
3. **Context handling**: Require context parameter (machinery/decorative), or infer from material properties?
4. **Priority**: Integrate validator into image generation today, or populate Materials.yaml first?

---

## Next Steps

**Immediate Action Required**:
1. Decide on population approach (auto vs manual)
2. Create population script
3. Integrate validator into image generation
4. Test with Acrylic (PMMA) regeneration

**User Decision Needed**:
- Should I proceed with auto-population script now?
- Should I integrate validator into generate.py before populating Materials.yaml?

