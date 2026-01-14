# Data Architecture Guide

**Purpose**: Complete data structure and architecture documentation  
**Audience**: AI assistants, developers, data architects  
**Last Updated**: December 20, 2025  
**Status**: Consolidated from 5 data architecture documents

---

## 🎯 Overview

Z-Beam Generator uses a **flattened YAML data structure** with **strict separation of concerns** between category-level ranges and material-specific values. The system follows a **zero null policy** for numerical properties and maintains a **single source of truth** for all data.

**Architecture Version**: 2.0 (Post-Flattening, October 2025)

---

## 📐 Core Architecture Principles

### 1. Single Source of Truth

```
Categories.yaml     →  Category-wide min/max ranges (comparison context)
      ↓
Materials.yaml      →  Material-specific values ONLY (individual data)
      ↓
Generator           →  Combines both sources during generation
      ↓
Frontmatter         →  OUTPUT ONLY - displays complete property data
```

**🔥 CRITICAL DATA STORAGE POLICY**:

- ✅ **Materials.yaml** - Single source of truth for all material data (READ/WRITE)
- ✅ **Categories.yaml** - Single source of truth for category ranges (READ/WRITE)
- ❌ **Frontmatter files** - OUTPUT ONLY, never data storage (WRITE ONLY)
- **Data Flow**: Materials.yaml → Frontmatter (one-way only)

**See**: `docs/05-data/DATA_STORAGE_POLICY.md` for complete policy.

### 2. Layer Separation (Generator vs Generated)

**Policy**: `GENERATOR_VS_GENERATED_CRITICAL.md`

```
┌─────────────────────────────────────────────────────────────┐
│ LAYER 1: SOURCE DATA (Single Source of Truth)               │
│ • data/materials/Materials.yaml                              │
│ • data/contaminants/Contaminants.yaml                        │
│ • data/associations/DomainAssociations.yaml                  │
│ FIX HERE: When data is wrong (missing values, ranges)       │
└──────────────────────┬───────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────┐
│ LAYER 2: EXPORT PROCESS (Transformation Logic)              │
│ • export/core/frontmatter_exporter.py (orchestration)          │
│ • export/config/*.yaml (domain configurations)               │
│ • export/enrichers/**/*.py (enrichment logic)                │
│ FIX HERE: When generation logic is wrong                    │
└──────────────────────┬───────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────┐
│ LAYER 3: FRONTMATTER FILES (Generated Output)               │
│ • ../z-beam/frontmatter/materials/*.yaml                     │
│ • ❌ NEVER EDIT DIRECTLY - These get regenerated            │
└─────────────────────────────────────────────────────────────┘
```

**CRITICAL RULE**: If frontmatter has an issue, fix the GENERATOR (Layer 2) or DATA (Layer 1), not the generated files. Next regeneration would overwrite manual edits.

### 3. Two-Category Properties System

**Policy**: `TWO_CATEGORY_SYSTEM.md`

Properties organized into TWO primary categories:

1. **laser_material_interaction** - How laser affects the material
   - Absorption coefficient, reflectivity, penetration depth, thermal properties
   
2. **material_characteristics** - Inherent material properties
   - Density, hardness, melting point, electrical/thermal properties

**Why This Matters**:
- Clear separation between laser-specific and general properties
- Consistent categorization across all 121 materials
- Generator uses category to organize frontmatter sections
- Schema validation enforces proper categorization

---

## 📁 File Structure

### Materials.yaml (Flattened Architecture)

**Version**: 2.0 (Post-Flattening, October 2025)  
**Location**: `data/materials/Materials.yaml`  
**Total Materials**: 121 across 9 categories

**Key Change**: Direct O(1) access - `materials['Aluminum']` instead of nested navigation.

