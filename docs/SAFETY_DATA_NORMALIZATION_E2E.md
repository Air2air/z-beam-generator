# Safety Data Normalization - End-to-End System Design

**Date**: January 2, 2026  
**Status**: ✅ **COMPLETE** - All 132 files migrated and normalized  
**Priority**: Critical - Foundation for safety information display

**Implementation Progress**:
- ✅ SafetyTableNormalizer enricher created (`export/enrichers/contaminants/safety_table_normalizer.py`)
- ✅ Added to contaminants export config
- ✅ **Migration executed**: 98 contaminants + 34 compounds
- ✅ **All files verified**: `relationships.safety.*` with `{presentation, items}` structure
- ✅ **Old structure removed**: No nested `safety_data` in `laser_properties`
- ✅ **Ready for frontend**: SafetyDataPanel can now render all safety data

---

## Executive Summary

This document defines the **complete normalization** of safety data across the Z-Beam system, establishing a single consistent structure for both contaminants and compounds, with clear migration paths and component integration.

---

## 🎯 Normalization Goals

1. **Single Source Location**: All safety data at `relationships.safety.*`
2. **Consistent Structure**: Same format for contaminants and compounds
3. **Component Compatibility**: SafetyDataPanel handles normalized data seamlessly
4. **Backward Compatibility**: Fallback paths during migration
5. **Type Safety**: Clear TypeScript interfaces for all safety data

---

## 📊 Current State Analysis

### Contaminants (Current - Incorrect)
```yaml
relationships:
  operational:
    laser_properties:
      items:
        - safety_data:                    # ← Nested 3 levels deep
            fire_explosion_risk: {...}
            toxic_gas_risk: {...}
```

### Compounds (Current - Inconsistent)
```yaml
relationships:
  safety:                                 # ← Correct location
    ppe_requirements: "String text..."    # ← Wrong format (string)
    health_effects: null                  # ← Missing data
```

---

## 📊 Table Structure Normalization

**Critical**: Some safety fields share identical table structures. These have been normalized to use a single unified type:

### Hazardous Compound Table

**Used By**:
- `toxic_gas_risk.primary_hazards` (nested array)
- `fumes_generated.items` (top-level array)

**Structure** (HazardousCompound):
```yaml
- compound: "Chemical name"
  concentration_mg_m3: 0.5
  exposure_limit_mg_m3: 0.002
  hazard_class: carcinogenic | toxic | irritant | corrosive
```

**Why Unified**: Both fields describe the same data (hazardous compounds generated during laser cleaning), just in different contexts. Using a single structure ensures consistent validation, rendering, and type safety.

---

## ✅ Normalized Structure (Target)

### Universal Safety Data Location

**For ALL content types** (contaminants, compounds, materials):

