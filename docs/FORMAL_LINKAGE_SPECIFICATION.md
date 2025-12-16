# Formal Linkage Specification

> **⚠️ SUPERSEDED NOTICE**  
> **Date**: December 15, 2025  
> **Replacement**: This specification has been **SUPERSEDED** by the implemented `domain_linkages` structure.  
> **Current Specification**: See [DOMAIN_LINKAGES_STRUCTURE.md](./DOMAIN_LINKAGES_STRUCTURE.md)  
> **Migration Status**: ✅ COMPLETE - All 4 domains migrated (see [DOMAIN_LINKAGES_MIGRATION_COMPLETE_DEC15_2025.md](../DOMAIN_LINKAGES_MIGRATION_COMPLETE_DEC15_2025.md))
>
> **This document remains for historical reference only.** All new development should use the `domain_linkages` structure.

---

**Version**: 1.0 (ARCHIVED)  
**Date**: December 15, 2025  
**Purpose**: Normalize bidirectional relationships between Materials, Settings, Contaminants, and Compounds

---

## Executive Summary

This specification defines a normalized data linkage system enabling **bidirectional card-based discovery** across all four primary domains. Each entity can display related entities with context-aware relationship metadata.

**Current State**: Partial implicit linkage (contaminants → compounds via byproducts, contaminants → materials via valid_materials)  
**Target State**: Full bidirectional explicit linkage with relationship semantics  
**Implementation**: 3 tiers (Critical, Enhanced, Optional)

**⚠️ NOTE**: This specification was used for initial planning but has been replaced by the implemented `domain_linkages` structure which includes standardized `id`, `title`, `url`, `image` fields plus domain-specific metadata.

---

## 1. Data Domains

### Domain Inventory

| Domain | File | Count | ID Format | Primary Key |
|--------|------|-------|-----------|-------------|
| **Materials** | Materials.yaml | 153 | kebab-case | material_id |
| **Settings** | Settings.yaml | 169 | kebab-case | setting_id |
| **Contaminants** | Contaminants.yaml | 98 | kebab-case | contaminant_id |
| **Compounds** | Compounds.yaml | 20 | kebab-case | compound_id |

---

## 2. Relationship Types

### 2.1 Material ↔ Contaminant

**Semantics**: Which contaminants form on which materials, and vice versa

**Material → Contaminant** (Forward):
```yaml
materials:
  aluminum:
    related_contaminants:
      - contaminant_id: "aluminum-oxidation"
        relationship: "forms"              # Contaminant naturally forms on material
        likelihood: "very_high"            # Frequency: very_high, high, moderate, low
        context: ["outdoor", "marine"]     # Settings where this occurs
      - contaminant_id: "anodizing-defects"
        relationship: "susceptible_to"     # Material is prone to this contamination
        likelihood: "moderate"
        context: ["industrial"]
```

**Contaminant → Material** (Reverse):
```yaml
contamination_patterns:
  aluminum-oxidation:
    valid_materials: ["Aluminum", "Aluminum Alloys"]  # EXISTING FIELD
    # OR add structured version:
    related_materials:
      - material_id: "aluminum"
        relationship: "forms_on"           # Contaminant forms on material
        severity: "moderate"               # Impact: low, moderate, high, severe
        removal_difficulty: "easy"         # easy, moderate, difficult, extreme
```

**Relationship Values**:
- `forms`: Contaminant naturally develops on material
- `susceptible_to`: Material is prone to contamination
- `forms_on`: Inverse of forms
- `adheres_to`: Contaminant sticks to material surface
- `embedded_in`: Contaminant embedded within material structure

---

### 2.2 Contaminant ↔ Compound

**Semantics**: Which compounds are produced when removing contaminants

**Contaminant → Compound** (Forward):
```yaml
contamination_patterns:
  adhesive-residue:
    laser_properties:
      removal_characteristics:
        byproducts:                        # EXISTING FIELD - Keep as is
          - compound: "carbon-dioxide"
            hazard_level: low              # low, moderate, high, severe
            phase: gas                     # gas, liquid, solid, aerosol
            concentration: "high"          # NEW: high, moderate, low
          - compound: "vocs"
            hazard_level: moderate
            phase: gas
            concentration: "moderate"
```

**Compound → Contaminant** (Reverse):
```yaml
compounds:
  carbon-dioxide:
    produced_by_contaminants:              # NEW FIELD
      - contaminant_id: "adhesive-residue"
        conditions: "laser_ablation"       # Process that produces compound
        concentration: "high"              # Expected concentration
        hazard_context: "enclosed_spaces"  # When hazardous
      - contaminant_id: "organic-coatings"
        conditions: "thermal_decomposition"
        concentration: "moderate"
```

**Relationship Values**:
- `laser_ablation`: Produced during laser removal
- `thermal_decomposition`: Produced by heat
- `chemical_breakdown`: Produced by chemical reaction
- `vaporization`: Material vaporizes during removal
- `combustion`: Material burns during removal

---

### 2.3 Material ↔ Setting

**Semantics**: Which materials are commonly found in which settings

**Material → Setting** (Forward):
```yaml
materials:
  steel:
    common_settings:                       # NEW FIELD
      - setting_id: "outdoor-industrial"
        frequency: "very_high"             # very_high, high, moderate, low
        typical_applications:
          - "structural_components"
          - "machinery"
          - "infrastructure"
      - setting_id: "marine"
        frequency: "high"
        typical_applications:
          - "ships"
          - "offshore_platforms"
```

