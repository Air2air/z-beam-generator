# Frontmatter Structure Specification

**Document Purpose**: Define the canonical frontmatter structure for all article types  
**Audience**: Frontmatter generator, content creators, developers  
**Created**: December 17, 2025  
**Version**: 5.0.0 (Flattened Domain Linkages)

---

## Overview

All frontmatter files follow a consistent structure with **logical field ordering** and **flattened domain linkages**. Each linkage type is a top-level array that maps directly to one GridSection in the frontend.

### Key Principles

1. **Flat Structure**: No nested `domain_linkages` object - each linkage type is top-level
2. **Logical Ordering**: Fields organized by purpose (identity → dates → author → content → technical → linkages → SEO)
3. **Consistent Naming**: Same field names across all article types
4. **Frontend-Friendly**: Each array maps to one `<GridSection>` component
5. **Type-Specific Fields**: Each article type has specialized description/technical fields

---

## Universal Field Order

All frontmatter files use this field ordering:

```yaml
# ============================================================================
# IDENTITY - What this article is
# ============================================================================
id: string                    # Unique identifier (kebab-case)
title: string                 # Display title (Title Case)
slug: string                  # URL slug (matches id)
category: string              # Primary category
subcategory: string           # Subcategory
schema_version: string        # Schema version (e.g., "5.0.0")
content_type: string          # unified_contamination | unified_material | unified_compound | unified_settings

# ============================================================================
# DATES & METADATA - When this was created/modified
# ============================================================================
datePublished: ISO8601        # Publication date
dateModified: ISO8601         # Last modification date

# ============================================================================
# AUTHOR - Who wrote this
# ============================================================================
author:
  id: number
  name: string
  country: string
  title: string               # Academic title (Ph.D., etc.)
  # ... (see Author Schema below)

# ============================================================================
# CONTENT - Human-readable text (type-specific)
# ============================================================================
contamination_description: string   # For contaminants only
material_description: string        # For materials only
compound_description: string        # For compounds only
settings_description: string        # For settings only

micro:                              # Optional microscopy content
  before: string
  after: string

# ============================================================================
# TECHNICAL DATA - Scientific properties (type-specific)
# ============================================================================
laser_properties:                   # Contaminants, Materials
  optical_properties: {}
  thermal_properties: {}
  removal_characteristics: {}
  safety_data: {}

physical_properties: {}             # Materials, Compounds
chemical_properties: {}             # Compounds
mechanical_properties: {}           # Materials

# ============================================================================
# DOMAIN LINKAGES - Cross-references (FLATTENED TO TOP LEVEL)
# ============================================================================
produces_compounds: []              # Contaminants → Compounds (safety-critical)
removes_contaminants: []            # Materials → Contaminants
found_in_materials: []              # Compounds → Materials
effective_against: []               # Settings → Contaminants

related_materials: []               # Cross-reference to materials
related_contaminants: []            # Cross-reference to contaminants
related_compounds: []               # Cross-reference to compounds
related_settings: []                # Cross-reference to settings

# ============================================================================
# SEO & NAVIGATION - Search and discovery
# ============================================================================
breadcrumb: []
valid_materials: []                 # Contaminants only
valid_contaminants: []              # Materials only
compatible_materials: []            # Compounds/Settings
eeat: {}                            # E-E-A-T metadata

# ============================================================================
# INTERNAL - System metadata
# ============================================================================
_metadata:
  voice: {}
```

---

## Field Reference

Complete data dictionary for all frontmatter fields. Each linkage field is an **array** containing **multiple card objects**.

### Identity Fields

| Field | Title | Description | Type | Required | Used By | Example |
|-------|-------|-------------|------|----------|---------|---------|
| `id` | Unique Identifier | Kebab-case unique identifier | string | ✅ | All | `adhesive-residue-contamination` |
| `title` | Display Title | Human-readable title (Title Case) | string | ✅ | All | `Adhesive Residue Contamination` |
| `slug` | URL Slug | URL-safe identifier (matches id) | string | ✅ | All | `adhesive-residue-contamination` |
| `category` | Primary Category | Top-level classification | string | ✅ | All | `organic-residue` |
| `subcategory` | Subcategory | Secondary classification | string | ✅ | All | `adhesive` |
| `schema_version` | Schema Version | Version of this specification | string | ✅ | All | `5.0.0` |
| `content_type` | Content Type | Article type identifier | string | ✅ | All | `unified_contamination` |