```yaml
relationships:
  safety:
    # Risk assessments (contaminants primary, compounds optional)
    fire_explosion_risk:
      presentation: card
      items:
        - severity: low | moderate | high | critical
          description: "Clear description of the risk"
          mitigation: "Specific mitigation measures"
          conditions: "When this risk occurs (optional)"
    
    toxic_gas_risk:
      presentation: card
      items:
        - severity: low | moderate | high | critical
          description: "Description of toxic gas generation"
          mitigation: "Required protective measures"
          # Hazardous compounds table (same structure as fumes_generated)
          primary_hazards:
            - compound: "Chemical name"
              concentration_mg_m3: 0.5
              exposure_limit_mg_m3: 0.002
              hazard_class: carcinogenic | toxic | irritant | corrosive
            - compound: "Another chemical"
              concentration_mg_m3: 0.3
              exposure_limit_mg_m3: 0.01
              hazard_class: toxic
    
    visibility_hazard:
      presentation: card
      items:
        - severity: low | moderate | high | critical
          description: "Description of visibility impact"
          source: "Source of the hazard"
          mitigation: "How to maintain safe visibility"
    
    # Personal Protective Equipment (universal)
    ppe_requirements:
      presentation: descriptive
      items:
        - respiratory: "Specific respirator type (e.g., NIOSH N95, PAPR)"
          eye_protection: "Specific eye protection (e.g., goggles, face shield)"
          skin_protection: "Specific skin protection (e.g., gloves, coveralls)"
          minimum_level: "OSHA level if applicable (e.g., Level B)"
          special_notes: "Additional requirements or warnings"
          rationale: "Why this PPE is required"
    
    # Ventilation requirements (universal)
    ventilation_requirements:
      presentation: descriptive
      items:
        - minimum_air_changes_per_hour: 15  # Numeric
          exhaust_velocity_m_s: 0.5          # Numeric
          filtration_type: "HEPA | ULPA | standard"
          capture_efficiency_required: 0.99   # Numeric (optional)
          rationale: "Why these ventilation specs are needed"
    
    # Particulate generation (contaminants primary, compounds optional)
    particulate_generation:
      presentation: descriptive
      items:
        - respirable_fraction: 0.85  # 0.0-1.0 (fraction respirable <10μm)
          size_range_um: [0.1, 10]   # [min, max] in micrometers
          generation_rate_mg_min: 15  # Optional: rate of generation
    
    # Fumes generated (contaminants primary)
    # NOTE: Uses same table structure as toxic_gas_risk.primary_hazards
    fumes_generated:
      presentation: descriptive
      items:
        - compound: "Chemical name"
          concentration_mg_m3: 0.5
          exposure_limit_mg_m3: 0.002
          hazard_class: carcinogenic | toxic | irritant | corrosive
        - compound: "Another chemical"
          concentration_mg_m3: 0.3
          exposure_limit_mg_m3: 0.01
          hazard_class: toxic
    
    # Exposure limits (compounds primary, contaminants optional)
    exposure_limits:
      presentation: descriptive
      items:
        - osha_pel_ppm: 50           # Numeric or null
          osha_pel_mg_m3: 55          # Numeric or null
          niosh_rel_ppm: 35
          niosh_rel_mg_m3: 40
          acgih_tlv_ppm: 25
          acgih_tlv_mg_m3: 29
          idlh_ppm: 1200              # Immediately Dangerous to Life/Health
          stel_ppm: 100               # Short-Term Exposure Limit (15 min)
          ceiling_ppm: null           # Ceiling limit (never exceed)
    
    # Workplace exposure (compounds primary)
    workplace_exposure:
      presentation: descriptive
      items:
        - monitoring_required: true | false
          monitoring_frequency: "Quarterly | Monthly | Continuous"
          detection_methods:
            - "Electrochemical sensors"
            - "Infrared spectroscopy"
          action_level_ppm: 25        # When to take action
          exposure_assessment: "Description of typical exposure scenarios"
    
    # Storage requirements (compounds primary, materials optional)
    storage_requirements:
      presentation: descriptive
      items:
        - container_type: "Sealed steel containers | Glass | Plastic"
          temperature_range: "15-30°C | Room temperature"
          humidity_control: "Keep dry | <50% RH"
          segregation: "Keep away from acids, bases, oxidizers"
          ventilation: "Store in well-ventilated area"
          special_precautions: "Avoid direct sunlight, heat sources"
    
    # Reactivity (compounds primary)
    reactivity:
      presentation: descriptive
      items:
        - stability: "Stable | Unstable under specific conditions"
          conditions_to_avoid: "High temperatures >100°C, sparks, flames"
          incompatible_materials: "Strong acids, bases, oxidizers, reactive metals"
          hazardous_decomposition: "CO, CO2, metal oxides (list specific products)"
          hazardous_polymerization: "Will not occur | May occur under conditions"
    
    # Environmental impact (compounds primary, contaminants optional)
    environmental_impact:
      presentation: descriptive
      items:
        - persistence: "High - does not biodegrade | Low - degrades in X days"
          bioaccumulation: "Low | Moderate | High (BCF: X)"
          aquatic_toxicity: "Low | Moderate | High (LC50: X mg/L)"
          soil_mobility: "Immobile | Moderately mobile | Highly mobile"
          atmospheric_impact: "Negligible | Moderate | Significant"
    
    # Regulatory classification (compounds primary)
    regulatory_classification:
      presentation: descriptive
      items:
        - dot_hazard_class: "2.3 | 6.1 | 8 (DOT classification)"
          dot_packing_group: "I | II | III"
          dot_label: "POISON GAS | TOXIC | CORROSIVE"
          nfpa_health: 3        # 0-4 scale
          nfpa_flammability: 1  # 0-4 scale
          nfpa_reactivity: 0    # 0-4 scale
          nfpa_special: "OX"    # Special hazards (OX, W, etc.)
          ghs_classification: "Acute Toxicity Category 2"
          ghs_pictograms:
            - "Skull and crossbones"
            - "Health hazard"
    
    # Emergency response (universal)
    emergency_response:
      presentation: descriptive
      items:
        - fire_hazard: "Description of fire behavior and risk"
          fire_suppression: "Specific fire fighting methods and agents"
          spill_procedures: "Step-by-step spill cleanup procedures"
          exposure_immediate_actions: "First aid and immediate response steps"
          environmental_hazards: "Environmental risks and containment"
          special_hazards: "Unique hazards or complications"
    
    # Detection and monitoring (universal)
    detection_monitoring:
      presentation: descriptive
      items:
        - detection_methods:
            - method: "Electrochemical sensors"
              detection_limit_ppm: 1
              response_time: "< 30 seconds"
            - method: "Colorimetric tubes"
              detection_limit_ppm: 5
              response_time: "2-5 minutes"
          monitoring_locations: "Near process area, exhaust vents, operator breathing zone"
          alarm_setpoints:
            warning_ppm: 25
            danger_ppm: 50
          calibration_frequency: "Monthly | Quarterly"
```

