# Normalized Data Design Proposal

## Executive Summary

**Current Problem**: Data is duplicated across three systems with inconsistent structures:
- Materials.yaml: Simple flat properties (16 properties, 1,951 values)
- Categories.yaml: Complex nested ranges and metadata
- Frontmatter files: Over-engineered nested structure with redundant category ranges

**Proposed Solution**: Single source of truth with clear separation of concerns and zero duplication.

---

## 🎯 Design Principles

1. **Single Source of Truth**: Each piece of data stored exactly once
2. **Normalization**: Reference data instead of copying it
3. **Flat Structure**: Minimize nesting depth (max 2 levels)
4. **Type Safety**: Clear data types for validation
5. **Easy Querying**: Fast lookups without deep traversal
6. **Human Readable**: YAML remains editable by humans

---

## 📊 Current Structure Analysis

### Problems Identified

| File | Current Issues | Duplication |
|------|---------------|-------------|
| **Materials.yaml** | ✅ Good structure, but lacks metadata | None (this is clean) |
| **Categories.yaml** | 3,139 lines with excessive nesting, complex property groups | High - repeats material data |
| **Frontmatter** | 122 files × 399 lines = 48,678 lines, deeply nested properties with min/max/confidence/description per property | Extreme - copies Materials + Categories data |

**Total Duplication**: ~95% of frontmatter data is redundant (category ranges, property metadata)

---

## ✨ Proposed Normalized Structure

### 1. Materials.yaml (Source of Truth for Material Data)

```yaml
# Single source of truth for all material properties
# 122 materials × 16 properties = 1,951 values (100% complete)

metadata:
  version: "2.0.0"
  last_updated: "2025-10-15"
  total_materials: 122
  total_properties: 16
  completion: 100.0

# Property definitions (define once, reference everywhere)
property_definitions:
  density:
    unit: "g/cm³"
    description: "Material density at room temperature"
    category: "material_properties"
    display_order: 1
  
  thermalConductivity:
    unit: "W/(m·K)"
    description: "Thermal conductivity at 20°C"
    category: "energy_coupling"
    display_order: 2
  
  # ... (16 total properties defined once)

# Material data (flat, simple, fast)
materials:
  Copper:
    category: metal
    subcategory: non_ferrous
    properties:
      density: 8.96
      thermalConductivity: 401
      specificHeat: 385.0
      thermalExpansion: 16.5
      thermalDiffusivity: 9.7
      youngsModulus: 110
      tensileStrength: 210
      compressiveStrength: 369.0
      flexuralStrength: 345.0
      fractureToughness: 25.0
      hardness: 369.0
      laserAbsorption: 3.5
      laserReflectivity: 98.6
      thermalDestruction: 1358
      oxidationResistance: 400
      corrosionResistance: 550
  
  # ... (122 materials, flat structure)
```

**Benefits**:
- ✅ Property definitions centralized (no repetition)
- ✅ Flat structure (easy to query)
- ✅ Human readable
- ✅ 100% complete data
- ✅ Single source of truth

---

### 2. Categories.yaml (Aggregate Statistics Only)

```yaml
# Computed ranges and statistics from Materials.yaml
# This file is GENERATED, not manually edited

metadata:
  version: "2.0.0"
  generated_from: "Materials.yaml"
  generated_date: "2025-10-15"
  auto_generated: true  # Flag that this is computed
  
categories:
  metal:
    material_count: 45
    subcategories:
      - ferrous
      - non_ferrous
      - alloy
    
    # Property ranges (min/max computed from all metal materials)
    property_ranges:
      density:
        min: 0.53
        max: 22.6
        avg: 8.2
        median: 7.9
      
      thermalConductivity:
        min: 15
        max: 429
        avg: 95
        median: 80
      
      # ... (16 properties with ranges)
    
    # Recommended machine settings (category-level defaults)
    machine_settings:
      power:
        min: 20
        max: 200
        recommended: 100
        unit: "W"
      
      speed:
        min: 100
        max: 2000
        recommended: 500
        unit: "mm/s"
      
      frequency:
        min: 20
        max: 100
        recommended: 50
        unit: "kHz"
      
      # ... (6 machine settings)
  
  # ... (9 categories)
```