**Setting → Material** (Reverse):
```yaml
settings:
  outdoor-industrial:
    common_materials:                      # NEW FIELD
      - material_id: "steel"
        frequency: "very_high"
        typical_condition: "weathered"     # pristine, weathered, corroded, damaged
      - material_id: "aluminum"
        frequency: "high"
        typical_condition: "oxidized"
      - material_id: "concrete"
        frequency: "high"
        typical_condition: "stained"
```

**Frequency Values**: `very_high`, `high`, `moderate`, `low`, `rare`

---

### 2.4 Setting ↔ Contaminant

**Semantics**: Which contaminants are common in which settings

**Setting → Contaminant** (Forward):
```yaml
settings:
  marine:
    common_contaminants:                   # NEW FIELD
      - contaminant_id: "salt-deposits"
        frequency: "very_high"
        severity: "high"                   # Typical severity in this setting
        seasonal_variation: true           # Whether frequency varies by season
      - contaminant_id: "rust"
        frequency: "very_high"
        severity: "severe"
        seasonal_variation: false
```

**Contaminant → Setting** (Reverse):
```yaml
contamination_patterns:
  salt-deposits:
    common_settings:                       # NEW FIELD
      - setting_id: "marine"
        frequency: "very_high"
        formation_rate: "fast"             # fast, moderate, slow
      - setting_id: "coastal"
        frequency: "high"
        formation_rate: "moderate"
```

**Formation Rate**: `fast`, `moderate`, `slow`, `intermittent`

---

### 2.5 Material ↔ Compound (Optional)

**Semantics**: Which compounds are produced when processing specific materials

**Material → Compound** (Forward):
```yaml
materials:
  aluminum:
    laser_processing_byproducts:           # NEW FIELD (Optional)
      - compound_id: "aluminum-oxide"
        process: "ablation"
        concentration: "high"
        particle_size: "nanoparticles"
      - compound_id: "ozone"
        process: "plasma_formation"
        concentration: "low"
```

**Compound → Material** (Reverse):
```yaml
compounds:
  aluminum-oxide:
    source_materials:                      # NEW FIELD (Optional)
      - material_id: "aluminum"
        generation_process: "oxidation_layer_removal"
        typical_exposure: "high"
      - material_id: "aluminum-alloys"
        generation_process: "laser_ablation"
        typical_exposure: "moderate"
```

---

## 3. Schema Definition

### 3.1 Field Specifications

#### related_contaminants (Materials)
```yaml
related_contaminants:
  type: array
  items:
    contaminant_id:
      type: string
      format: kebab-case
      required: true
    relationship:
      type: string
      enum: [forms, susceptible_to, prone_to, attracts]
      required: true
    likelihood:
      type: string
      enum: [very_high, high, moderate, low, rare]
      required: true
    context:
      type: array
      items: string  # setting_ids where this relationship is relevant
      required: false
    severity:
      type: string
      enum: [low, moderate, high, severe]
      required: false
```

#### related_materials (Contaminants)
```yaml
related_materials:
  type: array
  items:
    material_id:
      type: string
      format: kebab-case
      required: true
    relationship:
      type: string
      enum: [forms_on, adheres_to, embedded_in, coats]
      required: true
    severity:
      type: string
      enum: [low, moderate, high, severe]
      required: true
    removal_difficulty:
      type: string
      enum: [easy, moderate, difficult, extreme]
      required: false
```

#### produced_by_contaminants (Compounds)
```yaml
produced_by_contaminants:
  type: array
  items:
    contaminant_id:
      type: string
      format: kebab-case
      required: true
    conditions:
      type: string
      enum: [laser_ablation, thermal_decomposition, chemical_breakdown, vaporization, combustion]
      required: true
    concentration:
      type: string
      enum: [very_high, high, moderate, low, trace]
      required: false
    hazard_context:
      type: string
      description: "When/where this compound is hazardous"
      required: false
```

#### common_settings (Materials)
```yaml
common_settings:
  type: array
  items:
    setting_id:
      type: string
      format: kebab-case
      required: true
    frequency:
      type: string
      enum: [very_high, high, moderate, low, rare]
      required: true
    typical_applications:
      type: array
      items: string
      required: false
```

#### common_materials (Settings)
```yaml
common_materials:
  type: array
  items:
    material_id:
      type: string
      format: kebab-case
      required: true
    frequency:
      type: string
      enum: [very_high, high, moderate, low, rare]
      required: true
    typical_condition:
      type: string
      enum: [pristine, weathered, oxidized, corroded, damaged, stained]
      required: false
```

#### common_contaminants (Settings)
```yaml
common_contaminants:
  type: array
  items:
    contaminant_id:
      type: string
      format: kebab-case
      required: true
    frequency:
      type: string
      enum: [very_high, high, moderate, low, rare]
      required: true
    severity:
      type: string
      enum: [low, moderate, high, severe]
      required: false
    seasonal_variation:
      type: boolean
      required: false
```

---

## 4. Implementation Tiers

### Tier 1: Critical (Enables Card Display)

**Priority**: IMMEDIATE  
**Effort**: 2-3 days  
**Impact**: Core feature functionality

