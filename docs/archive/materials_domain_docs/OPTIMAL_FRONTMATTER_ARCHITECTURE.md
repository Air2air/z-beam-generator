# Optimal Frontmatter Architecture Proposal
**Date:** November 12, 2025  
**Context:** Unifying materials and settings frontmatter for the same materials

---

## Current Problem

**Two separate files for the same material:**
- `/frontmatter/materials/aluminum-laser-cleaning.yaml` (15KB)
- `/frontmatter/settings/aluminum-settings.yaml` (10KB optimized, was 26KB)

**Issues:**
1. **Duplication:** Basic machine settings exist in both files
2. **Split content:** Material properties in one file, settings details in another
3. **Maintenance:** Updates require touching 2 files
4. **Complexity:** Developer must understand which file contains what data
5. **Navigation:** Two separate URLs for related content about the same material

---

## Proposed Architecture

### Option 1: Single Unified File (Recommended)

**Concept:** One comprehensive YAML file per material with clear section organization

```
/frontmatter/materials/aluminum-laser-cleaning.yaml (unified)
├─ Core Metadata (author, category, SEO)
├─ Material Properties (physical, thermal, optical)
├─ Machine Settings (basic parameters for materials page)
├─ Settings Authority (detailed parameters for settings page)
├─ Challenges & Troubleshooting (diagnostic content)
└─ Research Citations (shared across all sections)
```

**URL Strategy:**
- Materials page: `/materials/metal/non-ferrous/aluminum`
- Settings page: `/settings/metal/non-ferrous/aluminum` (reads same file, different view)

**Benefits:**
- ✅ Single source of truth
- ✅ No duplication
- ✅ Easier maintenance (one file to update)
- ✅ Consistent author attribution
- ✅ Shared research citations
- ✅ Clear section boundaries

**File Structure:**
```yaml
# ============================================================================
# UNIFIED ALUMINUM LASER CLEANING FRONTMATTER
# Materials Page: /materials/metal/non-ferrous/aluminum
# Settings Page: /settings/metal/non-ferrous/aluminum
# ============================================================================

# ----------------------------------------------------------------------------
# CORE METADATA (Shared by both pages)
# ----------------------------------------------------------------------------
name: "Aluminum"
slug: "aluminum-laser-cleaning"
category: "metal"
subcategory: "non-ferrous"

author:
  name: "Todd Dunning"
  jobTitle: "Junior Optical Materials Specialist"
  affiliation:
    name: "Coherent Inc."
    type: "Organization"
  expertise:
    - "Optical Materials for Laser Systems"
    - "Laser Optics Design"
    - "Industrial Laser Processing"
  credentials:
    - "MA Optics and Photonics, UC Irvine, 2019"
    - "3+ years in laser systems development"
  email: "info@z-beam.com"

# Materials page metadata
materials_page:
  title: "Aluminum Laser Cleaning"
  subtitle: "Precision Laser Cleaning for Aluminum Surfaces"
  description: "Comprehensive guide to laser cleaning aluminum..."
  images:
    hero: "/images/material/aluminum-laser-cleaning-hero.jpg"
    micro: "/images/material/aluminum-laser-cleaning-micro.jpg"
  caption:
    before: "Surface shows degraded microstructure..."
    after: "Superior restoration quality achieved..."

# Settings page metadata
settings_page:
  title: "Aluminum Laser Cleaning Settings - Complete Parameter Guide"
  subtitle: "Research-Validated Parameters for Safe, Effective Processing"
  description: "Essential parameters with damage thresholds..."
  keywords:
    - "aluminum laser cleaning settings"
    - "laser cleaning parameters aluminum"

# ----------------------------------------------------------------------------
# MATERIAL PROPERTIES (Materials page primary, Settings reference)
# ----------------------------------------------------------------------------
material_properties:
  physical:
    density: { value: 2.7, unit: "g/cm³", range: [2.6, 2.8] }
    tensile_strength: { value: 310, unit: "MPa", range: [90, 310] }
    hardness: { value: 0.95, unit: "GPa", range: [0.2, 1.5] }
    melting_point: { value: 933.47, unit: "K", range: [893, 943] }
    boiling_point: { value: 2792, unit: "K", range: [2740, 2800] }
  
  thermal:
    thermal_conductivity: { value: 167, unit: "W/(m·K)", range: [150, 205] }
    thermal_diffusivity: { value: 6.4e-05, unit: "m²/s", range: [6.0e-05, 8.0e-05] }
    specific_heat: { value: 896, unit: "J/(kg·K)", range: [880, 920] }
    thermal_expansion: { value: 23.6e-06, unit: "1/K", range: [22.0e-06, 25.0e-06] }
    thermal_shock_resistance: { value: 250, unit: "K", range: [200, 350] }
  
  optical:
    absorptivity_1064nm: { value: 0.08, unit: "dimensionless", range: [0.02, 0.15] }
    reflectivity_1064nm: { value: 0.92, unit: "dimensionless", range: [0.85, 0.98] }
    absorption_coefficient: { value: 1200000, unit: "m⁻¹", range: [800000, 2000000] }
  
  laser_interaction:
    ablation_threshold: { value: 1.2, unit: "J/cm²", range: [0.8, 2.5] }
    damage_threshold: { value: 3.5, unit: "J/cm²", range: [2.0, 8.0] }
    thermal_relaxation_time: { value: 5.0e-09, unit: "s", range: [1.0e-09, 10.0e-09] }
    heat_affected_zone_depth: { value: 50, unit: "μm", range: [20, 100] }

# ----------------------------------------------------------------------------
# MACHINE SETTINGS (Dual-purpose: Materials display + Settings detail)
# ----------------------------------------------------------------------------
machine_settings:
  # Basic parameters (displayed on materials page)
  basic:
    power_range: { value: 100, unit: "W", range: [50, 150], optimal: [80, 120] }
    wavelength: { value: 1064, unit: "nm", range: [1030, 1090], optimal: [1064, 1064] }
    spot_size: { value: 8, unit: "mm", range: [5, 12], optimal: [7, 9] }
    repetition_rate: { value: 30, unit: "kHz", range: [20, 50], optimal: [25, 35] }
    energy_density: { value: 3, unit: "J/cm²", range: [2, 4.5], optimal: [2.5, 3.5] }
    pulse_width: { value: 10, unit: "ns", range: [8, 15], optimal: [9, 12] }
    scan_speed: { value: 1000, unit: "mm/s", range: [500, 2000], optimal: [800, 1200] }
    pass_count: { value: 2, unit: "passes", range: [1, 3], optimal: [2, 2] }
    overlap_ratio: { value: 60, unit: "%", range: [50, 75], optimal: [55, 65] }
  
  # Detailed parameters (used by settings page only)
  detailed:
    power_range:
      criticality: "high"
      precision: "±5W"
      rationale: |
        Aluminum's high thermal conductivity ({{thermal_conductivity}}) requires 
        precise power control. Power density must be maintained at 0.8-1.2 MW/cm².
      damage_threshold:
        too_low: "Incomplete oxide removal, residual contamination"
        too_high: "Surface melting, oxidation layer formation, roughness >2μm Ra"
        warning_signs:
          - "Visual discoloration (blue/yellow tint)"
          - "Melt pool formation or surface rippling"
      material_interaction:
        mechanism: "Photothermal ablation with plasma-assisted removal"
        dominant_factor: "Thermal diffusion length (380nm @ 10ns)"
        critical_parameter: "Peak power density"
        energy_coupling: "Absorption increases 0.05→0.35 (oxide layer)"
      research: [Zhang2021, Kumar2022]
    
    # ... (repeat for other 8 parameters with same detail structure)

# ----------------------------------------------------------------------------
# CHALLENGES & TROUBLESHOOTING (Settings page exclusive)
# ----------------------------------------------------------------------------
challenges:
  surface_characteristics:
    - challenge: "Native oxide layer regeneration"
      severity: "high"
      impact: "Al₂O₃ forms within seconds, affecting adhesion"
      solutions:
        - "Inert atmosphere (Argon, <100ppm O₂)"
        - "Apply coating within 5 minutes"
      prevention: "Store in controlled atmosphere"
      research: [Martinez2023]
  
  thermal_management:
    - challenge: "Thermal accumulation in multi-pass"
      severity: "high"
      impact: "Temperature rise causes oxidation, warping"
      solutions:
        - "30-60 second cooling between passes"
        - "Reduce rep rate for subsequent passes"
      prevention: "IR pyrometry monitoring, limit to <150°C"
      research: [Oltra2021]
  
  # ... (contamination_challenges, safety_compliance)

troubleshooting:
  - symptom: "Incomplete contamination removal"
    causes:
      - "Energy density below threshold (<2 J/cm²)"
      - "Insufficient overlap (<50%)"
    solutions:
      - "Increase power to 120W or reduce spot to 7mm"
      - "Reduce scan speed to 800 mm/s"
    verification: "Visual inspection, XPS surface chemistry"
    prevention: "Pre-process surface characterization"
    research: [Veiko2022]
  
  # ... (4 more troubleshooting issues)

# ----------------------------------------------------------------------------
# RESEARCH CITATIONS (Shared across all sections)
# ----------------------------------------------------------------------------
research_library:
  Zhang2021:
    author: "Zhang et al."
    year: 2021
    title: "Laser cleaning of aluminum alloys: Process optimization"
    journal: "Applied Surface Science"
    doi: "10.1016/j.apsusc.2021.149876"
    key_finding: "Power range 80-120W optimal for 6061-T6, minimal HAZ at 100W"
    url: "https://doi.org/10.1016/j.apsusc.2021.149876"
  
  Kumar2022:
    author: "Kumar & Lee"
    year: 2022
    title: "Thermal effects in nanosecond laser cleaning"
    journal: "Journal of Materials Processing Technology"
    doi: "10.1016/j.jmatprotec.2022.117534"
    key_finding: "Damage threshold 1.5 MW/cm² for aluminum alloys"
    url: "https://doi.org/10.1016/j.jmatprotec.2022.117534"
  
  # ... (4 more citations)

# ----------------------------------------------------------------------------
# FAQ (Materials page)
# ----------------------------------------------------------------------------
faq:
  - question: "How does laser cleaning remove oxidation from aluminum?"
    answer: "Laser vaporizes oxide layers without damaging base metal..."
  # ... (6 more FAQs)

# ----------------------------------------------------------------------------
# REGULATORY STANDARDS (Materials page)
# ----------------------------------------------------------------------------
regulatory_standards:
  - name: "ANSI Z136.1"
    description: "Safe Use of Lasers"
    url: "https://webstore.ansi.org/..."
  # ... (FDA, IEC, OSHA)
```

