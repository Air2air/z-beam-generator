# Relationship Section Metadata Specification

**For Backend Frontmatter Generation**  
**Date:** December 24, 2025  
**Status:** ✅ COMPLETE - 100% Coverage Achieved

---

## Overview

All relationship fields in frontmatter YAML files **MUST** include `_section` metadata that defines how the section appears in the UI. This metadata provides title, description, icon, display order, and visual variant for each relationship section.

**Current Status:** 2,004/2,004 relationship fields have `_section` metadata (100% coverage)

---

## Required Structure

Every relationship field with `items` MUST have a `_section` block:

```yaml
relationships:
  [group]:                          # Optional: technical/safety/operational group
    [field_name]:
      presentation: card            # How items are displayed
      items: [...]                  # Array of relationship items
      _section:                     # ✅ REQUIRED
        title: "Section Title"      # ✅ REQUIRED - Display name
        description: "Section desc" # ✅ REQUIRED - Subtitle text
        icon: "box"                 # ✅ REQUIRED - Icon identifier
        order: 1                    # ✅ REQUIRED - Display order (1-99)
        variant: "default"          # ✅ REQUIRED - Visual style
```

---

## Field Requirements

### Required Fields

| Field | Type | Description | Example Values |
|-------|------|-------------|----------------|
| `title` | string | Section header text | "Regulatory Standards", "Health Effects" |
| `description` | string | Section subtitle/explanation | "Safety and compliance standards applicable to this laser setting" |
| `icon` | string | Icon identifier | "shield-check", "alert-triangle", "box", "droplet", "eye" |
| `order` | integer | Display sequence (1-99) | 1, 2, 3... |
| `variant` | string | Visual style | "default", "danger", "warning", "success" |

### Icon Options

Common icons used across the system:
- `box` - Materials, objects
- `shield-check` - Safety, regulatory
- `alert-triangle` - Warnings, health effects
- `droplet` - Contaminants, removal
- `eye` - Visual characteristics
- `settings` - Technical parameters
- `zap` - Energy, laser properties

### Variant Options

- `default` - Standard blue styling
- `danger` - Red styling (health hazards, prohibited items)
- `warning` - Yellow styling (cautions, risks)
- `success` - Green styling (optimized settings)

---

## Hierarchical Structure

Relationships can be organized in two ways:

### 1. Top-Level Fields (No Group)
```yaml
relationships:
  visual_characteristics:
    presentation: card
    items: [...]
    _section:
      title: "Visual Characteristics"
      description: "Physical appearance and identification features"
      icon: "eye"
      order: 10
      variant: "default"
```

### 2. Grouped Fields (technical/safety/operational)
```yaml
relationships:
  technical:
    affects_materials:
      presentation: card
      items: [...]
      _section:
        title: "Affects Materials"
        description: "Materials where this contaminant is commonly present"
        icon: "box"
        order: 1
        variant: "default"
    
    produces_compounds:
      presentation: card
      items: [...]
      _section:
        title: "Hazardous Compounds Generated"
        description: "Compounds produced during laser removal"
        icon: "alert-triangle"
        order: 2
        variant: "danger"
  
  safety:
    regulatory_standards:
      presentation: card
      items: [...]
      _section:
        title: "Regulatory Standards"
        description: "Safety and compliance standards"
        icon: "shield-check"
        order: 3
        variant: "default"
```

---

## Complete Examples by Entity Type

### Materials Example
```yaml
# frontmatter/materials/[category]/[material].yaml
relationships:
  technical:
    contaminated_by:
      presentation: card
      items:
        - id: rust-oxidation-contamination
          frequency: very_common
          severity: high
      _section:
        title: "Common Contaminants"
        description: "Contaminants frequently found on this material"
        icon: "droplet"
        order: 1
        variant: "default"
    
    industry_applications:
      presentation: card
      items:
        - industry: automotive
          use_case: "Surface preparation"
      _section:
        title: "Industry Applications"
        description: "Industries where this material requires laser cleaning"
        icon: "box"
        order: 2
        variant: "default"
  
  safety:
    regulatory_standards:
      presentation: card
      items:
        - type: regulatory_standards
          id: osha-ppe-requirements
      _section:
        title: "Regulatory Standards"
        description: "Safety and compliance standards"
        icon: "shield-check"
        order: 3
        variant: "default"
```

### Contaminants Example
```yaml
# frontmatter/contaminants/[category]/[contaminant].yaml
relationships:
  technical:
    affects_materials:
      presentation: card
      items:
        - id: aluminum-laser-cleaning
          frequency: common
          severity: moderate
      _section:
        title: "Found On Materials"
        description: "Materials where this contaminant is commonly present"
        icon: "box"
        order: 1
        variant: "default"
    
    produces_compounds:
      presentation: card
      items:
        - id: aluminum-oxide-compound
          phase: solid
          hazard_level: low
      _section:
        title: "Hazardous Compounds Generated"
        description: "Compounds produced during laser removal"
        icon: "alert-triangle"
        order: 2
        variant: "danger"
  
  safety:
    regulatory_standards:
      presentation: card
      items:
        - type: regulatory_standards
          id: osha-ppe-requirements
      _section:
        title: "Regulatory Standards"
        description: "Safety and compliance standards"
        icon: "shield-check"
        order: 3
        variant: "default"
```