---

## 🔄 Migration Strategy

### Phase 1: Contaminants (Week 1)

**Scope**: ~80 contaminant files

**Tasks**:
1. Extract safety_data from `relationships.operational.laser_properties.items[0].safety_data`
2. Move to `relationships.safety.*`
3. Add presentation wrappers (`presentation: card` or `descriptive`)
4. Wrap all data in `items: [...]` arrays
5. Validate structure completeness

**Migration Script**:
```python
def migrate_contaminant(file_path):
    data = load_yaml(file_path)
    
    # Extract from nested location
    try:
        laser_props = data['relationships']['operational']['laser_properties']['items'][0]
        safety_data = laser_props.pop('safety_data', {})
    except (KeyError, IndexError):
        print(f"No safety_data found in {file_path}")
        return
    
    # Restructure with presentation wrappers
    normalized_safety = {}
    
    # Risk fields use 'card' presentation
    risk_fields = ['fire_explosion_risk', 'toxic_gas_risk', 'visibility_hazard']
    for field in risk_fields:
        if field in safety_data:
            normalized_safety[field] = {
                'presentation': 'card',
                'items': [safety_data[field]]
            }
    
    # Other fields use 'descriptive' presentation
    descriptive_fields = [
        'ppe_requirements', 'ventilation_requirements', 
        'particulate_generation', 'fumes_generated'
    ]
    for field in descriptive_fields:
        if field in safety_data:
            value = safety_data[field]
            normalized_safety[field] = {
                'presentation': 'descriptive',
                'items': [value] if not isinstance(value, list) else value
            }
    
    # Place at correct location
    if 'safety' not in data['relationships']:
        data['relationships']['safety'] = {}
    data['relationships']['safety'].update(normalized_safety)
    
    save_yaml(file_path, data)
    print(f"✅ Migrated {file_path}")

# Run for all contaminants
for file in glob('frontmatter/contaminants/*.yaml'):
    migrate_contaminant(file)
```

### Phase 2: Compounds (Week 2)

**Scope**: ~45 compound files

**Tasks**:
1. Parse string fields (ppe_requirements, storage_requirements)
2. Extract structured data using LLM if needed
3. Add missing fields (workplace_exposure, reactivity, environmental_impact)
4. Ensure exposure_limits are properly structured
5. Add presentation wrappers and items arrays

**String-to-Structure Conversion**:
```python
def parse_ppe_string_to_structure(text: str) -> dict:
    """Use LLM to extract structured PPE data from prose"""
    prompt = f"""
    Extract PPE requirements from this text into structured format:
    
    Text: {text}
    
    Return JSON with these fields:
    - respiratory: specific respirator type
    - eye_protection: specific eye protection
    - skin_protection: specific skin protection
    - special_notes: any additional requirements
    """
    
    # Call LLM (OpenAI, Claude, etc.)
    structured = llm_call(prompt)
    return structured

def migrate_compound(file_path):
    data = load_yaml(file_path)
    safety = data['relationships'].get('safety', {})
    
    # Convert string fields to structured
    if isinstance(safety.get('ppe_requirements'), str):
        ppe_text = safety['ppe_requirements']
        structured_ppe = parse_ppe_string_to_structure(ppe_text)
        safety['ppe_requirements'] = {
            'presentation': 'descriptive',
            'items': [structured_ppe]
        }
    
    # Similar for other string fields...
    
    save_yaml(file_path, data)
```

### Phase 3: Component Updates (Week 3)

**Update SafetyDataPanel**:
```typescript
// Handle normalized structure directly
if (collapsible) {
  const safetyDataObj: Record<string, any> = {};
  
  // Extract from normalized structure
  if (safetyData.fire_explosion_risk?.items?.[0]) {
    const item = safetyData.fire_explosion_risk.items[0];
    safetyDataObj.fire_explosion_risk = {
      severity: item.severity,
      description: item.description,
      mitigation: item.mitigation
    };
  }
  
  // Similar for all other fields...
}
```