---

## Option 2: Nested Directory Structure

**Concept:** Organize by material first, then by content type

```
/frontmatter/materials/
  aluminum/
    ├── _core.yaml          # Shared metadata, author
    ├── properties.yaml     # Material properties
    ├── settings.yaml       # Machine settings (basic + detailed)
    ├── challenges.yaml     # Challenges & troubleshooting
    └── research.yaml       # Citations library
```

**Benefits:**
- Clear separation of concerns
- Easier to find specific content
- Can update one section without touching others

**Drawbacks:**
- More complex loading logic
- Need to merge 5 files for each page
- Potential for inconsistency across files

---

## Option 3: Inheritance Model

**Concept:** Base material file + settings extension

```yaml
# /frontmatter/materials/aluminum-laser-cleaning.yaml (BASE)
name: "Aluminum"
material_properties: { ... }
machine_settings:
  basic: { ... }  # Simple parameters
faq: { ... }

# /frontmatter/settings/aluminum-settings.yaml (EXTENDS)
$extends: "materials/aluminum-laser-cleaning"
machine_settings:
  detailed: { ... }  # Add detailed parameters
  challenges: { ... }
  troubleshooting: { ... }
research_library: { ... }
```

**Benefits:**
- Base material file stays simple
- Settings adds complexity only where needed
- Clear inheritance chain

**Drawbacks:**
- Need to implement YAML inheritance
- Harder to see complete picture
- Potential confusion about what overrides what

---

## Recommended Approach: Option 1 (Unified File)

### Why Unified is Best

1. **Single Source of Truth**
   - One file per material = one update point
   - No risk of data drift
   - Easy to keep consistent

2. **Content Relationships**
   - Settings reference material properties directly
   - Research citations used across sections
   - Author applies to entire material

3. **Simplified Mental Model**
   ```
   aluminum-laser-cleaning.yaml
   ├─ Used by /materials/metal/non-ferrous/aluminum
   └─ Used by /settings/metal/non-ferrous/aluminum
   ```

4. **Maintenance Benefits**
   - Add new research citation once, use everywhere
   - Update thermal conductivity once, propagates to settings rationale
   - Change author once, both pages updated

5. **Size is Reasonable**
   ```
   Current split:  15KB (materials) + 10KB (settings) = 25KB total
   Unified:        ~18KB (remove duplication, shared citations)
   ```

### Implementation Strategy

#### Phase 1: Create Unified Schema
```typescript
interface UnifiedMaterialFrontmatter {
  // Core metadata (shared)
  name: string;
  slug: string;
  category: string;
  subcategory: string;
  author: AuthorEEAT;
  
  // Page-specific metadata
  materials_page: MaterialsPageMetadata;
  settings_page: SettingsPageMetadata;
  
  // Content sections
  material_properties: MaterialProperties;
  machine_settings: {
    basic: BasicMachineSettings;      // Materials page
    detailed: DetailedMachineSettings; // Settings page
  };
  challenges?: ChallengesSection;      // Settings only
  troubleshooting?: TroubleshootingSection; // Settings only
  research_library: ResearchLibrary;   // Shared
  faq: FAQ[];                          // Materials only
  regulatory_standards: Standard[];    // Materials only
}
```

#### Phase 2: Update Content API
```typescript
// app/utils/contentAPI.ts

export async function getUnifiedMaterial(slug: string) {
  const content = await loadYaml(`frontmatter/materials/${slug}.yaml`);
  return content;
}

// Materials page uses full content
export async function getMaterialArticle(slug: string) {
  return getUnifiedMaterial(slug);
}

// Settings page uses same content, different view
export async function getSettingsArticle(slug: string) {
  return getUnifiedMaterial(slug);
}
```

#### Phase 3: Update Page Components
```typescript
// Materials page: use materials_page metadata + material_properties + faq
export default async function MaterialsPage({ params }) {
  const material = await getMaterialArticle(slug);
  
  return (
    <Layout metadata={material.materials_page}>
      <MaterialProperties data={material.material_properties} />
      <BasicMachineSettings data={material.machine_settings.basic} />
      <FAQ items={material.faq} />
      <Citations library={material.research_library} />
    </Layout>
  );
}

// Settings page: use settings_page metadata + detailed settings + challenges
export default async function SettingsPage({ params }) {
  const material = await getSettingsArticle(slug);
  
  return (
    <SettingsLayout 
      metadata={material.settings_page}
      materialProperties={material.material_properties}
    >
      <ParameterRelationships data={material.machine_settings.detailed} />
      <DiagnosticCenter 
        challenges={material.challenges}
        troubleshooting={material.troubleshooting}
      />
      <Citations library={material.research_library} />
    </SettingsLayout>
  );
}
```

#### Phase 4: Migration Path
1. **Week 1:** Create first unified file (aluminum)
2. **Week 2:** Update content API to support unified format
3. **Week 3:** Update both page components to read unified format
4. **Week 4:** Test thoroughly
5. **Week 5:** Migrate remaining materials
6. **Week 6:** Remove old split files

### Validation Rules

```yaml
# Unified file must have:
required:
  - name
  - slug
  - category
  - author
  - materials_page
  - material_properties
  - machine_settings.basic

# Settings content is optional (some materials may not need settings page)
optional:
  - settings_page           # If present, enables settings page
  - machine_settings.detailed
  - challenges
  - troubleshooting

# Validation: Settings page requires detailed content
if settings_page exists:
  require:
    - machine_settings.detailed
    - research_library
```

---

## Size Comparison