1. **Compound → Contaminant** (Reverse link for byproducts)
   - Add `produced_by_contaminants` to Compounds.yaml
   - Populate by analyzing existing `byproducts` in Contaminants.yaml
   - Enables: "This compound is produced when removing [contaminants]"

2. **Contaminant → Material** (Normalize existing `valid_materials`)
   - Keep `valid_materials` array (backward compatibility)
   - Add optional `related_materials` for structured relationships
   - Enables: "This contamination forms on [materials]"

3. **Material → Contaminant** (Forward link)
   - Add `related_contaminants` to Materials.yaml
   - Populate based on contaminant `valid_materials` (reverse mapping)
   - Enables: "Common contaminants on this material: [list]"

**Deliverables**:
- [ ] Schema validation rules
- [ ] Automated linkage generation script
- [ ] Bidirectional consistency checker
- [ ] Card UI component specification

---

### Tier 2: Enhanced (Better Discovery)

**Priority**: HIGH  
**Effort**: 3-4 days  
**Impact**: Improved user experience, contextual recommendations

4. **Material → Setting**
   - Add `common_settings` to Materials.yaml
   - Enables: "Commonly found in [settings]"

5. **Setting → Material**
   - Add `common_materials` to Settings.yaml
   - Enables: "Typical materials in this setting: [list]"

6. **Setting → Contaminant**
   - Add `common_contaminants` to Settings.yaml
   - Enables: "Common contamination in this setting: [list]"

7. **Contaminant → Setting**
   - Add `common_settings` to Contaminants.yaml
   - Enables: "Most common in [settings]"

**Deliverables**:
- [ ] Setting-based filtering UI
- [ ] Contextual recommendations engine
- [ ] Material-setting-contaminant triangle visualization

---

### Tier 3: Optional (Advanced Features)

**Priority**: LOW  
**Effort**: 2 days  
**Impact**: Advanced use cases, research features

8. **Material → Compound**
   - Add `laser_processing_byproducts` to Materials.yaml
   - Enables: "Compounds produced when processing this material"

9. **Compound → Material**
   - Add `source_materials` to Compounds.yaml
   - Enables: "Typically produced from [materials]"

**Deliverables**:
- [ ] Process simulation tool
- [ ] Compound exposure calculator
- [ ] Material-specific safety recommendations

---

## 5. Data Population Strategy

### 5.1 Automated Linkage Generation

**Phase 1: Reverse Engineering Existing Relationships**

```python
# Example: Generate compound → contaminant links
def generate_compound_contaminant_links():
    """
    Analyze all contaminants' byproducts to build reverse links
    """
    compound_links = {}
    
    for contaminant_id, data in contaminants.items():
        byproducts = data['laser_properties']['removal_characteristics']['byproducts']
        
        for bp in byproducts:
            compound_id = bp['compound']
            if compound_id not in compound_links:
                compound_links[compound_id] = []
            
            compound_links[compound_id].append({
                'contaminant_id': contaminant_id,
                'conditions': 'laser_ablation',
                'concentration': map_hazard_to_concentration(bp['hazard_level']),
                'phase': bp['phase']
            })
    
    return compound_links
```

**Phase 2: Manual Curation**

High-value relationships requiring domain expertise:
- Material → Setting (requires application knowledge)
- Setting → Material (requires industry context)
- Setting → Contaminant (requires environmental understanding)

**Phase 3: Validation**

- Bidirectional consistency checks
- Orphaned reference detection
- Circular dependency prevention

---

### 5.2 Linkage Generation Script

**Location**: `scripts/data/generate_linkages.py`

```python
#!/usr/bin/env python3
"""
Generate bidirectional linkages between domains

Usage:
    python3 scripts/data/generate_linkages.py --tier 1
    python3 scripts/data/generate_linkages.py --all
    python3 scripts/data/generate_linkages.py --validate
"""

def generate_tier1_links():
    """
    Generate critical bidirectional links:
    - Compound → Contaminant (reverse byproducts)
    - Material → Contaminant (reverse valid_materials)
    """
    pass

def generate_tier2_links():
    """
    Generate enhanced links requiring manual curation:
    - Material ↔ Setting
    - Setting ↔ Contaminant
    """
    pass

def validate_links():
    """
    Validate all linkages:
    - Check for orphaned references
    - Verify bidirectionality
    - Detect inconsistencies
    """
    pass
```

---

## 6. UI/UX Specifications

### 6.1 Card Display Components

**Material Card - Related Entities Section**:
```html
<div class="related-entities">
  <h3>Common Contaminants</h3>
  <ul>
    <li v-for="rel in material.related_contaminants">
      <a :href="`/contaminants/${rel.contaminant_id}`">
        {{ rel.name }}
      </a>
      <span class="likelihood">{{ rel.likelihood }}</span>
      <span class="context" v-if="rel.context">
        in {{ rel.context.join(', ') }} settings
      </span>
    </li>
  </ul>
  
  <h3>Related Compounds</h3>
  <ul>
    <li v-for="compound in getRelatedCompounds(material)">
      <a :href="`/compounds/${compound.id}`">
        {{ compound.name }}
      </a>
      <span class="hazard">{{ compound.hazard_level }}</span>
    </li>
  </ul>
</div>
```

