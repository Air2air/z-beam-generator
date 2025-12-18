# Frontmatter Formatting Guide

**Purpose**: Show the correct YAML formatting for frontmatter files  
**Audience**: Python frontmatter generators, content creators  
**Created**: December 17, 2025  
**Schema Version**: 5.0.0

---

## 🚨 **CRITICAL: Use yaml.SafeDumper** 🚨

**THE #1 MOST IMPORTANT REQUIREMENT:**

```python
# ❌ WRONG - Creates Python tags that break JavaScript parsers
yaml.dump(data)
yaml.dump(data, default_flow_style=False)

# ✅ CORRECT - MUST use SafeDumper parameter
yaml.dump(data, Dumper=yaml.SafeDumper)
```

**Why This Matters:**
- Without `Dumper=yaml.SafeDumper`, Python creates tags like `!!python/object/apply:collections.OrderedDict`
- JavaScript's `js-yaml` parser **CANNOT** read these Python-specific tags
- This causes **ALL tests to fail** with `YAMLException: unknown tag` errors
- **153 material files failed** because this parameter was missing

**Verification:**
Your YAML file should **NEVER** contain:
- ❌ `!!python/object/apply:collections.OrderedDict`
- ❌ `!!python/object:...`
- ❌ Any `!!python/` prefixed tags

If you see these tags in your output → **You forgot `Dumper=yaml.SafeDumper`**

---

## 🚨 Critical Requirements

### 1. **PURE YAML ONLY**
- ❌ **NO Python-specific tags** (e.g., `!<tag:yaml.org,2002:python/object/apply:collections.OrderedDict>`)
- ❌ **NO serialized Python objects**
- ❌ **NO pickle data**
- ✅ **ONLY standard YAML types**: strings, numbers, booleans, arrays, objects

### 2. **Clean Serialization**
When generating from Python:
```python
import yaml

# ❌ WRONG - Creates Python-specific tags (!!python/object/apply:...)
yaml.dump(data)
yaml.dump(data, default_flow_style=False)
yaml.dump(data, sort_keys=False)

# ✅ CORRECT - Pure YAML output
yaml.dump(
    data, 
    default_flow_style=False,
    sort_keys=False,
    allow_unicode=True,
    Dumper=yaml.SafeDumper  # ← THIS PARAMETER IS MANDATORY!
)
```

**⚠️ WARNING**: If you omit `Dumper=yaml.SafeDumper`, your YAML will have Python tags and **ALL JavaScript tests will fail**.

**Quick Check**: Run `head -5 your-file.yaml` - If you see `!!python/` anywhere, you forgot SafeDumper.

### 3. **Field Ordering**
Follow exact order from `FRONTMATTER_STRUCTURE_SPECIFICATION.md`:
1. Identity fields
2. Dates & metadata
3. Author
4. Content (type-specific descriptions)
5. Technical data (type-specific)
6. Domain linkages (flattened, top-level)
7. SEO & navigation

---

## ✅ Correct Format Examples

### Example 1: Material Frontmatter (Aluminum)

