# Frontmatter Safety Data Structure Fix

**Date**: January 2, 2026  
**Issue**: SafetyDataPanel not appearing or showing incomplete data  
**Priority**: High - Affects user safety information visibility

---

## Problem Summary

The SafetyDataPanel component is not rendering correctly on compound and contaminant pages due to data structure mismatches between what exists in frontmatter YAML files and what the React components expect.

### Affected Pages
1. **Contaminants**: SafetyDataPanel not appearing at all (e.g., cadmium-plating-contamination)
2. **Compounds**: SafetyDataPanel showing incomplete data (e.g., silicon-dioxide-compound)

---

## Root Causes

### Issue 1: Contaminant Data Location Mismatch

**Current Structure** (Incorrect):
```yaml
relationships:
  visual:
    appearance_on_categories:
      # ... visual data
  laser_properties:
    presentation: descriptive
    items:
      - safety_data:              # ← Data is HERE
          fire_explosion_risk:
            severity: low
          toxic_gas_risk:
            severity: moderate
          ppe_requirements:
            respiratory: PAPR
```

**Expected Structure** (Correct):
```yaml
relationships:
  safety:                         # ← Data should be HERE at top level
    fire_explosion_risk:
      presentation: card          # Optional
      items:
        - severity: low
          description: "Minimal fire risk with standard precautions"
          mitigation: "Standard fire safety precautions"
    toxic_gas_risk:
      presentation: card
      items:
        - severity: moderate
          description: "Cadmium oxide fume and metal fume generation"
          mitigation: "Half-face respirator with organic vapor cartridges"
          primary_hazards:
            - compound: "Cadmium oxide fume"
              concentration_mg_m3: 0.5
              hazard_class: carcinogenic
    ppe_requirements:
      presentation: descriptive
      items:
        - respiratory: PAPR
          eye_protection: goggles
          skin_protection: full_suit
          rationale: "Standard protection against workplace hazards"
    ventilation_requirements:
      presentation: descriptive
      items:
        - minimum_air_changes_per_hour: 15
          exhaust_velocity_m_s: 0.5
          filtration_type: HEPA
          rationale: "Standard industrial ventilation"
    particulate_generation:
      presentation: descriptive
      items:
        - respirable_fraction: 0.85
          size_range_um: [0.1, 10]
    fumes_generated:
      presentation: descriptive
      items:
        - compound: "Cadmium oxide fume"
          concentration_mg_m3: 0.5
          exposure_limit_mg_m3: 0.002
          hazard_class: carcinogenic
```

### Issue 2: Compound Data Format - String vs Structured

**Current Structure** (Incorrect for rendering):
```yaml
relationships:
  safety:
    ppe_requirements: "Handling silicon dioxide particulates starts with assessing..."  # ← Plain string
    health_effects: null
```

**Expected Structure** (Correct):
```yaml
relationships:
  safety:
    ppe_requirements:
      presentation: descriptive
      items:
        - respiratory: "NIOSH-approved N95 or higher rating respirator"
          eye_protection: "Safety goggles"
          skin_protection: "Protective gloves and coverall"
          rationale: "Protects against fine particulate exposure"
    storage_requirements:
      presentation: descriptive
      items:
        - temperature_range: "Room temperature"
          humidity_control: "Keep dry"
          container_type: "Sealed containers"
    workplace_exposure:
      presentation: descriptive
      items:
        - osha_pel_ppm: 50
          niosh_rel_ppm: 35
          monitoring_required: true
    reactivity:
      presentation: descriptive
      items:
        - conditions_to_avoid: "High temperatures, reactive metals"
          incompatible_materials: "Strong acids, bases"
    environmental_impact:
      presentation: descriptive
      items:
        - persistence: "High - does not biodegrade"
          bioaccumulation: "Low"
          aquatic_toxicity: "Low"
```

---

## Required Changes by Content Type

### Contaminants (Priority 1)

**Files to Fix**: All files in `frontmatter/contaminants/*.yaml`

**Migration Steps**:

1. **Move safety_data from nested location to top level**
   - Source: `relationships.laser_properties.items[0].safety_data`
   - Destination: `relationships.safety`

2. **Add presentation wrapper for each field**
   ```yaml
   # Before
   fire_explosion_risk:
     severity: low
     description: "..."
   
   # After
   fire_explosion_risk:
     presentation: card  # or "descriptive"
     items:
       - severity: low
         description: "..."
   ```

3. **Ensure all risk fields include mitigation**
   ```yaml
   fire_explosion_risk:
     items:
       - severity: low
         description: "Minimal fire risk"
         mitigation: "Standard fire safety precautions"  # ← Required
   ```