**Contaminant Card - Related Entities Section**:
```html
<div class="related-entities">
  <h3>Forms On Materials</h3>
  <ul>
    <li v-for="mat in contaminant.related_materials">
      <a :href="`/materials/${mat.material_id}`">
        {{ mat.name }}
      </a>
      <span class="severity">{{ mat.severity }} impact</span>
      <span class="removal">{{ mat.removal_difficulty }} to remove</span>
    </li>
  </ul>
  
  <h3>Hazardous Byproducts</h3>
  <ul>
    <li v-for="bp in contaminant.byproducts">
      <a :href="`/compounds/${bp.compound}`">
        {{ getCompoundName(bp.compound) }}
      </a>
      <span class="hazard">{{ bp.hazard_level }}</span>
      <span class="phase">{{ bp.phase }}</span>
    </li>
  </ul>
  
  <h3>Common Settings</h3>
  <ul>
    <li v-for="setting in contaminant.common_settings">
      <a :href="`/settings/${setting.setting_id}`">
        {{ setting.name }}
      </a>
      <span class="frequency">{{ setting.frequency }}</span>
    </li>
  </ul>
</div>
```

**Compound Card - Related Entities Section**:
```html
<div class="related-entities">
  <h3>Produced By</h3>
  <ul>
    <li v-for="rel in compound.produced_by_contaminants">
      <a :href="`/contaminants/${rel.contaminant_id}`">
        {{ rel.name }}
      </a>
      <span class="conditions">{{ rel.conditions }}</span>
      <span class="concentration">{{ rel.concentration }} concentration</span>
    </li>
  </ul>
  
  <h3>Found On Materials</h3>
  <ul v-if="compound.source_materials">
    <li v-for="mat in compound.source_materials">
      <a :href="`/materials/${mat.material_id}`">
        {{ mat.name }}
      </a>
      <span class="context">{{ mat.generation_process }}</span>
    </li>
  </ul>
</div>
```

### Layout Decision Matrix

**Automatic layout selection based on result count**:

| Result Count | Layout | Category Filter | Subcategory Filter | Grid Columns |
|--------------|--------|----------------|-------------------|--------------|
| 1-4 | Simple list/horizontal | No | No | 1-2 |
| 5-12 | Grid | No | No | 2-3 |
| 13-24 | Grid with filters | Yes | No | 3-4 |
| 25-50 | Grid with filters | Yes | Yes (if 13+ in category) | 4 |
| 51+ | Paginated grid | Yes | Yes (if 13+ in category) | 4 |

**Category Grouping by Domain**:

```typescript
const categoryGroups = {
  materials: {
    metals: ['ferrous', 'non-ferrous', 'alloys'],
    plastics: ['thermoplastic', 'thermoset'],
    glass: ['soda-lime', 'borosilicate', 'specialty'],
    wood: ['hardwood', 'softwood'],
    ceramics: ['oxide', 'non-oxide', 'composite']
  },
  contaminants: {
    corrosion: ['oxidation', 'pitting', 'general'],
    'organic-residue': ['adhesive', 'grease', 'oil', 'sealant'],
    particulate: ['dust', 'debris', 'filings'],
    coating: ['paint', 'powder-coat', 'plating']
  },
  compounds: {
    carcinogenic: ['iarc-group-1', 'iarc-group-2a'],
    toxic: ['acute', 'chronic'],
    irritant: ['respiratory', 'dermal', 'ocular']
  },
  settings: {
    'pulsed-fiber': ['low-power', 'medium-power', 'high-power'],
    'continuous-wave': ['low-power', 'high-power']
  }
}
```

---

## 7. Validation Rules

### 7.1 Referential Integrity

**All links must reference valid entities**:
```yaml
# VALID
related_contaminants:
  - contaminant_id: "rust"  # Must exist in Contaminants.yaml

# INVALID
related_contaminants:
  - contaminant_id: "non-existent-contaminant"  # ❌ Not in data
```

**Validation Script**:
```bash
python3 scripts/validation/validate_linkages.py
```

Expected output:
```
Validating linkages...
✅ Materials: 153 materials, 487 contaminant links (all valid)
✅ Contaminants: 98 contaminants, 96 compound links (5 orphaned)
⚠️  Orphaned compound references:
   • VOCs (11 refs) - should be 'vocs'
   • H2O (53 refs) - non-hazardous, OK to omit
✅ Compounds: 20 compounds, 45 contaminant links (all valid)
```

---

### 7.2 Bidirectional Consistency

**Forward and reverse links must match**:

```yaml
# Materials.yaml
aluminum:
  related_contaminants:
    - contaminant_id: "aluminum-oxidation"

# Contaminants.yaml  
aluminum-oxidation:
  related_materials:
    - material_id: "aluminum"  # Must be present
```

**Consistency Checker**:
```python
def check_bidirectional_consistency():
    """
    Verify all forward links have corresponding reverse links
    """
    # Check Material → Contaminant matches Contaminant → Material
    # Check Contaminant → Compound matches Compound → Contaminant
    # etc.
    pass
```

---

## 8. Migration Plan

### Phase 1: Schema Definition (Complete)
- ✅ Define field specifications
- ✅ Create validation rules
- ✅ Document relationship types

