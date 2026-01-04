# Frontmatter Unified Schema Proposal

**Date**: January 3, 2026  
**Status**: 🔴 PROPOSAL - Awaiting Approval  
**Impact**: High - Affects all frontmatter files (materials, contaminants, settings, compounds)

---

## 🎯 Executive Summary

**Problem**: Materials frontmatter uses scattered, flat structure with unclear content organization. Contaminants use superior subject-area concentration under `relationships` key.

**Solution**: Unify all content types under consistent subject-area schema with clear relationship keys.

**Benefit**: 
- ✅ Obvious subject area concentrations
- ✅ Clear content section separation
- ✅ Consistent structure across all content types
- ✅ Better component rendering logic
- ✅ Easier maintenance and navigation

---

## 📊 Current State Analysis (All 4 Domains)

**Regeneration Date**: January 3, 2026  
**Files Analyzed**: 132 materials, 88 contaminants, 132 settings, 9 compounds  
**Total Size**: ~200,000 lines across all frontmatter

---

### 1️⃣ Materials (⚠️ Partially Improved, Still Issues)

**File**: `yttria-stabilized-zirconia-laser-cleaning.yaml` (450 lines, recently regenerated)

```yaml
# CURRENT STATE - Mix of old and new patterns
name: Yttria-Stabilized Zirconia
category: ceramic
micro:                              # ❌ Still top-level
  before: "..."
  after: "..."
faq: [{...}]                        # ❌ Still top-level
components:                          # ❌ Still confusing
  micro: {before: "...", after: "..."}  # ❌ Duplicate of above!
properties:                          # ✅ Good - technical data
  material_characteristics: {...}
  laser_material_interaction: {...}
contamination:                       # ❌ Old format
  valid: [...]
  prohibited: [...]
relationships:
  interactions:
    contaminated_by:
      presentation: card           # ✅ NEW - Has presentation
      items: [id1, id2...]         # ❌ Still just flat IDs
      sectionMetadata:             # ✅ NEW - Has metadata!
        section_title: "Common Contaminants"
        section_description: "Types of contamination..."
        icon: droplet
        order: 1
  operational:                      # ✅ NEW - Subject area!
    expert_answers:
      presentation: collapsible    # ✅ Has presentation
      items:
        - question: "..."
          answer: "..."
          severity: medium
```

**Assessment:**
- ✅ **IMPROVED**: Added `sectionMetadata` with titles, descriptions, icons, order
- ✅ **IMPROVED**: Added `presentation` hints (card, collapsible)
- ✅ **IMPROVED**: Started using subject areas (`operational.expert_answers`)
- ❌ **STILL BROKEN**: Duplicate `micro` (top-level AND in components)
- ❌ **STILL BROKEN**: `faq` at top level AND in `relationships.operational.expert_answers`
- ❌ **STILL SCATTERED**: Content across multiple locations
- ⚠️ **CONFUSING**: `components` purpose unclear (has micro/description)

**Grade**: C+ (Was F, now partially improved but still inconsistent)

---

### 2️⃣ Contaminants (✅ Excellent Structure - No Changes Needed)

**File**: `zinc-plating-contamination.yaml` (354 lines, recently regenerated)

```yaml
# CURRENT STATE - EXCELLENT
name: Zinc Electroplating
category: metallic-coating
relationships:
  safety:                           # ✅ Clear subject area
    regulatory_standards:
      presentation: card
      items: [{id: "...", type: "..."}]
    fire_explosion_risk:
      presentation: card
      items: [{severity: "...", description: "..."}]
    fumes_generated:
      presentation: table
      items: [{compound: "...", concentration: "..."}]
    ppe_requirements:
      presentation: descriptive
      items: [{eye_protection: "...", respiratory: "..."}]
  
  interactions:                     # ✅ Clear subject area
    produces_compounds:
      presentation: card
      items: [{id: "zinc-oxide-compound"}]
    affects_materials:
      presentation: card
      items: [{id: "aluminum-laser-cleaning"}, ...]
  
  visual:                           # ✅ Clear subject area
    appearance_on_categories:
      presentation: descriptive
      items:
        - appearance_on_categories:
            metal: {appearance: "...", coverage: "...", pattern: "..."}
            ceramic: {appearance: "...", coverage: "...", pattern: "..."}
  
  operational:                      # ✅ Clear subject area
    laser_properties:
      presentation: descriptive
      items:
        - laser_parameters: {...}
        - optical_properties: {...}
        - removal_characteristics: {...}
```