### Current (Split Files)
```
materials/aluminum-laser-cleaning.yaml:  15KB
  ├─ Metadata: 2KB
  ├─ Material properties: 8KB
  ├─ Basic machine settings: 2KB
  ├─ FAQ: 2KB
  └─ Standards: 1KB

settings/aluminum-settings.yaml:        10KB
  ├─ Metadata: 1KB
  ├─ Detailed parameters: 5KB
  ├─ Challenges: 2KB
  ├─ Troubleshooting: 1KB
  └─ Research citations: 1KB

Total: 25KB across 2 files
```

### Proposed (Unified)
```
materials/aluminum-laser-cleaning.yaml:  18KB (single file)
  ├─ Core metadata (shared): 2KB
  ├─ Page-specific metadata: 1KB
  ├─ Material properties: 8KB
  ├─ Machine settings (basic + detailed): 5KB
  ├─ Challenges & troubleshooting: 3KB
  ├─ Research library (shared): 1KB
  ├─ FAQ: 2KB
  └─ Standards: 1KB

Total: 18KB in 1 file
Savings: 7KB (28% reduction) + simpler maintenance
```

---

## Benefits Summary

### Developer Experience
- ✅ One file to edit per material
- ✅ Clear section organization
- ✅ Easy to find all content about a material
- ✅ Reduced cognitive load

### Content Quality
- ✅ Consistent author attribution
- ✅ Shared research citations
- ✅ Material properties always in sync
- ✅ No duplication = no drift

### Performance
- ✅ Single file read instead of two
- ✅ Smaller total size (18KB vs 25KB)
- ✅ Can cache one file for both pages

### Maintainability
- ✅ Update material property once
- ✅ Add research citation once
- ✅ Change author once
- ✅ Less chance of errors

---

## Migration Example

### Before (Split)
```yaml
# materials/aluminum-laser-cleaning.yaml (15KB)
name: Aluminum
author: { ... }
materialProperties:
  thermalConductivity: { value: 167, unit: "W/(m·K)" }
machineSettings:
  powerRange: { value: 80, unit: W }

# settings/aluminum-settings.yaml (10KB)
name: Aluminum Laser Cleaning Settings
author: { ... }  # Duplicated
materialRef: "aluminum-laser-cleaning"  # Reference
components:
  parameter_relationships:
    - id: powerRange
      value: 100  # Slightly different from materials!
      rationale: "Aluminum's high thermal conductivity (205 W/m·K)..."  # Hardcoded!
```

### After (Unified)
```yaml
# materials/aluminum-laser-cleaning.yaml (18KB)
name: "Aluminum"
slug: "aluminum-laser-cleaning"
author: { ... }  # Single source

materials_page:
  title: "Aluminum Laser Cleaning"
settings_page:
  title: "Aluminum Laser Cleaning Settings"

material_properties:
  thermal:
    thermal_conductivity: { value: 167, unit: "W/(m·K)" }

machine_settings:
  basic:
    power_range: { value: 100, unit: W, optimal: [80, 120] }
  detailed:
    power_range:
      criticality: high
      rationale: |
        Aluminum's high thermal conductivity ({{thermal_conductivity}}) 
        requires precise power control.  # Template variable!
      research: [Zhang2021]

research_library:
  Zhang2021: { ... }
```

**No duplication, no drift, single source of truth!**

---

## Recommendation

**Implement Option 1: Single Unified File**

This approach:
1. Eliminates all duplication between materials and settings
2. Creates single source of truth per material
3. Reduces total file size by 28%
4. Simplifies maintenance significantly
5. Improves content consistency
6. Maintains clear section organization
7. Enables both pages from one file

**Next Steps:**
1. Create unified schema definition
2. Migrate aluminum as proof of concept
3. Test both materials and settings pages
4. Roll out to remaining materials
5. Deprecate split file structure

---

**Questions to resolve:**
1. Should we keep separate URLs (/materials/... and /settings/...) or consolidate?
   - **Answer:** Keep separate URLs, both read same unified file
2. How should we handle materials that don't need a settings page?
   - **Answer:** Make settings_page, detailed machine_settings, challenges, troubleshooting all optional
3. Should research_library be optional or required?
   - **Answer:** Required if ANY citations are present. Empty if no citations yet researched.

---

## Citation Architecture (CRITICAL REQUIREMENT)

### Core Principle: NO FALLBACKS, NO DEFAULTS

**Every data point MUST have explicit citations or be marked as "needs_research".**

**FORBIDDEN:**
- ❌ `source: "literature"` (too vague)
- ❌ `source: "estimated"` (not acceptable)
- ❌ `source: "typical value"` (no defaults allowed)
- ❌ Empty source field
- ❌ Category-level fallback ranges

**REQUIRED:**
- ✅ Explicit citation ID referencing research_library
- ✅ Confidence score (85-100%)
- ✅ Multiple sources when available
- ✅ `needs_research: true` flag if data incomplete

### Citation Structure for All Fields

```yaml
# ----------------------------------------------------------------------------
# CITATION ARCHITECTURE (Required for ALL data fields)
# ----------------------------------------------------------------------------

# Example 1: Material Property with Full Citations
material_properties:
  physical:
    density:
      value: 2.7
      unit: g/cm³
      range: [2.6, 2.8]
      confidence: 95
      
      # REQUIRED: Citations with multi-source support
      citations:
        primary:
          id: ASTM_C615_2023
          relevance: "Industry standard specification for granite dimension stone"
          specific_location: "Table 1, Physical Properties"
          confidence: 98
        
        supporting:
          - id: USGS_2023
            value: 2.75
            confidence: 97
            notes: "High-feldspar Sierra Nevada granite specimens"
            variance_explanation: "+1.9% due to increased feldspar content"
          
          - id: Schon2015
            value: 2.65
            confidence: 97
            notes: "Quartz-rich New England granite specimens"
            variance_explanation: "-1.9% due to higher quartz/lower feldspar ratio"
          
          - id: AI_Research_DeepSeek_20251107
            value: 2.7
            confidence: 90
            notes: "Multi-source synthesis validated against 8 geological databases"
            validation_status: "peer_review_pending"
      
      source_summary:
        total_sources: 4
        primary_source_type: "industry_standard"
        validation_status: "peer_reviewed"
        last_updated: "2025-11-07"
        needs_research: false
    
    # Example of incomplete data (EXPLICIT, not hidden)
    thermal_shock_resistance:
      value: null  # Explicitly null, not missing
      unit: "K"
      range: null
      confidence: 0
      
      citations: {}  # Empty, not missing
      
      source_summary:
        total_sources: 0
        needs_research: true
        research_priority: "high"
        notes: "Property not yet researched - requires experimental measurement"

# Example 2: Machine Setting with Citations
machine_settings:
  basic:
    power_range:
      value: 100
      unit: W
      range: [50, 150]
      optimal: [80, 120]
      
      # REQUIRED: At least one citation for recommended values
      citations:
        - id: Zhang2021
          relevance: "Experimental validation on 6061-T6 aluminum alloy"
          key_finding: "Power range 80-120W optimal, minimal HAZ at 100W"
          confidence: 96
          experimental_conditions:
            sample_size: 45
            wavelength: 1064
            spot_size: 8
        
        - id: Kumar2022
          relevance: "Theoretical damage threshold calculations"
          key_finding: "Power density 0.8-1.2 MW/cm² for safe cleaning"
          confidence: 94
          methodology: "Finite element thermal modeling"
      
      source_summary:
        total_sources: 2
        validation_status: "experimentally_validated"
        needs_research: false

# Example 3: Detailed Setting with Template Variables
machine_settings:
  detailed:
    power_range:
      criticality: "high"
      precision: "±5W"
      
      # Rationale can reference properties via template variables
      rationale: |
        Aluminum's high thermal conductivity ({{thermal_conductivity}}) requires 
        precise power control to maintain optimal energy density. The thermal 
        diffusion length at 10ns pulse width is ~380nm, requiring peak power 
        density between 0.8-1.2 MW/cm² to exceed ablation threshold without 
        substrate melting [Zhang2021, Kumar2022].
      
      damage_threshold:
        too_low: "Incomplete oxide removal, residual contamination >10% surface coverage"
        too_high: "Surface melting at >150W, oxidation layer reformation, roughness increase from 0.8μm to >2μm Ra"
        warning_signs:
          - "Visual discoloration (blue/yellow oxide tint)"
          - "Melt pool formation or surface rippling visible under 50x magnification"
          - "Increased reflectivity indicating new oxide layer formation"
      
      material_interaction:
        mechanism: "Photothermal ablation with plasma-assisted contaminant removal"
        dominant_factor: "Thermal diffusion length (380nm @ 10ns pulse width)"
        critical_parameter: "Peak power density (must exceed 0.5 MW/cm² for ablation)"
        energy_coupling: "Absorption increases from 0.05 (bare Al) to 0.35 (Al₂O₃ layer)"
      
      # REQUIRED: Citations for all claims
      research: [Zhang2021, Kumar2022, Martinez2023]
```

