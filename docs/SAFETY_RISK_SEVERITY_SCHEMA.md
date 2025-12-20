# Safety Risk & Severity Schema

**Purpose**: Standardized vocabulary for safety risk assessment in laser cleaning operations  
**Usage**: Frontmatter generation, UI components (RiskCard, InfoCard), safety panels  
**Last Updated**: December 20, 2025

---

## Risk/Severity Levels

### Standardized Values

```yaml
# Use EXACTLY these lowercase values in frontmatter:
severity_levels:
  - critical  # Immediate danger, requires emergency protocols
  - high      # Severe risk, mandatory controls required
  - moderate  # Significant risk, protective measures needed
  - medium    # (alias for moderate) - both accepted
  - low       # Minimal risk, standard precautions sufficient
  - none      # No significant risk identified
```

### Visual Mapping

| Severity | Color | Border | Background | Text | Use Case |
|----------|-------|--------|------------|------|----------|
| `critical` | Red | `border-red-500` | `bg-red-900/20` | `text-red-400` | Immediate hazard |
| `high` | Red | `border-red-500` | `bg-red-900/20` | `text-red-400` | Severe risk |
| `moderate` | Yellow | `border-yellow-500` | `bg-yellow-900/20` | `text-yellow-400` | Significant risk |
| `medium` | Yellow | `border-yellow-500` | `bg-yellow-900/20` | `text-yellow-400` | (alias) |
| `low` | Green | `border-green-500` | `bg-green-900/20` | `text-green-400` | Minimal risk |
| `none` | Gray | `border-gray-600` | `bg-gray-800/50` | `text-gray-400` | No risk |

---

## Safety Data Fields

### Complete Schema Structure

```yaml
# Material/Contaminant Frontmatter Safety Section
safety_data:
  # Risk Assessment (required - use severity levels above)
  fire_explosion_risk: "moderate"      # Fire/explosion potential
  toxic_gas_risk: "high"               # Toxic gas generation
  visibility_hazard: "low"             # Smoke/particulate visibility impact
  
  # Personal Protective Equipment (required)
  ppe_requirements:
    respiratory: "P100 Respirator"     # NIOSH/OSHA designation
    eye_protection: "Safety Goggles"   # Specific type required
    skin_protection: "Leather Gloves"  # Material and coverage
  
  # Ventilation Requirements (required for moderate+ risks)
  ventilation_requirements:
    minimum_air_changes_per_hour: 12                # ACH rate
    exhaust_velocity_m_s: 0.75                      # Capture velocity (m/s)
    filtration_type: "HEPA + Activated Carbon"      # Filter specification
  
  # Particulate Generation (required)
  particulate_generation:
    respirable_fraction: 0.65          # Fraction <10μm (0.0-1.0)
    size_range_um: [0.5, 10.0]         # Min/max particle size (μm)
  
  # Substrate Compatibility Warnings (optional)
  substrate_compatibility_warnings:
    - "May cause discoloration on painted surfaces"
    - "Not recommended for thin aluminum substrates (<2mm)"
```

---

## Field-Specific Guidelines

### 1. Risk Assessment Fields

**Fire/Explosion Risk** (`fire_explosion_risk`)
- **Critical**: Pyrophoric materials, explosive vapors
- **High**: Flammable residues, combustible dust generation
- **Moderate**: Heat-sensitive substrates, confined spaces
- **Low**: Non-flammable materials, well-ventilated areas

**Toxic Gas Risk** (`toxic_gas_risk`)
- **Critical**: Highly toxic gases (HCN, phosgene, HF)
- **High**: Toxic fumes requiring SCBA (chromium VI, lead)
- **Moderate**: Irritant gases requiring respirator
- **Low**: Minimal off-gassing, nuisance particulates

**Visibility Hazard** (`visibility_hazard`)
- **High**: Dense smoke generation, confined spaces
- **Moderate**: Significant particulate generation
- **Low**: Light haze, well-ventilated areas