**Assessment:**
- ✅ **PERFECT**: Clear subject-area concentration
- ✅ **PERFECT**: Rich, structured content under each relationship
- ✅ **PERFECT**: Consistent presentation metadata
- ✅ **PERFECT**: No duplicate or scattered content
- ✅ **PERFECT**: Easy to understand and navigate

**Grade**: A+ (This is the gold standard model)

---

### 3️⃣ Settings (⚠️ Partially Improved, Similar to Materials)

**File**: `aluminum-settings.yaml` (368 lines, recently regenerated)

```yaml
# CURRENT STATE - Mix of patterns
name: Aluminum
content_type: settings
relationships:
  safety:                           # ✅ NEW - Subject area
    regulatory_standards:
      presentation: card
      items: [{id: "...", type: "..."}]
      sectionMetadata:              # ✅ Has metadata
        section_title: "Safety Standards & Compliance"
        icon: shield-check
        order: 10
  
  interactions:                     # ✅ Subject area
    removes_contaminants:
      presentation: card
      items:
        - id: rust-oxidation-contamination
          effectiveness: high       # ✅ Rich metadata!
```

**Assessment:**
- ✅ **IMPROVED**: Using relationship subject areas
- ✅ **IMPROVED**: Has sectionMetadata
- ✅ **IMPROVED**: Presentation hints present
- ✅ **GOOD**: Rich metadata (effectiveness levels)
- ⚠️ **INCOMPLETE**: Need more subject areas (compatibility, equipment, etc.)

**Grade**: B (Better than materials, but less complete than contaminants)

---

### 4️⃣ Compounds (⚠️ Minimal Structure)

**File**: `metal-vapors-mixed-compound.yaml` (250 lines, recently regenerated)

```yaml
# CURRENT STATE - Minimal relationships
name: Metal Vapors (Mixed)
category: vapor
hazard_class: irritant
chemical_formula: Various
health_effects: "Long text content..."  # ❌ Top-level content
exposure_guidelines: "Long text..."     # ❌ Top-level content
detection_methods: "Long text..."       # ❌ Top-level content
first_aid: "Long text..."              # ❌ Top-level content
ppe_requirements: "Long text..."        # ❌ Top-level content
faq: [{...}]                           # ❌ Top-level content
relationships:
  interactions:                         # ⚠️ Only one subject area
    produced_from_contaminants:
      presentation: card
      items:
        - id: brass-plating-contamination
          frequency: unknown
          severity: moderate
          typical_context: "Laser removal of..."
  
  safety:                               # ✅ Has safety section
    health_effects:
      - route: inhalation
        effect: "..."
        severity: moderate
        onset: short-term
```

**Assessment:**
- ⚠️ **MIXED**: Has some subject areas (interactions, safety)
- ❌ **SCATTERED**: Most content at top level (health_effects, exposure_guidelines, etc.)
- ✅ **GOOD**: Rich metadata in relationship items (frequency, severity, context)
- ❌ **INCOMPLETE**: Missing subject areas (formation, applications, handling)
- ❌ **INCONSISTENT**: Some content in relationships, some at top level

**Grade**: C (Basic structure present but content scattered)

---

## 📊 Domain Comparison Matrix

| Domain | Subject Areas | Presentation | sectionMetadata | Rich Items | Content Location | Grade |
|--------|---------------|--------------|-----------------|------------|------------------|-------|
| **Materials** | ⚠️ Partial (2/5) | ✅ Yes | ✅ Yes | ❌ Flat IDs | ❌ Scattered | C+ |
| **Contaminants** | ✅ Complete (4/4) | ✅ Yes | ✅ Yes | ✅ Structured | ✅ Concentrated | A+ |
| **Settings** | ⚠️ Partial (2/4) | ✅ Yes | ✅ Yes | ✅ Some rich | ⚠️ Mostly good | B |
| **Compounds** | ⚠️ Minimal (2/6) | ✅ Yes | ❌ No | ✅ Some rich | ❌ Very scattered | C |

---