### Phase 2: Automated Generation (Week 1)
- [ ] Write linkage generation script
- [ ] Generate Compound → Contaminant reverse links
- [ ] Generate Material → Contaminant forward links
- [ ] Validate Tier 1 linkages

### Phase 3: Manual Curation (Week 2)
- [ ] Curate Material → Setting relationships (top 20 materials)
- [ ] Curate Setting → Contaminant relationships (top 10 settings)
- [ ] Validate Tier 2 linkages

### Phase 4: UI Integration (Week 3)
- [ ] Implement card components
- [ ] Add related entity sections
- [ ] Test navigation flows
- [ ] Deploy to production

### Phase 5: Validation & Refinement (Week 4)
- [ ] User testing
- [ ] Fix inconsistencies
- [ ] Optimize queries
- [ ] Document usage patterns

---

## 9. API Endpoints

### 9.1 Linkage Queries

**Get related entities**:
```
GET /api/materials/{material_id}/related
Response: {
  contaminants: [...],
  settings: [...],
  compounds: [...]
}

GET /api/contaminants/{contaminant_id}/related
Response: {
  materials: [...],
  settings: [...],
  compounds: [...]
}

GET /api/compounds/{compound_id}/related
Response: {
  contaminants: [...],
  materials: [...]
}
```

**Linkage statistics**:
```
GET /api/linkages/stats
Response: {
  total_links: 1234,
  by_type: {
    "material_contaminant": 487,
    "contaminant_compound": 96,
    "material_setting": 203,
    ...
  },
  coverage: {
    materials_with_contaminant_links: "95%",
    contaminants_with_compound_links: "26%",
    ...
  }
}
```

---

## 10. Examples

### 10.1 Complete Example: Aluminum

**Materials.yaml**:
```yaml
aluminum:
  name: "Aluminum"
  category: "Metal"
  
  # Tier 1: Critical
  related_contaminants:
    - contaminant_id: "aluminum-oxidation"
      relationship: "forms"
      likelihood: "very_high"
      context: ["outdoor", "marine", "industrial"]
      severity: "moderate"
    - contaminant_id: "anodizing-defects"
      relationship: "susceptible_to"
      likelihood: "moderate"
      context: ["industrial"]
      severity: "low"
    - contaminant_id: "salt-deposits"
      relationship: "attracts"
      likelihood: "high"
      context: ["marine", "coastal"]
      severity: "high"
  
  # Tier 2: Enhanced
  common_settings:
    - setting_id: "outdoor-industrial"
      frequency: "very_high"
      typical_applications:
        - "structural_components"
        - "machinery"
        - "vehicle_bodies"
    - setting_id: "marine"
      frequency: "high"
      typical_applications:
        - "ship_hulls"
        - "offshore_platforms"
    - setting_id: "aerospace"
      frequency: "very_high"
      typical_applications:
        - "aircraft_structures"
        - "spacecraft_components"
  
  # Tier 3: Optional
  laser_processing_byproducts:
    - compound_id: "aluminum-oxide"
      process: "ablation"
      concentration: "high"
      particle_size: "nanoparticles"
```

### 10.2 Complete Example: Rust (Contaminant)

**Contaminants.yaml**:
```yaml
rust:
  name: "Rust"
  category: "Corrosion"
  
  # EXISTING: Keep as is
  valid_materials: ["Steel", "Iron", "Cast Iron"]
  
  # Tier 1: Critical
  related_materials:
    - material_id: "steel"
      relationship: "forms_on"
      severity: "high"
      removal_difficulty: "moderate"
    - material_id: "iron"
      relationship: "forms_on"
      severity: "severe"
      removal_difficulty: "difficult"
    - material_id: "cast-iron"
      relationship: "forms_on"
      severity: "high"
      removal_difficulty: "moderate"
  
  # EXISTING: Byproducts (compound linkage)
  laser_properties:
    removal_characteristics:
      byproducts:
        - compound: "iron-oxide"
          hazard_level: moderate
          phase: solid
          concentration: "high"
        - compound: "carbon-monoxide"
          hazard_level: high
          phase: gas
          concentration: "low"
  
  # Tier 2: Enhanced
  common_settings:
    - setting_id: "outdoor-industrial"
      frequency: "very_high"
      formation_rate: "fast"
      seasonal_variation: true
    - setting_id: "marine"
      frequency: "very_high"
      formation_rate: "very_fast"
      seasonal_variation: false
```

### 10.3 Complete Example: Carbon Monoxide (Compound)

**Compounds.yaml**:
```yaml
carbon-monoxide:
  name: "Carbon Monoxide"
  chemical_formula: "CO"
  category: "toxic_gas"
  
  # Tier 1: Critical (NEW)
  produced_by_contaminants:
    - contaminant_id: "rust"
      conditions: "laser_ablation"
      concentration: "low"
      hazard_context: "enclosed_spaces"
    - contaminant_id: "organic-coatings"
      conditions: "thermal_decomposition"
      concentration: "high"
      hazard_context: "indoor_operations"
    - contaminant_id: "carbon-deposits"
      conditions: "combustion"
      concentration: "moderate"
      hazard_context: "poor_ventilation"
  
  # Tier 3: Optional (NEW)
  source_materials:
    - material_id: "steel"
      generation_process: "rust_removal"
      typical_exposure: "low"
    - material_id: "wood"
      generation_process: "organic_matter_ablation"
      typical_exposure: "high"
```