### Research Library Structure (REQUIRED)

```yaml
# ----------------------------------------------------------------------------
# RESEARCH LIBRARY (Required if any citations exist)
# ----------------------------------------------------------------------------
research_library:
  
  # Academic Journal Articles
  Zhang2021:
    type: journal_article
    author: "Zhang, L., Wang, X., Chen, M."
    year: 2021
    title: "Laser cleaning of aluminum alloys: Process optimization and surface integrity"
    journal: "Applied Surface Science"
    volume: 551
    article_id: "149876"
    doi: "10.1016/j.apsusc.2021.149876"
    url: "https://doi.org/10.1016/j.apsusc.2021.149876"
    
    abstract_snippet: "Investigated nanosecond pulsed laser cleaning of 6061-T6 aluminum alloy surfaces. Characterized oxide removal mechanisms and heat-affected zone formation across power ranges 50-200W."
    
    key_findings:
      - finding: "Power range 80-120W optimal for complete oxide removal"
        specific_value: "100W nominal, ±5W precision"
        confidence: 96
      - finding: "Minimal heat-affected zone depth at 100W, 1064nm"
        specific_value: "HAZ depth: 15-25μm"
        confidence: 95
      - finding: "Damage threshold exceeded above 150W"
        specific_value: "Surface melting observed at 155W"
        confidence: 98
    
    methodology: "Experimental study with scanning electron microscopy (SEM), energy-dispersive X-ray spectroscopy (EDS), and surface profilometry"
    sample_size: 45
    sample_material: "6061-T6 aluminum alloy"
    
    experimental_parameters:
      wavelength: 1064
      wavelength_unit: nm
      spot_size: 8
      spot_size_unit: mm
      pulse_width: 10
      pulse_width_unit: ns
      repetition_rate: 30
      repetition_rate_unit: kHz
    
    quality_indicators:
      peer_reviewed: true
      impact_factor: 6.7
      citation_count: 143
      confidence: high
      authority: high
    
    relevance_to_our_work: "Direct experimental validation of aluminum laser cleaning parameters matching our equipment specifications"
  
  # Industry Standards
  ASTM_C615_2023:
    type: industry_standard
    organization: "ASTM International"
    standard_id: "ASTM C615-23"
    title: "Standard Specification for Granite Dimension Stone"
    year: 2023
    url: "https://store.astm.org/c615.html"
    
    scope: "Covers physical and mechanical requirements for granite building dimension stone, including density, compressive strength, flexural strength, and absorption properties."
    
    key_data:
      - property: "Density"
        value: "2600-2800"
        unit: "kg/m³"
        table_location: "Table 1, Physical Properties"
        specification: "Average of 5 specimens, reported to nearest 10 kg/m³"
      
      - property: "Compressive Strength"
        value: "131-250"
        unit: "MPa"
        table_location: "Table 2, Mechanical Properties"
        specification: "Minimum average of 5 specimens"
      
      - property: "Absorption"
        value: "<0.4"
        unit: "% by weight"
        table_location: "Table 1, Physical Properties"
        specification: "Maximum average of 5 specimens"
    
    quality_indicators:
      authority: authoritative
      peer_reviewed: true
      consensus_document: true
      update_frequency: "Annual review, major revision every 5 years"
    
    relevance_to_our_work: "Industry-standard physical property specifications for commercial granite materials"
  
  # Government Databases
  USGS_2023:
    type: government_database
    organization: "U.S. Geological Survey"
    title: "USGS Mineral Commodity Summaries 2023 - Dimension Stone"
    year: 2023
    page_range: "52-53"
    url: "https://www.usgs.gov/centers/national-minerals-information-center/dimension-stone-statistics-and-information"
    
    data_coverage: "Physical and geological properties of commercial granite types from major U.S. quarries and global producers"
    geographic_scope: "United States (primary), global data (secondary)"
    
    key_data:
      - property: "Granite Density (Sierra Nevada type)"
        value: 2750
        unit: "kg/m³"
        sample_description: "Dense granite with high orthoclase feldspar content from California batholith formations"
    
    quality_indicators:
      authority: authoritative
      update_frequency: annual
      data_collection_method: "Compiled from industry reports, geological surveys, and laboratory measurements"
    
    relevance_to_our_work: "Government-validated geological property data for regional granite classifications"
  
  # Academic Textbooks
  Schon2015:
    type: textbook
    author: "Schön, J.H."
    year: 2015
    title: "Physical Properties of Rocks: Fundamentals and Principles of Petrophysics"
    edition: 2
    publisher: "Elsevier"
    isbn: "978-0-08-100404-3"
    pages: "118-125"
    chapter: "Chapter 4: Density and Porosity of Sedimentary and Crystalline Rocks"
    url: "https://www.sciencedirect.com/book/9780081004043/"
    
    key_data:
      - property: "Granite Density (quartz-rich varieties)"
        value: 2650
        unit: "kg/m³"
        context: "Light-colored granite with 40-45% quartz content, typical of New England plutonic formations"
        measurement_method: "Helium pycnometry and Archimedes method"
    
    quality_indicators:
      peer_reviewed: true
      authority: high
      academic_citations: 847
      field_standard: true
    
    relevance_to_our_work: "Academic reference for relationship between mineral composition and density in granite varieties"
  
  # AI Research (with validation status)
  AI_Research_DeepSeek_20251107:
    type: ai_research
    model: "DeepSeek R1"
    model_version: "v3.5"
    research_date: "2025-11-07T12:51:40Z"
    researcher: "Z-Beam PropertyValueResearcher"
    
    query: "Granite density ranges, mineral composition impact on density variation, laser cleaning implications"
    
    sources_consulted: 8
    source_types:
      - "Geological databases (USGS, BGS)"
      - "Academic papers (ScienceDirect, SpringerLink)"
      - "Industry handbooks (ASTM, Natural Stone Institute)"
    
    key_findings:
      - finding: "Average commercial granite density: 2700 kg/m³"
        confidence: 90
        variance_range: [2600, 2800]
        variance_explanation: "Depends on quartz vs. feldspar content ratio"
    
    raw_response: |
      Material: Granite
      Property: Density
      Description: Mass per unit volume of the material
      Unit: kg/m³ (or g/cm³)
      Relevance: Affects thermal mass and energy distribution during cleaning
      
      Laser Cleaning Impact: Influences heat diffusion rates and required energy 
      density; higher density increases thermal inertia, requiring higher laser 
      energy for effective ablation without excessive heating, while variations 
      due to mineral composition (e.g., quartz vs. feldspar content) can alter 
      local heat distribution patterns.
      
      Typical Range: 2600-2800 kg/m³ (2.6-2.8 g/cm³)
      Commercial Average: 2700 kg/m³ (2.7 g/cm³)
      
      Mineral Composition Impact:
      - High quartz (40-45%): Lower density ~2650 kg/m³
      - High feldspar (60-65%): Higher density ~2750 kg/m³
      - Mafic minerals (hornblende, biotite >20%): Highest density ~2800 kg/m³
    
    quality_indicators:
      confidence: 90
      validation_status: "needs_expert_review"
      validated_against: ["ASTM_C615_2023", "USGS_2023", "Schon2015"]
      validation_result: "Values within published ranges, composition explanations consistent with petrophysics literature"
    
    methodology: "Multi-source synthesis with geological context analysis and cross-validation against authoritative standards"
    
    limitations:
      - "AI-generated synthesis requires expert geological validation"
      - "Specific quarry variations not captured in averaged data"
      - "Weathering effects on density not quantified"
    
    relevance_to_our_work: "Initial discovery and validation framework for property research pipeline; provides baseline for expert review"

# Additional citation types as needed...
```