```yaml
metadata:
  version: "2.0"
  lastUpdated: "2025-12-20"
  totalMaterials: 121

category_metadata:
  metal:
    article_type: material
    description: Metal materials for laser cleaning applications
  # ... 8 more categories

materials:
  Aluminum:
    category: metal
    title: Aluminum
    author:
      id: todd-dunning
      name: Todd Dunning
    properties:
      laser_material_interaction:
        absorptionCoefficient:
          value: 0.12
          unit: dimensionless
          source: "Laser Institute Handbook, 2023"
        # ... more laser interaction properties
      material_characteristics:
        density:
          value: 2700
          unit: kg/m³
          source: "Materials Database 2024"
        # ... more material characteristics
    description: "[Generated text from QualityEvaluatedGenerator]"
    micro: "[Generated text from QualityEvaluatedGenerator]"
    faq: "[Generated text from QualityEvaluatedGenerator]"
    settings_description: "[Generated text from QualityEvaluatedGenerator]"
  # ... 120 more materials
```

### Categories.yaml

**Location**: `data/categories/Categories.yaml`  
**Purpose**: Category-wide min/max ranges for numerical properties

```yaml
categories:
  metal:
    properties:
      laser_material_interaction:
        absorptionCoefficient:
          min: 0.05
          max: 0.95
          unit: dimensionless
        reflectivity:
          min: 0.20
          max: 0.98
          unit: dimensionless
        # ... more ranges
      material_characteristics:
        density:
          min: 534
          max: 22650
          unit: kg/m³
        # ... more ranges
  # ... 8 more categories
```

### Contaminants.yaml

**Location**: `data/contaminants/Contaminants.yaml`  
**Purpose**: Contamination pattern definitions with visual appearance data

**Policy**: `docs/05-data/CONTAMINANT_APPEARANCE_POLICY.md`

```yaml
contaminants:
  rust:
    name: "Rust (Iron Oxide)"
    pattern_id: "rust"
    category: oxidation
    commonality: 95
    appearance:
      colors: ["#8B4513", "#CD853F", "#A0522D"]
      texture: "Rough, flaky surface with uneven thickness"
      distribution: "Patches concentrated on edges"
      # ... 13 more appearance fields
    valid_materials:
      - Steel
      - Iron
      - Cast Iron
  # ... 99 more contamination patterns
```

**Coverage**: 100 contamination patterns × 159 materials = 15,900 expected combinations (~4% populated, growing via batch research)

---

## 🔢 Property Data Rules

### 1. Material-Specific Values ONLY in Materials.yaml

**CRITICAL RULE**: Min/max ranges exist **EXCLUSIVELY** in Categories.yaml, **NEVER** in Materials.yaml.

```yaml
# ✅ CORRECT in Materials.yaml
materials:
  Aluminum:
    properties:
      material_characteristics:
        density:
          value: 2700          # Single value only
          unit: kg/m³
          source: "Materials Database 2024"

# ❌ WRONG in Materials.yaml
materials:
  Aluminum:
    properties:
      material_characteristics:
        density:
          value: 2700
          min: 2600           # ❌ NEVER add min/max to materials
          max: 2800           # ❌ Ranges belong in Categories.yaml
```

### 2. Material Variance Handling

If a material property has an inherent range (e.g., alloy composition variations, grade differences):

- **Value field**: MUST contain the **averaged/consolidated single number**
- **Source field**: Document the range information for context
- **Min/max fields**: MUST NOT exist at material level

```yaml
# ✅ CORRECT: Document range in source, value is average
materials:
  "Stainless Steel 316":
    properties:
      material_characteristics:
        carbonContent:
          value: 0.05         # Average
          unit: "%"
          source: "ASTM A240: 0.03-0.08% carbon (average used: 0.055%)"
```

### 3. Property Validation Rule

**VITAL**: If a property is **NOT** defined in Categories.yaml for a given category, it **MUST NOT** be added to any material in that category in Materials.yaml.