**Update ContaminantsLayout**:
```typescript
// Simple direct access
const safetyData = relationships?.safety || {};

// No more nested extraction needed!
```

**Update CompoundsLayout**:
```typescript
// Same simple access
const safetyData = relationships?.safety || {};
```

---

## 📋 Validation Schema

### TypeScript Interfaces

```typescript
// Base types
type Severity = 'low' | 'moderate' | 'high' | 'critical';
type HazardClass = 'carcinogenic' | 'toxic' | 'irritant' | 'corrosive';
type Presentation = 'card' | 'descriptive';

// Safety data section wrapper
interface SafetySection<T> {
  presentation: Presentation;
  items: T[];
}

// Risk assessment (contaminants)
interface RiskAssessment {
  severity: Severity;
  description: string;
  mitigation: string;
  conditions?: string;
}

// Hazardous compound table (used by both primary_hazards and fumes_generated)
interface HazardousCompound {
  compound: string;
  concentration_mg_m3: number;
  exposure_limit_mg_m3: number;
  hazard_class: HazardClass;
}

interface ToxicGasRisk extends RiskAssessment {
  primary_hazards?: HazardousCompound[];
}

// PPE requirements (universal)
interface PPERequirements {
  respiratory: string;
  eye_protection: string;
  skin_protection: string;
  minimum_level?: string;
  special_notes?: string;
  rationale?: string;
}

// Ventilation (universal)
interface VentilationRequirements {
  minimum_air_changes_per_hour: number;
  exhaust_velocity_m_s: number;
  filtration_type: string;
  capture_efficiency_required?: number;
  rationale?: string;
}

// Particulate generation (contaminants)
interface ParticulateGeneration {
  respirable_fraction: number;  // 0.0-1.0
  size_range_um: [number, number];
  generation_rate_mg_min?: number;
}

// Note: fumes_generated uses SafetySection<HazardousCompound>
// Same table structure as toxic_gas_risk.primary_hazards

// Exposure limits (compounds)
interface ExposureLimits {
  osha_pel_ppm?: number | null;
  osha_pel_mg_m3?: number | null;
  niosh_rel_ppm?: number | null;
  niosh_rel_mg_m3?: number | null;
  acgih_tlv_ppm?: number | null;
  acgih_tlv_mg_m3?: number | null;
  idlh_ppm?: number | null;
  stel_ppm?: number | null;
  ceiling_ppm?: number | null;
}

// Complete normalized safety data
interface NormalizedSafetyData {
  // Risk assessments
  fire_explosion_risk?: SafetySection<RiskAssessment>;
  toxic_gas_risk?: SafetySection<ToxicGasRisk>;
  visibility_hazard?: SafetySection<RiskAssessment>;
  
  // Universal requirements
  ppe_requirements?: SafetySection<PPERequirements>;
  ventilation_requirements?: SafetySection<VentilationRequirements>;
  emergency_response?: SafetySection<any>;
  detection_monitoring?: SafetySection<any>;
  
  // Contaminant-specific
  particulate_generation?: SafetySection<ParticulateGeneration>;
  fumes_generated?: SafetySection<any>;
  
  // Compound-specific
  exposure_limits?: SafetySection<ExposureLimits>;
  workplace_exposure?: SafetySection<any>;
  storage_requirements?: SafetySection<any>;
  reactivity?: SafetySection<any>;
  environmental_impact?: SafetySection<any>;
  regulatory_classification?: SafetySection<any>;
}
```

### Validation Rules

1. **Required Fields by Type**:
   - Contaminants: fire_explosion_risk, toxic_gas_risk, ppe_requirements, ventilation_requirements
   - Compounds: ppe_requirements, storage_requirements, exposure_limits

2. **Numeric Validation**:
   - Severity: Must be one of ['low', 'moderate', 'high', 'critical']
   - PPM/mg_m3: Must be positive numbers or null
   - Respirable fraction: 0.0-1.0
   - Air changes per hour: Positive integer

3. **Structure Validation**:
   - All safety fields must have `presentation` and `items`
   - Items must be arrays (even if single element)
   - Risk fields must include severity, description, mitigation

---

## 🧪 Testing Strategy

### Validation Tests