```yaml
# ============================================================================
# IDENTITY
# ============================================================================
id: aluminum-laser-cleaning
title: Aluminum Laser Cleaning
slug: aluminum-laser-cleaning
category: metal
subcategory: non-ferrous
schema_version: "5.0.0"
content_type: unified_material

# ============================================================================
# DATES & METADATA
# ============================================================================
datePublished: "2025-12-17T00:00:00Z"
dateModified: "2025-12-17T12:30:00Z"

# ============================================================================
# AUTHOR
# ============================================================================
author:
  id: 1
  name: "Dr. Sarah Chen"
  country: "United States"
  title: "Ph.D."
  credentials: "Materials Science"
  institution: "MIT"
  bio: "Laser ablation specialist with 15 years experience"

# ============================================================================
# CONTENT
# ============================================================================
description: "Lightweight metal widely used in aerospace and automotive industries. Laser cleaning effectively removes oxidation and surface contamination without damaging the substrate."

micro:
  before: "Aluminum surface shows dark oxidation layer with pitting and corrosion"
  after: "Bright metallic surface with uniform texture and zero contamination"

subtitle: "Precision Surface Restoration for Aerospace-Grade Aluminum"

faq:
  - question: "Can laser cleaning remove anodized coatings?"
    answer: "Yes, laser cleaning can selectively remove anodized layers while preserving base metal integrity."
  - question: "What wavelength is best for aluminum?"
    answer: "1064nm Nd:YAG lasers provide optimal results with minimal thermal impact."

# ============================================================================
# TECHNICAL DATA
# ============================================================================
laser_properties:
  optical_properties:
    reflectivity: 0.92
    absorption_coefficient: 0.08
    recommended_wavelength: "1064nm"
  thermal_properties:
    melting_point: 660.3
    thermal_conductivity: 237.0
    specific_heat: 0.897
  removal_characteristics:
    optimal_fluence_min: 0.5
    optimal_fluence_max: 3.0
    pulse_duration: "nanosecond"
    surface_damage_threshold: 5.0
  safety_data:
    fume_hazard_level: "low"
    eye_protection_required: true
    ventilation_required: true

physical_properties:
  density: 2.70
  hardness_mohs: 2.75
  tensile_strength: 90.0
  elastic_modulus: 69.0

# ============================================================================
# DOMAIN LINKAGES (FLATTENED - TOP LEVEL)
# ============================================================================
removes_contaminants:
  - title: "Rust and Corrosion"
    url: "/contaminants/rust-corrosion"
    contaminant_category: "corrosion"
    micro: "Iron oxide buildup from environmental exposure"
    hazard_level: "medium"
  - title: "Oil and Grease"
    url: "/contaminants/oil-grease"
    contaminant_category: "organic"
    micro: "Petroleum-based lubricants and residues"
    hazard_level: "low"
  - title: "Paint and Coatings"
    url: "/contaminants/paint-coatings"
    contaminant_category: "coating"
    micro: "Industrial paint layers and protective coatings"
    hazard_level: "medium"

related_materials:
  - title: "Steel"
    url: "/materials/steel"
    material_type: "metal"
    micro: "Ferrous alloy with high strength"
  - title: "Titanium"
    url: "/materials/titanium"
    material_type: "metal"
    micro: "High-strength lightweight metal"

related_settings:
  - title: "Precision Cleaning"
    url: "/settings/precision-cleaning"
    setting_category: "precision"
    micro: "High-accuracy contamination removal"
  - title: "High-Speed Processing"
    url: "/settings/high-speed"
    setting_category: "speed"
    micro: "Rapid throughput for industrial applications"

# ============================================================================
# SEO & NAVIGATION
# ============================================================================
breadcrumb:
  - name: "Home"
    url: "/"
  - name: "Materials"
    url: "/materials"
  - name: "Metals"
    url: "/materials/metal"
  - name: "Aluminum"
    url: "/materials/aluminum-laser-cleaning"

valid_contaminants:
  - rust-corrosion
  - oil-grease
  - paint-coatings
  - oxidation

seo:
  metaTitle: "Aluminum Laser Cleaning | Precision Surface Restoration"
  metaDescription: "Complete guide to laser cleaning aluminum surfaces. Remove oxidation, coatings, and contaminants without substrate damage."
  keywords:
    - aluminum laser cleaning
    - aerospace aluminum restoration
    - anodized coating removal
    - oxide layer cleaning
```

---

### Example 2: Contaminant Frontmatter (Rust)

