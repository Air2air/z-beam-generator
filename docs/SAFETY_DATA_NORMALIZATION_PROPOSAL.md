# Safety Data Structure Normalization Proposal

**Date**: December 20, 2025  
**Purpose**: Normalize data structure between "thin" risk fields and "complete" nested objects  
**Target**: SafetyData component in frontend

---

## Current Inconsistency

### Thin Entries (String Values Only)
```yaml
fire_explosion_risk: "low"
toxic_gas_risk: "moderate"
visibility_hazard: "high"
```

### Complete Entries (Structured Objects)
```yaml
ppe_requirements:
  respiratory: "P100 Respirator"
  eye_protection: "Safety Goggles"
  skin_protection: "Leather Gloves"

ventilation_requirements:
  minimum_air_changes_per_hour: 12
  exhaust_velocity_m_s: 0.75
  filtration_type: "HEPA + Activated Carbon"

particulate_generation:
  respirable_fraction: 0.65
  size_range_um: [0.5, 10.0]
```

**Problem**: Thin entries lack context, making it harder to render rich UI components with consistent patterns.

---

## Proposed Normalized Structure

### Option A: Enrich Thin Entries (Recommended)

**Rationale**: Add context fields to risk assessments, making all six keys structurally consistent.

```yaml
safety_data:
  # Risk Assessment (enriched with context)
  fire_explosion_risk:
    severity: "moderate"
    description: "Flammable residues may ignite under high-power settings"
    mitigation: "Ensure fire extinguisher within 10m, avoid enclosed spaces"
    
  toxic_gas_risk:
    severity: "high"
    primary_hazards:
      - compound: "Formaldehyde"
        concentration_mg_m3: 10
      - compound: "Benzene"
        concentration_mg_m3: 5
    description: "Multiple carcinogenic compounds detected"
    mitigation: "Full-face respirator with organic vapor cartridge required"
    
  visibility_hazard:
    severity: "moderate"
    description: "Dense particulate generation reduces visibility by 40-60%"
    source: "Respirable fraction: 0.7 (70% of particles <10μm)"
    mitigation: "Maintain clear sight lines, use extraction at source"
  
  # Personal Protective Equipment (already structured)
  ppe_requirements:
    respiratory: "Full-Face Respirator"
    eye_protection: "Safety Goggles"
    skin_protection: "Chemical-Resistant Gloves"
    rationale: "Protects against carcinogenic vapor and particulate exposure"
  
  # Ventilation Requirements (already structured)
  ventilation_requirements:
    minimum_air_changes_per_hour: 15
    exhaust_velocity_m_s: 1.0
    filtration_type: "HEPA + Activated Carbon"
    rationale: "High toxic gas risk requires enhanced ventilation and vapor capture"
  
  # Particulate Generation (already structured)
  particulate_generation:
    respirable_fraction: 0.7
    size_range_um: [0.1, 10.0]
    total_generation_rate_mg_min: 250
    composition:
      - "Aluminum oxide (60%)"
      - "Epoxy resin residue (30%)"
      - "Adhesive compounds (10%)"
```

**Benefits**:
- ✅ All six keys have consistent nested structure
- ✅ Rich context for UI rendering (tooltips, expandable cards)
- ✅ Machine-readable for filtering/sorting
- ✅ Human-readable descriptions for non-technical users
- ✅ Backward compatible (severity field preserves original value)

---

### Option B: Keep Thin + Add Metadata Layer

**Rationale**: Preserve simple risk severity values but add a separate metadata object.

```yaml
safety_data:
  # Simple severity values (preserved)
  fire_explosion_risk: "moderate"
  toxic_gas_risk: "high"
  visibility_hazard: "moderate"
  
  # Structured details
  ppe_requirements: { ... }
  ventilation_requirements: { ... }
  particulate_generation: { ... }
  
  # NEW: Risk assessment metadata (optional)
  risk_metadata:
    fire_explosion:
      description: "Flammable residues may ignite under high-power settings"
      mitigation: "Ensure fire extinguisher within 10m"
    toxic_gas:
      primary_hazards: ["Formaldehyde", "Benzene"]
      description: "Multiple carcinogenic compounds detected"
    visibility:
      description: "Dense particulate reduces visibility by 40-60%"
      source_metric: "respirable_fraction"
      source_value: 0.7
```