## 🎯 Key Findings

### ✅ Positive Progress
1. **sectionMetadata** added to materials/settings (title, description, icon, order)
2. **Presentation hints** present across all domains
3. **Subject areas emerging** in all domains (but incomplete)
4. **Contaminants are perfect** - gold standard achieved

### ❌ Critical Issues Remaining
1. **Content duplication** in materials (micro at top + in components, faq top + in relationships)
2. **Scattered content** in compounds (most content at top level)
3. **Incomplete subject areas** in materials/settings/compounds
4. **Inconsistent patterns** across domains (each uses different structure)
5. **`components` confusion** in materials (unclear purpose)

---

## 🔍 Detailed Domain Analysis

### Materials - Current Issues

**Duplicate Content Problem:**
```yaml
# PROBLEM: micro appears in TWO places
micro:                              # Location 1 (top-level)
  before: "The durability of yttria-stabilized..."
  after: "After cleaning, the surface reveals..."

components:                          # Location 2 (nested)
  micro:
    before: "We've found the contaminated surface..."
    after: "After laser treatment, the surface appears..."
```

**FAQ Duplication Problem:**
```yaml
# PROBLEM: FAQ content in TWO places
faq:                                # Location 1 (top-level)
  - question: "How do I safely laser clean YSZ?"
    answer: "I've seen YSZ hold up well..."

relationships:
  operational:
    expert_answers:                 # Location 2 (relationship)
      items:
        - question: "How do I safely laser clean YSZ?"
          answer: "I've seen YSZ hold up well..."
```

**Result**: Confusing, maintenance nightmare, unclear which is authoritative

---

### Contaminants - Gold Standard ⭐

**Why It Works:**
```yaml
relationships:
  safety:                           # Subject area 1
    regulatory_standards: {...}     # 5+ rich subsections
    ppe_requirements: {...}
    toxic_gas_risk: {...}
    fumes_generated: {...}
    ventilation_requirements: {...}
  
  interactions:                     # Subject area 2
    produces_compounds: {...}       # 2 rich subsections
    affects_materials: {...}
  
  visual:                           # Subject area 3
    appearance_on_categories:       # 1 mega-detailed section
      metal: {appearance, coverage, pattern, texture...}
      ceramic: {appearance, coverage, pattern, texture...}
      # 12 material categories with full details
  
  operational:                      # Subject area 4
    laser_properties: {...}         # 3 rich subsections
    removal_characteristics: {...}
```

**Result**: Clear organization, no duplication, easy to navigate, obvious rendering

---

### Settings - Needs Expansion

**Current (Good start):**
```yaml
relationships:
  safety:
    regulatory_standards: {...}
  interactions:
    removes_contaminants:
      items:
        - id: rust-oxidation-contamination
          effectiveness: high       # ✅ Rich metadata
```

**Missing Subject Areas:**
- `compatibility` - Which materials work with these settings?
- `equipment` - Compatible laser systems/manufacturers
- `applications` - Industry-specific use cases
- `optimization` - Parameter tuning guidance

---

### Compounds - Needs Restructuring

**Current Problems:**
```yaml
# SCATTERED CONTENT at top level
health_effects: "3000 character string..."
exposure_guidelines: "2000 character string..."
detection_methods: "1500 character string..."
first_aid: "1000 character string..."
ppe_requirements: "2000 character string..."
faq: [{...}]

# MINIMAL relationships section
relationships:
  interactions:
    produced_from_contaminants: {...}
  safety:
    health_effects: [{route, effect, severity}]  # ❌ Duplicate of top-level!
```

**Should Be:**
```yaml
# Clean metadata at top
chemical_formula: "Fe2O3"
cas_number: "1309-37-1"

# ALL content in relationships
relationships:
  safety:
    health_effects: {...}
    exposure_guidelines: {...}
    ppe_requirements: {...}
    first_aid: {...}
  
  formation:
    produced_from_contaminants: {...}
    reaction_conditions: {...}
  
  detection:
    methods: {...}
    monitoring: {...}
```

---

## 🏗️ Proposed Unified Schema

### Core Principle
**All content sections go under `content` key. All relationships go under `relationships` key with clear subject areas.**

### Universal Structure

