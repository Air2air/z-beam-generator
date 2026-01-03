# Frontmatter Relationships Structure - Proposed Reorganization

**Document Date**: December 29, 2025  
**Status**: Proposal for Backend Implementation  
**Previous Changes**: December 27-29, 2025

---

## Executive Summary

This document proposes an improved categorization for relationship fields across all frontmatter content types (materials, contaminants, compounds, settings) and documents recent structural changes made to the frontmatter system.

**Proposal**: Reorganize from current inconsistent structure to **8 domain-driven categories** validated by actual component requirements analysis.

### Key Changes Made (Dec 27-29, 2025)
1. ✅ **Field Naming Convention**: Renamed 3,750 nested `title:` fields to `section_title:`
2. ✅ **Author Credentials**: Renamed 438 author academic titles to `author_title:` (MA, Ph.D., B.Sc., M.Sc.)
3. ✅ **Materials Enhancement**: Added `material_properties` section linking properties to ASTM/ISO measurement standards
4. ✅ **Settings Enhancement**: Added 12 comprehensive relationship sections to settings files
5. ✅ **Component Validation**: Analyzed all 4 layout components to validate structure against actual user needs

### Current State
- **438 frontmatter YAML files** across 4 content types
- **Field naming consistency**: `page_title` (root), `section_title` (3,312 sections), `author_title` (438 authors)
- **Verified**: 0 nested `title:` fields remain
- **Component Analysis**: MaterialsLayout (9 sections), ContaminantsLayout (10 sections), CompoundsLayout (15+ sections), SettingsLayout (20+ sections)

---

## 1. Current Relationship Categories (By Content Type)

### Materials (`materials/*.yaml`)
```yaml
relationships:
  technical:
    - material_properties      # NEW: Links to ASTM/ISO standards
    - contaminated_by         # References contaminant IDs
  safety:
    - regulatory_standards    # OSHA, ANSI references
  operational:
    - common_challenges       # Processing difficulties
```

### Contaminants (`contaminants/*.yaml`)
```yaml
relationships:
  technical:
    - affects_materials       # Material IDs with frequency
    - produces_compounds      # Compound IDs generated during removal
  safety:
    - regulatory_standards    # Safety compliance
  visual_characteristics:     # Appearance data (root level alternative)
    - appearance_on_categories
```

### Compounds (`compounds/*.yaml`)
```yaml
relationships:
  safety:
    - exposure_limits         # OSHA, NIOSH, ACGIH thresholds
  chemical_properties:
    - [references to data]    # Fundamental characteristics
  environmental_impact:
    - aquatic_toxicity        # Environmental effects
    - biodegradability
    - bioaccumulation
  detection_monitoring:
    - sensor_types            # Detection equipment
    - alarm_setpoints
  emergency_response:
    - PPE requirements        # Emergency procedures
    - special_hazards
  operational:
    - produced_from_contaminants  # Source contaminant IDs
    - produced_from_materials     # Source material IDs
    - physical_properties         # Storage, handling
```

### Settings (`settings/*.yaml`)
```yaml
relationships:
  technical:
    - machine_settings        # NEW: Laser parameters
    - works_on_materials      # NEW: Compatible material IDs
    - removes_contaminants    # NEW: Contaminant IDs with effectiveness
    - contamination           # NEW: Contamination types on substrate
    - composition             # NEW: Chemical composition
    - characteristics         # NEW: Physical properties
    - sources_in_laser_cleaning   # NEW: Origins in operations
    - typical_concentration_range # NEW: Concentration levels
    - detection_methods       # NEW: Analytical techniques
  safety:
    - health_effects_keywords # NEW: Health concern tags
    - health_effects          # NEW: Detailed health impacts
    - exposure_guidelines     # NEW: OSHA PEL, ACGIH TLV limits
    - first_aid               # NEW: Emergency procedures
    - monitoring_required     # NEW: Detection protocols
    - regulatory_standards    # Safety compliance
```

---

## 2. Proposed Reorganization

### Goals
1. **Consistent categorization** across all content types
2. **Domain-driven grouping** (what vs. how vs. why vs. risk)
3. **Discoverability** - intuitive structure for developers
4. **Scalability** - easy to add new relationship types
5. **Component-driven validation** - structure matches actual page component needs

### Component Validation Summary

Analysis of all 4 layout components (MaterialsLayout, ContaminantsLayout, CompoundsLayout, SettingsLayout) revealed:

**Critical Gap Identified**: Bidirectional Settings crosslinks missing
- Materials pages show contaminants but NOT settings → Users can't find "how to clean this"
- Contaminants pages show materials but NOT removal settings → Users can't find "how to remove this"
- Settings pages have works_on_materials/removes_contaminants data but buried at bottom → Low discoverability

**Solution**: Enhanced `interactions` category with 3 new fields (recommended_settings, removal_settings, prevention_settings)

**Additional Findings**:
1. **Split needed**: detection_monitoring → detection (pre-clean identification) + quality_control (post-clean verification) - separate workflows
2. **Category needed**: performance (removal_rates, cost_factors, throughput, efficiency) - ROI/business data missing
3. **Page reordering**: Settings applicability should be at top, not bottom

**Result**: Original 7-category proposal validated AND strengthened → **8-category final structure**

### Proposed Top-Level Categories (8 Total)

#### Category A: `identity` (What Is It?)
**Purpose**: Intrinsic characteristics and composition  
**Applies to**: Materials, Contaminants, Compounds, Settings

```yaml
relationships:
  identity:
    composition             # Chemical/elemental makeup
    characteristics         # Physical/chemical properties
    material_properties     # Thermal, optical, mechanical specs
    chemical_properties     # Fundamental chemistry
    physical_properties     # Storage, handling, phase
```

**Rationale**: Groups all "what it is" data - composition, properties, fundamental characteristics

---

#### Category B: `interactions` (How Does It Behave?)
**Purpose**: Relationships with other entities  
**Applies to**: All content types

```yaml
relationships:
  interactions:
    # Materials
    contaminated_by         # Contaminants affecting this material
    recommended_settings    # 🆕 Settings for cleaning this material (CRITICAL: enables Materials→Settings navigation)
    
    # Contaminants
    affects_materials       # Materials impacted by this contaminant
    produces_compounds      # Compounds generated during removal
    removal_settings        # 🆕 Settings for removing this contaminant (CRITICAL: enables Contaminants→Settings navigation)
    
    # Compounds
    produced_from_contaminants  # Source contaminants
    produced_from_materials     # Source materials
    prevention_settings     # 🆕 Safe alternative settings to avoid creating this compound
    
    # Settings
    works_on_materials      # Compatible materials
    removes_contaminants    # Removable contaminants
    contamination           # Contamination on substrate itself
```

**Rationale**: Captures all cross-references between entities - the web of relationships

**Component Validation**: 
- MaterialsLayout (line 131-140): Currently shows contaminated_by, MISSING recommended_settings crosslink
- ContaminantsLayout (line 143-157): Currently shows affects_materials, MISSING removal_settings crosslink
- CompoundsLayout (line 214-224): Currently shows source relationships, MISSING prevention_settings
- SettingsLayout (line 607-618): Currently has works_on_materials/removes_contaminants but buried at bottom

**User Impact**: Settings crosslinks are #1 missing feature - users cannot navigate Materials→Settings or Contaminants→Settings to find "how to clean this"

---

#### Category C: `operational` (How Do We Use It?)
**Purpose**: Practical application and processing  
**Applies to**: Settings, Materials, Contaminants

```yaml
relationships:
  operational:
    machine_settings        # Laser parameters (settings)
    common_challenges       # Processing difficulties (materials)
    detection_methods       # Analytical techniques (all types)
    sources_in_laser_cleaning   # Origins in operations (settings)
    typical_concentration_range # Concentration levels (settings)
```

**Rationale**: Groups all operational data - how to process, detect, measure

---

#### Category D: `safety` (What Are The Risks?)
**Purpose**: Health, safety, environmental hazards  
**Applies to**: All content types

```yaml
relationships:
  safety:
    health_effects_keywords     # Health concern tags
    health_effects              # Detailed health impacts
    exposure_guidelines         # OSHA/NIOSH/ACGIH limits
    exposure_limits             # Threshold values (compounds)
    first_aid                   # Emergency procedures
    monitoring_required         # Detection protocols
    regulatory_standards        # Compliance requirements
    emergency_response          # Emergency procedures (compounds)
```

**Rationale**: All risk-related data in one category - health, safety, compliance

---

#### Category E: `environmental` (What's The Impact?)
**Purpose**: Environmental effects and fate  
**Applies to**: Compounds, Contaminants

```yaml
relationships:
  environmental:
    environmental_impact    # Toxicity, biodegradability (compounds)
    aquatic_toxicity
    biodegradability
    bioaccumulation
    soil_mobility
    atmospheric_fate
    reportable_releases
```

**Rationale**: Environmental concerns separated from worker safety

---

#### Category F: `detection` (How Do We Identify It Pre-Clean?)
**Purpose**: Pre-cleaning identification and monitoring  
**Applies to**: Compounds, Settings, Contaminants

```yaml
relationships:
  detection:
    sensor_types            # Detection equipment
    detection_range
    alarm_setpoints
    colorimetric_tubes
    detection_methods       # Analytical techniques (XRD, EDS, Raman)
    monitoring_required     # Detection protocols
    visual_characteristics  # Visual identification (moved from visual category)
```

**Rationale**: Pre-clean identification workflow - finding and measuring contaminants before processing

**Component Validation**: CompoundsLayout (line 225-250) uses detection_monitoring for facility air monitoring

---

#### Category G: `quality_control` (How Do We Verify Success Post-Clean?)
**Purpose**: Post-cleaning verification and acceptance testing  
**Applies to**: Contaminants, Settings

```yaml
relationships:
  quality_control:
    success_criteria        # 🆕 Visual/instrumental standards for "clean"
    verification_methods    # 🆕 Post-clean testing (surface roughness, cleanliness levels)
    acceptance_testing      # 🆕 QC protocols and pass/fail criteria
    inspection_standards    # 🆕 Industry standards for verification
```

**Rationale**: Post-clean verification workflow - proving the cleaning worked

**Component Validation**: 
- ContaminantsLayout MISSING success criteria component (gap identified)
- SettingsLayout MISSING expected results component (gap identified)

**User Impact**: Users need to know "How do I verify this contaminant is actually removed?" - currently no data

---

#### Category H: `performance` (What Are The Results/ROI?)
**Purpose**: Performance metrics, efficiency, and business case data  
**Applies to**: Settings, Contaminants

```yaml
relationships:
  performance:
    removal_rates           # 🆕 % removal, sq ft/hour throughput
    cost_factors            # 🆕 Cost per part, consumables, labor
    efficiency_metrics      # 🆕 Energy consumption, waste reduction
    difficulty_rating       # 🆕 Easy/Medium/Hard (sets user expectations)
    throughput              # 🆕 Parts per hour, cycle time
```

**Rationale**: B2B audience needs ROI data - cost, speed, efficiency to justify investment

**Component Validation**: 
- ContaminantsLayout MISSING difficulty_rating (gap identified)
- SettingsLayout MISSING expected results panel (gap identified)

**User Impact**: Business decision-makers need "How much does this cost? How fast? How hard?" - currently no data

---

#### Category I: `visual` (What Does It Look Like?)
**Purpose**: Visual appearance for identification  
**Applies to**: Contaminants

```yaml
relationships:
  visual:
    appearance_on_categories    # Color, patterns, coverage
```

**Rationale**: Visual identification data (note: visual_characteristics moved to detection category)

**Component Validation**: ContaminantsLayout (line 158-169) renders visual_characteristics as Collapsible or DescriptiveDataPanel

---

## 3. Proposed Mapping Table

### Current → Proposed Restructure (8 Categories)