---

## 11. Success Metrics

### 11.1 Data Quality

- **Linkage Coverage**: >90% of materials have contaminant links
- **Bidirectional Consistency**: 100% forward/reverse match
- **Referential Integrity**: 0 orphaned references
- **Manual Curation**: Top 50 materials have setting links

### 11.2 User Experience

- **Card Click-Through**: >30% users explore related entities
- **Navigation Depth**: Average 3+ entity types per session
- **Discovery Rate**: >40% users find new relevant content
- **Query Performance**: <100ms for related entity lookup

### 11.3 Content Quality

- **Relationship Accuracy**: >95% validated by domain experts
- **Context Relevance**: >90% setting contexts accurate
- **Severity Ratings**: >95% severity assessments correct

---

## 12. Maintenance

### 12.1 Ongoing Updates

**When adding new material**:
1. Add `related_contaminants` (required)
2. Add `common_settings` (optional)
3. Run validation script
4. Update reverse links automatically

**When adding new contaminant**:
1. Add `valid_materials` or `related_materials` (required)
2. Add `byproducts` (required)
3. Add `common_settings` (optional)
4. Update reverse links in materials and compounds

**When adding new compound**:
1. Add `produced_by_contaminants` by analyzing contaminant byproducts
2. Run reverse linkage generator
3. Validate against contaminant data

### 12.2 Automated Sync

**Bidirectional Link Maintenance**:
```bash
# Run nightly
python3 scripts/data/sync_bidirectional_links.py

# Output:
# ✅ Synced 487 material→contaminant links
# ✅ Created 487 contaminant→material reverse links
# ✅ Synced 96 contaminant→compound links
# ✅ Created 96 compound→contaminant reverse links
# ⚠️  5 orphaned compound references found
```

---

---

## 13. Cross-Domain Normalization (Additional Categories)

### 13.1 Regulatory Standards & Citations

**Problem**: Scattered regulatory references across `eeat.citations`, `regulatoryStandards`, and `regulatory_classification`

**Current State**:
```yaml
# Materials.yaml
eeat:
  citations:
    - "ASTM E2490"
    - "ISO 11146"
regulatoryStandards:
  - name: "OSHA 29 CFR 1910.1200"
    url: "..."

# Contaminants.yaml
eeat:
  citations:
    - "IEC 60825 - Safety of Laser Products"
    - "OSHA 29 CFR 1926.95"

# Compounds.yaml
regulatory_classification:
  un_number: "UN1198"
  dot_hazard_class: "3"
  nfpa_codes: {health: 3, flammability: 2}
```

**Normalized Structure**:
```yaml
# NEW: data/shared/RegulatoryStandards.yaml
regulatory_standards:
  osha-29-cfr-1926-95:
    id: "osha-29-cfr-1926-95"
    name: "OSHA 29 CFR 1926.95"
    full_name: "Personal Protective Equipment"
    organization: "OSHA"
    category: "ppe"
    url: "https://www.osha.gov/laws-regs/regulations/standardnumber/1926/1926.95"
    applicability: ["materials", "contaminants", "compounds"]
  
  iec-60825:
    id: "iec-60825"
    name: "IEC 60825"
    full_name: "Safety of Laser Products"
    organization: "IEC"
    category: "laser_safety"
    url: "https://webstore.iec.ch/publication/3587"
    applicability: ["materials", "contaminants"]

# Reference in domains
materials:
  aluminum:
    regulatory_compliance:
      - standard_id: "astm-e2490"
        applicability: "laser_cleaning"
      - standard_id: "iso-11146"
        applicability: "beam_characterization"

contaminants:
  adhesive-residue:
    regulatory_compliance:
      - standard_id: "iec-60825"
        applicability: "laser_safety"
      - standard_id: "osha-29-cfr-1926-95"
        applicability: "ppe_requirements"

compounds:
  formaldehyde:
    regulatory_compliance:
      - standard_id: "osha-29-cfr-1910-1048"
        applicability: "exposure_control"
      - standard_id: "dot-hazmat"
        classification: "UN1198"
```

---

### 13.2 Exposure Limits (Single Source of Truth)

**Problem**: DUPLICATE exposure limits in contaminants.fumes_generated AND compounds.workplace_exposure

**Current State (DUPLICATION)**:
```yaml
# Contaminants.yaml
laser_properties:
  safety_data:
    fumes_generated:
      - compound: "Formaldehyde"                    # ❌ Duplicates data
        concentration_mg_m3: 1-10
        exposure_limit_mg_m3: 0.3                   # ❌ Duplicated from Compounds.yaml
        hazard_class: carcinogenic

# Compounds.yaml
formaldehyde:
  workplace_exposure:
    osha_pel:
      twa_8hr: "0.75 ppm"                           # ✅ Authoritative source
    niosh_rel:
      ceiling: "0.016 ppm"                          # ✅ Authoritative source
```

