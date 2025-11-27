# Data Field Locations Guide

**Purpose**: Definitive guide to where each field lives in the data architecture  
**Audience**: AI assistants, developers debugging "field not found" issues  
**Last Updated**: November 27, 2025

---

## 🎯 Quick Lookup: "Where is X field?"

| Field Name | Location | Level | File |
|------------|----------|-------|------|
| `name` | Materials, Settings, Contaminants | Top-level | All YAML files |
| `category` | Materials, Settings | Top-level | Materials.yaml, MachineSettings.yaml |
| `subcategory` | Materials | Top-level | Materials.yaml |
| `title` | Materials, Settings | Top-level | Materials.yaml, MachineSettings.yaml |
| `material_description` | Materials | Top-level | Materials.yaml |
| `caption` | Materials, Contaminants | Top-level | Materials.yaml, Contaminants.yaml |
| `faq` | Materials, Contaminants | Top-level | Materials.yaml, Contaminants.yaml |
| `common_contaminants` | Materials | Top-level (cached) | Materials.yaml |
| `visual_appearance` | Contaminants | **NESTED** under patterns | Contaminants.yaml |
| `laser_properties` | Contaminants | **NESTED** under patterns | Contaminants.yaml |
| `valid_materials` | Contaminants | **NESTED** under patterns | Contaminants.yaml |

---

## 📂 File-by-File Field Map

### **Materials.yaml**

```yaml
materials:
  [material_name]:
    # === STRUCTURAL (always present) ===
    name: string                      # Display name
    category: string                  # Primary category (metal, ceramic, etc.)
    subcategory: string               # Specific type (ferrous, non-ferrous, etc.)
    title: string                     # SEO-friendly title
    
    # === AI-GENERATED CONTENT ===
    material_description: string      # 15-word description (formerly "subtitle")
    caption: object                   # Before/after image captions
    faq: [list]                       # FAQ questions/answers
    
    # === CACHED DATA (from other sources) ===
    common_contaminants: [list]       # Synced from Contaminants.yaml
    
    # === MACHINE SETTINGS (if present) ===
    power: {...}                      # Power range and unit
    speed: {...}                      # Speed range and unit
    frequency: {...}                  # Frequency range and unit
    # ... other settings ...
    
    # === METADATA ===
    author: int                       # Author ID (1-10)
```

**Key Points**:
- ✅ `material_description` replaced `subtitle` (Nov 22, 2025)
- ❌ `visual_appearance` does NOT exist here
- ❌ `distribution` does NOT exist here
- ✅ `common_contaminants` is CACHED (source: Contaminants.yaml)

---

### **Contaminants.yaml**

```yaml
contamination_patterns:
  [pattern_id]:
    # === CORE FIELDS ===
    name: string
    description: string
    valid_materials: [list]           # Which materials this can contaminate
    
    # === VISUAL APPEARANCE (10 patterns) ===
    visual_appearance:                 # ← NESTED, not top-level
      color_range: [list]              # Visual: Color variations
      texture: string                  # Visual: Surface texture
      thickness: string                # Visual: Layer thickness
    
    # === LASER INTERACTION ===
    laser_properties:
      absorption_characteristics: string
      removal_difficulty: string
      safety_considerations: string
    
    # === MATERIAL RESTRICTIONS ===
    prohibited_materials: [list]       # Materials that CAN'T have this
    
    # === AI-GENERATED CONTENT (10 patterns) ===
    caption: string
    faq: string
    title: string
    author: string
```

**Key Points**:
- ✅ `visual_appearance` is NESTED under contamination_patterns
- ❌ NOT at top level of contamination_patterns
- ✅ Describes how contamination LOOKS on surfaces
- ✅ Only 10/100 patterns have visual_appearance

---

### **MachineSettings.yaml**

```yaml
materials:
  [material_name]:
    # === CORE SETTINGS ===
    power: {...}
    speed: {...}
    frequency: {...}
    pulseWidth: {...}
    # ... ~14 total settings ...
    
    # === METADATA ===
    name: string
    category: string
    title: string
    settings_description: string      # Similar to material_description
```

**Key Points**:
- ✅ Uses `settings_description` (not material_description)
- ✅ 132/166 materials have settings (34 missing)
- ✅ All settings have min/max ranges

---

### **Categories.yaml**

```yaml
categories:
  [category_name]:
    # === CATEGORY METADATA ===
    name: string
    description: string
    
    # === PROPERTY RANGES (propagate to materials) ===
    properties:
      density:
        min: number
        max: number
        unit: string
      # ... other properties ...
```

**Key Points**:
- ✅ Defines property ranges at category level
- ✅ Materials inherit these ranges
- ✅ Null material ranges = use category range

---

## 🚨 Common "Field Not Found" Issues

### Issue 1: Looking for visual_appearance at wrong level

**❌ WRONG**:
```python
# Checking Materials.yaml
for material_name, material_data in materials['materials'].items():
    visual = material_data.get('visual_appearance')  # ❌ Doesn't exist here
```