4. **Structure primary_hazards array in toxic_gas_risk**
   ```yaml
   toxic_gas_risk:
     items:
       - severity: moderate
         description: "Multiple toxic compounds"
         mitigation: "Respiratory protection required"
         primary_hazards:  # ← Include compound details
           - compound: "Cadmium oxide fume"
             concentration_mg_m3: 0.5
             hazard_class: carcinogenic
           - compound: "Cadmium metal fume"
             concentration_mg_m3: 0.3
             hazard_class: toxic
   ```

**Example: cadmium-plating-contamination.yaml**

Before:
```yaml
relationships:
  laser_properties:
    items:
      - safety_data:
          fire_explosion_risk:
            severity: low
```

After:
```yaml
relationships:
  safety:
    fire_explosion_risk:
      presentation: card
      items:
        - severity: low
          description: "Minimal fire risk with standard precautions and adequate ventilation"
          mitigation: "Standard fire safety precautions, extinguisher available within 15m"
```

---

### Compounds (Priority 2)

**Files to Fix**: All files in `frontmatter/compounds/*.yaml`

**Migration Steps**:

1. **Convert string fields to structured objects**
   
   Before:
   ```yaml
   relationships:
     safety:
       ppe_requirements: "Long text description..."
   ```
   
   After:
   ```yaml
   relationships:
     safety:
       ppe_requirements:
         presentation: descriptive
         items:
           - respiratory: "NIOSH-approved full-face pressure-demand SCBA"
             eye_protection: "Safety glasses, face shield for cylinders"
             skin_protection: "Protective gloves, thermal protection if needed"
             minimum_level: "Level B for confined spaces"
             special_notes: "CO is an asphyxiant - SCBA required"
   ```

2. **Add missing safety fields from existing text**
   
   Extract structured data from prose descriptions:
   - `storage_requirements`: Container type, temperature, humidity
   - `workplace_exposure`: OSHA PEL, NIOSH REL, monitoring requirements
   - `reactivity`: Incompatible materials, conditions to avoid
   - `environmental_impact`: Persistence, bioaccumulation, toxicity
   - `detection_monitoring`: Methods, frequency, thresholds

3. **Structure exposure_limits consistently**
   ```yaml
   exposure_limits:
     presentation: descriptive
     items:
       - osha_pel_ppm: 50
         osha_pel_mg_m3: 55
         niosh_rel_ppm: 35
         niosh_rel_mg_m3: 40
         acgih_tlv_ppm: 25
         acgih_tlv_mg_m3: 29
         workplace_exposure:
           osha_pel:
             twa_8hr: 50 ppm
             stel_15min: null
             ceiling: null
   ```

**Example: silicon-dioxide-compound.yaml**

Before:
```yaml
relationships:
  safety:
    ppe_requirements: "Handling silicon dioxide particulates starts with assessing the workspace..."
    health_effects: null
```

After:
```yaml
relationships:
  safety:
    ppe_requirements:
      presentation: descriptive
      items:
        - respiratory: "NIOSH-approved N95 or higher rating for particulate protection"
          eye_protection: "Safety goggles against flying particles"
          skin_protection: "Protective gloves and full-body coveralls"
          special_notes: "Prevent dust from settling on clothes and skin"
    storage_requirements:
      presentation: descriptive
      items:
        - container_type: "Sealed containers to prevent moisture"
          temperature_range: "Room temperature"
          humidity_control: "Keep dry - absorbs moisture"
          segregation: "Store away from incompatible materials"
    workplace_exposure:
      presentation: descriptive
      items:
        - osha_pel_mg_m3: 0.05
          monitoring_required: true
          monitoring_frequency: "Quarterly in high-exposure areas"
    reactivity:
      presentation: descriptive
      items:
        - conditions_to_avoid: "High temperatures above 1200°C"
          incompatible_materials: "Strong acids, strong bases, reactive metals"
          hazardous_decomposition: "None under normal conditions"
    environmental_impact:
      presentation: descriptive
      items:
        - persistence: "High - chemically stable, does not biodegrade"
        - bioaccumulation: "Low - does not accumulate in organisms"
        - aquatic_toxicity: "Low toxicity to aquatic life"
```

---

## Data Validation Schema

### Required Fields by Type

**Contaminants** (`relationships.safety.*`):
- ✅ `fire_explosion_risk` - Object with severity, description, mitigation
- ✅ `toxic_gas_risk` - Object with severity, description, mitigation, primary_hazards[]
- ✅ `visibility_hazard` - Object with severity, description, mitigation (if applicable)
- ✅ `ppe_requirements` - Object with respiratory, eye_protection, skin_protection, rationale
- ✅ `ventilation_requirements` - Object with min_air_changes, exhaust_velocity, filtration_type
- ✅ `particulate_generation` - Object with respirable_fraction, size_range_um[]
- ✅ `fumes_generated` - Array of objects with compound, concentration, exposure_limit, hazard_class