**Benefits**:
- ✅ Backward compatible (existing severity strings unchanged)
- ✅ Optional enrichment (metadata can be added incrementally)
- ✅ Simpler queries (can check `toxic_gas_risk == "high"` without nested access)

**Drawbacks**:
- ⚠️ Inconsistent structure (three simple + three complex + one metadata)
- ⚠️ Harder to render uniformly in UI (need special cases)

---

## Recommended Frontend Organization

### Component Hierarchy for SafetyData

```typescript
<SafetyData>
  <SafetySection title="Risk Assessment">
    <RiskCard 
      type="fire_explosion_risk"
      data={safety_data.fire_explosion_risk}
    />
    <RiskCard 
      type="toxic_gas_risk"
      data={safety_data.toxic_gas_risk}
    />
    <RiskCard 
      type="visibility_hazard"
      data={safety_data.visibility_hazard}
    />
  </SafetySection>

  <SafetySection title="Personal Protective Equipment">
    <PPECard data={safety_data.ppe_requirements} />
  </SafetySection>

  <SafetySection title="Environmental Controls">
    <VentilationCard data={safety_data.ventilation_requirements} />
  </SafetySection>

  <SafetySection title="Exposure Data">
    <ParticulateCard data={safety_data.particulate_generation} />
    <FumesCard data={safety_data.fumes_generated} />
  </SafetySection>
</SafetyData>
```

### Logical Grouping

**1. Risk Assessment** (What hazards exist?)
- Fire/Explosion Risk
- Toxic Gas Risk  
- Visibility Hazard

**2. Personal Protective Equipment** (What should operators wear?)
- PPE Requirements

**3. Environmental Controls** (What facility requirements?)
- Ventilation Requirements