```yaml
# ========================================
# METADATA (Same for all content types)
# ========================================
id: aluminum-laser-cleaning
name: Aluminum
category: metal
subcategory: non-ferrous
content_type: materials
schema_version: 6.0.0
full_path: /materials/metal/non-ferrous/aluminum-laser-cleaning
datePublished: '2026-01-03T22:26:13.411157Z'
dateModified: '2026-01-03T22:26:13.411157Z'

# ========================================
# CONTENT (Generated/Curated Text)
# ========================================
content:
  # SEO & Page Headers
  seo:
    page_title: "Aluminum: High Reflectivity Laser Cleaning"
    page_description: "Brief overview for page header"
    meta_description: "SEO meta description"
  
  # Editorial Content
  editorial:
    subtitle: "Short punchy subtitle"
    description: "Full detailed article (2000+ words)"
    settings_description: "Machine settings guidance article"
  
  # Visual Content
  visual:
    micro:
      before: "Before treatment microscopic description"
      after: "After treatment microscopic description"
  
  # Interactive Content
  interactive:
    faq:
      - question: "What makes aluminum suitable?"
        answer: "Detailed answer..."
      - question: "How do you set up?"
        answer: "Detailed answer..."

# ========================================
# PROPERTIES (Technical Data)
# ========================================
properties:
  material_characteristics:
    density: {value: 2.7, unit: "g/cm³", confidence: 98, min: 0.53, max: 22.6}
    porosity: {value: 0, unit: "%", confidence: 95}
    # ... all material properties
  
  laser_material_interaction:
    thermalConductivity: {value: 237.0, unit: "W/(m·K)", confidence: 92}
    laserReflectivity: {value: 0.92, unit: "%", confidence: 91}
    # ... all laser properties

# ========================================
# RELATIONSHIPS (Cross-References & Context)
# ========================================
relationships:
  # Subject Area 1: Contamination Interactions
  contamination:
    presentation: section
    affected_by:
      presentation: card
      items:
        - id: aluminum-oxidation-contamination
          frequency: very_common
          severity: moderate
        - id: industrial-oil-contamination
          frequency: common
          severity: low
    
    produces:
      presentation: card
      items:
        - id: aluminum-oxide-compound
          conditions: "High temperature exposure"
  
  # Subject Area 2: Material Compatibility
  compatibility:
    presentation: section
    works_with_materials:
      presentation: table
      items:
        - id: steel-laser-cleaning
          compatibility: excellent
          notes: "Common pairing in automotive"
        - id: copper-laser-cleaning
          compatibility: good
          notes: "Requires parameter adjustment"
    
    settings_references:
      presentation: card
      items:
        - id: aluminum-settings
          application: "Primary settings configuration"
  
  # Subject Area 3: Safety Context
  safety:
    presentation: section
    regulatory_standards:
      presentation: card
      items:
        - id: ansi-z136-1-laser-safety
          applicability: required
        - id: osha-ppe-requirements
          applicability: required
    
    hazards:
      presentation: descriptive
      items:
        - type: reflectivity
          severity: high
          description: "95% reflectivity creates eye hazard"
          mitigation: "Appropriate eyewear rated for 1064nm"
  
  # Subject Area 4: Application Context
  applications:
    presentation: section
    industries:
      presentation: card
      items:
        - industry: aerospace
          use_cases: ["Aircraft panels", "Engine components"]
        - industry: automotive
          use_cases: ["Body panels", "Heat sinks"]
    
    processes:
      presentation: table
      items:
        - process: "Pre-welding cleaning"
          parameters: "Low power, high speed"
        - process: "Paint removal"
          parameters: "Medium power, moderate speed"

# ========================================
# ASSETS (Images, Media)
# ========================================
images:
  hero:
    url: /images/material/aluminum-laser-cleaning-hero.jpg
    alt: "Aluminum surface undergoing laser cleaning"
    width: 1200
    height: 630
  micro:
    url: /images/material/aluminum-laser-cleaning-micro.jpg
    alt: "Aluminum microscopic view of laser cleaning"
    width: 800
    height: 600

# ========================================
# AUTHORSHIP
# ========================================
author:
  id: 1
  name: Yi-Chun Lin
  country: Taiwan
  title: Ph.D.
  expertise: ["Laser Materials Processing"]
  # ... author details

# ========================================
# CARD DISPLAY CONFIG
# ========================================
card:
  default:
    heading: Aluminum
    subtitle: "metal / non-ferrous"
    badge: {text: "Common", variant: "info"}
    metric: {value: "1064", unit: "nm", legend: "Optimal Wavelength"}
    severity: low
    icon: cube
```