**Normalized Structure (REFERENCE ONLY)**:
```yaml
# Contaminants.yaml - Reference compounds, don't duplicate
laser_properties:
  safety_data:
    fumes_generated:
      - compound_id: "formaldehyde"                 # ✅ Link to Compounds.yaml
        concentration_range_mg_m3: "1-10"           # Context-specific data
        generation_conditions: "thermal_decomposition"
        # NO exposure_limit_mg_m3 field (get from Compounds.yaml via compound_id)

# Compounds.yaml - Single source of truth
formaldehyde:
  workplace_exposure:                               # ✅ Authoritative limits
    osha_pel:
      twa_8hr: "0.75 ppm"
      action_level: "0.5 ppm"
    niosh_rel:
      ceiling: "0.016 ppm (0.02 mg/m³)"
      idlh: "20 ppm"
    acgih_tlv:
      ceiling: "0.3 ppm"
```

**Migration Rule**: Remove ALL `exposure_limit_*` fields from contaminants, replace compound names with `compound_id` links

---

### 13.3 PPE Requirements (Standardized Schema)

**Problem**: Inconsistent field names (`eye_protection` vs `eye`) and detail levels

**Current State (INCONSISTENT)**:
```yaml
# Contaminants.yaml
laser_properties:
  safety_data:
    ppe_requirements:
      eye_protection: "goggles"                     # ❌ Inconsistent name
      respiratory: "full_face"                      # ❌ Simple value
      skin_protection: "gloves"                     # ❌ Inconsistent name

# Compounds.yaml
ppe_requirements:
  eye: "Chemical splash goggles or face shield"    # ❌ Inconsistent name
  respiratory: "NIOSH-approved full-face..."       # ❌ Detailed value
  skin: "Nitrile or butyl rubber gloves..."        # ❌ Inconsistent name
```

**Normalized Structure**:
```yaml
# NEW: data/shared/PPE.yaml (lookup table)
ppe_specifications:
  ppe-eye-goggles:
    id: "ppe-eye-goggles"
    name: "Safety Goggles"
    type: "eye_protection"
    protection_level: "moderate"
    standards: ["ANSI Z87.1"]
    description: "Chemical splash goggles with side shields"
  
  ppe-respiratory-full-face:
    id: "ppe-respiratory-full-face"
    name: "Full-Face Respirator"
    type: "respiratory"
    protection_level: "high"
    standards: ["NIOSH-42CFR84"]
    description: "Full-face pressure-demand respirator with organic vapor cartridges"
  
  ppe-skin-nitrile-gloves:
    id: "ppe-skin-nitrile-gloves"
    name: "Nitrile Gloves"
    type: "skin_protection"
    protection_level: "moderate"
    standards: ["ASTM D6978"]
    description: "Nitrile gloves with breakthrough time >8 hours"

# Reference in domains (STANDARDIZED)
# Contaminants.yaml
laser_properties:
  safety_data:
    ppe_requirements:                               # ✅ Standardized format
      - ppe_id: "ppe-eye-goggles"
        reason: "particulate_generation"
        required: true
      - ppe_id: "ppe-respiratory-full-face"
        reason: "toxic_fumes"
        required: true
        context: "enclosed_spaces"
      - ppe_id: "ppe-skin-nitrile-gloves"
        reason: "chemical_contact"
        required: false

# Compounds.yaml
ppe_requirements:                                   # ✅ Standardized format
  - ppe_id: "ppe-eye-goggles"
    reason: "vapor_exposure"
    required: true
    special_notes: "Use face shield for splash hazard"
  - ppe_id: "ppe-respiratory-full-face"
    reason: "carcinogen_exposure"
    required: true
    special_notes: "Formaldehyde-specific cartridges required"
```

**Benefits**:
- Consistent field naming across domains
- Reusable PPE specifications
- Standards-based requirements
- Context-aware recommendations

---

### 13.4 Hazard Classifications (Unified System)

**Problem**: Multiple hazard classification systems (hazard_class, hazard_level, toxicity_level)

**Current State (MULTIPLE SYSTEMS)**:
```yaml
# Contaminants.yaml
byproducts:
  - compound: "formaldehyde"
    hazard_level: "moderate"                        # ❌ Different scale

fumes_generated:
  - compound: "Formaldehyde"
    hazard_class: "carcinogenic"                    # ❌ Different field

# Compounds.yaml
formaldehyde:
  category: "carcinogen"                            # ❌ Different field
  hazard_class: "carcinogenic"                      # ❌ Different field
  toxicity_level: "high"                            # ❌ Another scale
```

**Normalized Structure**:
```yaml
# NEW: Unified hazard classification
# Compounds.yaml (authoritative)
formaldehyde:
  hazard_profile:
    primary_hazard:
      type: "carcinogenic"
      severity: "severe"
      iarc_classification: "Group 1"
    secondary_hazards:
      - type: "respiratory_irritant"
        severity: "high"
      - type: "skin_sensitizer"
        severity: "moderate"
    exposure_hazard:
      acute_toxicity: "moderate"
      chronic_toxicity: "severe"
      target_organs: ["respiratory", "nasal_passages"]

# Contaminants.yaml (reference)
byproducts:
  - compound_id: "formaldehyde"
    exposure_context: "fumes"
    concentration_level: "moderate"                 # Contaminant-specific context
    # Hazard info comes from Compounds.yaml via compound_id
```

---

### 13.5 Process Parameters (Shared Schema)

**Problem**: Different parameter schemas in contaminants (`laser_parameters`) and materials (`machineSettings`)