### Validation Rules (STRICT)

```python
def validate_frontmatter_citations(data):
    """
    Validate that ALL data fields have explicit citations.
    NO FALLBACKS, NO DEFAULTS, NO EXCEPTIONS.
    """
    
    errors = []
    
    # Validate material_properties
    for category, properties in data.get('material_properties', {}).items():
        for prop_name, prop_data in properties.items():
            
            # Check if property has value
            if prop_data.get('value') is not None:
                # Non-null value MUST have citations
                if 'citations' not in prop_data or not prop_data['citations']:
                    errors.append(f"material_properties.{category}.{prop_name} has value but NO CITATIONS")
                
                # Validate primary citation exists
                if 'citations' in prop_data:
                    if 'primary' not in prop_data['citations']:
                        errors.append(f"material_properties.{category}.{prop_name} missing PRIMARY citation")
                    
                    # Validate citation IDs exist in research_library
                    primary_id = prop_data['citations'].get('primary', {}).get('id')
                    if primary_id and primary_id not in data.get('research_library', {}):
                        errors.append(f"Citation {primary_id} referenced but not found in research_library")
                    
                    # Validate supporting citations
                    for citation in prop_data['citations'].get('supporting', []):
                        if citation['id'] not in data.get('research_library', {}):
                            errors.append(f"Citation {citation['id']} referenced but not found in research_library")
            
            else:
                # Null value MUST have needs_research flag
                if not prop_data.get('source_summary', {}).get('needs_research'):
                    errors.append(f"material_properties.{category}.{prop_name} has null value but needs_research not set to true")
    
    # Validate machine_settings.basic
    for param_name, param_data in data.get('machine_settings', {}).get('basic', {}).items():
        if 'citations' not in param_data or not param_data['citations']:
            errors.append(f"machine_settings.basic.{param_name} has NO CITATIONS")
        
        # Validate citation IDs
        for citation in param_data.get('citations', []):
            if citation['id'] not in data.get('research_library', {}):
                errors.append(f"Citation {citation['id']} referenced but not found in research_library")
    
    # Validate machine_settings.detailed (if exists)
    for param_name, param_data in data.get('machine_settings', {}).get('detailed', {}).items():
        if 'research' not in param_data or not param_data['research']:
            errors.append(f"machine_settings.detailed.{param_name} has NO research citations")
        
        # Validate citation IDs
        for citation_id in param_data.get('research', []):
            if citation_id not in data.get('research_library', {}):
                errors.append(f"Citation {citation_id} referenced but not found in research_library")
    
    # Validate research_library completeness
    for citation_id, citation_data in data.get('research_library', {}).items():
        required_fields = ['type', 'year', 'title']
        for field in required_fields:
            if field not in citation_data:
                errors.append(f"research_library.{citation_id} missing required field: {field}")
        
        # Type-specific validation
        citation_type = citation_data.get('type')
        if citation_type == 'journal_article':
            if 'doi' not in citation_data and 'url' not in citation_data:
                errors.append(f"research_library.{citation_id} (journal_article) missing DOI and URL")
        
        elif citation_type == 'industry_standard':
            if 'organization' not in citation_data:
                errors.append(f"research_library.{citation_id} (industry_standard) missing organization")
        
        elif citation_type == 'ai_research':
            if 'validation_status' not in citation_data:
                errors.append(f"research_library.{citation_id} (ai_research) missing validation_status")
            if 'model' not in citation_data:
                errors.append(f"research_library.{citation_id} (ai_research) missing model")
    
    # CRITICAL: If research_library is empty but citations exist, ERROR
    referenced_citations = set()
    # ... (collect all citation IDs as shown above)
    
    if referenced_citations and not data.get('research_library'):
        errors.append("CRITICAL: Citations referenced but research_library is empty")
    
    if errors:
        raise ValidationError(f"Citation validation failed:\n" + "\n".join(errors))
    
    return True
```

### Generator Requirements

```python
def generate_unified_material_with_citations(material_data):
    """
    Generate unified material frontmatter with strict citation enforcement.
    """
    
    # Load research data
    property_research = load_yaml('materials/data/PropertyResearch.yaml')
    setting_research = load_yaml('materials/data/SettingResearch.yaml')
    
    # Build research_library from all sources
    research_library = {}
    
    # Extract citations from PropertyResearch.yaml
    material_name = material_data['name']
    if material_name in property_research:
        for prop_name, prop_data in property_research[material_name].items():
            for source_value in prop_data.get('research', {}).get('values', []):
                citation_id = generate_citation_id(source_value)
                research_library[citation_id] = build_citation_entry(source_value)
    
    # Extract citations from SettingResearch.yaml
    if material_name in setting_research:
        for setting_name, setting_data in setting_research[material_name].items():
            for source_value in setting_data.get('research', {}).get('values', []):
                citation_id = generate_citation_id(source_value)
                research_library[citation_id] = build_citation_entry(source_value)
    
    # Build material_properties with citations
    material_properties = {}
    for category in ['physical', 'thermal', 'optical', 'laser_interaction']:
        material_properties[category] = {}
        
        for prop_name in get_properties_for_category(category):
            prop_entry = build_property_with_citations(
                material_name, 
                prop_name, 
                property_research,
                research_library
            )
            
            material_properties[category][prop_name] = prop_entry
    
    # Build machine_settings with citations
    machine_settings = {
        'basic': build_basic_settings_with_citations(
            material_name,
            setting_research,
            research_library
        )
    }
    
    # Optionally add detailed settings
    if material_data.get('has_settings_page'):
        machine_settings['detailed'] = build_detailed_settings_with_citations(
            material_name,
            setting_research,
            research_library
        )
    
    # Assemble unified frontmatter
    output = {
        'name': material_data['name'],
        'slug': f"{material_data['name'].lower()}-laser-cleaning",
        'category': material_data['category'],
        'subcategory': material_data['subcategory'],
        'author': get_author_metadata(material_data['author_id']),
        'materials_page': generate_materials_metadata(material_data),
        'material_properties': material_properties,
        'machine_settings': machine_settings,
        'research_library': research_library,  # ALWAYS include
        'faq': generate_faq(material_data),
        'regulatory_standards': get_standards(),
        'breadcrumb': generate_breadcrumb(material_data),
        '_metadata': generate_metadata()
    }
    
    # Validate before returning
    validate_frontmatter_citations(output)
    
    return output


def build_property_with_citations(material_name, prop_name, property_research, research_library):
    """
    Build property entry with explicit citations.
    NO DEFAULTS, NO FALLBACKS.
    """
    
    prop_data = property_research.get(material_name, {}).get(prop_name, {})
    
    # Check if property has been researched
    if not prop_data or not prop_data.get('research', {}).get('values'):
        # NOT RESEARCHED - explicit null
        return {
            'value': None,
            'unit': None,
            'range': None,
            'confidence': 0,
            'citations': {},
            'source_summary': {
                'total_sources': 0,
                'needs_research': True,
                'research_priority': 'high',
                'notes': f"Property {prop_name} not yet researched for {material_name}"
            }
        }
    
    # RESEARCHED - build from sources
    primary = prop_data.get('primary', {})
    sources = prop_data.get('research', {}).get('values', [])
    
    # Build citations object
    citations = {
        'primary': {
            'id': generate_citation_id(sources[0]),  # Use first source as primary
            'relevance': sources[0].get('notes', ''),
            'confidence': sources[0].get('confidence', 90)
        },
        'supporting': []
    }
    
    # Add supporting sources
    for i, source in enumerate(sources[1:], start=1):
        citations['supporting'].append({
            'id': generate_citation_id(source),
            'value': source.get('value'),
            'confidence': source.get('confidence', 90),
            'notes': source.get('notes', ''),
            'variance_explanation': calculate_variance(source['value'], primary['value'])
        })
    
    return {
        'value': primary.get('value'),
        'unit': primary.get('unit'),
        'range': [
            min(s.get('value', primary['value']) for s in sources),
            max(s.get('value', primary['value']) for s in sources)
        ],
        'confidence': primary.get('confidence', 95),
        'citations': citations,
        'source_summary': {
            'total_sources': len(sources),
            'primary_source_type': sources[0].get('source_type', 'unknown'),
            'validation_status': prop_data.get('metadata', {}).get('validation_status', 'needs_validation'),
            'last_updated': prop_data.get('metadata', {}).get('last_researched', ''),
            'needs_research': False
        }
    }
```

