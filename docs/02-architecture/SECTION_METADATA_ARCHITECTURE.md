# Section Metadata Architecture

**Date**: January 15, 2026  
**Status**: ✅ MANDATORY POLICY  
**Scope**: All domains (materials, contaminants, compounds, settings)

---

## 🎯 Core Principle

**ALL section metadata MUST be defined in source data files (Layer 1) using normalized `_section` structure.**

Frontmatter files are generated output - never edit them directly.

---

## 📐 Three-Layer Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│ LAYER 1: SOURCE DATA (Materials.yaml, Contaminants.yaml, etc.) │
│ • Define _section metadata HERE                                 │
│ • Single source of truth                                        │
│ • FIX HERE: When section metadata is wrong                      │
└──────────────────────────┬──────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────────┐
│ LAYER 2: EXPORT LOGIC (export/core/, export/generation/)       │
│ • Reads _section from source data                               │
│ • Transforms for frontmatter output                             │
│ • FIX HERE: When export logic is wrong                          │
└──────────────────────────┬──────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────────┐
│ LAYER 3: FRONTMATTER OUTPUT (../z-beam/frontmatter/*.yaml)     │
│ • Generated files (DO NOT EDIT)                                 │
│ • Regenerated on every --export                                 │
│ • ⛔ NEVER EDIT THESE FILES DIRECTLY                            │
└─────────────────────────────────────────────────────────────────┘
```

---

## 📋 Normalized _section Structure

### Required Format (MANDATORY)

```yaml
sectionName:
  _section:
    sectionTitle: Human-Readable Title
    sectionDescription: Brief description of what this section contains
    sectionMetadata: Developer-facing text describing the function of this section
    icon: lucide-icon-name
    order: 50
    variant: default
  # Section content follows
  items:
    - ...
```

### ❌ DEPRECATED Formats (DO NOT USE)

```yaml
# ❌ WRONG: title/description as siblings
sectionName:
  title: Title
  description: Description
  _section:
    icon: wrench
    order: 50
  
# ❌ WRONG: _metadata instead of _section
sectionName:
  title: Title
  _metadata:
    icon: wrench
    order: 50
    generatedAt: '2026-01-14T08:26:41.000Z'

# ❌ WRONG: Only _section without sectionTitle/sectionDescription
sectionName:
  _section:
    icon: wrench
    order: 50
```

---

## 🔧 Field Specifications

### sectionTitle
- **Type**: String
- **Required**: Yes
- **Purpose**: Displayed as section heading in UI
- **Format**: Title Case, human-readable
- **Example**: `"Aluminum's Distinctive Traits"`, `"Similar Non-Ferrous Metals"`

### sectionDescription
- **Type**: String (can be multi-line)
- **Required**: Yes
- **Purpose**: Brief explanation of section content
- **Format**: 1-2 sentences, plain text
- **Example**: `"Physical properties that define aluminum's behavior during laser cleaning processes"`

### sectionMetadata
- **Type**: String
- **Required**: Yes
- **Purpose**: Developer-facing text that explains the function of the whole section
- **Format**: 1 sentence, implementation-focused
- **Example**: `"Developer purpose: defines how to generate material-characteristics coverage for this section."`

### icon
- **Type**: String
- **Required**: Yes
- **Values**: Lucide icon names (wrench, zap, layers, droplet, shield-check, briefcase, help-circle)
- **Purpose**: Visual indicator for section type
- **Default**: Use domain-appropriate icon

### order
- **Type**: Integer
- **Required**: Yes
- **Purpose**: Controls display sequence (lower = earlier)
- **Range**: 0-200
- **Common values**:
  - 50-60: Property sections
  - 70-80: Relationship sections
  - 90-110: Reference sections

### variant
- **Type**: String
- **Required**: Yes
- **Values**: `default`, `compact`, `expanded`
- **Purpose**: Controls section rendering style
- **Default**: `default`

---

## 📦 Domain-Specific Implementations

### Materials Domain

**Source**: `data/materials/Materials.yaml`

```yaml
aluminum-laser-cleaning:
  properties:
    materialCharacteristics:
      _section:
        sectionTitle: Aluminum's Distinctive Traits
        sectionDescription: Physical properties that define aluminum's behavior during laser cleaning processes
        icon: wrench
        order: 50
        variant: default
      description: 'When working with aluminum...'
      # Property data follows
      density:
        value: 2.70
        # ...
    
    laserMaterialInteraction:
      _section:
        sectionTitle: Aluminum Laser Interaction Dynamics
        sectionDescription: How laser energy interacts with aluminum surfaces during cleaning operations
        icon: zap
        order: 60
        variant: default
      description: 'Laser energy interacts with aluminum...'
      # Property data follows
  
  relationships:
    discovery:
      relatedMaterials:
        _section:
          sectionTitle: Similar Non-Ferrous Metals
          sectionDescription: Other lightweight metals with comparable laser cleaning characteristics
          icon: layers
          order: 72
          variant: default
        # Items array
    
    interactions:
      contaminatedBy:
        _section:
          sectionTitle: Common Contaminants
          sectionDescription: Aluminum surfaces attract oxides, oils, and industrial residues
          icon: droplet
          order: 10
          variant: default
        items:
          - id: aluminum-oxidation-contamination
            # ...
    
    operational:
      industryApplications:
        _section:
          sectionTitle: Industry Applications
          sectionDescription: Aluminum's lightweight strength makes it essential across industries
          icon: briefcase
          order: 40
          variant: default
        items:
          - id: aerospace
            # ...
    
    safety:
      regulatoryStandards:
        _section:
          sectionTitle: Regulatory Standards
          sectionDescription: Aluminum laser cleaning operations must comply with OSHA safety protocols
          icon: shield-check
          order: 20
          variant: default
        items:
          - name: FDA
            # ...
  
  faq:
    _section:
      sectionTitle: Aluminum Laser Cleaning FAQ
      sectionDescription: Expert answers to common questions about laser cleaning aluminum surfaces
      icon: help-circle
      order: 100
      variant: default
    items:
      - question: What safety considerations...
        answer: Professionals often deal with...
```

---

## 🚫 Migration: Removing Legacy Formats

### Step 1: Identify Legacy Patterns

```bash
# Find title/description siblings
grep -n "        title:" data/materials/Materials.yaml

# Find _metadata blocks
grep -n "        _metadata:" data/materials/Materials.yaml
```

### Step 2: Normalize to _section

```yaml
# BEFORE (legacy)
materialCharacteristics:
  title: Aluminum's Distinctive Traits
  sectionDescription: Physical properties...
  _section:
    icon: wrench
    order: 50
    variant: default
  description: 'When working with aluminum...'
  _metadata:
    icon: wrench
    order: 70
    generatedAt: '2026-01-14T08:26:41.000Z'

# AFTER (normalized)
materialCharacteristics:
  _section:
    sectionTitle: Aluminum's Distinctive Traits
    sectionDescription: Physical properties...
    icon: wrench
    order: 50
    variant: default
  description: 'When working with aluminum...'
```

### Step 3: Remove Deprecated Fields

- ❌ Remove `title:` (move to `_section.sectionTitle`)
- ❌ Remove `_metadata:` blocks entirely
- ❌ Remove `generatedAt` timestamps (not needed)
- ✅ Keep `description:` for paragraph content (separate from sectionDescription)

### Step 4: Regenerate Frontmatter

```bash
# Regenerate single material
python3 run.py --export --domain materials --item aluminum-laser-cleaning

# Regenerate all materials
python3 run.py --export --domain materials
```

---

## ✅ Verification Checklist

After normalizing source data:

- [ ] **No `title:` fields** at section level (only `sectionTitle` inside `_section`)
- [ ] **No `_metadata:` blocks** anywhere (replaced by `_section`)
- [ ] **All sections have `_section`** with 5 required fields
- [ ] **Export succeeds** without errors
- [ ] **Frontmatter contains section metadata** correctly
- [ ] **UI displays custom titles** when viewing on localhost
- [ ] **No console errors** in browser

---

## 🔍 Common Mistakes & Fixes

### Mistake 1: Editing Frontmatter Directly

❌ **WRONG**:
```bash
# Editing generated output
vim ../z-beam/frontmatter/materials/aluminum-laser-cleaning.yaml
```

✅ **CORRECT**:
```bash
# Edit source data
vim data/materials/Materials.yaml

# Then regenerate
python3 run.py --export --domain materials --item aluminum-laser-cleaning
```

### Mistake 2: Using title Instead of sectionTitle

❌ **WRONG**:
```yaml
_section:
  title: My Section  # Wrong field name
  icon: wrench
```

✅ **CORRECT**:
```yaml
_section:
  sectionTitle: My Section
  sectionDescription: Brief description
  icon: wrench
  order: 50
  variant: default
```

### Mistake 3: Missing Required Fields

❌ **WRONG**:
```yaml
_section:
  sectionTitle: My Section
  icon: wrench
  # Missing sectionDescription, order, variant
```

✅ **CORRECT**:
```yaml
_section:
  sectionTitle: My Section
  sectionDescription: Complete description here
  icon: wrench
  order: 50
  variant: default
```

### Mistake 4: Mixing Legacy and New Formats

❌ **WRONG**:
```yaml
materialCharacteristics:
  title: Old Format  # Legacy field
  _section:
    sectionTitle: New Format  # Conflict!
    icon: wrench
```

✅ **CORRECT**:
```yaml
materialCharacteristics:
  _section:
    sectionTitle: Consistent Format
    sectionDescription: Description here
    icon: wrench
    order: 50
    variant: default
```

---

## 📊 Progress Tracking

### Materials Domain Status (as of Jan 15, 2026)

| Material | materialCharacteristics | laserMaterialInteraction | relatedMaterials | FAQ | Status |
|----------|------------------------|-------------------------|------------------|-----|--------|
| Aluminum | ✅ Normalized | ✅ Normalized | ✅ Normalized | ⏳ Pending | 75% |
| Steel | ⏳ Has `_metadata` | ⏳ Has `_metadata` | ⏳ Has `_metadata` | ⏳ Pending | 0% |
| Others | ❓ Unknown | ❓ Unknown | ❓ Unknown | ⏳ Pending | 0% |

**Target**: 100% normalized across all 153 materials

---

## 🔄 Bulk Normalization Script

For normalizing all materials at once:

```python
# scripts/tools/normalize_section_metadata.py

import yaml
import re
from pathlib import Path

def normalize_section(section_data, section_name):
    """Normalize legacy format to _section structure"""
    
    # Extract fields
    title = section_data.get('title')
    description = section_data.get('sectionDescription')
    
    # Get icon/order from _section or _metadata
    icon = None
    order = None
    if '_section' in section_data:
        icon = section_data['_section'].get('icon')
        order = section_data['_section'].get('order')
    if '_metadata' in section_data:
        icon = icon or section_data['_metadata'].get('icon')
        order = order or section_data['_metadata'].get('order')
    
    # Create normalized structure
    normalized = {
        '_section': {
            'sectionTitle': title,
            'sectionDescription': description,
            'icon': icon,
            'order': order,
            'variant': 'default'
        }
    }
    
    # Copy remaining fields (excluding legacy ones)
    for key, value in section_data.items():
        if key not in ['title', 'sectionDescription', '_section', '_metadata']:
            normalized[key] = value
    
    return normalized

# Usage
with open('data/materials/Materials.yaml', 'r') as f:
    data = yaml.safe_load(f)

for material_key, material_data in data['materials'].items():
    if 'properties' in material_data:
        for prop_key in ['materialCharacteristics', 'laserMaterialInteraction']:
            if prop_key in material_data['properties']:
                material_data['properties'][prop_key] = normalize_section(
                    material_data['properties'][prop_key],
                    prop_key
                )

with open('data/materials/Materials.yaml', 'w') as f:
    yaml.dump(data, f, default_flow_style=False, sort_keys=False)
```

---

## 🎯 Implementation Priority

### Phase 1: Core Sections (High Priority)
1. ✅ materialCharacteristics (aluminum done)
2. ✅ laserMaterialInteraction (aluminum done)
3. ✅ relatedMaterials (aluminum done)
4. ⏳ FAQ (all materials need restructuring)

### Phase 2: Relationship Sections (Medium Priority)
5. ✅ contaminatedBy (aluminum has `_section`)
6. ✅ industryApplications (aluminum has `_section`)
7. ✅ regulatoryStandards (aluminum has `_section`)

### Phase 3: Bulk Migration (Low Priority)
8. ⏳ All remaining materials (152 materials)
9. ⏳ Contaminants domain
10. ⏳ Compounds domain
11. ⏳ Settings domain

---

## 📚 Related Documentation

- **Frontend**: `docs/SECTION_TITLE_DESCRIPTION_IMPLEMENTATION.md` - UI implementation details
- **Policy**: `docs/08-development/FRONTMATTER_SOURCE_OF_TRUTH_POLICY.md` - Layer separation rules
- **Export**: `export/core/universal_exporter.py` - Export logic implementation
- **Components**: `app/components/MaterialsLayout/MaterialsLayout.tsx` - Section rendering

---

## ✅ Success Criteria

A section is considered "normalized" when:

1. ✅ Source data has `_section` with all 5 required fields
2. ✅ No legacy `title:` or `_metadata:` fields present
3. ✅ Export generates correct frontmatter
4. ✅ UI displays custom sectionTitle
5. ✅ sectionDescription appears below title
6. ✅ Re-export produces identical output (idempotent)

---

## 🚨 Critical Rules

1. **NEVER edit frontmatter files directly** - they are generated output
2. **ALWAYS normalize in source data** (Materials.yaml, etc.)
3. **ALWAYS regenerate after source changes** - run `--export`
4. **ALWAYS verify persistence** - export twice, confirm no changes
5. **ALWAYS use all 5 required _section fields** - no partial implementations

---

**Last Updated**: January 15, 2026  
**Next Review**: After Phase 3 completion