**Ensures**:
- Consistency across all materials in a category
- Generator can properly orchestrate data (no orphaned properties)
- Schema validation works correctly
- No undefined property behavior in frontmatter generation

```yaml
# If Categories.yaml has:
categories:
  metal:
    properties:
      material_characteristics:
        density: { min: 534, max: 22650, unit: kg/m³ }
        hardness: { min: 20, max: 9000, unit: HV }

# Then Materials.yaml can ONLY use these properties:
materials:
  Aluminum:
    properties:
      material_characteristics:
        density: { value: 2700, unit: kg/m³ }
        hardness: { value: 167, unit: HV }
        # ❌ CANNOT add new property not in Categories.yaml
```

### 4. Qualitative Properties Rule

Properties with **non-numerical values** (text, enums, ratings) handled differently:

1. **No min/max ranges**: Qualitative properties have `min: null, max: null` (always)
2. **Move to characteristics**: If found in legacy Materials.yaml, move out of numerical sections
3. **Separate categorization**: Store in their own section to avoid mixing with numerical data
4. **Stored in frontmatter characteristics section** (not quantitative properties)

**Examples**:
```yaml
# ✅ CORRECT: Qualitative properties
materials:
  Aluminum:
    characteristics:
      crystallineStructure: "FCC"             # Text value
      oxidationResistance: "high"             # Enum value
      corrosionResistance: "excellent"        # Rating value

# ❌ WRONG: Mixing with numerical properties
materials:
  Aluminum:
    properties:
      material_characteristics:
        crystallineStructure: "FCC"           # ❌ Not numerical
```

### 5. Zero Null Policy for Numerical Properties

**ZERO NULL POLICY**: All numerical material properties **MUST** have min/max ranges.

If ranges don't exist in Categories.yaml:
- Add category ranges through AI research, OR
- Calculate from sibling materials in the same category

**NO EXCEPTIONS** - All numerical properties must have non-null min/max ranges.

**Achievement**: Qualitative properties omit min/max fields entirely, achieving zero null values system-wide.

---

## 🔍 Property Data Metric Format

**Policy**: `PROPERTY_DATA_METRIC_FORMAT.md`

All numerical properties follow consistent format:

```yaml
propertyName:
  value: 2700                    # Required: numerical value
  unit: kg/m³                    # Required: unit of measurement
  source: "Database Name 2024"   # Recommended: data source citation
  # NO min/max at material level (belongs in Categories.yaml)
```

**Units Standardization**:
- Temperature: K (Kelvin)
- Density: kg/m³
- Energy: J/mol
- Thermal conductivity: W/(m·K)
- Electrical resistivity: Ω·m
- Pressure: Pa

**Source Citation**:
- Include publication year
- Use recognized databases (MatWeb, ASM, CRC Handbook)
- For AI research: "Perplexity AI Research 2024"

---

## 🔄 Data Access Patterns

### 1. Direct Material Access (O(1))

```python
# ✅ CORRECT: Flattened structure
material_data = materials['Aluminum']
density = material_data['properties']['material_characteristics']['density']['value']

# ❌ WRONG: Old nested structure (removed Oct 2025)
material_data = materials['metal']['items'][0]  # No longer valid
```

### 2. Category Range Lookup

```python
# Load category ranges
category_ranges = categories['metal']['properties']['material_characteristics']['density']
min_density = category_ranges['min']  # 534
max_density = category_ranges['max']  # 22650

# Load material value
material_density = materials['Aluminum']['properties']['material_characteristics']['density']['value']  # 2700

# Calculate position in range
position = (material_density - min_density) / (max_density - min_density)  # 0.098 (9.8% through range)
```

### 3. Property Iteration

```python
# Iterate all laser interaction properties for a material
for prop_name, prop_data in materials['Aluminum']['properties']['laser_material_interaction'].items():
    value = prop_data['value']
    unit = prop_data['unit']
    
    # Get category range
    category_range = categories['metal']['properties']['laser_material_interaction'][prop_name]
    min_val = category_range['min']
    max_val = category_range['max']
```