```yaml
# ============================================================================
# IDENTITY
# ============================================================================
id: rust-corrosion-laser-removal
title: Rust and Corrosion Laser Removal
slug: rust-corrosion-laser-removal
category: corrosion
subcategory: oxidation
schema_version: "5.0.0"
content_type: unified_contamination

# ============================================================================
# DATES & METADATA
# ============================================================================
datePublished: "2025-12-17T00:00:00Z"
dateModified: "2025-12-17T12:30:00Z"

# ============================================================================
# AUTHOR
# ============================================================================
author:
  id: 2
  name: "Dr. James Wilson"
  country: "United Kingdom"
  title: "Ph.D."
  credentials: "Corrosion Science"
  institution: "Oxford University"
  bio: "Corrosion prevention specialist"

# ============================================================================
# CONTENT
# ============================================================================
contamination_description: "Iron oxide formation on ferrous metals caused by oxidation. Laser ablation removes rust layers while preserving base metal, offering advantages over mechanical or chemical methods."

micro:
  before: "Thick rust layer with flaking and pitting"
  after: "Clean metallic surface with minimal roughness"

subtitle: "Efficient Rust Removal Without Surface Damage"

# ============================================================================
# TECHNICAL DATA
# ============================================================================
laser_properties:
  removal_characteristics:
    optimal_fluence_min: 1.0
    optimal_fluence_max: 5.0
    pulse_duration: "nanosecond"
    recommended_wavelength: "1064nm"
  safety_data:
    fume_hazard_level: "medium"
    eye_protection_required: true
    ventilation_required: true
    respiratory_protection: "recommended"

chemical_properties:
  composition: "Fe2O3, Fe3O4"
  ph_level: null
  reactivity: "stable"
  toxicity_level: "low"

# ============================================================================
# DOMAIN LINKAGES (FLATTENED - TOP LEVEL)
# ============================================================================
produces_compounds:
  - title: "Iron Oxide (Fe2O3)"
    url: "/compounds/iron-oxide-fe2o3"
    compound_category: "oxide"
    micro: "Reddish-brown powder particles"
    cas_number: "1309-37-1"
    hazard_level: "low"

related_materials:
  - title: "Steel"
    url: "/materials/steel"
    material_type: "metal"
    micro: "Primary ferrous alloy affected by rust"
  - title: "Iron"
    url: "/materials/iron"
    material_type: "metal"
    micro: "Pure iron substrate vulnerable to oxidation"

related_contaminants:
  - title: "Corrosion"
    url: "/contaminants/corrosion"
    contaminant_category: "corrosion"
    micro: "General metal degradation"

related_settings:
  - title: "Rust Removal"
    url: "/settings/rust-removal"
    setting_category: "specialized"
    micro: "Optimized parameters for rust ablation"

# ============================================================================
# SEO & NAVIGATION
# ============================================================================
breadcrumb:
  - name: "Home"
    url: "/"
  - name: "Contaminants"
    url: "/contaminants"
  - name: "Corrosion"
    url: "/contaminants/corrosion"
  - name: "Rust"
    url: "/contaminants/rust-corrosion-laser-removal"

valid_materials:
  - steel
  - iron
  - carbon-steel
  - stainless-steel
```

---

### Example 3: Settings Frontmatter

```yaml
# ============================================================================
# IDENTITY
# ============================================================================
id: precision-cleaning-settings
title: Precision Cleaning Settings
slug: precision-cleaning-settings
category: precision
subcategory: high-accuracy
schema_version: "5.0.0"
content_type: unified_settings

# ============================================================================
# DATES & METADATA
# ============================================================================
datePublished: "2025-12-17T00:00:00Z"
dateModified: "2025-12-17T12:30:00Z"

# ============================================================================
# AUTHOR
# ============================================================================
author:
  id: 1
  name: "Dr. Sarah Chen"
  country: "United States"
  title: "Ph.D."

# ============================================================================
# CONTENT
# ============================================================================
settings_description: "Precision laser parameters optimized for selective contamination removal with minimal substrate impact. Ideal for aerospace and medical device applications."

micro:
  before: null
  after: null

subtitle: "Micron-Level Contamination Control"

# ============================================================================
# TECHNICAL DATA
# ============================================================================
laser_parameters:
  wavelength: "1064nm"
  pulse_duration: "10ns"
  repetition_rate: "20kHz"
  beam_diameter: "0.1mm"
  scanning_speed: "100mm/s"
  energy_per_pulse: "0.5mJ"

performance_metrics:
  removal_rate: "0.1mm²/s"
  selectivity: "high"
  substrate_damage_risk: "minimal"

# ============================================================================
# DOMAIN LINKAGES (FLATTENED - TOP LEVEL)
# ============================================================================
effective_against:
  - title: "Rust and Corrosion"
    url: "/contaminants/rust-corrosion"
    contaminant_category: "corrosion"
    micro: "Iron oxide layers"
  - title: "Oil and Grease"
    url: "/contaminants/oil-grease"
    contaminant_category: "organic"
    micro: "Petroleum residues"

related_materials:
  - title: "Aluminum"
    url: "/materials/aluminum"
    material_type: "metal"
    micro: "Lightweight aerospace metal"

related_settings:
  - title: "High-Speed Processing"
    url: "/settings/high-speed"
    setting_category: "speed"
    micro: "Rapid throughput settings"

# ============================================================================
# SEO & NAVIGATION
# ============================================================================
breadcrumb:
  - name: "Home"
    url: "/"
  - name: "Settings"
    url: "/settings"
  - name: "Precision"
    url: "/settings/precision"
  - name: "Precision Cleaning"
    url: "/settings/precision-cleaning-settings"
```

---

## ❌ Common Formatting Errors