**Benefits**:
- ✅ Auto-generated from Materials.yaml (zero manual maintenance)
- ✅ Clear that it's computed data
- ✅ Fast lookup for category statistics
- ✅ Reduced from 3,139 lines to ~300 lines

**Script**: `scripts/generate_categories_from_materials.py` (auto-regenerate on Materials.yaml changes)

---

### 3. Frontmatter Files (Minimal, Reference-Based)

```yaml
# Minimal frontmatter - references Materials.yaml instead of duplicating

# === CORE IDENTIFIERS (4 fields) ===
material_id: "Copper"  # References Materials.yaml
title: "Copper Laser Cleaning"
slug: "copper-laser-cleaning"
category: "metal"  # Denormalized for fast filtering

# === CONTENT (3 fields) ===
description: "Laser cleaning parameters for Copper surfaces"
subtitle: "Copper's high thermal conductivity means it quickly spreads laser energy..."
content_sections:
  - introduction
  - applications
  - process_parameters
  - safety_considerations

# === AUTHOR (1 field) ===
author_id: 2  # References author database

# === REGULATORY (1 field) ===
regulatory_standards:
  - "FDA 21 CFR 1040.10"
  - "ANSI Z136.1"
  - "IEC 60825"
  - "OSHA 29 CFR 1926.95"

# === IMAGES (1 field) ===
images:
  hero: "/images/material/copper-laser-cleaning-hero.jpg"

# === ENVIRONMENTAL IMPACT (1 field) ===
environmental_impact:
  - benefit: "Chemical Waste Elimination"
    description: "Eliminates hazardous chemical waste streams"
    quantified: "Up to 100% reduction in chemical cleaning agents"

# === OUTCOME METRICS (1 field) ===
outcome_metrics:
  - metric: "Contaminant Removal Efficiency"
    target: "> 95%"
    measurement: "Visual inspection + surface analysis"

# === APPLICATIONS (1 field) ===
applications:
  - industry: "Electronics"
    use_case: "PCB cleaning"
  - industry: "Medical"
    use_case: "Surgical instrument restoration"

# === TOTAL: 10 sections ===
# All material properties pulled from Materials.yaml at runtime
# All category ranges pulled from Categories.yaml at runtime
```

**Benefits**:
- ✅ Reduced from 399 lines to ~80 lines (80% reduction)
- ✅ Zero property duplication
- ✅ References Materials.yaml via `material_id`
- ✅ Fast to update (change Materials.yaml once, affects all frontmatter)
- ✅ Human-readable unique content only

---

## 🔄 Data Flow

```
┌─────────────────┐
│ Materials.yaml  │ ← Single source of truth (manual edits)
│   122 materials │ ← 16 properties × 122 = 1,951 values
│   100% complete │
└────────┬────────┘
         │
         │ (auto-generate)
         ▼
┌─────────────────┐
│ Categories.yaml │ ← Computed ranges (auto-generated)
│  9 categories   │ ← Min/max/avg for each property
│  Auto-computed  │
└────────┬────────┘
         │
         │ (runtime reference)
         ▼
┌─────────────────┐
│ Frontmatter/    │ ← Minimal content (manual edits)
│ copper.yaml     │ ← References Materials.yaml
│ 80 lines        │ ← No property duplication
└─────────────────┘
```

---

## 📦 Implementation Plan

### Phase 1: Normalize Materials.yaml (2 hours)

**Script**: `scripts/normalize_materials.py`

```python
# 1. Extract property definitions from first material
# 2. Create property_definitions section
# 3. Flatten material properties (remove nesting)
# 4. Validate 100% completion
```

**Output**: Materials.yaml v2.0 (flat structure, property definitions)

---

### Phase 2: Auto-Generate Categories.yaml (1 hour)

**Script**: `scripts/generate_categories_from_materials.py`