---

## Python Generator Implementation Guide

### Complete YAML Schema for Generator

```yaml
# ============================================================================
# UNIFIED MATERIAL FRONTMATTER SCHEMA
# Version: 2.0 (Unified Structure)
# Generated by: Z-Beam Python Frontmatter Generator
# ============================================================================

# ----------------------------------------------------------------------------
# REQUIRED: Core Metadata (all materials must have)
# ----------------------------------------------------------------------------
name: string                    # Material common name (e.g., "Aluminum")
slug: string                    # URL-safe identifier (e.g., "aluminum-laser-cleaning")
category: string                # Primary category (e.g., "metal", "ceramic", "polymer")
subcategory: string             # Secondary category (e.g., "non-ferrous", "oxide")

# ----------------------------------------------------------------------------
# REQUIRED: Author E-E-A-T Metadata
# ----------------------------------------------------------------------------
author:
  id: integer                   # Author ID (1-10)
  name: string                  # Full name
  country: string               # ISO country code
  country_display: string       # Display name
  title: string                 # Academic/professional title (e.g., "MA", "PhD")
  sex: string                   # "m" | "f"
  jobTitle: string              # Professional role
  expertise: string[]           # Array of expertise areas (3-5 items)
  affiliation:
    name: string                # Organization name
    type: string                # "Organization" | "University"
  credentials: string[]         # Array of credentials (3-5 items)
  email: string                 # Contact email
  image: string                 # Author photo path
  imageAlt: string              # Image alt text
  url: string                   # Author profile URL
  sameAs: string[]              # Social/professional profiles
  persona_file: string          # Reference to persona YAML
  formatting_file: string       # Reference to formatting YAML

# ----------------------------------------------------------------------------
# REQUIRED: Materials Page Metadata
# ----------------------------------------------------------------------------
materials_page:
  title: string                 # Page title (SEO optimized)
  subtitle: string              # Engaging subtitle with voice
  description: string           # Meta description (150-160 chars)
  datePublished: ISO8601        # Publication date
  dateModified: ISO8601         # Last modified date
  images:
    hero:
      url: string               # Hero image path
      alt: string               # Alt text
    micro:
      url: string               # Microscopic image path
      alt: string               # Alt text
  caption:
    before: string              # Before cleaning description (voice-applied)
    after: string               # After cleaning description (voice-applied)

# ----------------------------------------------------------------------------
# OPTIONAL: Settings Page Metadata (only if settings page exists)
# ----------------------------------------------------------------------------
settings_page:                  # OPTIONAL - omit if no settings page needed
  title: string                 # Settings page title
  subtitle: string              # Settings subtitle
  description: string           # Settings meta description
  keywords: string[]            # SEO keywords array (10-15 items)

# ----------------------------------------------------------------------------
# REQUIRED: Material Properties (for materials page)
# ----------------------------------------------------------------------------
material_properties:
  
  # Physical properties
  physical:
    density:
      value: float
      unit: string
      range: [float, float]     # [min, max]
      source: string            # "literature" | "measured" | "calculated"
      notes: string             # Optional context
    
    tensile_strength:
      value: float
      unit: string
      range: [float, float]
      source: string
      notes: string
    
    hardness:
      value: float
      unit: string
      range: [float, float]
      source: string
      notes: string
    
    melting_point:
      value: float
      unit: string              # "K" or "°C"
      range: [float, float]
      source: string
      notes: string
    
    boiling_point:
      value: float
      unit: string
      range: [float, float]
      source: string
      notes: string
    
    # ... (add other physical properties as needed)
  
  # Thermal properties
  thermal:
    thermal_conductivity:
      value: float
      unit: string              # "W/(m·K)"
      range: [float, float]
      source: string
      notes: string
    
    thermal_diffusivity:
      value: float
      unit: string              # "m²/s"
      range: [float, float]
      source: string
      notes: string
    
    specific_heat:
      value: float
      unit: string              # "J/(kg·K)"
      range: [float, float]
      source: string
      notes: string
    
    thermal_expansion:
      value: float
      unit: string              # "1/K" or "×10⁻⁶/K"
      range: [float, float]
      source: string
      notes: string
    
    thermal_shock_resistance:
      value: float
      unit: string              # "K" (temperature differential)
      range: [float, float]
      source: string
      notes: string
  
  # Optical properties
  optical:
    absorptivity_1064nm:
      value: float              # 0.0 to 1.0
      unit: "dimensionless"
      range: [float, float]
      source: string
      notes: string
    
    reflectivity_1064nm:
      value: float              # 0.0 to 1.0
      unit: "dimensionless"
      range: [float, float]
      source: string
      notes: string
    
    absorption_coefficient:
      value: float
      unit: string              # "m⁻¹" or "cm⁻¹"
      range: [float, float]
      source: string
      notes: string
  
  # Laser interaction properties
  laser_interaction:
    ablation_threshold:
      value: float
      unit: string              # "J/cm²"
      range: [float, float]
      source: string
      notes: string
    
    damage_threshold:
      value: float
      unit: string              # "J/cm²"
      range: [float, float]
      source: string
      notes: string
    
    thermal_relaxation_time:
      value: float
      unit: string              # "s" (seconds, typically ns)
      range: [float, float]
      source: string
      notes: string
    
    heat_affected_zone_depth:
      value: float
      unit: string              # "μm"
      range: [float, float]
      source: string
      notes: string

# ----------------------------------------------------------------------------
# REQUIRED: Machine Settings (basic for materials page)
# ----------------------------------------------------------------------------
machine_settings:
  
  # Basic parameters (displayed on materials page)
  basic:
    power_range:
      value: float              # Recommended value
      unit: string              # "W"
      range: [float, float]     # [min, max]
      optimal: [float, float]   # [optimal_min, optimal_max]
      notes: string             # Brief explanation
    
    wavelength:
      value: float
      unit: string              # "nm"
      range: [float, float]
      optimal: [float, float]
      notes: string
    
    spot_size:
      value: float
      unit: string              # "mm" or "μm"
      range: [float, float]
      optimal: [float, float]
      notes: string
    
    repetition_rate:
      value: float
      unit: string              # "kHz"
      range: [float, float]
      optimal: [float, float]
      notes: string
    
    energy_density:
      value: float
      unit: string              # "J/cm²"
      range: [float, float]
      optimal: [float, float]
      notes: string
    
    pulse_width:
      value: float
      unit: string              # "ns", "ps", or "fs"
      range: [float, float]
      optimal: [float, float]
      notes: string
    
    scan_speed:
      value: float
      unit: string              # "mm/s"
      range: [float, float]
      optimal: [float, float]
      notes: string
    
    pass_count:
      value: integer
      unit: "passes"
      range: [integer, integer]
      optimal: [integer, integer]
      notes: string
    
    overlap_ratio:
      value: float
      unit: string              # "%"
      range: [float, float]
      optimal: [float, float]
      notes: string
  
  # ----------------------------------------------------------------------------
  # OPTIONAL: Detailed parameters (for settings page only)
  # ----------------------------------------------------------------------------
  detailed:                     # OPTIONAL - only if settings_page exists
    power_range:
      criticality: string       # "critical" | "high" | "medium" | "low"
      precision: string         # e.g., "±5W"
      rationale: string         # Multi-line explanation (can use {{template_vars}})
      damage_threshold:
        too_low: string         # What happens if too low
        too_high: string        # What happens if too high
        warning_signs: string[] # Array of observable signs
      material_interaction:
        mechanism: string       # Physical mechanism description
        dominant_factor: string # Primary controlling factor
        critical_parameter: string # Most important parameter
        energy_coupling: string # How energy couples to material
      research: string[]        # Array of citation IDs referencing research_library
    
    wavelength:
      # ... (same structure as power_range)
    
    spot_size:
      # ... (same structure)
    
    # ... (repeat for all 9 parameters)

# ----------------------------------------------------------------------------
# OPTIONAL: Challenges (settings page only)
# ----------------------------------------------------------------------------
challenges:                     # OPTIONAL - only if settings_page exists
  
  surface_characteristics:
    - challenge: string         # Challenge name
      severity: string          # "critical" | "high" | "medium" | "low"
      impact: string            # Description of impact
      solutions: string[]       # Array of solution approaches
      prevention: string        # Preventive measures
      research: string[]        # Optional: citation IDs
  
  thermal_management:
    - challenge: string
      severity: string
      impact: string
      solutions: string[]
      prevention: string
      research: string[]
  
  contamination_challenges:
    - challenge: string
      severity: string
      impact: string
      solutions: string[]
      prevention: string
      research: string[]
  
  safety_compliance:
    - challenge: string
      severity: string
      impact: string
      solutions: string[]
      prevention: string
      research: string[]

# ----------------------------------------------------------------------------
# OPTIONAL: Troubleshooting (settings page only)
# ----------------------------------------------------------------------------
troubleshooting:                # OPTIONAL - only if settings_page exists
  - symptom: string             # Observable problem
    causes: string[]            # Array of possible causes
    solutions: string[]         # Array of solutions
    verification: string        # How to verify fix
    prevention: string          # How to prevent in future
    research: string[]          # Optional: citation IDs

# ----------------------------------------------------------------------------
# OPTIONAL: Research Library (settings page only)
# ----------------------------------------------------------------------------
research_library:               # OPTIONAL - only if settings_page exists
  CitationID:                   # Unique citation identifier (e.g., "Zhang2021")
    author: string              # Author(s) name
    year: integer               # Publication year
    title: string               # Paper title
    journal: string             # Journal name
    doi: string                 # DOI identifier
    key_finding: string         # Summary of relevant finding
    url: string                 # Full DOI URL

# ----------------------------------------------------------------------------
# REQUIRED: FAQ (materials page)
# ----------------------------------------------------------------------------
faq:
  - question: string            # Question with **bold keywords**
    answer: string              # Answer with voice-applied language

# ----------------------------------------------------------------------------
# REQUIRED: Regulatory Standards (materials page)
# ----------------------------------------------------------------------------
regulatory_standards:
  - name: string                # Standard acronym (e.g., "ANSI")
    description: string         # Full standard name
    url: string                 # Standard URL
    image: string               # Logo path

# ----------------------------------------------------------------------------
# OPTIONAL: Internal Metadata (generator tracking)
# ----------------------------------------------------------------------------
_metadata:
  voice:
    author_name: string
    author_country: string
    voice_applied: boolean
    content_type: string        # "material"
  material_metadata:
    last_updated: ISO8601
    normalization_applied: boolean
    restructured_date: ISO8601
    structure_version: string   # "2.0"

# ----------------------------------------------------------------------------
# OPTIONAL: Breadcrumb (for navigation)
# ----------------------------------------------------------------------------
breadcrumb:
  - label: string
    href: string
```