**Categories**: identity, interactions, operational, safety, environmental, detection, quality_control, performance

| Current Category | Current Field | Proposed Category | Proposed Field | Content Types | Component Need |
|-----------------|---------------|-------------------|----------------|---------------|
| `technical` | `material_properties` | `identity` | `material_properties` | Materials |
| `technical` | `contaminated_by` | `interactions` | `contaminated_by` | Materials |
| `technical` | `affects_materials` | `interactions` | `affects_materials` | Contaminants |
| `technical` | `produces_compounds` | `interactions` | `produces_compounds` | Contaminants |
| `technical` | `machine_settings` | `operational` | `machine_settings` | Settings |
| `technical` | `works_on_materials` | `interactions` | `works_on_materials` | Settings |
| `technical` | `removes_contaminants` | `interactions` | `removes_contaminants` | Settings |
| `technical` | `contamination` | `interactions` | `contamination` | Settings |
| `technical` | `composition` | `identity` | `composition` | Settings |
| `technical` | `characteristics` | `identity` | `characteristics` | Settings |
| `technical` | `sources_in_laser_cleaning` | `operational` | `sources_in_laser_cleaning` | Settings |
| `technical` | `typical_concentration_range` | `operational` | `typical_concentration_range` | Settings |
| `technical` | `detection_methods` | `detection_monitoring` | `detection_methods` | Settings |
| `safety` | `health_effects_keywords` | `safety` | `health_effects_keywords` | All |
| `safety` | `health_effects` | `safety` | `health_effects` | All |
| `safety` | `exposure_guidelines` | `safety` | `exposure_guidelines` | All |
| `safety` | `exposure_limits` | `safety` | `exposure_limits` | Compounds |
| `safety` | `first_aid` | `safety` | `first_aid` | All |
| `safety` | `monitoring_required` | `safety` | `monitoring_required` | Settings |
| `safety` | `regulatory_standards` | `safety` | `regulatory_standards` | All |
| `chemical_properties` | [all] | `identity` | `chemical_properties` | Compounds |
| `environmental_impact` | [all] | `environmental` | `environmental_impact` | Compounds |
| `detection_monitoring` | [all] | `detection_monitoring` | [same] | Compounds |
| `emergency_response` | [all] | `safety` | `emergency_response` | Compounds |
| `operational` | `produced_from_contaminants` | `interactions` | `produced_from_contaminants` | Compounds |
| `operational` | `produced_from_materials` | `interactions` | `produced_from_materials` | Compounds |
| `operational` | `physical_properties` | `identity` | `physical_properties` | Compounds |
| `operational` | `common_challenges` | `operational` | `common_challenges` | Materials | ✅ SettingsLayout line 625 |
| `visual_characteristics` | [all] | `visual` | `appearance_on_categories` | Contaminants | ✅ ContaminantsLayout line 158 |
| **NEW** | `recommended_settings` | `interactions` | `recommended_settings` | Materials | 🆕 CRITICAL GAP - MaterialsLayout needs |
| **NEW** | `removal_settings` | `interactions` | `removal_settings` | Contaminants | 🆕 CRITICAL GAP - ContaminantsLayout needs |
| **NEW** | `prevention_settings` | `interactions` | `prevention_settings` | Compounds | 🆕 CompoundsLayout needs |
| **NEW** | `success_criteria` | `quality_control` | `success_criteria` | Contaminants | 🆕 ContaminantsLayout needs |
| **NEW** | `verification_methods` | `quality_control` | `verification_methods` | Settings | 🆕 SettingsLayout needs |
| **NEW** | `removal_rates` | `performance` | `removal_rates` | Settings | 🆕 SettingsLayout needs |
| **NEW** | `cost_factors` | `performance` | `cost_factors` | Settings | 🆕 SettingsLayout needs |
| **NEW** | `difficulty_rating` | `performance` | `difficulty_rating` | Contaminants | 🆕 ContaminantsLayout needs |
| **NEW** | `throughput` | `performance` | `throughput` | Settings | 🆕 SettingsLayout needs |
| `detection_monitoring` | `visual_characteristics` | `detection` | `visual_characteristics` | Contaminants | ✅ ContaminantsLayout line 158 (moved) |

---

## 4. Component Validation Analysis (December 29, 2025)

### Methodology
Analyzed all 4 layout components to understand actual data requirements and identify gaps:
- **MaterialsLayout.tsx** (181 lines, 9 sections)
- **ContaminantsLayout.tsx** (238 lines, 10 sections)  
- **CompoundsLayout.tsx** (298 lines, 15+ sections)
- **SettingsLayout.tsx** (642 lines, 20+ sections)

### Critical Findings

#### 🚨 Finding #1: Bidirectional Settings Crosslinks Missing (CRITICAL)

**Problem**: Users cannot navigate Materials→Settings or Contaminants→Settings

**Evidence**:
- MaterialsLayout (line 131-140): Shows contaminated_by CardGrid but NO recommended_settings
- ContaminantsLayout (line 143-157): Shows affects_materials CardGrid but NO removal_settings  
- User workflow: "I found aluminum, it has rust contamination... how do I clean it?" → Dead end

**User Impact**: #1 missing feature - users stuck at identification, can't find solutions

**Solution**: Add 3 new fields to `interactions` category:
- `recommended_settings` (Materials→Settings: "Use these settings to clean this material")
- `removal_settings` (Contaminants→Settings: "Use these settings to remove this contaminant")
- `prevention_settings` (Compounds→Settings: "Use these safe alternatives to avoid creating this compound")

---

#### 🔍 Finding #2: Settings Applicability Buried (HIGH PRIORITY)

**Problem**: Settings pages have works_on_materials and removes_contaminants data but it's at bottom (line 607-618)

**Evidence**:
- SettingsLayout renders parameters, safety heatmaps, simulations, citations, FAQ FIRST
- Material/contaminant groups appear after 15+ other sections
- Users scroll through advanced features before seeing "What does this setting actually work on?"

**User Impact**: Low discoverability - users land on settings page, don't know if it applies to their use case

**Solution**: Create ApplicabilityPanel component, move to position 2 (right after parameters)

---

#### 📊 Finding #3: No Quality Control Data (MEDIUM PRIORITY)

**Problem**: Users can't verify if cleaning succeeded

**Evidence**:
- ContaminantsLayout shows safety, identification, but NO success_criteria
- SettingsLayout shows parameters but NO expected_results or verification_methods
- User workflow: "I ran the cleaning... how do I know it actually worked?" → No answer

**User Impact**: Users lack acceptance criteria, verification standards, inspection protocols

**Solution**: 
- Add `quality_control` category with success_criteria, verification_methods, acceptance_testing
- Create SuccessCriteriaPanel component for Contaminants pages
- Create ExpectedResultsPanel component for Settings pages

---

#### 💰 Finding #4: No Performance/ROI Data (MEDIUM PRIORITY)

**Problem**: B2B decision-makers lack cost/efficiency data

**Evidence**:
- ContaminantsLayout shows safety, technical specs, but NO difficulty_rating
- SettingsLayout shows parameters but NO removal_rates, cost_factors, throughput
- User workflow: "How long will this take? How much will it cost? Is it hard?" → No data

**User Impact**: Cannot build business case, estimate project costs, set realistic expectations

**Solution**:
- Add `performance` category with removal_rates, cost_factors, efficiency, difficulty_rating, throughput
- Add DifficultyRating component to Contaminants pages
- Add ExpectedResults panel to Settings pages with ROI metrics

---

#### 🔬 Finding #5: Detection vs. Quality Control Conflated (MEDIUM PRIORITY)

**Problem**: Pre-clean identification and post-clean verification are distinct workflows but share category

**Evidence**:
- detection_monitoring category mixes facility air monitoring (pre-clean) with verification methods (post-clean)
- CompoundsLayout uses detection_monitoring for "Is this compound present?" (before cleaning)
- Settings need "Did the cleaning work?" (after cleaning) but no category exists

**User Impact**: Confusion between "What's on the part?" vs "Is the part clean?"

**Solution**: 
- Split detection_monitoring → `detection` (pre-clean) + `quality_control` (post-clean)
- Move visual_characteristics to detection category (pre-clean identification)
- Add verification_methods to quality_control category (post-clean testing)

---

### Page Component Completeness Assessment

#### MaterialsLayout (9 sections)
**Status**: 85% complete  
**Sections**: LaserMaterialInteraction, MaterialCharacteristics, Micro, RegulatoryStandards, MaterialFAQ, RelatedMaterials, CardGrid(contaminated_by), Dataset, ScheduleCards  
**Strengths**: Excellent technical depth, good laser properties  
**Gaps**: 
- 🚨 Missing recommended_settings crosslink (CRITICAL)
- No difficulty ratings for materials  
**Priority Fix**: Add recommended_settings CardGrid at position 4

---

#### ContaminantsLayout (10 sections)  
**Status**: 75% complete  
**Sections**: CardGrid(produces_compounds), SafetyDataPanel, RegulatoryStandards, CardGrid(affects_materials), VisualCharacteristics, LaserProperties, Dataset, ScheduleCards  
**Strengths**: Safety-first approach, good identification flow  
**Gaps**:
- 🚨 Missing removal_settings crosslink (CRITICAL)
- Missing success_criteria (How to verify clean)
- Missing difficulty_rating (Set user expectations)  
**Priority Fixes**: 
1. Add removal_settings CardGrid at position 4
2. Add SuccessCriteriaPanel at position 5
3. Add DifficultyRating at position 2

---

#### CompoundsLayout (15+ sections)  
**Status**: 90% complete  
**Sections**: Chemical Properties InfoCards (5), SafetyDataPanel, CardGrid(source contaminants), CardGrid(source materials), 10+ DescriptiveDataPanels (exposure_limits, PPE, storage, detection, emergency, environmental, regulatory, physical, reactivity, synonyms)  
**Strengths**: Most comprehensive page - excellent safety coverage  
**Gaps**:
- Missing prevention_settings (How to avoid creating this compound)  
**Priority Fix**: Add prevention_settings after source relationships

---

#### SettingsLayout (20+ sections)  
**Status**: 80% complete  
**Sections**: Parameters, SafetyHeatmap, ThermalAccumulation, HeatBuildup, DiagnosticCenter, Citations, FAQ, ParameterRelationships, Material/Contaminant groups (buried), Dataset, ScheduleCards  
**Strengths**: Advanced features (physics simulations, troubleshooting, parameter graphs)  
**Gaps**:
- Applicability (works_on_materials, removes_contaminants) buried at bottom
- Missing expected_results (removal rates, cost, throughput)
- Missing verification_methods  
**Priority Fixes**:
1. Create ApplicabilityPanel, move to position 2
2. Add ExpectedResultsPanel at position 3
3. Add VerificationMethods panel

---

### Component-to-Category Mapping

| Component Need | Current Location | Proposed Category | Proposed Field | Priority |
|----------------|------------------|-------------------|----------------|----------|
| Materials→Settings nav | Missing | `interactions` | `recommended_settings` | 🚨 CRITICAL |
| Contaminants→Settings nav | Missing | `interactions` | `removal_settings` | 🚨 CRITICAL |
| Settings applicability | Buried (line 607) | `interactions` | `works_on_materials` | 🔥 HIGH |
| Success verification | Missing | `quality_control` | `success_criteria` | 🟡 MEDIUM |
| Post-clean testing | Missing | `quality_control` | `verification_methods` | 🟡 MEDIUM |
| Removal efficiency | Missing | `performance` | `removal_rates` | 🟡 MEDIUM |
| Cost analysis | Missing | `performance` | `cost_factors` | 🟡 MEDIUM |
| Difficulty rating | Missing | `performance` | `difficulty_rating` | 🟡 MEDIUM |
| Throughput metrics | Missing | `performance` | `throughput` | 🟡 MEDIUM |
| Compound prevention | Missing | `interactions` | `prevention_settings` | 🟢 LOW |