### Date & Metadata Fields

| Field | Title | Description | Type | Required | Used By | Example |
|-------|-------|-------------|------|----------|---------|---------|
| `datePublished` | Publication Date | ISO8601 timestamp of first publication | ISO8601 | ✅ | All | `2025-12-17T12:39:32.181899` |
| `dateModified` | Modification Date | ISO8601 timestamp of last edit | ISO8601 | ✅ | All | `2025-12-17T12:39:32.181899` |

### Author Field

| Field | Title | Description | Type | Required | Used By | Example |
|-------|-------|-------------|------|----------|---------|---------|
| `author` | Author Information | Complete author object with credentials | object | ✅ | All | See Author Schema |

### Content Fields (Type-Specific)

| Field | Title | Description | Type | Required | Used By | Example |
|-------|-------|-------------|------|----------|---------|---------|
| `contamination_description` | Contamination Description | Technical description of contaminant properties | string | ✅ | Contaminants | `Adhesive residue consists of...` |
| `material_description` | Material Description | Technical description of material properties | string | ✅ | Materials | `Aluminum is a lightweight...` |
| `compound_description` | Compound Description | Technical description of compound properties | string | ✅ | Compounds | `Carbon monoxide is a toxic...` |
| `settings_description` | Settings Description | Description of laser parameter optimization | string | ✅ | Settings | `Optimized parameters for...` |
| `micro` | Microscopy Content | Before/after microscopy observations | object | ❌ | All | `{before: "...", after: "..."}` |

### Technical Data Fields (Type-Specific)

| Field | Title | Description | Type | Required | Used By | Example |
|-------|-------|-------------|------|----------|---------|---------|
| `laser_properties` | Laser Properties | Optical, thermal, removal, and safety data | object | ✅ | Contaminants, Materials | See examples |
| `physical_properties` | Physical Properties | Density, hardness, state, etc. | object | ✅ | Materials, Compounds | See examples |
| `chemical_properties` | Chemical Properties | Molecular formula, CAS, exposure limits | object | ✅ | Compounds | See examples |
| `mechanical_properties` | Mechanical Properties | Strength, elasticity, hardness | object | ❌ | Materials | See examples |

### Domain Linkage Fields (Arrays of Card Objects)

**Note**: Each field is an **array** containing **multiple card objects**. Each object renders as one card in the grid.

| Field | Grid Title | Grid Description | Type | Cards | Used By | Example |
|-------|------------|------------------|------|-------|---------|---------|
| `produces_compounds` | Hazardous Compounds Generated | Compounds produced during laser removal with exposure limits and safety controls | array | 3-10 | Contaminants | `[{carbon-monoxide}, {acetaldehyde}, ...]` |
| `removes_contaminants` | Removable Contaminants | Contaminants that can be removed from this material | array | 5-20 | Materials | `[{oxide-layer}, {oil-grease}, ...]` |
| `found_in_materials` | Found in Materials | Materials where this compound is commonly detected | array | 3-15 | Compounds | `[{aluminum}, {steel}, ...]` |
| `effective_against` | Effective Against | Contaminants these settings effectively remove | array | 1-5 | Settings | `[{adhesive-residue}, ...]` |
| `related_materials` | Compatible Materials | Materials frequently contaminated or related | array | 10-30 | All | `[{aluminum}, {steel}, ...]` |
| `related_contaminants` | Related Contaminants | Contaminants that often appear together | array | 3-10 | All | `[{oil-grease}, {oxide-layer}, ...]` |
| `related_compounds` | Related Compounds | Compounds with similar properties or hazards | array | 3-10 | All | `[{carbon-dioxide}, {vocs}, ...]` |
| `related_settings` | Recommended Settings | Machine settings optimized for this context | array | 2-8 | All | `[{1064nm-100w}, {532nm-50w}, ...]` |

**Array Structure**: Each linkage field contains multiple objects with identical structure:
```yaml
produces_compounds:           # Array field (3 cards)
  - id: carbon-monoxide       # Card object 1
    title: Carbon Monoxide
    url: /compounds/...
    image: /images/...
    # ... (15+ properties per card)
  - id: acetaldehyde          # Card object 2
    title: Acetaldehyde
    # ... (same structure)
  - id: vocs                  # Card object 3
    title: VOCs
    # ... (same structure)
```