---

## 📋 Content Type Specifics

### Materials

```yaml
content:
  seo: {...}
  editorial:
    subtitle: "..."
    description: "Full material article"
    settings_description: "Machine settings article"
  visual:
    micro: {before: "...", after: "..."}
  interactive:
    faq: [{question: "...", answer: "..."}]

relationships:
  contamination:
    affected_by: [...]
    produces: [...]
  compatibility:
    works_with_materials: [...]
    settings_references: [...]
  safety:
    regulatory_standards: [...]
    hazards: [...]
  applications:
    industries: [...]
    processes: [...]
```

### Contaminants

```yaml
content:
  seo: {...}
  editorial:
    description: "Full contaminant article"
  visual:
    appearance_details:
      presentation: descriptive
      items:
        - appearance_on_categories:
            metal: {color_variations: "...", common_patterns: "..."}
            ceramic: {color_variations: "...", common_patterns: "..."}
  interactive:
    faq: [...]  # If applicable

relationships:
  safety:
    regulatory_standards: [...]
    ppe_requirements: [...]
    toxic_gas_risk: [...]
    fumes_generated: [...]
    ventilation_requirements: [...]
  interactions:
    produces_compounds: [...]
    affects_materials: [...]
  operational:
    laser_properties: [...]
    removal_characteristics: [...]
  visual:
    appearance_on_categories: [...]  # Could be in content or relationships
```

### Settings

```yaml
content:
  seo: {...}
  editorial:
    description: "Settings guidance article"
  technical:
    machine_settings:
      presentation: table
      items:
        - parameter: powerRange
          value: 100
          unit: W
          notes: "Adjust for oxide thickness"

relationships:
  material_compatibility:
    optimized_for:
      presentation: card
      items:
        - id: aluminum-laser-cleaning
          optimization_level: primary
  equipment:
    compatible_systems:
      presentation: table
      items:
        - manufacturer: "LaserCo"
          model: "LC-1000"
          compatibility: excellent
  safety:
    regulatory_compliance: [...]
```

### Compounds

```yaml
content:
  seo: {...}
  editorial:
    description: "Compound formation article"
  chemical:
    properties:
      molecular_formula: "Fe2O3"
      cas_number: "1309-37-1"

relationships:
  formation:
    produced_by:
      presentation: card
      items:
        - id: rust-oxidation-contamination
          conditions: "Atmospheric oxidation"
  material_interactions:
    forms_on:
      presentation: card
      items:
        - id: steel-laser-cleaning
          frequency: very_common
  safety:
    hazard_classification: [...]
    handling_requirements: [...]
```

---

## 🎨 Presentation System

Each relationship section declares how it should be rendered:

```yaml
relationships:
  contamination:
    presentation: section      # Parent presentation
    affected_by:
      presentation: card       # Child presentation
      items: [...]
```

**Presentation Types:**
- `section` - Major collapsible section
- `card` - Card grid layout
- `table` - Tabular data display
- `descriptive` - Rich text with structured data
- `list` - Simple list layout
- `timeline` - Temporal sequence
- `comparison` - Side-by-side comparison

---

## 🔄 Migration Strategy

### Phase 1: Schema Definition (Week 1)
1. ✅ Define unified schema v6.0.0
2. ✅ Create TypeScript interfaces
3. ✅ Update validation schemas
4. ✅ Document migration guides

### Phase 2: Contaminants (Week 2)
1. Minor adjustments (already close to target)
2. Move visual content under `content.visual`
3. Ensure all relationships have presentation keys

### Phase 3: Materials (Week 3-4)
1. Create `content` section
2. Move micro/faq/components into `content`
3. Restructure relationships by subject area
4. Add presentation metadata

### Phase 4: Settings & Compounds (Week 5)
1. Apply unified schema
2. Populate relationship sections
3. Add presentation metadata

### Phase 5: Validation & Testing (Week 6)
1. Run migration scripts
2. Validate all frontmatter files
3. Test component rendering
4. Update documentation