```python
# 1. Read Materials.yaml
# 2. Group materials by category
# 3. Compute min/max/avg/median for each property
# 4. Generate category ranges
# 5. Add machine settings defaults
# 6. Mark as auto-generated
```

**Output**: Categories.yaml v2.0 (300 lines, auto-generated)

---

### Phase 3: Slim Down Frontmatter (3 hours)

**Script**: `scripts/normalize_frontmatter.py`

```python
# For each frontmatter file:
# 1. Extract unique content (subtitle, description, author, images)
# 2. Remove all property data (now in Materials.yaml)
# 3. Remove all category ranges (now in Categories.yaml)
# 4. Add material_id reference
# 5. Keep only 10 core sections
# 6. Reduce from 399 lines to ~80 lines
```

**Output**: 122 frontmatter files (80 lines each, 9,760 total lines vs 48,678)

**Savings**: 38,918 lines removed (80% reduction)

---

### Phase 4: Update Generation Pipeline (2 hours)

**Modify**: `components/frontmatter/generator.py`

```python
class FrontmatterGenerator:
    def generate(self, material_id):
        # 1. Load minimal frontmatter
        frontmatter = load_frontmatter(material_id)
        
        # 2. Inject material properties from Materials.yaml
        material = load_material(material_id)
        frontmatter['materialProperties'] = self._format_properties(material['properties'])
        
        # 3. Inject category ranges from Categories.yaml
        category = load_category(material['category'])
        frontmatter['categoryRanges'] = category['property_ranges']
        
        # 4. Inject machine settings
        frontmatter['machineSettings'] = category['machine_settings']
        
        # 5. Return complete frontmatter (computed at runtime)
        return frontmatter
```

**Benefits**:
- ✅ Frontmatter computed at runtime (zero duplication)
- ✅ Single update to Materials.yaml updates all 122 materials
- ✅ Fast (YAML load + dict merge)

---

## 📊 Impact Summary

### Before Normalization

| Component | Lines | Duplication | Maintenance |
|-----------|-------|-------------|-------------|
| Materials.yaml | 29,757 | Low | Manual |
| Categories.yaml | 3,139 | High | Manual |
| Frontmatter (122) | 48,678 | Extreme | Manual |
| **TOTAL** | **81,574** | **95%** | **High effort** |

### After Normalization

| Component | Lines | Duplication | Maintenance |
|-----------|-------|-------------|-------------|
| Materials.yaml | 3,500 | Zero | Manual |
| Categories.yaml | 300 | Zero | Auto-generated |
| Frontmatter (122) | 9,760 | Zero | Manual (unique content only) |
| **TOTAL** | **13,560** | **0%** | **Low effort** |

**Results**:
- ✅ **83% reduction** in total lines (81,574 → 13,560)
- ✅ **Zero duplication** (95% → 0%)
- ✅ **Single source of truth** (Materials.yaml)
- ✅ **Auto-generated ranges** (Categories.yaml)
- ✅ **Minimal frontmatter** (80 lines vs 399)

---

## 🚀 Migration Strategy

### Step 1: Backup Everything
```bash
python3 scripts/backup_all_data.py
# Creates timestamped backups of all YAML files
```

### Step 2: Normalize Materials.yaml
```bash
python3 scripts/normalize_materials.py
# Flattens structure, adds property_definitions
```

### Step 3: Generate Categories.yaml
```bash
python3 scripts/generate_categories_from_materials.py
# Computes ranges from Materials.yaml
```

### Step 4: Slim Frontmatter Files
```bash
python3 scripts/normalize_frontmatter.py
# Removes duplicated data, keeps unique content
```

### Step 5: Update Generation Pipeline
```bash
python3 scripts/update_frontmatter_generator.py
# Modifies generator to inject data at runtime
```

### Step 6: Validate Everything
```bash
python3 scripts/validate_normalized_data.py
# Ensures all 122 materials generate correctly
```

**Total Time**: 8 hours (automated scripts)

---

## 🎯 Key Benefits