### 2. PPE Requirements

**Respiratory Protection** (`ppe_requirements.respiratory`)
```yaml
# Standard values (use EXACTLY as shown):
- "N95 Respirator"               # Particulate only, low toxicity
- "P100 Respirator"              # High particulate filtration
- "Half-Face Respirator"         # Organic vapor + particulate
- "Full-Face Respirator"         # Eye protection + filtration
- "SCBA Required"                # Self-contained breathing apparatus
- "Supplied Air Required"        # Airline respirator system
```

**Eye Protection** (`ppe_requirements.eye_protection`)
```yaml
- "Safety Glasses"               # Impact protection only
- "Safety Goggles"               # Sealed eye protection
- "Face Shield"                  # Full-face coverage
- "Laser Safety Goggles"         # Wavelength-specific (specify nm)
- "Combination (Goggles + Shield)"  # Multi-layer protection
```

**Skin Protection** (`ppe_requirements.skin_protection`)
```yaml
- "Leather Gloves"               # Heat + abrasion
- "Chemical-Resistant Gloves"    # Specific to contaminant
- "Full Body Coverage"           # Tyvek suit, coveralls
- "Heat-Resistant Apron"         # Thermal protection
```

### 3. Ventilation Requirements

**Air Changes Per Hour** (`minimum_air_changes_per_hour`)
- **6-8 ACH**: Low-risk operations, minimal particulate
- **10-12 ACH**: Moderate risk, standard industrial ventilation
- **15-20 ACH**: High-risk operations, toxic materials
- **20+ ACH**: Critical risk, laboratory/confined space

**Exhaust Velocity** (`exhaust_velocity_m_s`)
- **0.5 m/s**: Low capture velocity for light particulates
- **0.75 m/s**: Standard industrial capture velocity
- **1.0+ m/s**: High velocity for heavy/toxic particulates

**Filtration Type** (`filtration_type`)
```yaml
- "Mechanical Filtration"        # Particulate capture only
- "HEPA Filtration"              # 99.97% at 0.3μm
- "Activated Carbon"             # Organic vapor adsorption
- "HEPA + Activated Carbon"      # Combined particulate + vapor
- "Wet Scrubber"                 # Liquid phase capture
```

### 4. Particulate Generation

**Respirable Fraction** (`respirable_fraction`)
- Value range: `0.0` to `1.0` (fraction, not percentage)
- **0.0-0.3**: Mostly coarse particles (>10μm)
- **0.3-0.6**: Mixed particle distribution
- **0.6-0.8**: High respirable fraction
- **0.8-1.0**: Almost entirely respirable (<10μm)

**Size Range** (`size_range_um`)
- Array format: `[min, max]` in micrometers
- Common ranges:
  - `[0.1, 5.0]`: Fine particulates
  - `[0.5, 10.0]`: Respirable range
  - `[2.0, 50.0]`: Coarse particulates

---

## Implementation Notes

### Utility Function

Risk colors are handled by the global utility:

```typescript
// app/utils/layoutHelpers.ts
export function getRiskColor(risk: string) {
  switch (risk?.toLowerCase()) {
    case 'high':
    case 'critical':
      return 'text-red-400 bg-red-900/20 border-red-500';
    case 'moderate':
    case 'medium':
      return 'text-yellow-400 bg-yellow-900/20 border-yellow-500';
    case 'low':
      return 'text-green-400 bg-green-900/20 border-green-500';
    default:
      return 'text-gray-400 bg-gray-800/50 border-gray-600';
  }
}
```

### Component Usage

**RiskCard** - For risk assessment cards:
```tsx
<RiskCard
  icon={Flame}
  label="Fire/Explosion Risk"
  severity={safetyData.fire_explosion_risk}  // "high", "moderate", "low"
/>
```