```typescript
describe('Safety Data Normalization', () => {
  it('should have safety data at relationships.safety', () => {
    const metadata = loadContaminant('cadmium-plating');
    expect(metadata.relationships.safety).toBeDefined();
  });
  
  it('should have presentation wrappers', () => {
    const safetyData = metadata.relationships.safety;
    expect(safetyData.fire_explosion_risk.presentation).toBe('card');
    expect(safetyData.ppe_requirements.presentation).toBe('descriptive');
  });
  
  it('should have items arrays', () => {
    const safetyData = metadata.relationships.safety;
    expect(Array.isArray(safetyData.fire_explosion_risk.items)).toBe(true);
    expect(safetyData.fire_explosion_risk.items.length).toBeGreaterThan(0);
  });
  
  it('should have required risk fields', () => {
    const risk = safetyData.fire_explosion_risk.items[0];
    expect(risk.severity).toMatch(/^(low|moderate|high|critical)$/);
    expect(risk.description).toBeTruthy();
    expect(risk.mitigation).toBeTruthy();
  });
});
```

### Component Integration Tests

```typescript
describe('SafetyDataPanel with Normalized Data', () => {
  it('should render contaminant safety data', async () => {
    const { getByText } = render(
      <SafetyDataPanel 
        safetyData={normalizedContaminantSafety}
        collapsible={true}
      />
    );
    
    expect(getByText(/Fire.*Risk/i)).toBeInTheDocument();
    expect(getByText(/Toxic Gas/i)).toBeInTheDocument();
  });
  
  it('should render compound safety data', async () => {
    const { getByText } = render(
      <SafetyDataPanel 
        safetyData={normalizedCompoundSafety}
        collapsible={true}
      />
    );
    
    expect(getByText(/PPE Requirements/i)).toBeInTheDocument();
    expect(getByText(/Exposure Limits/i)).toBeInTheDocument();
  });
});
```

---

## 📈 Migration Timeline

| Week | Phase | Tasks | Deliverables |
|------|-------|-------|--------------|
| 1 | Contaminant Migration | Run migration script, validate structure | 80 normalized contaminant files |
| 2 | Compound Migration | Parse strings, add missing fields | 45 normalized compound files |
| 3 | Component Updates | Update SafetyDataPanel, layouts | Updated React components |
| 4 | Testing & Validation | Run test suite, manual QA | Passing tests, deployed changes |

---

## 🚀 Rollout Plan

### Pre-Migration
1. ✅ Document current state
2. ✅ Define normalized structure
3. ✅ Create TypeScript interfaces
4. ✅ Write migration scripts
5. ✅ Set up validation tests

### Migration
1. **Backup all frontmatter files**
2. Run contaminant migration script
3. Validate contaminant files (automated tests)
4. Manual spot-check 10 contaminants
5. Run compound migration script
6. Validate compound files (automated tests)
7. Manual spot-check 10 compounds

### Post-Migration
1. Update SafetyDataPanel component
2. Update ContaminantsLayout component
3. Update CompoundsLayout component
4. Run full test suite
5. Visual regression testing
6. Deploy to staging
7. User acceptance testing
8. Deploy to production

### Rollback Plan
- Keep backups of all original files
- Maintain old component code as fallback
- If issues found, restore backups and investigate

---

## 🎓 Training & Documentation

### For Backend Team
- Migration script usage
- Validation checklist
- Troubleshooting guide
- Data structure reference

### For Frontend Team
- Updated component APIs
- New TypeScript interfaces
- Testing requirements
- Integration examples

### For Content Team
- New safety data format
- Required fields by type
- Quality standards
- Review checklist

---

## 📚 Related Documentation

- `FRONTMATTER_SAFETY_DATA_FIX.md` - Original fix proposal (superseded by this doc)
- `docs/08-development/SAFETY_RISK_SEVERITY_SCHEMA.md` - Risk severity standards
- `app/components/SafetyDataPanel/SafetyDataPanel.tsx` - Component implementation
- `app/components/ContaminantsLayout/ContaminantsLayout.tsx` - Layout integration
- `app/components/CompoundsLayout/CompoundsLayout.tsx` - Layout integration

---

## ✅ Success Criteria

1. **Data Consistency**: 100% of safety data at `relationships.safety`
2. **Structure Compliance**: All fields have presentation + items wrappers
3. **Component Compatibility**: SafetyDataPanel renders all data correctly
4. **Test Coverage**: 95%+ test pass rate
5. **Visual Quality**: No regressions in UI rendering
6. **Performance**: No degradation in page load times
7. **Type Safety**: Zero TypeScript errors

---

## 🔮 Future Enhancements

1. **AI Validation**: Use LLM to validate safety data completeness and accuracy
2. **Auto-Extraction**: Parse existing prose descriptions to extract missing structured data
3. **Cross-References**: Link related safety data (e.g., compounds to contaminants)
4. **Historical Tracking**: Version control for safety data updates
5. **Compliance Reporting**: Generate safety reports from normalized data