### For AI Assistants
- ✅ **Easier to understand** (flat structure)
- ✅ **Faster to query** (no deep nesting)
- ✅ **Clear source of truth** (Materials.yaml)
- ✅ **Less context needed** (no duplication)

### For Developers
- ✅ **Single update point** (change Materials.yaml once)
- ✅ **Auto-generated ranges** (no manual calculation)
- ✅ **Smaller files** (faster git operations)
- ✅ **Type safety** (property_definitions)

### For System
- ✅ **83% less data** (81,574 → 13,560 lines)
- ✅ **Zero duplication** (95% → 0%)
- ✅ **Faster builds** (less YAML parsing)
- ✅ **Easier testing** (single source to validate)

---

## 🔒 Validation Rules

### Materials.yaml Validation
```python
# 1. All 122 materials present
# 2. All 16 properties present for each material
# 3. All values are numeric (not null)
# 4. Property definitions match usage
# 5. Category references valid
```

### Categories.yaml Validation
```python
# 1. Auto-generated flag present
# 2. Ranges computed correctly (min ≤ max)
# 3. All materials counted in categories
# 4. Machine settings have recommended values
# 5. Generated date matches Materials.yaml update
```

### Frontmatter Validation
```python
# 1. material_id references valid material
# 2. No property data present (should reference Materials.yaml)
# 3. Unique content only (subtitle, description, etc.)
# 4. Author_id valid
# 5. Images exist
```

---

## 📝 Property Definitions Reference

```yaml
property_definitions:
  # Material Properties
  density:
    unit: "g/cm³"
    category: "material_properties"
    description: "Material density at room temperature"
    
  # Energy Coupling Properties
  thermalConductivity:
    unit: "W/(m·K)"
    category: "energy_coupling"
    description: "Thermal conductivity at 20°C"
  
  specificHeat:
    unit: "J/(kg·K)"
    category: "energy_coupling"
    description: "Specific heat capacity"
  
  thermalExpansion:
    unit: "μm/(m·K)"
    category: "energy_coupling"
    description: "Coefficient of thermal expansion"
  
  thermalDiffusivity:
    unit: "mm²/s"
    category: "energy_coupling"
    description: "Thermal diffusivity"
  
  laserAbsorption:
    unit: "%"
    category: "energy_coupling"
    description: "Laser energy absorption rate"
  
  laserReflectivity:
    unit: "%"
    category: "energy_coupling"
    description: "Laser energy reflectivity"
  
  thermalDestruction:
    unit: "°C"
    category: "energy_coupling"
    description: "Thermal destruction threshold"
  
  # Structural Response Properties
  youngsModulus:
    unit: "GPa"
    category: "structural_response"
    description: "Young's modulus of elasticity"
  
  tensileStrength:
    unit: "MPa"
    category: "structural_response"
    description: "Ultimate tensile strength"
  
  compressiveStrength:
    unit: "MPa"
    category: "structural_response"
    description: "Compressive strength"
  
  flexuralStrength:
    unit: "MPa"
    category: "structural_response"
    description: "Flexural (bending) strength"
  
  fractureToughness:
    unit: "MPa√m"
    category: "structural_response"
    description: "Fracture toughness"
  
  hardness:
    unit: "HV"
    category: "structural_response"
    description: "Vickers hardness"
  
  # Resistance Properties
  oxidationResistance:
    unit: "°C"
    category: "material_properties"
    description: "Oxidation resistance temperature"
  
  corrosionResistance:
    unit: "°C"
    category: "material_properties"
    description: "Corrosion resistance temperature"
```

---

## ✅ Recommendation

**Proceed with normalization?**

This design:
- ✅ Eliminates 95% duplication
- ✅ Reduces total data by 83%
- ✅ Creates single source of truth
- ✅ Maintains human readability
- ✅ Simplifies AI assistant work
- ✅ Enables auto-generation
- ✅ Improves maintainability

**Estimated time**: 8 hours (fully automated)

**Risk**: Low (full backups, reversible changes)

**Benefit**: High (permanent improvement in data quality and maintainability)