### Template Variable Substitution

**In detailed settings rationale, use template variables:**

```yaml
rationale: |
  {{material_name}}'s {{thermal_conductivity}} requires precise control.
  Below {{optimal_min}} results in incomplete removal.
```

**Generator should replace at generation time:**
- `{{material_name}}` → `material_properties.name`
- `{{thermal_conductivity}}` → `material_properties.thermal.thermal_conductivity.value` + `unit`
- `{{optimal_min}}` → `machine_settings.basic.power_range.optimal[0]`

### Generator Logic

```python
def generate_unified_material(material_data):
    """
    Generate unified material frontmatter.
    
    Args:
        material_data: Dictionary with material info
    
    Returns:
        YAML string for unified frontmatter
    """
    
    # Always include
    output = {
        'name': material_data['name'],
        'slug': f"{material_data['name'].lower()}-laser-cleaning",
        'category': material_data['category'],
        'subcategory': material_data['subcategory'],
        'author': get_author_metadata(material_data['author_id']),
        'materials_page': generate_materials_metadata(material_data),
        'material_properties': generate_properties(material_data),
        'machine_settings': {
            'basic': generate_basic_settings(material_data)
        },
        'faq': generate_faq(material_data),
        'regulatory_standards': get_standards(),
        'breadcrumb': generate_breadcrumb(material_data),
        '_metadata': generate_metadata()
    }
    
    # Conditionally add settings page content
    if material_data.get('has_settings_page'):
        output['settings_page'] = generate_settings_metadata(material_data)
        output['machine_settings']['detailed'] = generate_detailed_settings(material_data)
        output['challenges'] = generate_challenges(material_data)
        output['troubleshooting'] = generate_troubleshooting(material_data)
        output['research_library'] = generate_research_library(material_data)
    
    return yaml.dump(output, allow_unicode=True, sort_keys=False)
```

### Validation Rules

```python
def validate_unified_frontmatter(data):
    """Validate unified frontmatter structure."""
    
    # Required fields
    assert 'name' in data
    assert 'slug' in data
    assert 'category' in data
    assert 'author' in data
    assert 'materials_page' in data
    assert 'material_properties' in data
    assert 'machine_settings' in data
    assert 'basic' in data['machine_settings']
    assert 'faq' in data
    
    # If settings_page exists, require settings-specific content
    if 'settings_page' in data:
        assert 'detailed' in data['machine_settings'], "settings_page requires detailed machine_settings"
        assert 'research_library' in data, "settings_page should have research_library"
        # challenges and troubleshooting are optional but recommended
    
    # Validate property structure
    assert 'physical' in data['material_properties']
    assert 'thermal' in data['material_properties']
    assert 'optical' in data['material_properties']
    assert 'laser_interaction' in data['material_properties']
    
    # Validate basic machine settings (9 parameters required)
    required_params = [
        'power_range', 'wavelength', 'spot_size', 'repetition_rate',
        'energy_density', 'pulse_width', 'scan_speed', 'pass_count', 'overlap_ratio'
    ]
    for param in required_params:
        assert param in data['machine_settings']['basic']
    
    return True
```

### File Naming Convention

**Single file location:**
```
/frontmatter/materials/{slug}.yaml
```

**Examples:**
- `/frontmatter/materials/aluminum-laser-cleaning.yaml`
- `/frontmatter/materials/steel-laser-cleaning.yaml`
- `/frontmatter/materials/concrete-laser-cleaning.yaml`

### Migration Strategy

**Phase 1: Generate unified files for materials with settings**
- Start with materials that have both materials + settings pages
- Example: aluminum, steel, copper, brass, concrete, granite

**Phase 2: Generate unified files for materials without settings**
- Omit settings_page, detailed, challenges, troubleshooting, research_library
- Example: many ceramics, polymers

**Phase 3: Validate and test**
- Verify both /materials/ and /settings/ pages render correctly
- Check template variable substitution works

**Phase 4: Deploy**
- Replace old split files with unified files
- Update contentAPI to read unified structure

### Generator Command Example

```bash
# Generate unified frontmatter for aluminum (with settings page)
python generate_unified_material.py \
  --material aluminum \
  --category metal \
  --subcategory non-ferrous \
  --author-id 4 \
  --has-settings-page \
  --output /frontmatter/materials/aluminum-laser-cleaning.yaml

# Generate unified frontmatter for bamboo (no settings page)
python generate_unified_material.py \
  --material bamboo \
  --category organic \
  --subcategory wood \
  --author-id 6 \
  --output /frontmatter/materials/bamboo-laser-cleaning.yaml
```

---

## Implementation Roadmap

### Phase 1: Citation Infrastructure (Week 1)

**Day 1-2: Update Schema & Validation**
- [ ] Update TypeScript interfaces for citation structure
- [ ] Implement strict validation in Python (no fallbacks allowed)
- [ ] Add `needs_research` flag support for incomplete data
- [ ] Create citation ID generation utility (e.g., `Zhang2021`, `ASTM_C615_2023`)

**Day 3-4: Build Citation Extraction**
- [ ] Create `CitationBuilder` class to extract from PropertyResearch.yaml
- [ ] Create `CitationExtractor` for SettingResearch.yaml
- [ ] Implement multi-source aggregation (primary + supporting)
- [ ] Add confidence score calculations