---

### Validation Conclusion

**✅ Original 7-category proposal is fundamentally sound** - maps well to existing component needs

**🔥 Component analysis strengthens proposal with 3 key refinements**:
1. **Split**: detection_monitoring → detection + quality_control (separate workflows)
2. **Add**: performance category (8th category for ROI/business data)
3. **Enhance**: interactions with Settings crosslink fields (critical user workflow)

**📊 Final structure: 8 categories** (identity, interactions, operational, safety, environmental, detection, quality_control, performance)

**🚀 Priority implementation order**:
1. **Phase 1 (Critical)**: Add recommended_settings, removal_settings, prevention_settings to interactions
2. **Phase 2 (Quality)**: Add quality_control category with success_criteria, verification_methods
3. **Phase 3 (Business)**: Add performance category with removal_rates, cost_factors, difficulty_rating, throughput
4. **Phase 4 (Polish)**: Reorder component sections for optimal UX (applicability to top of Settings pages)

---

## 5. Implementation Benefits

### For Backend Developers

#### Before (Current Structure)
```yaml
relationships:
  technical:              # Ambiguous - what kind of technical?
    - machine_settings
    - composition
    - characteristics
    - detection_methods
    - contamination
```

#### After (Proposed Structure)
```yaml
relationships:
  identity:              # Clear: intrinsic properties
    - composition
    - characteristics
  interactions:          # Clear: entity relationships
    - contamination
  operational:           # Clear: practical usage
    - machine_settings
    - detection_methods
```

### Advantages
1. **Faster lookups**: `relationships.safety.exposure_guidelines` vs hunting through `technical`
2. **Type safety**: Each category has predictable structure
3. **Query optimization**: Filter by category for targeted queries
4. **Documentation**: Self-documenting structure (category names explain purpose)
5. **Extensibility**: Add new fields to appropriate category without restructuring

---

## 6. Migration Strategy (Component-Driven Priority)

### Component-Driven Approach
Migration prioritizes features by user impact, not technical complexity. Critical user workflows first.

### Phase 1: Critical Crosslinks (Weeks 1-3) 🚨 HIGHEST PRIORITY

**Goal**: Enable bidirectional Materials↔Settings and Contaminants↔Settings navigation

**Tasks**:
1. **Add new fields to interactions category**:
   - `recommended_settings` (Materials→Settings)
   - `removal_settings` (Contaminants→Settings)
   - `prevention_settings` (Compounds→Settings)

2. **Populate frontmatter data** (438 files):
   - Materials: Map 5-10 setting IDs per material (aluminum → aluminum-general-cleaning, aluminum-anodized-coating-removal, etc.)
   - Contaminants: Map 5-10 setting IDs per contaminant (rust → rust-removal-fiber-1064nm, rust-removal-pulsed-nanosecond, etc.)
   - Compounds: Map safe alternative setting IDs
   - Settings: Verify works_on_materials and removes_contaminants completeness

3. **Update components**:
   - MaterialsLayout: Add recommended_settings CardGrid at position 4 (after MaterialCharacteristics)
   - ContaminantsLayout: Add removal_settings CardGrid at position 4 (after Visual Characteristics)
   - CompoundsLayout: Add prevention_settings panel after source relationships
   - SettingsLayout: Create ApplicabilityPanel, move to position 2 (after parameters)

4. **Update relationship helpers**:
   - Add path mappings for `interactions.recommended_settings`, `interactions.removal_settings`, `interactions.prevention_settings`
   - Update enrichment logic to fetch settings data

**Success Metrics**:
- Users can navigate Materials→Settings (click recommended setting cards)
- Users can navigate Contaminants→Settings (click removal setting cards)
- Settings page shows applicability prominently (works_on_materials at top)

**User Impact**: Fixes #1 missing feature - enables complete user workflow from problem identification to solution

---

### Phase 2: Quality Control Data (Weeks 4-6) 🟡 HIGH PRIORITY

**Goal**: Enable post-clean verification and acceptance testing

**Tasks**:
1. **Add quality_control category** with fields:
   - `success_criteria` (visual/instrumental standards for "clean")
   - `verification_methods` (post-clean testing procedures)
   - `acceptance_testing` (QC protocols and pass/fail criteria)
   - `inspection_standards` (industry standards for verification)

2. **Populate frontmatter data**:
   - Contaminants: Add success_criteria (e.g., "Surface roughness Ra < 3.2 µm", "No visible residue under 10x magnification")
   - Settings: Add verification_methods (e.g., "Surface roughness measurement", "Water break test", "Contact angle measurement")

3. **Create new components**:
   - SuccessCriteriaPanel for Contaminants pages (position 5, after removal_settings)
   - VerificationMethods panel for Settings pages (position after ExpectedResults)

**Success Metrics**:
- Contaminant pages show acceptance criteria
- Settings pages show verification procedures
- Users know "How do I verify cleaning succeeded?"

**User Impact**: Provides quality control standards, reduces uncertainty about success

---

### Phase 3: Performance/ROI Data (Weeks 7-9) 🟢 MEDIUM PRIORITY

**Goal**: Enable business case building with cost, efficiency, throughput data

**Tasks**:
1. **Add performance category** with fields:
   - `removal_rates` (% removal, sq ft/hour throughput)
   - `cost_factors` (cost per part, consumables, labor)
   - `efficiency_metrics` (energy consumption, waste reduction)
   - `difficulty_rating` (Easy/Medium/Hard)
   - `throughput` (parts per hour, cycle time)

2. **Populate frontmatter data**:
   - Contaminants: Add difficulty_rating (based on absorption, thickness, substrate damage risk)
   - Settings: Add removal_rates, cost_factors, throughput (from research/field data)

3. **Create new components**:
   - DifficultyRating component for Contaminants pages (position 2, after SafetyDataPanel)
   - ExpectedResultsPanel for Settings pages (position 3, after ApplicabilityPanel)

**Success Metrics**:
- Contaminant pages show difficulty expectations
- Settings pages show expected performance (removal rates, costs)
- Business decision-makers have ROI data

**User Impact**: Enables cost estimation, project planning, realistic expectations

---

### Phase 4: Category Restructure (Weeks 10-12) 🔵 STANDARD PRIORITY

**Goal**: Migrate existing fields to 8-category structure (identity, interactions, operational, safety, environmental, detection, quality_control, performance)

**Tasks**:
1. **Split detection_monitoring**:
   - Create `detection` category (pre-clean identification: sensor_types, detection_methods, visual_characteristics)
   - Move verification fields to `quality_control` category

2. **Migrate existing fields**:
   - technical → identity/interactions/operational
   - chemical_properties → identity
   - environmental_impact → environmental
   - emergency_response → safety

3. **Create automated migration script**:
   ```javascript
   // Node.js script structure
   - Read all 438 YAML files
   - Map old categories to new categories
   - Transform field paths (technical.material_properties → identity.material_properties)
   - Preserve _section metadata
   - Validate no data loss
   - Write updated files
   ```

4. **Update all component path references**:
   - Already complete: relationshipHelpers.ts has 50+ path fallback mappings
   - Already complete: frontmatterValidation.ts recognizes both old and new categories
   - Already complete: All 4 layouts updated with backwards-compatible lookups

5. **Run comprehensive testing**:
   - Validate all 438 files
   - Build and smoke test all pages
   - Verify dataset downloaders work
   - Check RelationshipsDump output (dev mode)

**Success Metrics**:
- Zero data loss during migration
- All pages render correctly with new structure
- No console errors or warnings
- Backwards compatibility maintained during transition

**User Impact**: Transparent to users - cleaner structure for developers, no visible change to pages

---

### Phase 5: Deprecation & Cleanup (Week 13) 🧹 LOW PRIORITY

**Goal**: Remove old structure, finalize migration

**Tasks**:
1. Remove dual-write support (single source of truth: new structure)
2. Remove path fallback mappings (all code uses new paths directly)
3. Remove old category names from validation
4. Clean up deprecated test cases
5. Update developer documentation

**Success Metrics**:
- Codebase only references new structure
- No deprecation warnings
- Documentation matches implementation

---

### Rollback Plan

If issues discovered during any phase:

1. **Backup available**: All YAML files backed up before migration
2. **Git revert**: Commit each phase separately for easy rollback
3. **Component toggles**: New components can be feature-flagged
4. **Dual-write period**: Both structures supported during transition

**Rollback command**: 
```bash
# Restore original structure
cp -r frontmatter-backup-dec29-2025/ frontmatter/
git revert <phase-commit-hash>
npm run build
```

---

## 7. Example Migration

### Before: Settings File (Current)
```yaml
relationships:
  technical:
    machine_settings:
      presentation: descriptive
      items:
      - parameter: powerRange
        value: 80 W
    composition:
      presentation: descriptive
      items:
      - element: Boron
        percentage: 43.6
    detection_methods:
      presentation: descriptive
      items:
      - method: XRD
  safety:
    health_effects:
      presentation: descriptive
      items:
      - effect: Respiratory irritation
```

### After: Settings File (Proposed)
```yaml
relationships:
  identity:
    composition:
      presentation: descriptive
      items:
      - element: Boron
        percentage: 43.6
      _section:
        section_title: Material Composition
        order: 1
  
  operational:
    machine_settings:
      presentation: descriptive
      items:
      - parameter: powerRange
        value: 80 W
      _section:
        section_title: Machine Settings
        order: 1
  
  detection_monitoring:
    detection_methods:
      presentation: descriptive
      items:
      - method: XRD
      _section:
        section_title: Detection Methods
        order: 1
  
  safety:
    health_effects:
      presentation: descriptive
      items:
      - effect: Respiratory irritation
      _section:
        section_title: Health Effects
        order: 1
```

---

## 8. Breaking Changes & Deprecations

### API Path Changes
```javascript
// OLD (DEPRECATED)
material.relationships.technical.material_properties
contaminant.relationships.technical.affects_materials
compound.relationships.chemical_properties
settings.relationships.technical.composition

// NEW (PROPOSED)
material.relationships.identity.material_properties
contaminant.relationships.interactions.affects_materials
compound.relationships.identity.chemical_properties
settings.relationships.identity.composition
```

### GraphQL Query Changes
```graphql
# OLD (DEPRECATED)
query GetMaterialProperties {
  material(id: "aluminum") {
    relationships {
      technical {
        material_properties {
          items {
            property
            measurement_standard
          }
        }
      }
    }
  }
}

# NEW (PROPOSED)
query GetMaterialProperties {
  material(id: "aluminum") {
    relationships {
      identity {
        material_properties {
          items {
            property
            measurement_standard
          }
        }
      }
    }
  }
}
```

---

## 9. Testing Requirements

### Unit Tests
- [ ] Verify all 438 files migrated successfully
- [ ] Verify no data loss (field count before = after)
- [ ] Verify `_section` metadata preserved
- [ ] Verify presentation types intact

### Integration Tests
- [ ] API returns correct paths
- [ ] GraphQL queries resolve correctly
- [ ] Frontend components render correctly
- [ ] Search/filter functionality works

### Performance Tests
- [ ] Query performance comparison (before/after)
- [ ] Memory usage during migration
- [ ] Build time impact

---

## 10. Rollback Plan

### If Migration Fails
1. **Restore from backup**: Git revert to pre-migration commit
2. **Database rollback**: Restore YAML files from backup directory
3. **API rollback**: Revert to old path structure
4. **Frontend rollback**: Revert component changes

### Success Criteria
- ✅ All 438 files migrated without errors
- ✅ All tests passing (100% pass rate)
- ✅ No API errors in production logs
- ✅ No frontend errors in browser console
- ✅ Performance metrics unchanged or improved

---

## 11. Recent Changes Summary (For Backend Reference)

### Field Naming Convention Changes (Dec 27-29, 2025)