**Current State (DIFFERENT SCHEMAS)**:
```yaml
# Contaminants.yaml
laser_parameters:
  fluence_range:
    min_j_cm2: 0.3
    max_j_cm2: 1.2
    recommended_j_cm2: 0.8
  pulse_duration_range:
    min_ns: 10
    max_ns: 100
    recommended_ns: 30

# Materials.yaml
machineSettings:
  powerOutput: "50-100W"
  frequency: "20-50 kHz"
  scanSpeed: "500-2000 mm/s"
```

**Normalized Structure**:
```yaml
# Shared schema with overrides
# Contaminants.yaml (base parameters)
laser_parameters:
  power_range_w:
    min: 50
    max: 200
    recommended: 100
  fluence_range_j_cm2:
    min: 0.3
    max: 1.2
    recommended: 0.8
  scan_speed_mm_s:
    min: 500
    max: 2000
    recommended: 1000

# Materials.yaml (material-specific overrides)
laser_processing:
  base_parameters:
    reference: "standard_cleaning"              # Links to shared parameters
  material_overrides:
    - contaminant_id: "rust"
      power_adjustment: "+20%"                  # Higher power for rust on this material
      fluence_override: 1.5                     # Override for this combination
    - contaminant_id: "paint"
      scan_speed_reduction: "-30%"              # Slower for paint removal
```

---

### 13.6 Safety Data Consolidation

**Problem**: Safety data scattered across multiple sections in different formats

**Consolidated Safety Profile Schema**:
```yaml
# Standardized safety_profile for all domains
safety_profile:
  hazard_assessment:
    primary_hazards: []
    secondary_hazards: []
    special_concerns: []
  
  ppe_requirements:
    - ppe_id: "..."
      reason: "..."
      required: true/false
      context: "..."
  
  exposure_compounds:                           # Links to Compounds.yaml
    - compound_id: "formaldehyde"
      source: "fumes"
      concentration_range: "1-10 mg/m³"
      # Exposure limits come from Compounds.yaml
  
  ventilation_requirements:
    minimum_air_changes_per_hour: 12
    exhaust_velocity_m_s: 0.5
    filtration_type: "carbon"
  
  fire_explosion_risk: "low"
  visibility_hazard: "moderate"
  
  regulatory_compliance:
    - standard_id: "osha-29-cfr-1926-95"
      requirement: "ppe_mandatory"
    - standard_id: "iec-60825"
      requirement: "laser_class_4"
  
  substrate_warnings:                           # Material-specific
    - "May discolor painted surfaces"
    - "Can damage thin coatings"
```

---

## 14. Implementation Priority (Extended)

### Tier 1: Critical Data Integrity
1. ✅ Contaminant → Compound (byproducts)
2. ⚠️ Compound → Contaminant (reverse link)
3. ⚠️ Material ↔ Contaminant (bidirectional)
4. **🔥 Exposure limits deduplication** (remove from contaminants, reference compounds)
5. **🔥 Compound ID standardization** (replace names with IDs in fumes_generated)

### Tier 2: Enhanced Usability
6. Material → Setting
7. Setting → Material
8. Setting → Contaminant
9. **PPE schema standardization** (create PPE.yaml, update all references)
10. **Regulatory standards consolidation** (create RegulatoryStandards.yaml)

### Tier 3: Advanced Features
11. Material → Compound
12. Compound → Material
13. **Hazard classification unification** (single hazard_profile schema)
14. **Process parameter normalization** (shared schema with overrides)
15. **Safety data consolidation** (unified safety_profile)

---

## 15. Migration Checklist

### Phase 1: Deduplication (Week 1)
- [ ] Create `data/shared/RegulatoryStandards.yaml`
- [ ] Create `data/shared/PPE.yaml`
- [ ] Migrate all OSHA/IEC/ASTM standards to shared file
- [ ] Remove duplicate exposure limits from Contaminants.yaml
- [ ] Replace compound names with compound_ids in fumes_generated
- [ ] Standardize PPE field names across all domains

### Phase 2: Bidirectional Links (Week 2)
- [ ] Add `produced_by_contaminants` to Compounds.yaml
- [ ] Add `related_contaminants` to Materials.yaml
- [ ] Add `related_materials` to Contaminants.yaml
- [ ] Generate reverse links programmatically
- [ ] Validate bidirectional consistency

### Phase 3: Schema Standardization (Week 3)
- [ ] Unify hazard classification system
- [ ] Consolidate safety_profile schema
- [ ] Normalize process parameter schemas
- [ ] Update all domain files to new schemas
- [ ] Run validation suite

### Phase 4: UI Integration (Week 4)
- [ ] Implement card components with related entities
- [ ] Add regulatory standards display
- [ ] Show exposure limits from compounds (not duplicated)
- [ ] Display PPE requirements with standards
- [ ] Test cross-domain navigation

---

## Appendix A: Complete Schema

See separate file: `LINKAGE_SCHEMA.json`

## Appendix B: Validation Rules

See separate file: `LINKAGE_VALIDATION_RULES.md`

## Appendix C: Migration Scripts

See: `scripts/data/generate_linkages.py`

## Appendix D: Deduplication Script

See: `scripts/data/deduplicate_exposure_limits.py`

---

**Status**: Specification Complete (Extended with Cross-Domain Normalization)  
**Next Step**: Implement Tier 1 deduplication + automated generation  
**Estimated Timeline**: 4 weeks for full implementation (extended from 3 weeks)