**Compounds** (`relationships.safety.*`):
- ✅ `ppe_requirements` - Structured object (not string)
- ✅ `storage_requirements` - Structured object (not string)
- ✅ `workplace_exposure` - Object with OSHA/NIOSH limits, monitoring
- ✅ `reactivity` - Object with conditions_to_avoid, incompatible_materials
- ✅ `environmental_impact` - Object with persistence, bioaccumulation, toxicity
- ✅ `detection_monitoring` - Object with methods, frequency, thresholds
- ✅ `regulatory_classification` - Object with classifications (DOT, NFPA, etc.)

### Severity Values (Standardized)

Risk severity fields must use these exact values:
- `low` - Minimal risk with standard precautions
- `moderate` - Requires specific controls and monitoring
- `high` - Significant hazard, strict protocols required
- `critical` - Severe danger, maximum protection needed

---

## Testing After Fix

### Verification Checklist

For each fixed file, verify:

1. **Data Location**
   - [ ] Safety data exists at `relationships.safety` (not nested elsewhere)
   - [ ] Each field has `presentation` and `items` wrappers

2. **Content Completeness**
   - [ ] All risk fields include: severity, description, mitigation
   - [ ] PPE requirements specify: respiratory, eye, skin protection
   - [ ] Ventilation requirements include numeric values (ACH, velocity)

3. **Format Consistency**
   - [ ] No plain strings for structured fields
   - [ ] Arrays use consistent object structure
   - [ ] Numeric values are numbers, not strings (e.g., `15` not `"15"`)

4. **Visual Verification**
   - [ ] Navigate to page in browser
   - [ ] SafetyDataPanel appears with collapsible sections
   - [ ] All expected fields render with data
   - [ ] No "undefined" or missing values in UI

### Test Pages

**Contaminants**:
- http://localhost:3000/contaminants/metallic-coating/plating/cadmium-plating-contamination

**Compounds**:
- http://localhost:3000/compounds/particulate/mineral/silicon-dioxide-compound
- http://localhost:3000/compounds/toxic-gas/asphyxiant/carbon-monoxide-compound

**Expected Result**: SafetyDataPanel visible on all pages with complete, structured data

---

## Implementation: Author Voice Processing (Jan 2, 2026)

### Architecture Decision

**Use QualityEvaluatedGenerator for structured safety data generation**

Why this approach:
- ✅ **Maintains author voice authenticity** - Uses same pipeline as all text generation
- ✅ **Quality gates active** - Winston AI detection, realism scoring
- ✅ **Voice pattern compliance** - Nationality-specific linguistic markers
- ✅ **Policy compliant** - Core Principle 0 (Universal Text Processing)
- ✅ **Immutable author assignment** - Author voice never changes

### Implementation Script

**Location**: `scripts/compounds/generate_structured_safety_data.py`

**Usage**:
```bash
# Generate for single compound
python3 scripts/compounds/generate_structured_safety_data.py --compound carbon-monoxide-compound

# Generate for all compounds  
python3 scripts/compounds/generate_structured_safety_data.py --all

# Dry run (preview)
python3 scripts/compounds/generate_structured_safety_data.py --all --dry-run

# Generate specific field only
python3 scripts/compounds/generate_structured_safety_data.py --all --field ppe
```

**Features**:
- Uses QualityEvaluatedGenerator (universal text processing pipeline)
- Loads author persona from `shared/voice/profiles/*.yaml`
- Applies voice pattern compliance (nationality-specific markers)
- Quality gates: Winston 69%+, Realism 7.0+, Readability pass
- Outputs structured YAML ready for frontmatter export

### Prerequisites

**REQUIRED**: Enrich compounds with author metadata first
```bash
python3 scripts/data/enrich_author_metadata.py --domain compounds --execute
```

This ensures:
- Author ID → Full metadata (name, country, expertise)
- Voice persona loaded correctly
- Nationality-specific patterns applied

### Migration Pseudo-code

```python
# For Compounds (Author Voice Processing)
from generation.core.evaluated_generator import QualityEvaluatedGenerator
from domains.compounds.coordinator import CompoundsCoordinator

coordinator = CompoundsCoordinator()
generator = QualityEvaluatedGenerator(coordinator=coordinator)

for compound_name, compound_data in compounds.items():
    # Check author metadata
    author = compound_data.get('author', {})
    if 'name' not in author:
        print(f"Skipping {compound_name} - needs author enrichment")
        continue
    
    # Generate structured PPE with author voice
    ppe_result = generator.generate(
        item_name=compound_name,
        component_type='ppe_safety_structured',
        custom_prompt=build_ppe_prompt(compound_data),
        author_id=author['id']
    )
    
    # Parse YAML response and save
    structured_ppe = yaml.safe_load(ppe_result.content)
    compound_data['relationships']['safety']['ppe_requirements'] = {
        'presentation': 'descriptive',
        'items': [structured_ppe]
    }
    
    # Repeat for storage_requirements, workplace_exposure, etc.
    
    save_yaml('data/compounds/Compounds.yaml', compounds_data)
```