### SEO & Navigation Fields

| Field | Title | Description | Type | Required | Used By | Example |
|-------|-------|-------------|------|----------|---------|---------|
| `breadcrumb` | Breadcrumb Navigation | Hierarchical navigation path | array | ✅ | All | `[{label: "Home", href: "/"}, ...]` |
| `valid_materials` | Compatible Materials List | Simple string array of material names | array | ✅ | Contaminants | `["Aluminum", "Steel", ...]` |
| `valid_contaminants` | Removable Contaminants List | Simple string array of contaminant names | array | ✅ | Materials | `["Oxide Layer", "Oil", ...]` |
| `compatible_materials` | Compatible Materials List | Simple string array for compounds/settings | array | ❌ | Compounds, Settings | `["Aluminum", "Steel", ...]` |
| `eeat` | E-E-A-T Metadata | Experience, expertise, authority, trust signals | object | ✅ | All | `{citations: [...], isBasedOn: {}}` |

### Internal Fields

| Field | Title | Description | Type | Required | Used By | Example |
|-------|-------|-------------|------|----------|---------|---------|
| `_metadata` | Internal Metadata | System-generated metadata (voice, processing) | object | ❌ | All | `{voice: {...}}` |

---

## Article Type: Contaminants

### Example Structure
```yaml
# IDENTITY
id: adhesive-residue-contamination
title: Adhesive Residue / Tape Marks Contamination
slug: adhesive-residue-contamination
category: organic-residue
subcategory: adhesive
schema_version: 5.0.0
content_type: unified_contamination

# DATES & METADATA
datePublished: '2025-12-17T12:39:32.181899'
dateModified: '2025-12-17T12:39:32.181899'

# AUTHOR
author:
  id: 1
  name: Yi-Chun Lin
  country: Taiwan
  title: Ph.D.
  # ... (full author object)

# CONTENT
contamination_description: |
  Adhesive residue contamination consists of organic polymers from tapes 
  and labels, so sticky films form on surfaces...

micro:
  before: Adhesive residue contamination poses cleaning challenge...
  after: "Ikmanda Roswati, Ph.D.\nIndonesia"

# TECHNICAL DATA
laser_properties:
  optical_properties:
    absorption_coefficient_1064nm: 850
    wavelength_1064nm: 0.15
  thermal_properties:
    decomposition_temperature: 350
    melting_point: null
  removal_characteristics:
    primary_mechanism: thermal_ablation
    damage_risk_to_substrate: low
  safety_data:
    fire_explosion_risk: low
    toxic_gas_risk: moderate
    ppe_requirements:
      respiratory: full_face
      eye_protection: goggles
      skin_protection: gloves

# DOMAIN LINKAGES (FLATTENED)
produces_compounds:
  - id: carbon-monoxide-compound
    title: Carbon Monoxide
    url: /compounds/toxic-gas/asphyxiant/carbon-monoxide-compound
    image: /images/compounds/carbon-monoxide.jpg
    category: toxic-gas
    subcategory: asphyxiant
    frequency: very_common
    severity: high
    typical_context: Incomplete combustion of organic adhesives
    exposure_risk: high
    exposure_limits:
      osha_pel_mg_m3: 55
      niosh_rel_mg_m3: 40
      acgih_tlv_mg_m3: 29
      idlh_mg_m3: null
    exceeds_limits: false
    monitoring_required: false
    control_measures:
      ventilation_required: false
      ppe_level: none
      filtration_type: null
    concentration_range: 10-50 mg/m³
    hazard_class: toxic

related_materials:
  - id: aluminum-laser-cleaning
    title: Aluminum
    url: /materials/metal/non-ferrous/aluminum-laser-cleaning
    image: /images/material/aluminum-laser-cleaning-hero.jpg
    category: metal
    subcategory: non-ferrous
    frequency: common
    severity: moderate
    typical_context: general

related_contaminants:
  - id: oil-grease-contamination
    title: Oil / Grease Residue
    url: /contaminants/organic-residue/petroleum/oil-grease-contamination
    # ... (same structure as materials)

related_settings:
  - id: adhesive-removal-1064nm-100w
    title: Adhesive Removal - 1064nm 100W
    url: /settings/organic-removal/adhesive/adhesive-removal-1064nm-100w
    # ... (same structure)

# SEO & NAVIGATION
breadcrumb:
  - label: Home
    href: /
  - label: Contaminants
    href: /contaminants
  - label: Organic Residue
    href: /contaminants/organic-residue
  - label: Adhesive
    href: /contaminants/organic-residue/adhesive

valid_materials:
  - Aluminum
  - Steel
  - Stainless Steel
  # ... (list of compatible materials)

eeat:
  citations:
    - IEC 60825 - Safety of Laser Products
    - OSHA 29 CFR 1926.95 - Personal Protective Equipment
  isBasedOn:
    name: IEC 60825 - Safety of Laser Products
    url: https://webstore.iec.ch/publication/3587
  reviewedBy: Z-Beam Quality Assurance Team

# INTERNAL
_metadata:
  voice:
    author_name: Yi-Chun Lin
    author_country: Taiwan
    voice_applied: true
    content_type: contaminant
```