**InfoCard** - For PPE/ventilation/particulate data:
```tsx
<InfoCard
  icon={Shield}
  title="PPE Requirements"
  data={[
    { label: 'Respiratory', value: safetyData.ppe_requirements.respiratory },
    { label: 'Eye Protection', value: safetyData.ppe_requirements.eye_protection }
  ]}
/>
```

---

## Validation Rules

### Required Fields
- ✅ All three risk assessment fields (fire, toxic gas, visibility)
- ✅ PPE requirements (all three protection types)
- ✅ Ventilation requirements (for moderate+ risks)
- ✅ Particulate generation data

### Data Type Validation
- Risk levels: Must be one of `[critical, high, moderate, medium, low, none]`
- Respirable fraction: Must be float between 0.0 and 1.0
- Size range: Must be array of two positive numbers `[min, max]` where `min < max`
- ACH: Must be positive integer (typical range: 6-30)
- Exhaust velocity: Must be positive float (typical range: 0.5-2.0 m/s)

### Business Logic Validation
- If `fire_explosion_risk >= moderate` → ventilation required
- If `toxic_gas_risk >= high` → SCBA or supplied air required
- If `respirable_fraction > 0.6` → P100 minimum respiratory protection
- If `visibility_hazard >= high` → mechanical ventilation required

---

## Examples

### Example 1: High-Risk Contaminant (Lead-Based Paint)

```yaml
safety_data:
  fire_explosion_risk: "low"
  toxic_gas_risk: "critical"
  visibility_hazard: "moderate"
  
  ppe_requirements:
    respiratory: "SCBA Required"
    eye_protection: "Safety Goggles"
    skin_protection: "Chemical-Resistant Gloves"
  
  ventilation_requirements:
    minimum_air_changes_per_hour: 20
    exhaust_velocity_m_s: 1.2
    filtration_type: "HEPA + Activated Carbon"
  
  particulate_generation:
    respirable_fraction: 0.85
    size_range_um: [0.1, 5.0]
  
  substrate_compatibility_warnings:
    - "Generates highly toxic lead fumes"
    - "OSHA regulated substance - special protocols required"
    - "Medical surveillance required for operators"
```

### Example 2: Moderate-Risk Material (Aluminum)

```yaml
safety_data:
  fire_explosion_risk: "moderate"
  toxic_gas_risk: "low"
  visibility_hazard: "moderate"
  
  ppe_requirements:
    respiratory: "P100 Respirator"
    eye_protection: "Safety Goggles"
    skin_protection: "Leather Gloves"
  
  ventilation_requirements:
    minimum_air_changes_per_hour: 12
    exhaust_velocity_m_s: 0.75
    filtration_type: "HEPA Filtration"
  
  particulate_generation:
    respirable_fraction: 0.65
    size_range_um: [0.5, 10.0]
```

### Example 3: Low-Risk Cleaning (Concrete Dust)

```yaml
safety_data:
  fire_explosion_risk: "low"
  toxic_gas_risk: "low"
  visibility_hazard: "moderate"
  
  ppe_requirements:
    respiratory: "N95 Respirator"
    eye_protection: "Safety Glasses"
    skin_protection: "Leather Gloves"
  
  ventilation_requirements:
    minimum_air_changes_per_hour: 8
    exhaust_velocity_m_s: 0.5
    filtration_type: "Mechanical Filtration"
  
  particulate_generation:
    respirable_fraction: 0.35
    size_range_um: [2.0, 50.0]
```

---

## Related Documentation

- **Component Implementation**: `/app/components/RiskCard/RiskCard.tsx`
- **Utility Functions**: `/app/utils/layoutHelpers.ts`
- **Unified Safety Grid**: `/app/components/SafetyDataPanel/SafetyDataPanel.tsx`
- **InfoCard Component**: `/app/components/InfoCard/InfoCard.tsx`
- **Testing**: `/tests/utils/layoutHelpers.test.ts`

---

## Changelog

**December 20, 2025**
- Initial schema documentation
- Standardized severity vocabulary
- Comprehensive field guidelines
- Added validation rules and examples