### Error 1: Python-Specific Tags (MOST COMMON ERROR)
```yaml
# ❌ WRONG - Python serialization tags (causes ALL tests to fail)
!!python/object/apply:collections.OrderedDict
- - - id
    - aluminum-laser-cleaning
  - - title
    - Aluminum

# OR

produces_compounds: !<tag:yaml.org,2002:python/object/apply:collections.OrderedDict>
  - - preservedData
    - generationMetadata:

# ✅ CORRECT - Plain YAML (use yaml.SafeDumper)
id: aluminum-laser-cleaning
title: Aluminum

produces_compounds:
  - title: "Iron Oxide"
    url: "/compounds/iron-oxide"
    compound_category: "oxide"
```

**Root Cause**: Generator is using `yaml.dump(data)` instead of `yaml.dump(data, Dumper=yaml.SafeDumper)`

**Fix**: Add `Dumper=yaml.SafeDumper` parameter to ALL yaml.dump() calls

### Error 2: Nested relationships Object
```yaml
# ❌ WRONG - Old nested structure (v4.0.0)
relationships:
  produces_compounds: []
  related_materials: []

# ✅ CORRECT - Flattened structure (v5.0.0)
produces_compounds: []
related_materials: []
```

### Error 3: Inconsistent Field Order
```yaml
# ❌ WRONG - Random field order
faq: []
title: "Aluminum"
author: {}
produces_compounds: []
id: "aluminum"

# ✅ CORRECT - Logical ordering
id: "aluminum"
title: "Aluminum"
author: {}
faq: []
produces_compounds: []
```

### Error 4: Missing Required Fields
```yaml
# ❌ WRONG - Missing schema_version, content_type
id: aluminum
title: Aluminum

# ✅ CORRECT - All required fields
id: aluminum
title: Aluminum
schema_version: "5.0.0"
content_type: unified_material
```

### Error 5: Incorrect Array Format
```yaml
# ❌ WRONG - Single string instead of array
related_materials: "steel, titanium"

# ✅ CORRECT - Array of objects
related_materials:
  - title: "Steel"
    url: "/materials/steel"
    material_type: "metal"
  - title: "Titanium"
    url: "/materials/titanium"
    material_type: "metal"
```

---

## 🔧 Python Generator Template

```python
impo🚨 CRITICAL: Use Dumper=yaml.SafeDumper to avoid Python-specific tags!
    
    Without SafeDumper, you will get:
      !!python/object/apply:collections.OrderedDict
    
    With SafeDumper, you get:
      id: aluminum-laser-cleaning
      title: Aluminum Laser Cleaning
    
    The first format breaks ALL JavaScript test
from typing import Dict, Any
from collections import OrderedDict

def generate_frontmatter(data: Dict[str, Any]) -> str:
    """
    Generate clean YAML frontmatter compatible with JavaScript parsers.
    
    CRITICAL: Use SafeDumper to avoid Python-specific tags!
    """
    
    # Ensure proper field ordering
    ordered_data = OrderedDict([
        # Identity
        ('id', data.get('id')),
        ('title', data.get('title')),
        ('slug', data.get('slug')),
        ('category', data.get('category')),
        ('subcategory', data.get('subcategory')),
        ('schema_version', '5.0.0'),
        ('content_type', data.get('content_type')),
        
        # Dates
        ('datePublished', data.get('datePublished')),
        ('dateModified', data.get('dateModified')),
        
        # Author
        ('author', data.get('author')),
        
        # Content (type-specific)
        ('description', data.get('description')),
        ('micro', data.get('micro')),
        ('subtitle', data.get('subtitle')),
        ('faq', data.get('faq')),
        
        # Technical data
        ('laser_properties', data.get('laser_properties')),
        ('physical_properties', data.get('physical_properties')),
        
        # Domain linkages (FLATTENED - TOP LEVEL)
        ('removes_contaminants', data.get('removes_contaminants', [])),
        ('produces_compounds', data.get('produces_compounds', [])),
        ('related_materials', data.get('related_materials', [])),
        ('related_contaminants', data.get('related_contaminants', [])),
        ('related_settings', data.get('related_settings', [])),
        
      🚨 Generate YAML with SafeDumper (ABSOLUTELY MANDATORY!)
    yaml_output = yaml.dump(
        cleaned_data,
        default_flow_style=False,
        sort_keys=False,  # Preserve our ordering
        allow_unicode=True,
        width=80,
        indent=2,
        Dumper=yaml.SafeDumper  # ← THIS LINE IS MANDATORY - DO NOT OMIT!
    )
    
    # 🔍 VERIFY: First line should NOT contain "!!python/"
    if '!!python/' in yaml_output[:100]:
        raise ValueError(
            "ERROR: Python tags detected in YAML output! "
            "You forgot Dumper=yaml.SafeDumper parameter. "
            "This will break ALL JavaScript tests."
        # Generate YAML with SafeDumper (CRITICAL!)
    yaml_output = yaml.dump(
        cleaned_data,
        default_flow_style=False,
        sort_keys=False,  # Preserve our ordering
        allow_unicode=True,
        width=80,
        indent=2,
        Dumper=yaml.SafeDumper  # ← PREVENTS PYTHON TAGS!
    )
    
    return yaml_output

# Usage example
data = {
    'id': 'aluminum-laser-cleaning',
    'title': 'Aluminum Laser Cleaning',
    'slug': 'aluminum-laser-cleaning',
    'category': 'metal',
    'subcategory': 'non-ferrous',
    'content_type': 'unified_material',
    'datePublished': '2025-12-17T00:00:00Z',
    'dateModified': '2025-12-17T12:30:00Z',
    'author': {
        'id': 1,
        'name': 'Dr. Sarah Chen',
        'country': 'United States'
    },
    'description': 'Lightweight metal...',
    'removes_contaminants': [
        {
    🚨 FIRST: Verify No Python Tags
```bash
# Check first 10 lines of generated file
head -10 frontmatter/materials/aluminum-laser-cleaning.yaml