---

## Article Type: Materials

### Example Structure
```yaml
# IDENTITY
id: aluminum-laser-cleaning
title: Aluminum Laser Cleaning
slug: aluminum-laser-cleaning
category: metal
subcategory: non-ferrous
schema_version: 5.0.0
content_type: unified_material

# DATES & METADATA
datePublished: '2025-12-17T10:00:00.000000'
dateModified: '2025-12-17T10:00:00.000000'

# AUTHOR
author:
  id: 2
  name: Dr. Sarah Chen
  country: USA
  title: Ph.D.

# CONTENT
material_description: |
  Aluminum is a lightweight, corrosion-resistant metal widely used in aerospace,
  automotive, and construction industries...

micro:
  before: Aluminum surface contamination shows oxide layer...
  after: "Dr. Sarah Chen\nUSA"

# TECHNICAL DATA
laser_properties:
  optical_properties:
    reflectivity_1064nm: 0.92
    absorption_coefficient_1064nm: 120
  thermal_properties:
    melting_point: 660
    thermal_conductivity: 237

physical_properties:
  density_g_cm3: 2.7
  hardness_mohs: 2.75

mechanical_properties:
  tensile_strength_mpa: 310
  yield_strength_mpa: 276

# DOMAIN LINKAGES (FLATTENED)
removes_contaminants:
  - id: oxide-layer-contamination
    title: Oxide Layer
    url: /contaminants/corrosion/oxide/oxide-layer-contamination
    # ... (same structure)

related_materials:
  - id: steel-laser-cleaning
    title: Steel
    # ...

related_compounds:
  - id: aluminum-oxide-compound
    title: Aluminum Oxide
    # ...

related_settings:
  - id: aluminum-oxide-removal-1064nm
    title: Aluminum Oxide Removal - 1064nm
    # ...

# SEO & NAVIGATION
breadcrumb:
  - label: Home
    href: /
  - label: Materials
    href: /materials
  - label: Metal
    href: /materials/metal
  - label: Non-Ferrous
    href: /materials/metal/non-ferrous

valid_contaminants:
  - Oxide Layer
  - Oil / Grease
  - Paint / Coating
  # ...

eeat:
  citations:
    - ASTM B209 - Standard Specification for Aluminum
  isBasedOn:
    name: ASTM B209
    url: https://www.astm.org/b0209-14.html
```

---

## Article Type: Compounds

### Example Structure
```yaml
# IDENTITY
id: carbon-monoxide-compound
title: Carbon Monoxide
slug: carbon-monoxide-compound
category: toxic-gas
subcategory: asphyxiant
schema_version: 5.0.0
content_type: unified_compound

# DATES & METADATA
datePublished: '2025-12-17T11:00:00.000000'
dateModified: '2025-12-17T11:00:00.000000'

# AUTHOR
author:
  id: 3
  name: Dr. James Wilson
  country: UK
  title: Ph.D.

# CONTENT
compound_description: |
  Carbon monoxide is a colorless, odorless toxic gas produced during
  incomplete combustion of organic materials...

# TECHNICAL DATA
chemical_properties:
  molecular_formula: CO
  molecular_weight: 28.01
  cas_number: 630-08-0
  boiling_point: -191.5
  exposure_limits:
    osha_pel_mg_m3: 55
    niosh_rel_mg_m3: 40
    acgih_tlv_mg_m3: 29

physical_properties:
  state: gas
  color: colorless
  odor: odorless
  density_g_cm3: 0.00125

# DOMAIN LINKAGES (FLATTENED)
found_in_materials:
  - id: organic-paint-contamination
    title: Paint / Coating
    # ... (material that produces this compound)

related_compounds:
  - id: carbon-dioxide-compound
    title: Carbon Dioxide
    # ...

compatible_materials:
  - Aluminum
  - Steel
  # ... (materials where this compound is found)

# SEO & NAVIGATION
breadcrumb:
  - label: Home
    href: /
  - label: Compounds
    href: /compounds
  - label: Toxic Gas
    href: /compounds/toxic-gas
  - label: Asphyxiant
    href: /compounds/toxic-gas/asphyxiant
```