---

## ✅ Data Validation

### Schema Validation

**Tool**: `shared/validation/schema_validator.py`

```python
from shared.validation import SchemaValidator

validator = SchemaValidator()
is_valid, errors = validator.validate_material('Aluminum')

if not is_valid:
    for error in errors:
        print(f"Validation error: {error}")
```

**Checks**:
- All required fields present
- Property values within category ranges (optional)
- Units match expected format
- No min/max at material level
- All properties exist in category definition

### Completeness Checking

```bash
# Check data completeness
python3 run.py --data-completeness-report

# View data gaps and research priorities
python3 run.py --data-gaps
```

**Enforcement**: 
- Automatic inline validation during generation (strict mode enabled by default)
- Generation fails fast if data incomplete
- Prompts research commands when gaps detected

---

## 📊 Current Status (December 2025)

### Materials.yaml
- **Total materials**: 121
- **Categories**: 9 (metal, polymer, ceramic, composite, wood, stone, fabric, glass, other)
- **Property completeness**: 93.5% (1,975/2,240 properties)
- **Missing**: 265 property values (Priority: 5 properties = 96% of gaps)

### Categories.yaml
- **Category definitions**: 9 complete
- **Property ranges**: All numerical properties have min/max
- **Qualitative properties**: Properly excluded from ranges

### Contaminants.yaml
- **Contamination patterns**: 100
- **Visual appearance data**: ~4% complete (652/15,900 combinations)
- **Coverage**: Growing via batch research (`scripts/research/batch_visual_appearance_research.py`)

---

## 🚀 Adding New Data

### Add New Material

1. Add to Materials.yaml under `materials:` section
2. Assign to existing category
3. Provide all required properties from category definition
4. Single values only (no min/max)
5. Include source citations
6. Run validation: `python3 run.py --validate-material "MaterialName"`

### Add New Property

1. First add to Categories.yaml (define min/max range)
2. Then add to all materials in that category
3. Ensure consistent unit across all materials
4. Update schema validator if new field structure
5. Run full validation: `pytest tests/test_schema_validation.py`

### Add Contamination Pattern

1. Add to Contaminants.yaml under `contaminants:` section
2. Provide appearance data (16 fields if Format B, basic if Format A)
3. Define valid_materials list (specific materials or "ALL")
4. Assign category (oxidation, contamination, aging)
5. Set commonality score (0-100)

---

## 📚 Related Documentation

### Essential Reading
- **Data Storage Policy**: `docs/05-data/DATA_STORAGE_POLICY.md` - Complete storage rules
- **Contaminant Appearance Policy**: `docs/05-data/CONTAMINANT_APPEARANCE_POLICY.md` - Contamination data rules
- **Generator vs Generated**: `GENERATOR_VS_GENERATED_CRITICAL.md` - Layer separation
- **Property Data Format**: (Consolidated into this document)
- **Two-Category System**: (Consolidated into this document)
- **Data Separation**: (Consolidated into this document)

### Quick References
- **Quick Reference**: `docs/05-data/DATA_ARCHITECTURE_QUICK_REF.md` - Fast lookup for common patterns
- **System Requirements**: `system-requirements.md` - Overall system design
- **Export Architecture**: `EXPORT_SYSTEM_ARCHITECTURE.md` - How data becomes frontmatter

---

**Last Updated**: December 20, 2025  
**Consolidated From**:
- DATA_ARCHITECTURE.md (890 lines)
- DATA_STRUCTURE.md (521 lines)
- DATA_ARCHITECTURE_SEPARATION.md (225 lines)
- PROPERTY_DATA_METRIC_FORMAT.md (427 lines)
- TWO_CATEGORY_SYSTEM.md (342 lines)

**Total**: 2,405 lines → 580 lines (76% reduction, maintained essential information)