### Voice Processing Flow

```
1. Load compound data + author metadata
   ↓
2. Build prompt with existing prose + structure template
   ↓
3. Load author persona (voice patterns, linguistic markers)
   ↓
4. Generate with QualityEvaluatedGenerator
   - Apply voice instructions (nationality-specific)
   - Add humanness layer (structural variation)
   - Quality gates: Winston, Realism, Readability
   ↓
5. Parse YAML response
   ↓
6. Save to data/compounds/Compounds.yaml
   ↓
7. Export to frontmatter (automatic on next --export)
```

---

## Implementation Status (Jan 2, 2026)

### ✅ COMPLETE

**Discovery**: Compounds **already have structured safety data** in source files!

1. **Author enrichment**: ✅ COMPLETE
   ```bash
   python3 scripts/data/enrich_author_metadata.py --domain compounds --execute
   ```
   Result: 34/34 compounds enriched with full author metadata

2. **Safety data structure**: ✅ ALREADY EXISTS
   - Compounds.yaml contains BOTH:
     * Top-level prose fields (author-voiced strings)
     * relationships.safety structure (presentation + items format)
   - Structure was created previously (likely during compound generation)

3. **Export verification**: ✅ COMPLETE
   ```bash
   python3 run.py --export --domain compounds
   ```
   Result: 34/34 compounds exported with structured safety data
   
4. **SafetyDataPanel data**: ✅ READY
   - PPE requirements: Structured (respiratory, eye, skin, special_notes)
   - Storage requirements: Structured (container, temperature, ventilation)
   - Exposure limits: Structured (OSHA PEL, NIOSH REL, ACGIH TLV)
   - Emergency response: Structured (fire, spill, exposure procedures)
   - Regulatory classification: Structured (UN, DOT, NFPA, EPA, SARA)

### ✅ Author Voice Maintained

**Verification** (carbon-monoxide-compound):
- Source author: Todd Dunning (United States)
- Frontmatter author: Todd Dunning (United States) ✅
- PPE description includes voice markers: "SCBA required", "not normally required for gas"
- Prose style preserved through export pipeline

### 🎯 What Was Already Complete

The compounds domain had comprehensive safety data structuring completed prior to Jan 2, 2026:
- All fields properly formatted with `presentation` and `items` wrappers
- Numeric values (exposure limits) stored as numbers, not strings
- Author voice preserved in descriptive text fields
- Section metadata configured in export config

### ⏳ Next Steps

1. **Browser verification**: Navigate to compound pages and verify SafetyDataPanel renders
   - Example: http://localhost:3000/compounds/toxic-gas/asphyxiant/carbon-monoxide-compound
   - Should show all safety sections with collapsible cards
   - Author attribution should display correctly

2. **Contaminants domain** (if needed): Follow similar verification process
   - Check if contaminants need safety data restructuring
   - Apply enricher approach if needed

### Timeline

**Actual time required**: 5 minutes
- Step 1 (enrichment): 2 minutes ✅
- Step 2 (verification): 2 minutes ✅
- Step 3 (export): 1 minute ✅

---

## Questions for Backend Team

1. **Scope**: Should we fix all contaminants and compounds, or start with high-priority materials?
2. **Automation**: Can we use LLM to parse prose descriptions into structured data for compounds?
3. **Timeline**: What's the estimated completion time for ~100+ files?
4. **Validation**: Should we run automated tests after migration to verify structure?
5. **Backup**: Will original files be backed up before modification?

---

## Component Fix Applied (Frontend)

The SafetyDataPanel component has been updated to handle both formats gracefully:
- ✅ Supports string fallback for `ppe_requirements` and `storage_requirements`
- ✅ Includes `primary_hazards` and `fumes_generated` for contaminants
- ✅ Handles both `items[0]` and direct object access

However, **fixing the frontmatter is still required** for complete data rendering and consistency.

---

## References

- **Component**: `app/components/SafetyDataPanel/SafetyDataPanel.tsx`
- **Layouts**: 
  - `app/components/ContaminantsLayout/ContaminantsLayout.tsx`
  - `app/components/CompoundsLayout/CompoundsLayout.tsx`
- **Sample Files**:
  - `frontmatter/contaminants/cadmium-plating-contamination.yaml`
  - `frontmatter/compounds/silicon-dioxide-compound.yaml`
  - `frontmatter/compounds/carbon-monoxide-compound.yaml` (good example)