---

## 🛠️ Implementation Tools

### Migration Script Structure

```typescript
// migrate-to-unified-schema.ts

interface UnifiedFrontmatter {
  // Metadata
  id: string;
  name: string;
  category: string;
  
  // Content sections
  content: {
    seo: {...};
    editorial: {...};
    visual: {...};
    interactive: {...};
  };
  
  // Properties (technical data)
  properties: {...};
  
  // Relationships (cross-references)
  relationships: {
    [subjectArea: string]: {
      presentation: 'section';
      [relationshipType: string]: {
        presentation: PresentationType;
        items: Array<{...}>;
      };
    };
  };
  
  // Assets
  images: {...};
  
  // Authorship
  author: {...};
}

async function migrateMaterial(oldFormat: any): Promise<UnifiedFrontmatter> {
  return {
    // Copy metadata as-is
    ...extractMetadata(oldFormat),
    
    // Restructure content
    content: {
      seo: {
        page_title: oldFormat.page_title,
        page_description: oldFormat.page_description,
        meta_description: oldFormat.meta_description,
      },
      editorial: {
        subtitle: oldFormat.components?.subtitle,
        description: oldFormat.components?.description,
        settings_description: oldFormat.components?.settings_description,
      },
      visual: {
        micro: oldFormat.micro,
      },
      interactive: {
        faq: oldFormat.faq,
      },
    },
    
    // Properties stay same
    properties: oldFormat.properties,
    
    // Restructure relationships
    relationships: {
      contamination: {
        presentation: 'section',
        affected_by: {
          presentation: 'card',
          items: oldFormat.contamination?.valid?.map(id => ({
            id,
            frequency: 'common',
          })) || [],
        },
      },
      // ... other subject areas
    },
    
    // Copy assets/author as-is
    images: oldFormat.images,
    author: oldFormat.author,
  };
}
```

---

## 📊 Benefits Analysis

### Developer Experience
- ✅ **Obvious structure**: `relationships.safety` vs scattered fields
- ✅ **Consistent patterns**: All content types use same structure
- ✅ **Type safety**: Clear interfaces for all sections
- ✅ **Easy navigation**: Subject areas are self-documenting

### Content Quality
- ✅ **Clear separation**: Content vs data vs relationships
- ✅ **Rich context**: Relationships have metadata (frequency, severity, etc.)
- ✅ **Presentation hints**: Components know how to render each section
- ✅ **Scalability**: Easy to add new subject areas

### Maintenance
- ✅ **Single source**: One schema for all content types
- ✅ **Clear ownership**: Each section has obvious purpose
- ✅ **Easy updates**: Add new relationship types without breaking existing
- ✅ **Validation**: Schema-driven validation catches errors

### Component Rendering
```typescript
// Before (scattered)
if (material.micro) renderMicro(material.micro);
if (material.faq) renderFAQ(material.faq);
if (material.relationships?.interactions?.contaminated_by) ...;

// After (unified)
material.content.sections.forEach(section => {
  renderSection(section, section.presentation);
});

material.relationships.subjectAreas.forEach(area => {
  renderSubjectArea(area, area.presentation);
});
```

---

## 🚦 Decision Points

### ✅ Approved Changes
- Move to subject-area concentration under `relationships`
- Create `content` parent key for all generated text
- Add `presentation` metadata to all relationship sections

### ⏳ Pending Decisions
1. **Schema version**: Jump to v6.0.0 or increment to v5.1.0?
2. **Migration timing**: All at once or phased by domain?
3. **Backward compatibility**: Support old schema during transition?
4. **Validation**: Strict (fail on old format) or permissive (warn only)?

### 🔄 Backward Compatibility Options

**Option A: Hard Break (Recommended)**
- Update all frontmatter at once
- Components only support new schema
- Clean, no technical debt
- Risk: Downtime during migration

**Option B: Dual Support**
- Components support both schemas
- Gradual migration per domain
- Safe, no downtime
- Risk: Technical debt, complex code

---

## 🎯 Recommended Actions by Domain

### 1️⃣ Materials (HIGH PRIORITY - Most Work Needed)