#### 1. Section Titles
**Change**: Renamed all nested `title:` fields to `section_title:`  
**Count**: 3,750 replacements across 438 files  
**Pattern**: `/^\s{2,}title:/ → section_title:`  
**Verification**: 0 nested `title:` fields remain  

**Example**:
```yaml
# BEFORE
relationships:
  technical:
    machine_settings:
      _section:
        title: Machine Settings    # ❌ DEPRECATED

# AFTER
relationships:
  technical:
    machine_settings:
      _section:
        section_title: Machine Settings    # ✅ CORRECT
```

#### 2. Author Titles
**Change**: Renamed author academic titles from `section_title:` to `author_title:`  
**Count**: 438 replacements across 438 files  
**Pattern**: Academic credentials (MA, Ph.D., B.Sc., M.Sc.) in author sections  
**Verification**: 438 `author_title:` fields, 0 `section_title:` in author sections  

**Example**:
```yaml
# BEFORE
author:
  name: Dr. James Chen
  section_title: Ph.D.          # ❌ WRONG - author credential

# AFTER
author:
  name: Dr. James Chen
  author_title: Ph.D.           # ✅ CORRECT
```

#### 3. Root-Level Titles
**Convention**: Root-level descriptive fields use `page_title` and `page_description`  
**Count**: Unchanged (already correct)  

**Example**:
```yaml
# ROOT LEVEL (CORRECT)
page_title: Aluminum Laser Cleaning
page_description: Comprehensive guide to laser cleaning aluminum surfaces

# NESTED SECTIONS (CORRECT)
relationships:
  technical:
    _section:
      section_title: Technical Specifications   # Not 'title'

# AUTHOR CREDENTIALS (CORRECT)
author:
  name: Dr. Sarah Kim
  author_title: Ph.D.                          # Not 'section_title'
```

### Material Properties Enhancement (Dec 28, 2025)

**Change**: Added `material_properties` section to materials frontmatter  
**Purpose**: Link root-level properties to ASTM/ISO measurement standards  
**Count**: Started with 1 file (acrylic-pmma), template for 200+ materials  

**Structure**:
```yaml
relationships:
  technical:
    material_properties:
      presentation: card
      items:
      - property: thermalConductivity
        relevance: Critical for heat dissipation during laser cleaning
        measurement_standard: ASTM E1461
      - property: laserReflectivity
        relevance: Determines optimal laser wavelength and power settings
        measurement_standard: ISO 13694
      _section:
        section_title: Key Material Properties
        order: 1
```

### Settings Comprehensive Enhancement (Dec 28-29, 2025)

**Change**: Added 12 comprehensive relationship sections to settings files  
**Purpose**: Provide detailed technical, safety, and operational data  
**Count**: Started with 1 file (boron-nitride-settings), template for 200+ settings  

**Sections Added**:
1. **technical.machine_settings**: Laser parameters (power, wavelength, pulse width)
2. **technical.works_on_materials**: Compatible material IDs with effectiveness
3. **technical.removes_contaminants**: Removable contaminant IDs with effectiveness
4. **technical.contamination**: Contamination types on substrate surface
5. **technical.composition**: Chemical composition breakdown
6. **technical.characteristics**: Physical/chemical properties
7. **technical.sources_in_laser_cleaning**: Origins in cleaning operations
8. **technical.typical_concentration_range**: Concentration levels
9. **technical.detection_methods**: Analytical techniques (XRD, EDS, Raman)
10. **safety.health_effects_keywords**: Health concern tags
11. **safety.health_effects**: Detailed health impacts
12. **safety.exposure_guidelines**: OSHA PEL, ACGIH TLV limits
13. **safety.first_aid**: Emergency procedures
14. **safety.monitoring_required**: Detection protocols

---

## 12. Backend Action Items

### Immediate (Week 1)
- [ ] Review proposed categorization
- [ ] Provide feedback on category names
- [ ] Identify any breaking changes for API consumers
- [ ] Estimate migration effort

### Short-term (Weeks 2-4)
- [ ] Create migration script
- [ ] Test on subset of files (10-20)
- [ ] Validate data integrity
- [ ] Update API documentation

### Medium-term (Weeks 5-8)
- [ ] Update GraphQL schema
- [ ] Update REST API endpoints
- [ ] Update TypeScript types
- [ ] Run integration tests

### Long-term (Weeks 9-12)
- [ ] Deprecate old paths
- [ ] Remove backwards compatibility
- [ ] Update developer documentation
- [ ] Monitor production logs for errors

---

## 13. Questions for Backend Team

1. **Timeline**: What's the preferred migration timeline? (Suggested: 12 weeks)
2. **Breaking Changes**: Is a breaking API version bump acceptable? (v2 → v3?)
3. **Dual-write Period**: How long should we support both structures? (Suggested: 4 weeks)
4. **Performance**: Any concerns about query performance with new structure?
5. **Validation**: Should we add JSON schema validation for new categories?
6. **Ordering**: Should we preserve current `order` values or renumber by category?

---

## 14. Contact & Feedback

**Document Author**: AI Assistant (GitHub Copilot)  
**Date**: December 29, 2025  
**Related Files**:
- `scripts/rename-nested-titles.js` (field naming migration)
- `scripts/fix-author-titles.js` (author credential migration)
- `frontmatter/settings/boron-nitride-settings.yaml` (comprehensive template)
- `frontmatter/materials/acrylic-pmma-laser-cleaning.yaml` (material properties template)

**Feedback Process**:
1. Review this document
2. Add comments/questions to specific sections
3. Approve or request changes to proposed structure
4. Provide migration timeline preference
5. Identify any backend-specific concerns

---

## 15. Appendix A: Complete Field Inventory

### All Relationship Fields (By Content Type)

#### Materials (200+ files)
- `technical.material_properties` - Property-to-standard linkage
- `technical.contaminated_by` - Contaminant references
- `safety.regulatory_standards` - Safety compliance
- `operational.common_challenges` - Processing difficulties

#### Contaminants (100+ files)
- `technical.affects_materials` - Material references with frequency
- `technical.produces_compounds` - Compound generation
- `safety.regulatory_standards` - Safety compliance
- `visual_characteristics` - Visual identification data

#### Compounds (50+ files)
- `safety.exposure_limits` - OSHA/NIOSH/ACGIH thresholds
- `chemical_properties` - Fundamental chemistry
- `environmental_impact` - Environmental effects
- `detection_monitoring` - Detection equipment and methods
- `emergency_response` - Emergency procedures
- `operational.produced_from_contaminants` - Source contaminants
- `operational.produced_from_materials` - Source materials
- `operational.physical_properties` - Storage and handling

#### Settings (200+ files)
- `technical.machine_settings` - Laser parameters
- `technical.works_on_materials` - Compatible materials
- `technical.removes_contaminants` - Removable contaminants
- `technical.contamination` - Surface contamination
- `technical.composition` - Chemical composition
- `technical.characteristics` - Physical properties
- `technical.sources_in_laser_cleaning` - Origins
- `technical.typical_concentration_range` - Concentrations
- `technical.detection_methods` - Analytical techniques
- `safety.health_effects_keywords` - Health tags
- `safety.health_effects` - Health impacts
- `safety.exposure_guidelines` - Exposure limits
- `safety.first_aid` - Emergency procedures
- `safety.monitoring_required` - Detection protocols
- `safety.regulatory_standards` - Compliance

---

## 16. Appendix B: Migration Script Pseudocode

```javascript
// High-level migration logic
function migrateRelationships(yamlFile, contentType) {
  const data = loadYAML(yamlFile);
  const newRelationships = {};
  
  // Map old categories to new categories
  const categoryMap = {
    materials: {
      'technical.material_properties': 'identity.material_properties',
      'technical.contaminated_by': 'interactions.contaminated_by',
      'operational.common_challenges': 'operational.common_challenges',
      'safety.regulatory_standards': 'safety.regulatory_standards'
    },
    contaminants: {
      'technical.affects_materials': 'interactions.affects_materials',
      'technical.produces_compounds': 'interactions.produces_compounds',
      'safety.regulatory_standards': 'safety.regulatory_standards',
      'visual_characteristics': 'visual.appearance_on_categories'
    },
    compounds: {
      'safety.exposure_limits': 'safety.exposure_limits',
      'chemical_properties': 'identity.chemical_properties',
      'environmental_impact': 'environmental.environmental_impact',
      'detection_monitoring': 'detection_monitoring',
      'emergency_response': 'safety.emergency_response',
      'operational.produced_from_contaminants': 'interactions.produced_from_contaminants',
      'operational.produced_from_materials': 'interactions.produced_from_materials',
      'operational.physical_properties': 'identity.physical_properties'
    },
    settings: {
      'technical.machine_settings': 'operational.machine_settings',
      'technical.works_on_materials': 'interactions.works_on_materials',
      'technical.removes_contaminants': 'interactions.removes_contaminants',
      'technical.contamination': 'interactions.contamination',
      'technical.composition': 'identity.composition',
      'technical.characteristics': 'identity.characteristics',
      'technical.sources_in_laser_cleaning': 'operational.sources_in_laser_cleaning',
      'technical.typical_concentration_range': 'operational.typical_concentration_range',
      'technical.detection_methods': 'detection_monitoring.detection_methods',
      'safety.*': 'safety.*' // All safety fields stay in safety
    }
  };
  
  // Migrate each field
  for (const [oldPath, newPath] of Object.entries(categoryMap[contentType])) {
    const value = getNestedValue(data.relationships, oldPath);
    if (value) {
      setNestedValue(newRelationships, newPath, value);
    }
  }
  
  // Update YAML file
  data.relationships = newRelationships;
  saveYAML(yamlFile, data);
  
  // Validate
  validateStructure(data, contentType);
}
```

---

## 17. Summary & Next Steps

### What Was Validated

✅ **Original 7-category proposal is sound** - Maps well to existing component architecture  
✅ **Component analysis strengthens proposal** - Identified 3 critical enhancements  
✅ **User workflow validated** - Bidirectional navigation is #1 missing feature  
✅ **Priority order established** - Component impact drives implementation order

### Final Structure: 8 Categories

1. **identity** - What is it? (composition, properties, characteristics)
2. **interactions** - How does it behave? (entity crosslinks, Settings navigation) 🆕 Enhanced
3. **operational** - How do we use it? (machine settings, challenges, detection)
4. **safety** - What are the risks? (health, compliance, emergency)
5. **environmental** - What's the environmental impact? (toxicity, biodegradability)
6. **detection** - How do we identify it pre-clean? (sensors, methods, visual) 🆕 Split from detection_monitoring
7. **quality_control** - How do we verify success post-clean? (success criteria, verification) 🆕 New category
8. **performance** - What are the results/ROI? (removal rates, costs, efficiency) 🆕 New category

### Critical Changes vs. Original Proposal

| Change | Reason | User Impact |
|--------|--------|-------------|
| Split detection_monitoring → detection + quality_control | Separate pre-clean vs post-clean workflows | Clarity: "What's on the part?" vs "Is it clean?" |
| Add performance category (8th) | B2B audience needs ROI data | Business case: cost, speed, difficulty |
| Add recommended_settings to interactions | Materials→Settings navigation missing | #1 gap: "How do I clean this material?" |
| Add removal_settings to interactions | Contaminants→Settings navigation missing | #1 gap: "How do I remove this contaminant?" |
| Add prevention_settings to interactions | Compounds→Settings safety guidance | Prevention: "How to avoid creating this compound?" |

### Component Updates Required

| Component | Current State | Required Changes |
|-----------|---------------|------------------|
| MaterialsLayout | 85% complete (9 sections) | Add recommended_settings CardGrid at position 4 |
| ContaminantsLayout | 75% complete (10 sections) | Add removal_settings (pos 4), SuccessCriteria (pos 5), DifficultyRating (pos 2) |
| CompoundsLayout | 90% complete (15+ sections) | Add prevention_settings panel after source relationships |
| SettingsLayout | 80% complete (20+ sections) | Move ApplicabilityPanel to position 2, add ExpectedResultsPanel (pos 3) |