---

## Article Type: Settings

### Example Structure
```yaml
# IDENTITY
id: adhesive-removal-1064nm-100w
title: Adhesive Removal - 1064nm 100W
slug: adhesive-removal-1064nm-100w
category: organic-removal
subcategory: adhesive
schema_version: 5.0.0
content_type: unified_settings

# DATES & METADATA
datePublished: '2025-12-17T13:00:00.000000'
dateModified: '2025-12-17T13:00:00.000000'

# AUTHOR
author:
  id: 4
  name: Dr. Maria Garcia
  country: Spain
  title: Ph.D.

# CONTENT
settings_description: |
  Optimized laser parameters for removing adhesive residue from metal
  surfaces using 1064nm wavelength fiber laser...

# TECHNICAL DATA
laser_parameters:
  wavelength_nm: 1064
  power_w: 100
  pulse_duration_ns: 100
  repetition_rate_khz: 20
  scan_speed_mm_s: 800
  spot_size_mm: 0.5

process_parameters:
  passes: 3
  overlap: 0.5
  focal_offset_mm: 0

# DOMAIN LINKAGES (FLATTENED)
effective_against:
  - id: adhesive-residue-contamination
    title: Adhesive Residue / Tape Marks
    url: /contaminants/organic-residue/adhesive/adhesive-residue-contamination
    # ...

compatible_materials:
  - Aluminum
  - Steel
  - Stainless Steel
  # ...

related_settings:
  - id: adhesive-removal-532nm-50w
    title: Adhesive Removal - 532nm 50W
    # ...

# SEO & NAVIGATION
breadcrumb:
  - label: Home
    href: /
  - label: Settings
    href: /settings
  - label: Organic Removal
    href: /settings/organic-removal
  - label: Adhesive
    href: /settings/organic-removal/adhesive
```

---

## Domain Linkage Object Schema

All domain linkage arrays contain objects with this structure:

```yaml
- id: string                    # Unique identifier
  title: string                 # Display title
  url: string                   # Absolute URL path
  image: string                 # Image path
  category: string              # Category
  subcategory: string           # Subcategory
  frequency: string             # very_common | common | occasional | rare
  severity: string              # severe | high | moderate | low
  typical_context: string       # Usage context description
  
  # Additional fields for produces_compounds:
  exposure_risk: string         # high | moderate | low
  exposure_limits:
    osha_pel_mg_m3: number
    niosh_rel_mg_m3: number
    acgih_tlv_mg_m3: number
    idlh_mg_m3: number
  exceeds_limits: boolean
  monitoring_required: boolean
  control_measures:
    ventilation_required: boolean
    ppe_level: string           # full | enhanced | basic | none
    filtration_type: string
  concentration_range: string   # e.g., "10-50 mg/m³"
  hazard_class: string          # toxic | irritant | corrosive | carcinogenic
```

---

## Author Schema

```yaml
author:
  id: number
  name: string
  country: string
  country_display: string
  title: string                 # Ph.D., Dr., M.Sc., etc.
  sex: string                   # m | f
  jobTitle: string
  expertise: string[]
  affiliation:
    name: string
    type: string                # EducationalOrganization | Corporation
  credentials: string[]
  email: string
  image: string
  imageAlt: string
  url: string
  sameAs: string[]              # Social media / academic profiles
  persona_file: string          # Filename in prompts/personas/
  formatting_file: string       # Filename in prompts/formatting/
```

---

## Migration Guide