### Compounds Example
```yaml
# frontmatter/compounds/[category]/[compound].yaml
relationships:
  technical:
    produced_from_contaminants:
      presentation: card
      items:
        - id: rust-oxidation-contamination
          frequency: very_common
          severity: high
      _section:
        title: "Contaminant Sources"
        description: "Contaminants that produce this compound"
        icon: "droplet"
        order: 1
        variant: "default"
    
    produced_from_materials:
      presentation: card
      items:
        - id: steel-laser-cleaning
          frequency: common
      _section:
        title: "Material Sources"
        description: "Materials that produce this compound"
        icon: "box"
        order: 2
        variant: "default"
  
  safety:
    exposure_limits:
      presentation: card
      items:
        - limit_type: "OSHA PEL"
          value: 5
          unit: "ppm"
      _section:
        title: "Exposure Limits"
        description: "Workplace exposure thresholds"
        icon: "shield-check"
        order: 3
        variant: "danger"
  
  operational:
    health_effects:
      presentation: card
      items:
        - type: health_effects
          id: toluene-toxicology
      _section:
        title: "Health Effects"
        description: "Potential health impacts and medical considerations"
        icon: "alert-triangle"
        order: 4
        variant: "danger"
```

### Settings Example
```yaml
# frontmatter/settings/[category]/[setting].yaml
relationships:
  technical:
    works_on_materials:
      presentation: card
      items:
        - id: oak-laser-cleaning
          effectiveness: medium
      _section:
        title: "Optimized Materials"
        description: "Materials that work best with this laser cleaning setting"
        icon: "box"
        order: 1
        variant: "success"
    
    removes_contaminants:
      presentation: card
      items:
        - id: rust-oxidation-contamination
          effectiveness: high
      _section:
        title: "Removes Contaminants"
        description: "Types of contamination effectively removed by this setting"
        icon: "droplet"
        order: 2
        variant: "default"
  
  safety:
    regulatory_standards:
      presentation: card
      items:
        - type: regulatory_standards
          id: osha-ppe-requirements
      _section:
        title: "Regulatory Standards"
        description: "Safety and compliance standards applicable to this laser setting"
        icon: "shield-check"
        order: 3
        variant: "default"
```

---

## All Relationship Fields Requiring `_section`

### Materials (153 files)
- `technical.contaminated_by` (153 occurrences)
- `technical.industry_applications` (132 occurrences)
- `safety.regulatory_standards` (153 occurrences)

### Contaminants (98 files)
- `technical.affects_materials` (98 occurrences)
- `technical.produces_compounds` (98 occurrences)
- `safety.regulatory_standards` (98 occurrences)
- `visual_characteristics` (98 occurrences)
- `laser_properties` (98 occurrences)
- `materials` (98 occurrences)
- `prohibited_materials` (78 occurrences)

### Compounds (34 files)
- `technical.produced_from_contaminants` (34 occurrences)
- `technical.produced_from_materials` (15 occurrences)
- `safety.exposure_limits` (20 occurrences)
- `operational.health_effects` (20 occurrences)
- Plus top-level fields: chemical_properties, physical_properties, reactivity, storage_requirements, ppe_requirements, detection_monitoring, emergency_response, environmental_impact, regulatory_classification, synonyms_identifiers

### Settings (153 files)
- `technical.works_on_materials` (144 occurrences)
- `technical.removes_contaminants` (153 occurrences)
- `technical.common_challenges` (153 occurrences)
- `safety.regulatory_standards` (153 occurrences)
- `safety.prohibited_materials` (153 occurrences)

---

## Validation Rules

### MUST HAVE
- ✅ Every relationship field with `items` MUST have `_section`
- ✅ All 5 fields (title, description, icon, order, variant) are REQUIRED
- ✅ Order values must be unique within the same entity file
- ✅ Variant must be one of: default, danger, warning, success

### MUST NOT
- ❌ Empty or null `_section` blocks
- ❌ Missing any of the 5 required fields
- ❌ Duplicate order numbers in the same file
- ❌ Invalid variant values

---

## Frontend Integration

The frontend reads `_section` metadata from relationships and uses it for:

1. **Section Titles** - `_section.title` becomes the CardGrid header
2. **Section Descriptions** - `_section.description` becomes the subtitle
3. **Display Order** - `_section.order` determines section sequence
4. **Visual Styling** - `_section.variant` determines color scheme
5. **Icons** - `_section.icon` displays visual indicators

**Important:** `_section` position in the YAML doesn't matter - it can be first or last in the field block.

---

## Backend Generator Requirements

When generating frontmatter files, the backend MUST:

1. **Always include `_section`** - No relationship field should be generated without it
2. **Use consistent titles** - Same field name across files should use same title
3. **Order logically** - Group related sections together with sequential order numbers
4. **Choose appropriate variants** - Use "danger" for health/hazards, "default" for general info
5. **Match entity patterns** - Follow the examples above for each entity type

---

## Verification

Check section metadata coverage:
```bash
python3 << 'EOF'
import yaml
from pathlib import Path

total = 0
missing = 0

for entity_type in ['materials', 'contaminants', 'compounds', 'settings']:
    for file_path in Path(f'frontmatter/{entity_type}').rglob('*.yaml'):
        with open(file_path, 'r') as f:
            data = yaml.safe_load(f)
        
        if data and 'relationships' in data:
            for group, group_data in data['relationships'].items():
                if isinstance(group_data, dict):
                    for field, field_data in group_data.items():
                        if isinstance(field_data, dict) and 'items' in field_data:
                            total += 1
                            if '_section' not in field_data:
                                missing += 1
                                print(f"Missing: {file_path.name} - {group}.{field}")

print(f"\nTotal: {total}, Missing: {missing}, Coverage: {(total-missing)/total*100:.1f}%")
EOF
```

Expected output: `Total: 2004, Missing: 0, Coverage: 100.0%`

---

## Questions?

Contact the frontend team for clarification on:
- Icon selection for new relationship types
- Variant styling preferences
- Title/description wording guidelines
- Display order conventions