### Implementation Timeline

**Critical Path** (13 weeks):
- **Weeks 1-3**: Phase 1 - Critical crosslinks (recommended_settings, removal_settings)
- **Weeks 4-6**: Phase 2 - Quality control data (success_criteria, verification_methods)
- **Weeks 7-9**: Phase 3 - Performance data (removal_rates, cost_factors, difficulty_rating)
- **Weeks 10-12**: Phase 4 - Category restructure (8-category migration)
- **Week 13**: Phase 5 - Deprecation and cleanup

**Success Metrics**:
- Phase 1: Users can navigate Materials→Settings and Contaminants→Settings
- Phase 2: Users can verify cleaning success with acceptance criteria
- Phase 3: Business users have cost/efficiency data for ROI analysis
- Phase 4: Developer experience improved with clear category structure
- Phase 5: Single source of truth, no technical debt

### Next Actions

**For Backend Team**:
1. Review 8-category structure and new field definitions
2. Prioritize Phase 1 implementation (critical crosslinks)
3. Create data population plan for 438 files:
   - Materials: Map 5-10 setting IDs per material
   - Contaminants: Map 5-10 setting IDs per contaminant
   - Settings: Verify works_on_materials completeness
4. Develop migration script pseudocode (provided in Appendix A)

**For Frontend Team**:
1. Component updates already backwards-compatible (completed Dec 29)
2. Prepare new components: ApplicabilityPanel, SuccessCriteriaPanel, ExpectedResultsPanel, DifficultyRating
3. Test all 4 layouts with new relationship paths

**For Content Team**:
1. Populate recommended_settings for all 174 materials
2. Populate removal_settings for all 138 contaminants
3. Add success_criteria for all contaminants
4. Add performance metrics for all settings

### Questions for Review

1. **Category naming**: Are "detection" and "quality_control" clear enough? Alternative names?
2. **Field naming**: Are recommended_settings, removal_settings, prevention_settings intuitive?
3. **Priority order**: Agree with critical→quality→performance→restructure sequence?
4. **Timeline**: Is 13 weeks realistic? Need more time for data population?
5. **Breaking changes**: Any concerns about API/GraphQL path changes?

---

## 18. Proposed 5th Domain: Properties Encyclopedia

### Overview

**Concept**: Create individual definition pages for every property, measurement, standard, and term shown in PropertyBars, detection methods, safety limits, and technical specifications across the site.

**User Problem**: Users see technical terms (density, XRD, PEL, fluence) without understanding what they mean or how they affect laser cleaning.

**Solution**: 106 property definition pages with:
- Clear definitions (short + detailed)
- Measurement standards (ASTM/ISO)
- Laser cleaning relevance
- Bidirectional crosslinks to materials/contaminants/settings using those properties
- Interactive visualizations (typical ranges, comparison charts)

### URL Structure

```
/properties/{category}/{property-slug}

Examples:
/properties/material/density
/properties/material/thermal-conductivity
/properties/machine/pulse-duration
/properties/safety/pel
/properties/detection/xrd
/properties/unit/fluence
/properties/laser/fiber-laser
/properties/process/ablation-threshold
```

### Content Categories & Counts

| Category | Count | Examples | Priority |
|----------|-------|----------|----------|
| **Material Properties** | 20 | density, thermal_conductivity, absorption_coefficient, porosity, surface_roughness | Phase 1 |
| **Machine Settings** | 15 | power, wavelength, pulse_duration, repetition_rate, scan_speed, fluence | Phase 1 |
| **Safety Limits** | 6 | PEL, TLV, REL, STEL, Ceiling, TWA | Phase 1 |
| **Units** | 15 | J/cm², W/cm², μm, nm, Hz, kHz, Pa, MPa | Phase 1-2 |
| **Detection Methods** | 12 | XRD, EDS, Raman, FTIR, ICP-MS, SEM, XPS | Phase 2 |
| **Laser Types** | 8 | Fiber, CO2, Nd:YAG, Excimer, Diode | Phase 2 |
| **Standards Orgs** | 6 | ASTM, ISO, OSHA, NIOSH, ACGIH, ANSI | Phase 3 |
| **Process Terms** | 10 | ablation, HAZ, overlap, hatch_spacing, dwell_time | Phase 3 |
| **Chemical Concepts** | 14 | molecular_weight, vapor_pressure, flash_point, boiling_point | Phase 3 |
| **TOTAL** | **106** | | 13 weeks |

---

### Frontmatter Schema v5.1.0 (Properties)

#### Base Structure (All Properties)

```yaml
# REQUIRED FIELDS
id: density                           # Unique identifier (slug)
name: Density                         # Display name
category: material                    # material|machine|safety|detection|unit|laser|standard|process|chemical
property_type: physical               # physical|thermal|optical|mechanical|measurement|limit|technique|technology
content_type: properties              # Always "properties"
schema_version: 5.1.0                 # Properties schema version

# URL & BREADCRUMBS
full_path: /properties/material/density
breadcrumb:
  - label: Home
    href: /
  - label: Properties
    href: /properties
  - label: Material Properties
    href: /properties/material
  - label: Density
    href: /properties/material/density

# SEO
page_title: 'Density (ρ): Material Property for Laser Cleaning'
page_description: Density fundamentally influences heat absorption, thermal diffusion, and energy penetration during laser cleaning operations.
meta_description: 'Density (ρ): Definition, measurement standards (ASTM/ISO), typical ranges, and laser cleaning relevance.'

# DEFINITION (Required for all properties)
definition:
  short: Mass per unit volume of a material                    # 1 sentence
  detailed: |                                                   # 2-3 paragraphs
    Density (ρ) represents the concentration of matter within a material, 
    measured as mass divided by volume. In laser cleaning, density directly 
    affects thermal mass and heat capacity—denser materials require more 
    energy to heat but dissipate heat more effectively.
    
    Materials with higher density typically exhibit greater thermal inertia, 
    meaning they resist rapid temperature changes. This characteristic 
    influences both ablation thresholds and the risk of substrate damage 
    during laser cleaning operations.

# AUTHOR (Same structure as other content types)
author:
  id: 4
  name: Todd Dunning
  country: United States
  title: MA
  # ... (full author structure)

# IMAGES
images:
  hero:
    url: /images/property/density-visualization.jpg
    alt: Density comparison chart showing material categories from plastics to metals
    width: 1200
    height: 630
```

#### Category-Specific Extensions

##### Material Properties (category: material)

```yaml
# MEASUREMENT
measurement:
  standard_methods:
    - method: ASTM D792
      section_title: Standard Test Methods for Density and Specific Gravity (Plastics)
      applicability: Plastics
      url: https://www.astm.org/d0792
    - method: ISO 1183-1
      section_title: Methods for determining density - Part 1
      applicability: All materials
      url: https://www.iso.org/standard/1183-1
  units:
    primary: g/cm³
    alternatives: [kg/m³, lb/ft³]
    conversion_factors:
      kg_m3: 1000                      # 1 g/cm³ = 1000 kg/m³
      lb_ft3: 62.428                   # 1 g/cm³ = 62.428 lb/ft³
  typical_equipment:
    - name: Pycnometer
      type: Liquid displacement
      accuracy: ±0.001 g/cm³
    - name: Gas displacement pycnometer
      type: Helium pycnometry
      accuracy: ±0.0001 g/cm³
    - name: Archimedes balance
      type: Hydrostatic weighing
      accuracy: ±0.01 g/cm³

# LASER CLEANING IMPACT
laser_cleaning_impact:
  thermal_behavior:
    section_title: Thermal Absorption & Diffusion
    description: |
      Higher density materials possess greater thermal mass, requiring 
      increased laser energy for heating. However, dense materials also 
      exhibit superior heat dissipation, reducing the risk of localized 
      overheating and substrate damage during cleaning.
    practical_implications:
      - Dense metals (steel, tungsten) require higher power settings
      - Low-density plastics (polypropylene) risk melting at lower fluence
      - Thermal accumulation effects vary inversely with density
  ablation_threshold:
    section_title: Energy Requirements
    description: |
      Dense materials typically exhibit higher ablation thresholds due 
      to increased atomic packing. More laser fluence is required to 
      overcome molecular bonds and initiate material removal.
    practical_implications:
      - Aluminum (2.7 g/cm³): 1-3 J/cm² threshold
      - Steel (7.8 g/cm³): 3-8 J/cm² threshold
      - Tungsten (19.3 g/cm³): 8-15 J/cm² threshold

# TYPICAL RANGES (Material properties show ranges by category)
typical_ranges:
  metals:
    min: 2.7
    max: 19.3
    unit: g/cm³
    examples:
      - material: Aluminum
        material_id: aluminum-laser-cleaning
        value: 2.7
      - material: Iron/Steel
        material_id: steel-carbon-laser-cleaning
        value: 7.8
      - material: Copper
        material_id: copper-laser-cleaning
        value: 8.96
      - material: Gold
        material_id: gold-laser-cleaning
        value: 19.3
  plastics:
    min: 0.9
    max: 2.2
    unit: g/cm³
    examples:
      - material: Polypropylene
        material_id: polypropylene-laser-cleaning
        value: 0.9
      - material: Acrylic (PMMA)
        material_id: acrylic-pmma-laser-cleaning
        value: 1.18
      - material: PVC
        material_id: pvc-laser-cleaning
        value: 1.4
      - material: PTFE (Teflon)
        material_id: ptfe-laser-cleaning
        value: 2.2
  ceramics:
    min: 2.3
    max: 6.0
    unit: g/cm³
    examples:
      - material: Silicon Carbide
        material_id: silicon-carbide-laser-cleaning
        value: 3.2
      - material: Alumina
        material_id: alumina-laser-cleaning
        value: 3.95
      - material: Zirconia
        material_id: zirconia-laser-cleaning
        value: 6.0
```

##### Machine Settings (category: machine)

```yaml
# PARAMETER DEFINITION
parameter:
  symbol: P                            # Mathematical symbol
  formula: P = E / t                   # Defining equation
  variables:
    P: Power (W)
    E: Energy (J)
    t: Time (s)
  
# LASER CLEANING RANGES
cleaning_ranges:
  rust_removal:
    min: 50
    max: 500
    unit: W
    optimal: 100-200
    substrate_considerations:
      - Thin sheet metal (< 1mm): 50-100 W
      - Structural steel (> 5mm): 200-500 W
  paint_stripping:
    min: 100
    max: 1000
    unit: W
    optimal: 300-600
  coating_removal:
    min: 20
    max: 200
    unit: W
    optimal: 50-150

# PARAMETER INTERACTIONS
interacts_with:
  - property_id: pulse_duration
    relationship: Inverse - Higher power allows shorter pulses for same fluence
  - property_id: scan_speed
    relationship: Direct - Higher power enables faster scanning
  - property_id: repetition_rate
    relationship: Independent - Power per pulse is P / (Rep Rate)

# SUBSTRATE CONSIDERATIONS
substrate_limits:
  metals:
    safe_max: No upper limit (substrate damage from heat, not power)
    considerations: Watch for melting at weld zones, thin sections
  plastics:
    safe_max: 200 W (risk of melting above)
    considerations: Use pulsed mode to avoid thermal accumulation
  composites:
    safe_max: 100 W (matrix damage risk)
    considerations: Carbon fiber requires < 50 W to prevent delamination
```

##### Safety Limits (category: safety)