# Should see clean YAML like:
# id: aluminum-laser-cleaning
# title: Aluminum Laser Cleaning

# Should NOT see:
# !!python/object/apply:collections.OrderedDict
# !!python/object:...
```

If you see `!!python/` → **STOP** and fix your generator to use `Dumper=yaml.SafeDumper`

###         'title': 'Rust',
            'url': '/contaminants/rust',
            'contaminant_category': 'corrosion'
        }
    ]
}

yaml_content = generate_frontmatter(data)
print(yaml_content)
```

---

## ✅ Validation Checklist

Before committing frontmatter files:

### Schema Validation
- [ ] `schema_version: "5.0.0"` present
- [ ] `content_type` matches article type
- [ ] All required fields present for content type

### Format Validation
- [ ] Pure YAML (no Python tags)
- [ ] Correct field ordering (Identity → Dates → Author → Content → Technical → Linkages → SEO)
- [ ] Arrays use list format (not strings)
- [ ] Objects use mapping format

### Linkage Validation
- [ ] No nested `relationships` object
- [ ] All linkage arrays at top level
- [ ] Each linkage item has required fields (title, url, category, micro)
- [ ] URLs match slug format

### Content Validation
- [ ] Descriptions exist for content type (description, contamination_description, etc.)
- [ ] Author object complete
- [ ] Dates in ISO8601 format
- [ ] Breadcrumb array properly structured

### JavaScript Compatibility
- [ ] File parses with `js-yaml` library
- [ ] No `YAMLException` errors
- [ ] No unknown tags

---

## 📝 Testing Your Frontmatter

```javascript
// Test script to verify frontmatter parses correctly
const yaml = require('js-yaml');
const fs = require('fs');

try {
  const content = fs.readFileSync('path/to/frontmatter.yaml', 'utf8');
  const parsed = yaml.load(content);
  
  console.log('✅ YAML parses successfully');
  console.log('Schema version:', parsed.schema_version);
  console.log('Content type:', parsed.content_type);
  
  // Verify flattened structure
  if (parsed.relationships) {
    console.error('❌ ERROR: Found nested relationships (use v5.0.0 flattened structure)');
  }
  
  // Verify linkages are top-level
  const linkageFields = [
    'produces_compounds',
    'removes_contaminants',
    'related_materials',
    'related_contaminants',
    'related_settings'
  ];
  
  linkageFields.forEach(field => {
    if (parsed[field]) {
      console.log(`✅ ${field}: ${parsed[field].length} items`);
    }
  });
  
} catch (error) {
  console.error('❌ YAML parsing failed:', error.message);
  process.exit(1);
}
```

---

## 📚 Related Documentation

- **Structure Specification**: `FRONTMATTER_STRUCTURE_SPECIFICATION.md` - Complete field reference
- **Flattened Architecture**: `FLATTENED_ARCHITECTURE_MIGRATION_COMPLETE.md` - Migration details
- **Integration Guide**: `LINKAGE_SECTION_INTEGRATION_COMPLETE.md` - Frontend integration

---

**Last Updated**: December 17, 2025  
**Schema Version**: 5.0.0  
**Status**: Production Standard ✅