**✅ CORRECT**:
```python
# Checking Contaminants.yaml at correct nesting level
for pattern_id, pattern_data in contaminants['contamination_patterns'].items():
    if 'visual_appearance' in pattern_data:
        visual = pattern_data['visual_appearance']  # ✅ Found!
```

---

### Issue 2: Completeness check reports 0% but data exists

**Problem**: Script checks top-level fields only

**❌ WRONG COMPLETENESS CHECK**:
```python
# Only checks top-level
materials_with_visual = sum(1 for m in materials['materials'].values() 
                            if 'visual_appearance' in m)
# Result: 0 (because it doesn't exist at this level)
```

**✅ CORRECT COMPLETENESS CHECK**:
```python
# Checks correct location
patterns_with_visual = sum(1 for p in contaminants['contamination_patterns'].values()
                           if 'visual_appearance' in p)
# Result: 10 (actual count)
```

---

### Issue 3: subtitle vs material_description confusion

**Timeline**:
- **Before Nov 22, 2025**: Field was called `subtitle`
- **After Nov 22, 2025**: Renamed to `material_description`
- **Nov 27, 2025**: All `subtitle` references removed from codebase

**❌ OLD CODE (will fail)**:
```python
subtitle = material_data.get('subtitle')  # ❌ Field doesn't exist anymore
```

**✅ NEW CODE (correct)**:
```python
description = material_data.get('material_description')  # ✅ Current field name
```

---

## 📊 Field Existence by File

### Fields that exist in Materials.yaml:
- ✅ name, category, subcategory, title
- ✅ material_description, caption, faq
- ✅ common_contaminants (cached)
- ✅ Machine settings (power, speed, etc.)
- ✅ author (metadata)

### Fields that DO NOT exist in Materials.yaml:
- ❌ subtitle (removed Nov 27, 2025)
- ❌ visual_appearance (exists in Contaminants.yaml only)
- ❌ distribution (exists in Contaminants.yaml only)
- ❌ laser_properties (exists in Contaminants.yaml only)

### Fields that exist in Contaminants.yaml:
- ✅ name, description, valid_materials
- ✅ visual_appearance (nested, 10 patterns)
- ✅ laser_properties (nested)
- ✅ caption, faq (10 patterns with AI content)
- ✅ prohibited_materials, composition

### Fields that DO NOT exist in Contaminants.yaml:
- ❌ category (at material level - exists for 10 patterns)
- ❌ subcategory
- ❌ machine settings
- ❌ common_contaminants (this is the SOURCE)

---

## 🔄 Data Flow Diagram

```
Contaminants.yaml                     Materials.yaml
└── contamination_patterns            └── materials
    └── [pattern_id]                      └── [material_name]
        ├── name                              ├── name
        ├── valid_materials ─────sync────────>├── common_contaminants
        ├── visual_appearance (nested)        ├── material_description
        │   ├── color_range                   ├── caption
        │   ├── texture                       └── faq
        │   └── thickness                     
        └── laser_properties
```

**Sync Direction**: Contaminants.yaml → Materials.yaml (one-way)  
**Cached Field**: `common_contaminants` in Materials.yaml is cached from `valid_materials` in Contaminants.yaml  
**Sync Script**: `scripts/sync/populate_material_contaminants.py`

---

## 💡 For AI Assistants

### Before reporting "field not found":
1. ✅ Check this guide for correct field location
2. ✅ Verify field name spelling (subtitle vs material_description)
3. ✅ Check nesting level (top-level vs nested under patterns)
4. ✅ Confirm file (Materials.yaml vs Contaminants.yaml)
5. ✅ Run live test to verify behavior matches documentation

### When writing completeness checks:
1. ✅ Use correct file for each field
2. ✅ Check correct nesting level
3. ✅ Account for cached fields (don't count as missing)
4. ✅ Separate "doesn't exist" from "exists but empty"

### When verifying implementation:
1. ✅ Write test that proves feature works
2. ✅ Measure actual success rate/coverage
3. ✅ Compare metrics to documentation claims
4. ✅ Update docs if metrics don't match

---

## 📚 Related Documentation

- **Contaminants Schema**: `docs/schemas/CONTAMINANTS_SCHEMA.md`
- **Materials Schema**: `docs/schemas/MATERIALS_SCHEMA.md` (to be created)
- **Data Architecture**: `docs/DATA_ARCHITECTURE.md`
- **Hybrid Architecture**: `HYBRID_CONTAMINATION_ARCHITECTURE.md`

---

## 🔧 Maintenance

**When adding new fields**:
1. Add to this guide immediately
2. Specify file, level (top/nested), and purpose
3. Update completeness checker if required
4. Add to schema documentation

**When removing fields**:
1. Update this guide
2. Document removal date and reason
3. Provide migration path if applicable
4. Check for cached/derived fields