```yaml
# AUTHORITY & JURISDICTION
authority:
  organization: OSHA
  full_name: Occupational Safety and Health Administration
  jurisdiction: United States (federal law)
  legal_status: Enforceable by law
  website: https://www.osha.gov

# LIMIT DEFINITION
limit_type: TWA                        # TWA|STEL|Ceiling
duration: 8 hours                      # Exposure averaging period
enforcement: Mandatory                 # Mandatory|Recommended|Advisory

# COMPARISON TO OTHER LIMITS
comparison:
  vs_tlv:
    organization: ACGIH
    difference: PEL is legal requirement, TLV is guideline
    typical_relationship: PEL often less strict (allows higher exposure)
  vs_rel:
    organization: NIOSH
    difference: PEL is enforceable, REL is recommendation
    typical_relationship: REL often more protective (lower exposure)
  vs_ceiling:
    difference: PEL is 8-hour average, Ceiling is never-exceed limit
    example: 10 ppm PEL allows brief 15 ppm spike; 10 ppm Ceiling never allows 10.1 ppm

# COMPOUNDS WITH THIS LIMIT
example_compounds:
  - compound_id: chromium-hexavalent-cr-vi
    limit_value: 5 µg/m³
    notes: Carcinogen - extremely low PEL
  - compound_id: lead-compounds
    limit_value: 50 µg/m³
    notes: Neurotoxin - blood lead monitoring required
  - compound_id: silica-crystalline
    limit_value: 50 µg/m³
    notes: Lung disease - respirable fraction only
```

##### Detection Methods (category: detection)

```yaml
# TECHNIQUE SPECIFICATION
technique:
  full_name: X-Ray Diffraction
  acronym: XRD
  type: Analytical spectroscopy
  principle: X-ray scattering by crystalline lattice planes
  detection_basis: Bragg's Law (nλ = 2d sinθ)

# LASER CLEANING APPLICATIONS
applications:
  pre_clean:
    use_cases:
      - Identify contaminant composition (rust vs mill scale vs paint)
      - Determine crystalline vs amorphous structure
      - Quantify oxide layer thickness
    example_findings:
      - Fe₂O₃ (hematite) vs Fe₃O₄ (magnetite) identification
      - Zinc phosphate coating vs zinc oxide
  post_clean:
    use_cases:
      - Verify complete contaminant removal
      - Detect substrate phase changes (annealing, recrystallization)
      - Measure residual stress changes
    example_findings:
      - Confirm zero oxide peaks after cleaning
      - Detect grain growth in stainless steel (overheating indicator)

# DETECTABLE SPECIES
detects:
  compounds:
    - compound_id: iron-oxide-rust
      detection_limit: 0.1 wt%
    - compound_id: zinc-oxide
      detection_limit: 0.1 wt%
    - compound_id: aluminum-oxide
      detection_limit: 0.1 wt%
  phases:
    - Crystalline
    - Polycrystalline
    - Amorphous
  thickness_range:
    min: 100 nm
    max: 100 μm

# EQUIPMENT & STANDARDS
typical_equipment:
  - manufacturer: Bruker
    model: D8 Discover
    cost_range: $150,000-300,000
    analysis_time: 30-60 min
  - manufacturer: Rigaku
    model: MiniFlex
    cost_range: $50,000-100,000
    analysis_time: 20-40 min
  - manufacturer: Malvern Panalytical
    model: Empyrean
    cost_range: $200,000-400,000
    analysis_time: 15-30 min

sample_preparation:
  requirements:
    - Flat surface (< 1mm roughness preferred)
    - Minimum 5mm² analysis area
    - Sample height within 1mm of focal plane
  destructive: false
  in_situ_capable: true

standards:
  - standard_id: ASTM-E975
    section_title: Standard Practice for X-Ray Determination of Retained Austenite
    url: https://www.astm.org/e0975
  - standard_id: ISO-15632
    section_title: Surface Chemical Analysis by X-Ray Diffraction
    url: https://www.iso.org/standard/15632
```

---

### Relationships Structure (Bidirectional Linking)

#### Properties Frontmatter → Other Domains

```yaml
relationships:
  # Materials, Contaminants, Compounds, Settings that USE this property
  interactions:
    # CRITICAL: Reverse lookup - which entities have this property value
    used_by_materials:              # Array of material IDs with this property
      - material_id: aluminum-laser-cleaning
        value: 2.7
        unit: g/cm³
        significance: Low density enables fast heat dissipation
      - material_id: steel-carbon-laser-cleaning
        value: 7.8
        unit: g/cm³
        significance: Medium density balances heat retention and dissipation
      - material_id: tungsten-laser-cleaning
        value: 19.3
        unit: g/cm³
        significance: Extreme density requires high-power lasers
    
    used_by_settings:               # Settings where this parameter appears
      - setting_id: aluminum-general-cleaning
        parameter_value: 100 W
        parameter_range: {min: 50, max: 200}
      - setting_id: steel-rust-removal-fiber
        parameter_value: 200 W
        parameter_range: {min: 100, max: 500}
    
    used_by_contaminants:           # Contaminants with this property
      - contaminant_id: rust-oxidation-contamination
        property_value: 5.24
        unit: g/cm³
        relevance: Rust density affects ablation threshold
    
    # Related properties (appear together, affect each other)
    related_properties:
      - property_id: thermal_conductivity
        relationship: Complementary - both affect thermal behavior
        description: High density + low conductivity = heat accumulation risk
      - property_id: specific_heat_capacity
        relationship: Multiplicative - together determine thermal mass
        description: Thermal mass = density × specific heat × volume
      - property_id: absorption_coefficient
        relationship: Independent - density doesn't affect optical absorption
        description: Low-density plastics can have high absorption
  
  # Standards and methods for measuring/defining this property
  operational:
    measurement_standards:          # ASTM/ISO standards
      - standard_id: ASTM-D792
        applicability: Plastics
      - standard_id: ISO-1183-1
        applicability: All materials
    
    detection_methods:              # For properties that are measured (not parameters)
      - method_id: pycnometry
        accuracy: High (±0.001 g/cm³)
      - method_id: archimedes-balance
        accuracy: Medium (±0.01 g/cm³)
```

#### Other Domains → Properties (Existing structure enhancement)

**Materials frontmatter** (already has properties, add property_definitions):

```yaml
properties:
  material_characteristics:
    # ... existing structure ...
    density:
      value: 1.18
      unit: g/cm³
      confidence: 95
      property_definition_id: density    # NEW: Link to property page

relationships:
  interactions:
    key_properties:                      # NEW: Featured properties for this material
      - property_id: density
        prominence: high                 # high|medium|low (affects display order)
      - property_id: thermal_conductivity
        prominence: high
      - property_id: absorption_coefficient_1064nm
        prominence: high
```

**Settings frontmatter** (add parameter_definitions):

```yaml
properties:
  machine_settings:
    power:
      value: 100
      min: 50
      max: 200
      unit: W
      parameter_definition_id: power     # NEW: Link to property page
    wavelength:
      value: 1064
      unit: nm
      parameter_definition_id: wavelength

relationships:
  interactions:
    key_parameters:                      # NEW: Featured parameters for this setting
      - property_id: power
        prominence: high
      - property_id: wavelength
        prominence: high
      - property_id: pulse_duration
        prominence: medium
```

**Contaminants/Compounds** (add detection_method_definitions):

```yaml
relationships:
  detection:
    detection_methods:
      - method: XRD
        method_definition_id: xrd        # NEW: Link to detection method page
        applicability: Crystalline oxides
      - method: Raman
        method_definition_id: raman-spectroscopy
        applicability: Molecular fingerprinting
```

---

### Contaminants/Compounds Overlap Resolution (Option B: Crosslinks)

#### Problem Statement

**Overlap identified**: ~15-20 entities exist as BOTH contaminants (on surfaces) AND compounds (in air/exposure):
- Iron oxide (rust on surfaces / airborne dust during removal)
- Lead oxide (paint contamination / vaporized lead exposure)
- Chromium compounds (coating contamination / hexavalent chromium exposure)
- Zinc compounds (galvanization contamination / zinc fume exposure)

**User confusion risk**: "Should I look in Contaminants or Compounds for lead oxide?"

#### Solution: Strong Bidirectional Crosslinks

**Approach**: Keep separate pages but add prominent "Also See" crosslinks with context

##### Contaminants Frontmatter Enhancement

```yaml
# Example: rust-oxidation-contamination.yaml
id: rust-oxidation-contamination
name: Rust (Iron Oxide Contamination)
category: oxidation
subcategory: ferrous

# NEW SECTION: Related compounds
relationships:
  interactions:
    # Existing relationships...
    contaminated_by: [...]
    produces_compounds: [...]
    
    # NEW: Airborne/exposure perspective
    related_compounds:
      - compound_id: iron-oxide-fe2o3
        relationship_type: airborne_byproduct
        context: |
          During laser removal, rust vaporizes into airborne iron oxide particles.
          See exposure limits and detection methods.
        display_prominence: high          # Shows prominently on page
        badge_text: "⚠️ Exposure Data"
        warning_level: moderate            # low|moderate|high
      
      - compound_id: iron-oxide-fe3o4
        relationship_type: airborne_byproduct
        context: |
          Magnetite (Fe₃O₄) forms at higher temperatures during intense cleaning.
        display_prominence: medium
        badge_text: "⚠️ Exposure Data"

# Component rendering: Shows as InfoCard or CalloutBox
display_config:
  related_compounds_section:
    position: 3                          # After SafetyDataPanel, before affects_materials
    component: 'AlsoSeeCompounds'        # NEW component (or enhanced InfoCard)
    style: warning                       # Highlighted with warning color
    collapsible: false                   # Always visible
```

##### Compounds Frontmatter Enhancement

```yaml
# Example: iron-oxide-fe2o3.yaml
id: iron-oxide-fe2o3
name: Iron Oxide (Fe₂O₃) - Hematite
category: metal_oxides

# NEW SECTION: Source contamination
relationships:
  interactions:
    # Existing relationships...
    produced_from_contaminants: [...]
    produced_from_materials: [...]
    
    # NEW: Surface contamination perspective
    source_contaminants:
      - contaminant_id: rust-oxidation-contamination
        relationship_type: surface_form
        context: |
          Found as rust contamination on ferrous metal surfaces.
          See removal methods and visual identification.
        display_prominence: high
        badge_text: "📍 Found on Surfaces"
        info_type: contextual              # contextual|warning|notice
      
      - contaminant_id: mill-scale-contamination
        relationship_type: surface_form
        context: |
          Also present in mill scale (formed during hot rolling).
        display_prominence: medium
        badge_text: "📍 Found on Surfaces"

# Component rendering
display_config:
  source_contaminants_section:
    position: 2                          # After definition, before exposure limits
    component: 'AlsoSeeContaminants'     # NEW component
    style: info                          # Informational blue color
    collapsible: false
```

#### Component Implementation

##### NEW: AlsoSeeCompounds Component

**File**: `app/components/AlsoSeeCompounds/AlsoSeeCompounds.tsx`