### From Old Structure (4.0.0) to New Structure (5.0.0)

**Changes Required:**

1. **Flatten domain_linkages**:
   ```yaml
   # OLD
   domain_linkages:
     produces_compounds: [...]
     related_materials: [...]
   
   # NEW
   produces_compounds: [...]
   related_materials: [...]
   ```

2. **Remove duplicate fields**:
   ```yaml
   # OLD
   name: Adhesive Residue
   title: Adhesive Residue Contamination
   
   # NEW
   title: Adhesive Residue Contamination  # Keep title only
   ```

3. **Reorder fields** according to specification above

4. **Add missing fields**:
   - `concentration_range` to `produces_compounds` items
   - `hazard_class` to `produces_compounds` items

### Migration Script

Run the normalization script:

```bash
# Dry run (preview changes)
python3 scripts/normalize_frontmatter_structure.py --dry-run

# Apply changes to all frontmatter
python3 scripts/normalize_frontmatter_structure.py

# Apply to specific directory
python3 scripts/normalize_frontmatter_structure.py --path frontmatter/contaminants/
```

---

## Frontend Usage

With flattened structure, frontend code becomes simpler:

```tsx
// ContaminantsLayout.tsx
export function ContaminantsLayout({ metadata }) {
  const compounds = metadata.produces_compounds || [];
  const materials = metadata.related_materials || [];
  const contaminants = metadata.related_contaminants || [];
  
  return (
    <Layout>
      {/* Compounds - Safety Critical */}
      {compounds.length > 0 && (
        <GridSection
          title="Hazardous Compounds Generated"
          description="Compounds produced during laser removal with exposure limits"
        >
          <CompoundSafetyGrid compounds={compounds} sortBy="severity" />
        </GridSection>
      )}
      
      {/* Materials */}
      {materials.length > 0 && (
        <GridSection
          title="Compatible Materials"
          description="Materials frequently contaminated by this substance"
        >
          <DataGrid 
            data={materials} 
            mapper={materialLinkageToGridItem}
            sorter={sortByFrequency}
          />
        </GridSection>
      )}
      
      {/* Contaminants */}
      {contaminants.length > 0 && (
        <GridSection
          title="Related Contaminants"
          description="Contaminants that often appear together"
        >
          <DataGrid 
            data={contaminants} 
            mapper={contaminantLinkageToGridItem}
            sorter={sortBySeverity}
          />
        </GridSection>
      )}
    </Layout>
  );
}
```

**Benefits:**
- ✅ No nested property access (`metadata.produces_compounds` not `metadata.domain_linkages.produces_compounds`)
- ✅ Simpler conditional rendering
- ✅ Each array maps to one GridSection
- ✅ YAML field order controls display order

---

## Validation Rules

### Required Fields (All Types)
- `id`
- `title`
- `slug`
- `category`
- `subcategory`
- `schema_version`
- `content_type`
- `datePublished`
- `dateModified`
- `author`

### Required Fields (Type-Specific)
- **Contaminants**: `contamination_description`, `laser_properties.safety_data`
- **Materials**: `material_description`, `physical_properties`
- **Compounds**: `compound_description`, `chemical_properties`
- **Settings**: `settings_description`, `laser_parameters`

### Field Constraints
- `frequency`: Must be one of: `very_common`, `common`, `occasional`, `rare`
- `severity`: Must be one of: `severe`, `high`, `moderate`, `low`
- `exposure_risk`: Must be one of: `high`, `moderate`, `low`
- `ppe_level`: Must be one of: `full`, `enhanced`, `basic`, `none`

---

## Related Documentation

- `CONTENT_SECTION_TITLE_PATTERN.md` - Grid section title/description standards
- `SOLUTION_A_IMPLEMENTATION_GUIDE.md` - Grid architecture overview
- `scripts/normalize_frontmatter_structure.py` - Migration script
- `app/components/GridSection/GridSection.tsx` - Frontend component

---

## Version History

### 5.0.0 (December 17, 2025)
- Flattened domain_linkages structure
- Removed duplicate `name` field
- Standardized field ordering across all types
- Added `concentration_range` and `hazard_class` to compounds

### 4.0.0 (November 2025)
- Enhanced compound safety data in domain_linkages
- Added exposure limits and control measures

### 3.0.0 (October 2025)
- Unified content types
- Author voice integration