**4. Exposure Data** (What's being generated?)
- Particulate Generation
- Fumes Generated (if applicable)

---

## Implementation Recommendation

### Phase 1: Enrich Risk Fields (Option A)

1. **Update Schema** (`SAFETY_RISK_SEVERITY_SCHEMA.md`)
   - Define enriched risk field structure
   - Add required/optional field specifications
   - Update examples with new format

2. **Create Migration Script** (`scripts/maintenance/enrich_risk_fields.py`)
   ```python
   def enrich_fire_explosion_risk(severity, safety_data):
       """Generate description and mitigation from severity + context"""
       fire_risk_descriptions = {
           'critical': "Immediate ignition risk with pyrophoric materials",
           'high': "Flammable residues or explosive vapor generation",
           'moderate': "Combustible materials in confined spaces",
           'low': "Minimal fire risk with standard precautions"
       }
       
       return {
           'severity': severity,
           'description': fire_risk_descriptions.get(severity, ""),
           'mitigation': generate_mitigation(severity, 'fire')
       }
   
   def enrich_toxic_gas_risk(severity, fumes_generated):
       """Extract primary hazards from fumes_generated list"""
       high_risk_compounds = []
       
       for fume in fumes_generated:
           if fume['hazard_class'] in ['carcinogenic', 'highly_toxic']:
               high_risk_compounds.append({
                   'compound': fume['compound'],
                   'concentration_mg_m3': fume['concentration_mg_m3']
               })
       
       return {
           'severity': severity,
           'primary_hazards': high_risk_compounds,
           'description': generate_toxic_gas_description(severity, high_risk_compounds),
           'mitigation': generate_mitigation(severity, 'toxic_gas')
       }
   
   def enrich_visibility_hazard(severity, respirable_fraction):
       """Link to particulate_generation data"""
       visibility_impact = {
           'high': f"Dense smoke (respirable fraction: {respirable_fraction:.1%})",
           'moderate': f"Moderate particulate haze (respirable fraction: {respirable_fraction:.1%})",
           'low': f"Light haze (respirable fraction: {respirable_fraction:.1%})"
       }
       
       return {
           'severity': severity,
           'description': visibility_impact.get(severity, ""),
           'source': f"Respirable fraction: {respirable_fraction}",
           'mitigation': generate_mitigation(severity, 'visibility')
       }
   ```

3. **Update Universal Exporter**
   - Add enrichment logic to `BreadcrumbEnricher` or create `SafetyDataEnricher`
   - Apply enrichment during frontmatter generation
   - Preserve backward compatibility (read both old and new formats)

4. **Update Frontend Components**
   - Modify `RiskCard` to render enriched structure
   - Add tooltips/expandable sections for descriptions
   - Use `severity` field for color/icon (unchanged from current)
   - Display `description`, `mitigation`, `primary_hazards` as rich content

### Phase 2: Add Optional Rationale Fields

Add `rationale` fields to PPE, Ventilation, and Particulate to complete normalization:

```yaml
ppe_requirements:
  respiratory: "Full-Face Respirator"
  eye_protection: "Safety Goggles"
  skin_protection: "Chemical-Resistant Gloves"
  rationale: "Protects against carcinogenic vapor and particulate exposure"

ventilation_requirements:
  minimum_air_changes_per_hour: 15
  exhaust_velocity_m_s: 1.0
  filtration_type: "HEPA + Activated Carbon"
  rationale: "High toxic gas risk requires enhanced ventilation"
```

---

## Data Consistency Rules

### All Six Keys Should Have

1. **Primary Value** - The core data (severity string OR structured object)
2. **Context** - Why this value? (description, rationale)
3. **Actionable Guidance** - What to do? (mitigation, requirements)
4. **Data Provenance** - Where did this come from? (source metrics, calculations)

### Example: Fully Normalized Entry

```yaml
visibility_hazard:
  severity: "moderate"                     # PRIMARY VALUE
  description: "Particulate haze reduces visibility by 40-60%"  # CONTEXT
  mitigation: "Maintain clear sight lines, use source extraction"  # ACTIONABLE
  source: "Calculated from respirable_fraction: 0.7"  # PROVENANCE
  related_field: "particulate_generation.respirable_fraction"  # LINKAGE
```

---

## Migration Strategy

### Backward Compatibility

**Old format** (thin string):
```yaml
toxic_gas_risk: "high"
```

**New format** (enriched object):
```yaml
toxic_gas_risk:
  severity: "high"
  primary_hazards: [...]
  description: "..."
  mitigation: "..."
```

**Frontend handling**:
```typescript
function getSeverity(riskField: string | RiskObject): string {
  if (typeof riskField === 'string') {
    return riskField;  // Backward compatible
  }
  return riskField.severity;  // New format
}

function getDescription(riskField: string | RiskObject): string | null {
  if (typeof riskField === 'string') {
    return null;  // No description in old format
  }
  return riskField.description;  // New format
}
```

### Rollout Plan

1. **Week 1**: Update schema documentation
2. **Week 2**: Create enrichment script, test on 10 files
3. **Week 3**: Apply to all contaminants (98 files)
4. **Week 4**: Update frontend components to handle both formats
5. **Week 5**: Apply to all domains, verify UI rendering
6. **Week 6**: Remove backward compatibility code (optional)

---

## Summary

**Recommended Approach**: Option A (Enrich Thin Entries)

**Key Benefits**:
- Structural consistency across all six keys
- Rich context for UI components
- Machine-readable and human-readable
- Backward compatible migration path

**Frontend Organization**:
1. Risk Assessment (fire, toxic gas, visibility)
2. Personal Protective Equipment
3. Environmental Controls
4. Exposure Data

**Next Steps**:
1. Review and approve this proposal
2. Update `SAFETY_RISK_SEVERITY_SCHEMA.md` with enriched structure
3. Create `scripts/maintenance/enrich_risk_fields.py`
4. Test on 10 contaminant files
5. Apply to all domains
6. Update frontend components