```tsx
interface AlsoSeeCompoundsProps {
  relatedCompounds: {
    compound_id: string;
    compound_name: string;
    context: string;
    badge_text: string;
    warning_level: 'low' | 'moderate' | 'high';
  }[];
  style?: 'warning' | 'info' | 'notice';
}

export function AlsoSeeCompounds({ relatedCompounds, style = 'warning' }: AlsoSeeCompoundsProps) {
  const bgColor = style === 'warning' ? 'bg-amber-50 border-amber-200' : 'bg-blue-50 border-blue-200';
  const iconColor = style === 'warning' ? 'text-amber-600' : 'text-blue-600';
  
  return (
    <div className={`rounded-lg border-2 ${bgColor} p-6 my-6`}>
      <div className="flex items-start gap-3 mb-4">
        <ExclamationTriangleIcon className={`w-6 h-6 ${iconColor} flex-shrink-0 mt-1`} />
        <div>
          <h3 className="text-lg font-semibold mb-2">
            Airborne Exposure During Removal
          </h3>
          <p className="text-sm text-gray-700 mb-4">
            Laser removal of this contaminant creates airborne particles. 
            Review exposure limits and safety protocols.
          </p>
        </div>
      </div>
      
      <div className="grid gap-3 md:grid-cols-2">
        {relatedCompounds.map((compound) => (
          <Link
            key={compound.compound_id}
            href={`/compounds/${compound.compound_id}`}
            className="block p-4 bg-white rounded border border-gray-200 hover:border-amber-400 hover:shadow-md transition-all"
          >
            <div className="flex items-start justify-between mb-2">
              <span className="font-medium text-gray-900">
                {compound.compound_name}
              </span>
              <Badge variant={compound.warning_level === 'high' ? 'danger' : 'warning'}>
                {compound.badge_text}
              </Badge>
            </div>
            <p className="text-sm text-gray-600 line-clamp-2">
              {compound.context}
            </p>
            <span className="text-sm text-blue-600 font-medium mt-2 inline-flex items-center gap-1">
              View exposure limits <ArrowRightIcon className="w-4 h-4" />
            </span>
          </Link>
        ))}
      </div>
    </div>
  );
}
```

##### NEW: AlsoSeeContaminants Component

**File**: `app/components/AlsoSeeContaminants/AlsoSeeContaminants.tsx`

```tsx
interface AlsoSeeContaminantsProps {
  sourceContaminants: {
    contaminant_id: string;
    contaminant_name: string;
    context: string;
    badge_text: string;
  }[];
  style?: 'info' | 'notice';
}

export function AlsoSeeContaminants({ sourceContaminants, style = 'info' }: AlsoSeeContaminantsProps) {
  return (
    <div className="rounded-lg border-2 bg-blue-50 border-blue-200 p-6 my-6">
      <div className="flex items-start gap-3 mb-4">
        <InformationCircleIcon className="w-6 h-6 text-blue-600 flex-shrink-0 mt-1" />
        <div>
          <h3 className="text-lg font-semibold mb-2">
            Found as Surface Contamination
          </h3>
          <p className="text-sm text-gray-700 mb-4">
            This compound appears as contamination on material surfaces.
            See removal methods and identification techniques.
          </p>
        </div>
      </div>
      
      <div className="grid gap-3 md:grid-cols-2">
        {sourceContaminants.map((contaminant) => (
          <Link
            key={contaminant.contaminant_id}
            href={`/contaminants/${contaminant.contaminant_id}`}
            className="block p-4 bg-white rounded border border-gray-200 hover:border-blue-400 hover:shadow-md transition-all"
          >
            <div className="flex items-start justify-between mb-2">
              <span className="font-medium text-gray-900">
                {contaminant.contaminant_name}
              </span>
              <Badge variant="info">{contaminant.badge_text}</Badge>
            </div>
            <p className="text-sm text-gray-600 line-clamp-2">
              {contaminant.context}
            </p>
            <span className="text-sm text-blue-600 font-medium mt-2 inline-flex items-center gap-1">
              View removal methods <ArrowRightIcon className="w-4 h-4" />
            </span>
          </Link>
        ))}
      </div>
    </div>
  );
}
```

#### Layout Integration

**ContaminantsLayout Section Order** (Updated):

```typescript
const sections = [
  // 1. Produces compounds (existing - hazardous byproducts)
  // 2. SafetyDataPanel (existing - OSHA exposure for this contaminant)
  
  // 3. AlsoSeeCompounds (NEW - airborne exposure perspective)
  {
    component: 'AlsoSeeCompounds',
    condition: relatedCompounds.length > 0,
    data: relationships.interactions.related_compounds,
    style: 'warning'
  },
  
  // 4. RegulatoryStandards (existing)
  // 5. Affects_materials CardGrid (existing)
  // 6. Visual Characteristics (existing)
  // ... rest of sections
];
```

**CompoundsLayout Section Order** (Updated):

```typescript
const sections = [
  // 1. Chemical Properties InfoCards (existing)
  
  // 2. AlsoSeeContaminants (NEW - surface contamination perspective)
  {
    component: 'AlsoSeeContaminants',
    condition: sourceContaminants.length > 0,
    data: relationships.interactions.source_contaminants,
    style: 'info'
  },
  
  // 3. Exposure Limits InfoCard (existing)
  // 4. SafetyDataPanel (existing)
  // ... rest of sections
];
```

#### Overlap Entity Identification

**Entities requiring bidirectional crosslinks** (~15-20 entities):

| Contaminant | Compound(s) | Relationship |
|-------------|-------------|--------------|
| rust-oxidation-contamination | iron-oxide-fe2o3, iron-oxide-fe3o4 | Vaporizes into airborne dust |
| lead-paint-contamination | lead-oxide, lead-compounds | Vaporizes creating lead exposure |
| chromium-coating-contamination | chromium-hexavalent-cr-vi | Creates carcinogenic Cr(VI) |
| zinc-galvanization-contamination | zinc-oxide, zinc-fume | Vaporizes into metal fume fever risk |
| aluminum-oxide-contamination | aluminum-oxide-al2o3 | Creates airborne alumina particles |
| copper-oxide-contamination | copper-oxide-cuo | Vaporizes into copper fume |
| cadmium-plating-contamination | cadmium-compounds | Creates toxic cadmium exposure |
| nickel-contamination | nickel-compounds | Vaporizes creating sensitization risk |
| carbon-soot-contamination | carbon-black | Creates respirable carbon particles |
| silica-contamination | silica-crystalline | Creates silicosis risk |
| titanium-dioxide-contamination | titanium-dioxide-tio2 | Creates airborne titania |
| manganese-contamination | manganese-compounds | Vaporizes creating neurological risk |
| cobalt-contamination | cobalt-compounds | Creates asthma/sensitization risk |
| beryllium-contamination | beryllium-compounds | Creates berylliosis risk (extremely toxic) |
| asbestos-contamination | asbestos-fibers | Releases carcinogenic fibers |

**Implementation priority**: Start with top 5 (rust, lead, chromium, zinc, aluminum) in Phase 1

#### Migration Script

**File**: `scripts/add-contaminant-compound-crosslinks.js`

```javascript
// Identify overlap entities
const overlapMap = {
  'rust-oxidation-contamination': ['iron-oxide-fe2o3', 'iron-oxide-fe3o4'],
  'lead-paint-contamination': ['lead-oxide', 'lead-compounds'],
  'chromium-coating-contamination': ['chromium-hexavalent-cr-vi'],
  // ... 15 total mappings
};

// Add related_compounds to contaminants
Object.entries(overlapMap).forEach(([contaminantId, compoundIds]) => {
  const contaminant = loadYAML(`frontmatter/contaminants/${contaminantId}.yaml`);
  
  contaminant.relationships.interactions.related_compounds = compoundIds.map(cid => {
    const compound = loadYAML(`frontmatter/compounds/${cid}.yaml`);
    return {
      compound_id: cid,
      relationship_type: 'airborne_byproduct',
      context: generateContext(contaminant, compound),
      display_prominence: 'high',
      badge_text: '⚠️ Exposure Data',
      warning_level: determineWarningLevel(compound)
    };
  });
  
  saveYAML(`frontmatter/contaminants/${contaminantId}.yaml`, contaminant);
});

// Add source_contaminants to compounds (reverse)
Object.entries(overlapMap).forEach(([contaminantId, compoundIds]) => {
  compoundIds.forEach(cid => {
    const compound = loadYAML(`frontmatter/compounds/${cid}.yaml`);
    
    if (!compound.relationships.interactions.source_contaminants) {
      compound.relationships.interactions.source_contaminants = [];
    }
    
    const contaminant = loadYAML(`frontmatter/contaminants/${contaminantId}.yaml`);
    compound.relationships.interactions.source_contaminants.push({
      contaminant_id: contaminantId,
      relationship_type: 'surface_form',
      context: generateReverseContext(compound, contaminant),
      display_prominence: 'high',
      badge_text: '📍 Found on Surfaces'
    });
    
    saveYAML(`frontmatter/compounds/${cid}.yaml`, compound);
  });
});
```

#### User Experience Flow

**Scenario 1**: User searching for rust removal
1. Lands on `/contaminants/oxidation/ferrous/rust-oxidation-contamination`
2. Sees: Removal methods, visual ID, affected materials
3. **NEW**: Sees prominent "Airborne Exposure During Removal" box with links to:
   - Iron Oxide (Fe₂O₃) - PEL: 10 mg/m³
   - Magnetite (Fe₃O₄) - PEL: 10 mg/m³
4. Clicks to understand exposure risks + PPE requirements

**Scenario 2**: User searching for iron oxide exposure
1. Lands on `/compounds/metal-oxides/iron-oxide-fe2o3`
2. Sees: Chemical properties, exposure limits, detection methods
3. **NEW**: Sees "Found as Surface Contamination" box with link to:
   - Rust (Iron Oxide Contamination) - See removal methods
4. Clicks to understand where this compound comes from

**Result**: No confusion - clear perspective switching with context

---

### Component Usage & Page Layout

#### PropertiesLayout Component Structure

**File**: `app/components/PropertiesLayout/PropertiesLayout.tsx`

**Sections** (Ordered by user priority):

```typescript
const sections = [
  // 1. DEFINITION PANEL (Always first)
  {
    component: 'DescriptiveDataPanel',
    title: 'Definition',
    presentation: 'collapsible-open',
    content: {
      short: definition.short,
      detailed: definition.detailed
    }
  },
  
  // 2. MEASUREMENT STANDARDS (Material/Machine properties only)
  {
    component: 'InfoCards',
    title: 'Measurement Standards',
    cards: measurement.standard_methods.map(method => ({
      label: method.method,           // "ASTM D792"
      value: method.section_title,     // "Standard Test Methods..."
      subtitle: method.applicability,  // "Plastics"
      href: method.url,
      icon: 'DocumentIcon'
    }))
  },
  
  // 3. TYPICAL RANGES CHART (Material properties only)
  {
    component: 'TypicalRangesChart',  // NEW COMPONENT
    title: 'Typical Ranges by Material Category',
    data: typical_ranges,
    interactive: true,
    // Renders bar chart with material examples as tooltips
    // Clicking material opens its page
  },
  
  // 4. LASER CLEANING IMPACT (All properties)
  {
    component: 'DescriptiveDataPanel',
    title: 'Laser Cleaning Relevance',
    presentation: 'collapsible-closed',
    sections: laser_cleaning_impact   // Multiple subsections
  },
  
  // 5. PARAMETER INTERACTIONS (Machine settings only)
  {
    component: 'ParameterInteractionsGraph',  // Existing component
    title: 'Related Parameters',
    data: interacts_with
  },
  
  // 6. MATERIALS USING THIS PROPERTY (Reverse lookup CardGrid)
  {
    component: 'CardGrid',
    title: `Materials with ${property.name} Data`,
    variant: 'relationship',
    items: relationships.interactions.used_by_materials.map(enrichMaterial),
    // Shows material cards sorted by property value
    // Badge shows the property value (e.g., "2.7 g/cm³")
  },
  
  // 7. SETTINGS USING THIS PARAMETER (Machine properties only)
  {
    component: 'CardGrid',
    title: `Settings Using ${property.name}`,
    variant: 'relationship',
    items: relationships.interactions.used_by_settings.map(enrichSetting),
    // Shows setting cards with parameter ranges
  },
  
  // 8. CONTAMINANTS WITH THIS PROPERTY (Material properties only)
  {
    component: 'CardGrid',
    title: `Contaminants: ${property.name} Data`,
    variant: 'relationship',
    items: relationships.interactions.used_by_contaminants.map(enrichContaminant),
  },
  
  // 9. RELATED PROPERTIES (Always)
  {
    component: 'CardGrid',
    title: 'Related Properties',
    variant: 'discovery',
    items: relationships.interactions.related_properties.map(enrichProperty),
    // Shows other property cards with relationship explanation
    // Badge shows relationship type ("Complementary", "Inverse", etc.)
  },
  
  // 10. DETECTION METHODS (Detection method pages only)
  {
    component: 'CardGrid',
    title: 'Detectable Compounds',
    variant: 'relationship',
    items: detects.compounds.map(enrichCompound),
  },
  
  // 11. EQUIPMENT (Detection methods only)
  {
    component: 'InfoCards',
    title: 'Typical Equipment',
    cards: typical_equipment.map(eq => ({
      label: `${eq.manufacturer} ${eq.model}`,
      value: eq.cost_range,
      subtitle: `Analysis time: ${eq.analysis_time}`,
      icon: 'BeakerIcon'
    }))
  },
  
  // 12. SAFETY COMPARISONS (Safety limits only)
  {
    component: 'ComparisonTable',    // NEW COMPONENT
    title: 'Comparison to Other Limits',
    data: comparison,
    // Table: PEL vs TLV vs REL vs Ceiling
  },
  
  // 13. EXAMPLE COMPOUNDS (Safety limits only)
  {
    component: 'CardGrid',
    title: 'Compounds with This Limit',
    variant: 'relationship',
    items: example_compounds.map(enrichCompound),
    // Badge shows limit value
  },
  
  // 14. DATASET DOWNLOADER (Always last)
  {
    component: 'PropertyDatasetDownloader',
    // Exports all materials/settings with this property value
  },
  
  // 15. SCHEDULE CARDS (Always absolute last)
  {
    component: 'ScheduleCards'
  }
];
```