**Day 5: Testing**
- [ ] Unit tests for citation validation
- [ ] Test citation ID uniqueness
- [ ] Verify no fallback values allowed
- [ ] Test `needs_research` flag detection

### Phase 2: Voice Configuration Update (Week 1)

**Voice Enhancement Policy:**
```yaml
# components/text/config/voice_application.yaml

voice_targets:
  materials_page:
    subtitle: false          # DISABLED - keep technical
    caption_before: true     # Enable voice
    caption_after: true      # Enable voice
    faq_answers: true        # Enable voice
    description: false       # Keep technical
  
  settings_page:
    subtitle: false          # DISABLED - keep technical
    challenges: false        # Keep technical
    troubleshooting: false   # Keep technical
    rationale: false         # Keep technical for credibility
  
  research_pages:
    subtitle: false          # DISABLED - keep scientific
    research_findings: false # Keep scientific
    faq_answers: true        # Enable voice for engagement
```

**Implementation:**
- [ ] Update `VoicePostProcessor` to check field type before applying voice
- [ ] Add `voice_targets` configuration file
- [ ] Modify generator to skip subtitle voice enhancement
- [ ] Update existing frontmatter to remove voice from subtitles

**Code Changes Required:**
```python
# components/text/core/voice_postprocessor.py

class VoicePostProcessor:
    def __init__(self, voice_config_path: str = "components/text/config/voice_application.yaml"):
        self.voice_targets = self._load_voice_config(voice_config_path)
    
    def should_apply_voice(self, field_name: str, content_type: str) -> bool:
        """
        Check if voice should be applied to this field.
        
        Args:
            field_name: Field identifier (e.g., 'subtitle', 'caption_before')
            content_type: Page type (e.g., 'materials_page', 'settings_page')
        
        Returns:
            bool: True if voice should be applied
        """
        targets = self.voice_targets.get(content_type, {})
        return targets.get(field_name, False)
    
    def process_frontmatter(self, frontmatter_data: dict, content_type: str) -> dict:
        """
        Apply voice to frontmatter fields based on configuration.
        """
        # Subtitle: SKIP (disabled)
        if 'materials_page' in frontmatter_data:
            if self.should_apply_voice('subtitle', content_type):
                frontmatter_data['materials_page']['subtitle'] = self._apply_voice(
                    frontmatter_data['materials_page']['subtitle']
                )
        
        # Captions: APPLY
        if 'materials_page' in frontmatter_data:
            caption = frontmatter_data['materials_page'].get('caption', {})
            if self.should_apply_voice('caption_before', content_type):
                caption['before'] = self._apply_voice(caption['before'])
            if self.should_apply_voice('caption_after', content_type):
                caption['after'] = self._apply_voice(caption['after'])
        
        # FAQs: APPLY
        if 'faq' in frontmatter_data:
            if self.should_apply_voice('faq_answers', content_type):
                for faq in frontmatter_data['faq']:
                    faq['answer'] = self._apply_voice(faq['answer'])
        
        return frontmatter_data
```

### Phase 3: Unified Frontmatter Generator (Week 2)

**Day 1-2: Core Generator**
- [ ] Create `UnifiedFrontmatterGenerator` class
- [ ] Implement property extraction with citations
- [ ] Implement machine settings extraction with citations
- [ ] Add template variable substitution (e.g., `{{thermal_conductivity}}`)

**Day 3: Research Library Builder**
- [ ] Implement `ResearchLibraryBuilder`
- [ ] Extract citations from PropertyResearch.yaml
- [ ] Extract citations from SettingResearch.yaml
- [ ] Deduplicate citation entries
- [ ] Sort by type (journal, standard, database, AI research)

**Day 4: Integration**
- [ ] Integrate citation builder with generator
- [ ] Integrate voice postprocessor (with subtitle disabled)
- [ ] Add validation hooks
- [ ] Test with aluminum material

**Day 5: Testing**
- [ ] Generate aluminum unified frontmatter
- [ ] Verify all properties have citations
- [ ] Verify subtitle has NO voice markers
- [ ] Verify captions and FAQs HAVE voice markers
- [ ] Validate against schema

### Phase 4: Content API Update (Week 2)

**Update contentAPI.ts:**
```typescript
// app/utils/contentAPI.ts

export interface UnifiedMaterialFrontmatter {
  name: string;
  slug: string;
  category: string;
  subcategory: string;
  author: AuthorEEAT;
  
  materials_page: MaterialsPageMetadata;
  settings_page?: SettingsPageMetadata;  // Optional
  
  material_properties: MaterialProperties;
  machine_settings: {
    basic: BasicMachineSettings;
    detailed?: DetailedMachineSettings;  // Optional
  };
  
  challenges?: ChallengesSection;
  troubleshooting?: TroubleshootingSection;
  research_library: ResearchLibrary;  // Always present (may be empty)
  
  faq: FAQ[];
  regulatory_standards: Standard[];
  breadcrumb: Breadcrumb[];
  _metadata: Metadata;
}

export async function getUnifiedMaterial(slug: string): Promise<UnifiedMaterialFrontmatter> {
  const filePath = path.join(process.cwd(), 'frontmatter', 'materials', `${slug}.yaml`);
  const content = await fs.readFile(filePath, 'utf8');
  const data = yaml.parse(content);
  
  // Validate structure
  validateUnifiedFrontmatter(data);
  
  return data;
}
```

**Tasks:**
- [ ] Update TypeScript interfaces
- [ ] Update MaterialsPage component
- [ ] Update SettingsPage component
- [ ] Add citation rendering components
- [ ] Test both page types

### Phase 5: Migration & Deployment (Week 3)

**Day 1: Proof of Concept**
- [ ] Generate unified aluminum-laser-cleaning.yaml
- [ ] Deploy to test environment
- [ ] Verify both /materials/ and /settings/ pages work
- [ ] Performance testing (load time, caching)

**Day 2-3: Batch Migration**
- [ ] Generate unified files for all 132 materials
- [ ] Validate all files pass citation checks
- [ ] Verify no fallback values exist
- [ ] Check voice markers ONLY in appropriate fields

**Day 4: Deployment**
- [ ] Deploy unified files to production
- [ ] Monitor for errors
- [ ] Verify citation rendering on live site

**Day 5: Cleanup**
- [ ] Remove old split files
- [ ] Update documentation
- [ ] Archive old structure

### Success Metrics

**Validation Checks (ZERO TOLERANCE):**
- ✅ 0% of properties have fallback values (MUST BE 0%)
- ✅ 100% of non-null properties have citations
- ✅ 0% of subtitles have voice markers (MUST BE 0%)
- ✅ 100% of captions have voice markers
- ✅ 100% of FAQ answers have voice markers
- ✅ 100% of cited sources exist in research_library
- ✅ 0% of materials use category-level defaults (FORBIDDEN)

**Performance Metrics:**
- Single file load < 50ms (unified 18KB vs split 25KB)
- Citation tooltip render < 100ms
- Page build time < 2s per material

**Quality Metrics:**
- Average citation count per property: >2
- Average confidence score: >90%
- Peer-reviewed citations: >60%
- AI research citations: <30% (supplementary only)

---

## Command Summary

```bash
# Generate unified frontmatter with strict validation
python3 run.py \
  --generate-unified-frontmatter \
  --material aluminum \
  --author-id 4 \
  --has-settings-page \
  --disable-subtitle-voice \
  --strict-citations \
  --no-fallbacks

# Validate citations (fails if any fallbacks found)
python3 run.py \
  --validate-citations \
  --frontmatter frontmatter/materials/aluminum-laser-cleaning.yaml \
  --fail-on-fallbacks \
  --fail-on-missing-citations

# Batch generate all 132 materials
python3 run.py \
  --batch-generate-unified \
  --disable-subtitle-voice \
  --strict-citations \
  --no-fallbacks \
  --parallel-workers 8

# Audit voice application
python3 run.py \
  --audit-voice-markers \
  --check-subtitles-clean \
  --check-captions-voiced \
  --check-faqs-voiced \
  --fail-on-violations

# Deploy to production
python3 run.py \
  --deploy-unified-frontmatter \
  --verify-citations \
  --verify-no-fallbacks \
  --cleanup-old-files
```

---