**Immediate Fixes:**
1. ❌ **Remove duplicate `micro`** - Keep only in `content.visual.micro`
2. ❌ **Remove duplicate `faq`** - Keep only in `relationships.operational.expert_answers`
3. ❌ **Eliminate `components`** - Unclear purpose, content belongs elsewhere
4. ✅ **Preserve `sectionMetadata`** - Already added, working well
5. ✅ **Expand subject areas**:
   - `contamination` → `relationships.interactions.affected_by`
   - Add `relationships.compatibility` (works_with_materials, settings_references)
   - Add `relationships.applications` (industries, processes)

**Effort**: 2-3 weeks (132 materials × ~10 minutes each)

---

### 2️⃣ Contaminants (LOW PRIORITY - Already Excellent ⭐)

**Minor Tweaks Only:**
1. ✅ **Keep current structure** - It's the gold standard
2. ⚠️ **Optional**: Move `visual.appearance_on_categories` to `content.visual` if desired
3. ✅ **Document patterns** for other domains to follow

**Effort**: 1-2 days (documentation only)

---

### 3️⃣ Settings (MEDIUM PRIORITY - Expand Subject Areas)

**Additions Needed:**
1. ✅ **Keep current structure** - Good foundation
2. ➕ **Add `relationships.compatibility`**:
   ```yaml
   compatibility:
     optimized_for_materials:
       presentation: card
       items: [{id: "...", optimization_level: "primary"}]
   ```
3. ➕ **Add `relationships.equipment`**:
   ```yaml
   equipment:
     compatible_systems:
       presentation: table
       items: [{manufacturer: "...", model: "...", compatibility: "excellent"}]
   ```
4. ➕ **Add `relationships.applications`**:
   ```yaml
   applications:
     use_cases:
       presentation: descriptive
       items: [{process: "...", parameters: "..."}]
   ```

**Effort**: 1 week (132 settings × ~5 minutes each)

---

### 4️⃣ Compounds (MEDIUM-HIGH PRIORITY - Restructure Content)

**Major Refactoring:**
1. ❌ **Move all text content to relationships**:
   - `health_effects` → `relationships.safety.health_effects`
   - `exposure_guidelines` → `relationships.safety.exposure_guidelines`
   - `detection_methods` → `relationships.detection.methods`
   - `first_aid` → `relationships.safety.first_aid`
   - `ppe_requirements` → `relationships.safety.ppe_requirements`
   - `faq` → `relationships.operational.expert_answers`

2. ✅ **Keep only metadata at top level**:
   - `chemical_formula`, `cas_number`, `molecular_weight`
   - `hazard_class`, `category`, `subcategory`

3. ➕ **Add missing subject areas**:
   ```yaml
   relationships:
     formation:
       produced_from_contaminants: {...}
       reaction_conditions: {...}
     detection:
       methods: {...}
       monitoring_requirements: {...}
     handling:
       storage_requirements: {...}
       disposal_procedures: {...}
   ```

**Effort**: 1 week (9 compounds × ~60 minutes each)

---

## 📅 Phased Implementation Plan

### Phase 1: Documentation & Standards (Week 1)
- ✅ Finalize unified schema v6.0.0
- ✅ Document contaminants as reference model
- ✅ Create TypeScript interfaces
- ✅ Update validation schemas
- ✅ Create migration scripts template

### Phase 2: Quick Wins - Settings (Week 2)
- Expand subject areas (compatibility, equipment, applications)
- Low risk, high value
- Validates migration process
- ~5 minutes per file × 132 = ~11 hours

### Phase 3: High Value - Compounds (Week 3)
- Restructure content into relationships
- Medium risk, high value
- Cleaner architecture
- ~60 minutes per file × 9 = ~9 hours

### Phase 4: Heavy Lift - Materials (Week 4-5)
- Remove duplicates (micro, faq)
- Eliminate components confusion
- Expand subject areas
- High complexity, critical for consistency
- ~10 minutes per file × 132 = ~22 hours

### Phase 5: Validation & Testing (Week 6)
- Run migration scripts
- Validate all frontmatter
- Test component rendering
- Update documentation
- Verify no regressions

---

## 🎯 Success Metrics