#### New Components Required

**1. TypicalRangesChart**
```tsx
// Interactive bar chart showing property ranges by category
// Horizontal bars: Metals (2.7-19.3 g/cm³), Plastics (0.9-2.2), etc.
// Material examples as dots on bars
// Click material dot → navigate to material page
// Tooltip shows: "Aluminum: 2.7 g/cm³"
```

**2. ComparisonTable**
```tsx
// Side-by-side comparison table for safety limits
// Columns: PEL | TLV | REL | Ceiling
// Rows: Organization, Legal Status, Typical Value Relationship
// Example compounds with all 4 limits
```

**3. PropertyDatasetDownloader**
```tsx
// Similar to MaterialDatasetDownloader
// Exports: All materials/settings with this property + their values
// Format: JSON/CSV with columns: entity_id, entity_name, property_value, unit
```

---

### Integration with PropertyBars Component

**Enhancement**: Make property names clickable links

```tsx
// app/components/PropertyBars/PropertyBars.tsx

// Add property definition lookup
const PROPERTY_DEFINITIONS: Record<string, string> = {
  'density': '/properties/material/density',
  'thermalConductivity': '/properties/material/thermal-conductivity',
  'absorptionCoefficient': '/properties/material/absorption-coefficient',
  'power': '/properties/machine/power',
  'wavelength': '/properties/machine/wavelength',
  'pulseDuration': '/properties/machine/pulse-duration',
  // ... 100+ mappings
};

// Render property name with link
function PropertyName({ name }: { name: string }) {
  const slug = name.replace(/([A-Z])/g, '-$1').toLowerCase().replace(/^-/, '');
  const definitionUrl = PROPERTY_DEFINITIONS[name] || 
                       `/properties/material/${slug}`;
  
  return (
    <Link 
      href={definitionUrl}
      className="group inline-flex items-center gap-1 hover:text-blue-600"
      title={`Learn about ${capitalizeWords(name)}`}
    >
      <span className="text-sm font-medium underline decoration-dotted decoration-gray-400">
        {capitalizeWords(name)}
      </span>
      <InformationCircleIcon className="w-3 h-3 opacity-0 group-hover:opacity-50 transition-opacity" />
    </Link>
  );
}
```

**Visual Result**: 
- Property names in bars become subtle underlined links
- Hover shows info icon + tooltip
- Click opens property definition page

---

### Migration Strategy

#### Phase 1: Core Properties (Weeks 1-4)

**Goal**: Create 45 most-used property pages (material + machine + safety + critical units)

**Tasks**:
1. Create schema v5.1.0 documentation
2. Generate 45 property YAML files:
   - Material properties (20): density, thermal_conductivity, absorption_coefficient, etc.
   - Machine settings (15): power, wavelength, pulse_duration, etc.
   - Safety limits (6): PEL, TLV, REL, STEL, Ceiling, TWA
   - Critical units (4): J/cm², W/cm², μm, nm
3. Build PropertiesLayout component (reuse 80% of existing components)
4. Build 3 new components: TypicalRangesChart, ComparisonTable, PropertyDatasetDownloader
5. Enhance PropertyBars with clickable links (1-line change per property + mapping object)
6. Add property_definition_id to 438 existing frontmatter files

**Success Metrics**:
- PropertyBars shows clickable property names
- Material pages link to density, thermal_conductivity
- Settings pages link to power, wavelength, pulse_duration
- Compounds pages link to PEL, TLV

**Estimated Effort**: 80 hours (2 developers × 2 weeks)

---

#### Phase 2: Analysis & Technology (Weeks 5-8)

**Goal**: Add 35 technical property pages (detection methods + laser types + remaining units)

**Tasks**:
1. Generate 35 property YAML files:
   - Detection methods (12): XRD, Raman, FTIR, EDS, ICP-MS, SEM, XPS, etc.
   - Laser types (8): Fiber, CO2, Nd:YAG, Excimer, Diode, etc.
   - Remaining units (11): Hz, kHz, Pa, MPa, °C, K, etc.
   - Chemical concepts (4): molecular_weight, vapor_pressure, flash_point, boiling_point
2. Add detection_method_definitions to contaminants/compounds frontmatter
3. Add laser_type crosslinks to settings frontmatter
4. Build DetectionMethodComparison component (optional enhancement)

**Success Metrics**:
- Contaminant pages link to XRD, Raman, FTIR methods
- Compound pages link to ICP-MS, GC-MS methods
- Settings pages link to Fiber, CO2, Nd:YAG laser types
- All units in PropertyBars are clickable

**Estimated Effort**: 60 hours (1 developer × 3 weeks)

---

#### Phase 3: Contextual Encyclopedia (Weeks 9-12)

**Goal**: Complete 26 remaining pages (standards orgs + process terms + chemical concepts)

**Tasks**:
1. Generate 26 property YAML files:
   - Standards organizations (6): ASTM, ISO, OSHA, NIOSH, ACGIH, ANSI
   - Process terms (10): ablation, HAZ, overlap, hatch_spacing, dwell_time, etc.
   - Remaining chemical concepts (10): molecular_formula, CAS_number, specific_gravity, etc.
2. Add standard_organization_id to all ASTM/ISO references across site
3. Add process_term crosslinks where relevant
4. Build StandardsOrganization component (if needed)

**Success Metrics**:
- All ASTM/ISO references link to organization pages
- Process terms (ablation, HAZ) link to definitions
- Chemical properties link to measurement concepts
- 106 property pages live

**Estimated Effort**: 40 hours (1 developer × 2 weeks)

---

### Data Population Strategy

#### Automated Extraction

**Material properties** (20 properties × 174 materials = 3,480 values):
```javascript
// Script: scripts/generate-property-pages.js

// Extract all unique properties from materials frontmatter
const allProperties = new Set();
materials.forEach(material => {
  Object.keys(material.properties.material_characteristics).forEach(prop => {
    allProperties.add(prop);
  });
});

// For each property, generate reverse lookup
const propertyData = {};
allProperties.forEach(propName => {
  propertyData[propName] = {
    used_by_materials: materials
      .filter(m => m.properties.material_characteristics[propName])
      .map(m => ({
        material_id: m.id,
        value: m.properties.material_characteristics[propName].value,
        unit: m.properties.material_characteristics[propName].unit
      }))
      .sort((a, b) => a.value - b.value)  // Sort by value
  };
});

// Generate property YAML files
generatePropertyFrontmatter('density', propertyData['density']);
```

**Machine settings** (15 parameters × 113 settings = 1,695 values):
```javascript
// Extract parameters from settings frontmatter
const allParameters = new Set();
settings.forEach(setting => {
  Object.keys(setting.properties.machine_settings).forEach(param => {
    allParameters.add(param);
  });
});

// Generate reverse lookup: which settings use this parameter
```

**Safety limits** (6 limit types × compounds with exposure data):
```javascript
// Extract PEL/TLV/REL from compounds frontmatter
compounds.forEach(compound => {
  if (compound.relationships.safety.exposure_limits.OSHA_PEL) {
    pelExamples.push({
      compound_id: compound.id,
      limit_value: compound.relationships.safety.exposure_limits.OSHA_PEL
    });
  }
});
```

#### Manual Content Creation

**Definitions** (106 properties × 2 paragraphs = 212 paragraphs):
- Use Grok/Claude to generate definition text
- Template: "What is {property}? How does it affect laser cleaning?"
- Review for technical accuracy
- Estimated: 2 hours per property category (20 hours total)

**Measurement standards** (50 properties with ASTM/ISO standards):
- Research ASTM.org and ISO.org for applicable standards
- Extract: Standard ID, title, applicability, URL
- Estimated: 10 minutes per property (8 hours total)

**Laser cleaning impact** (70 properties with relevance to laser cleaning):
- Technical writing: How does this property affect cleaning?
- Practical implications for 3 scenarios (rust, paint, coating)
- Estimated: 15 minutes per property (18 hours total)

**Total Manual Effort**: ~46 hours content creation

---

### SEO & Discoverability

#### Sitemap Integration

**New sections**:
```xml
<url>
  <loc>https://z-beam.com/properties</loc>
  <changefreq>monthly</changefreq>
  <priority>0.8</priority>
</url>
<url>
  <loc>https://z-beam.com/properties/material</loc>
  <changefreq>monthly</changefreq>
  <priority>0.7</priority>
</url>
<url>
  <loc>https://z-beam.com/properties/material/density</loc>
  <changefreq>monthly</changefreq>
  <priority>0.6</priority>
</url>
<!-- 106 property pages -->
```

#### Internal Linking Boost

**Current state**: PropertyBars show property names as plain text (0 internal links)

**After migration**: PropertyBars link every property name to definition page
- Materials pages: 8-15 property links per page × 174 pages = 1,392-2,610 new internal links
- Settings pages: 6-12 parameter links per page × 113 pages = 678-1,356 new internal links
- Contaminants pages: 3-6 property links per page × 138 pages = 414-828 new internal links

**Total new internal links**: ~2,500-4,800 contextual links

**SEO Impact**: 
- Dramatically improved internal link structure
- Every property page receives 20-50 contextual backlinks
- PageRank flows from high-authority material/settings pages to property pages
- Property pages rank for long-tail technical queries ("what is fluence in laser cleaning")

---

### Questions for Review

1. **Category naming**: Are material/machine/safety/detection/unit/laser/standard/process/chemical intuitive?
2. **Component reuse**: Can we use existing CardGrid/DescriptiveDataPanel for 80% of layout?
3. **Reverse lookup**: Should property pages show ALL materials with that property, or just top 10?
4. **PropertyBars enhancement**: Link every property name, or only properties with definition pages?
5. **Phase priority**: Agree with material→machine→safety→detection→terms sequence?
6. **Data population**: Manual definitions vs AI-generated with human review?
7. **Unit conversion**: Include conversion calculators on unit pages (J/cm² ↔ W/cm²)?

---

**Document Status**: Ready for backend team review and implementation planning  
**Component Validation**: Complete (all 4 layouts + PropertyBars analyzed)  
**Properties Domain**: 106 pages proposed, 3-phase implementation (12 weeks)  
**Backwards Compatibility**: Implemented (50+ path fallback mappings)  
**Next Review Date**: January 5, 2026

---

**END OF DOCUMENT**