### Quantitative Goals
- ✅ **Zero content duplication** (currently: materials have 2+ duplicates)
- ✅ **100% subject-area concentration** (currently: 25% materials, 100% contaminants)
- ✅ **4+ subject areas per domain** (currently: 2-4 varies by domain)
- ✅ **Consistent presentation metadata** (currently: ~80% coverage)

### Qualitative Goals
- ✅ **Developer clarity**: Obvious where content belongs
- ✅ **Component simplicity**: Clear rendering logic
- ✅ **Maintenance ease**: Single location for each content type
- ✅ **Schema consistency**: All domains follow same pattern

---

## 🚦 Risk Assessment

### LOW RISK
- ✅ Settings expansion (additive only)
- ✅ Contaminants documentation (no changes)
- ✅ TypeScript interface creation

### MEDIUM RISK
- ⚠️ Compounds restructuring (content moves but no deletion)
- ⚠️ Materials duplicate removal (need careful testing)

### HIGH RISK
- 🔴 Component rendering changes (affects live site)
- 🔴 Breaking changes without backward compatibility

**Mitigation**: 
- Test on dev branch first
- Deploy with backward compatibility layer
- Monitor production errors closely
- Prepare rollback plan

---

## 📋 Implementation Checklist

**Pre-Implementation:**
- [ ] Approve unified schema proposal
- [ ] Choose migration strategy (hard break vs dual support)
- [ ] Create TypeScript interfaces
- [ ] Build automated migration scripts
- [ ] Test on 5 sample files (1 per domain + 1 extra material)

**Per Domain:**
- [ ] Run migration script
- [ ] Validate schema compliance
- [ ] Test component rendering
- [ ] Check for regressions
- [ ] Update documentation

**Post-Implementation:**
- [ ] Full site regression test
- [ ] Performance benchmarks
- [ ] SEO validation
- [ ] Deploy to production
- [ ] Monitor error logs (7 days)

---

## 🎓 Lessons from Current State

### What's Working ✅
1. **Contaminants architecture** - Perfect model to replicate
2. **sectionMetadata** - Great addition for UI rendering
3. **Presentation hints** - Components know how to display
4. **Subject-area concept** - Clear organization emerging

### What's Not Working ❌
1. **Content duplication** - Maintenance nightmare (micro + faq in 2 places)
2. **Inconsistent patterns** - Each domain uses different structure
3. **`components` confusion** - Unclear purpose, content mixed
4. **Scattered content** - Hard to find authoritative source

### What to Replicate 🎯
1. **Contaminant subject areas**: safety, interactions, visual, operational
2. **Rich relationship items**: Not just IDs, but full context
3. **Clear hierarchy**: Parent subject areas → child relationships → items
4. **Presentation metadata**: Hints for component rendering

---

## 💡 Next Steps
1. **Schema version**: Jump to v6.0.0 or increment to v5.1.0?
2. **Migration timing**: All at once or phased by content type?
3. **Backward compatibility**: Support old schema during transition?
4. **Validation**: Strict (fail on old format) or permissive (warn only)?

### 🔄 Backward Compatibility Options

**Option A: Hard Break (Recommended)**
- Update all frontmatter at once
- Components only support new schema
- Clean, no technical debt
- Risk: Downtime during migration

**Option B: Dual Support**
- Components support both schemas
- Gradual migration per content type
- Safe, no downtime
- Risk: Technical debt, complex code

---

## 📝 Next Steps

1. **Review this proposal** and approve/modify structure
2. **Choose migration option** (hard break vs dual support)
3. **Create TypeScript interfaces** for new schema
4. **Build migration scripts** for automated conversion
5. **Test on sample files** (1-2 materials, 1 contaminant)
6. **Execute migration** (all files)
7. **Update components** to render new structure
8. **Update documentation** with new schema

---

## 📚 Related Documentation

- `docs/01-core/frontmatter/FRONTMATTER_CURRENT_STRUCTURE.md` - Current state
- `docs/COLLAPSIBLE_NORMALIZATION_SCHEMA-2.md` - Collapsible UI patterns
- `types/centralized.ts` - TypeScript type definitions
- `schemas/*.json` - JSON schema validation files

---

**Status**: 🔴 AWAITING APPROVAL  
**Priority**: HIGH - Affects all content rendering  
**Estimated Effort**: 2-3 weeks for complete migration  
**Risk**: Medium - Requires careful testing but clear path forward
