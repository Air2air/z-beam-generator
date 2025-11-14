# Settings Page Data Requirements for Python Generator

## Task Overview
Generate/enhance data for settings pages that display 4 interactive components:
1. **ParameterRelationships** - Network visualization of parameter interdependencies
2. **MaterialSafetyHeatmap** - Shows damage risk zones (power vs pulse width)
3. **ProcessEffectivenessHeatmap** - Shows cleaning effectiveness zones
4. **ThermalAccumulation** - Simulates temperature buildup across passes
5. **DiagnosticCenter** - Material challenges and troubleshooting guide

## File Structure
Two files work together for each material:

**Settings File**: `/frontmatter/settings/{material}-settings.yaml`
- Contains: Machine parameters, material challenges, troubleshooting
- Used by: Settings page at `/settings/{category}/{subcategory}/{material}`

**Materials File**: `/frontmatter/materials/{material}-laser-cleaning.yaml`
- Contains: Material properties (thermal, optical, mechanical)
- Used by: Materials page AND loaded by settings page for component calculations

## Current Status Example (Alabaster)

### ✅ COMPLETE in alabaster-settings.yaml:
```yaml
machineSettings:
  powerRange: {value: 45, min: 1.0, max: 120, unit: W}
  wavelength: {value: 1064, min: 355, max: 10640, unit: nm}
  spotSize: {value: 80, min: 0.1, max: 500, unit: μm}
  repetitionRate: {value: 50, min: 1, max: 200, unit: kHz}
  fluenceThreshold: {value: 1.2, min: 0.3, max: 4.5, unit: J/cm²}
  pulseWidth: {value: 15, min: 0.1, max: 1000, unit: ns}
  scanSpeed: {value: 500, min: 10, max: 5000, unit: mm/s}
  passCount: {value: 2, min: 1, max: 10, unit: passes}
  overlapRatio: {value: 50, min: 10, max: 90, unit: '%'}

material_challenges:
  thermal_management: [extensive list with severity, thresholds, solutions]
  surface_characteristics: [detailed challenges]
  contamination_challenges: [specific to material]
```

### ✅ COMPLETE in alabaster-laser-cleaning.yaml:
```yaml
materialProperties:
  material_characteristics:
    thermalDiffusivity: {value: 1.82e-07, unit: m²/s}
    thermalConductivity: {value: 0.86, unit: W/(m·K)}
    thermalDestruction: {value: 423.0, unit: K}
    density: {value: 2.32, unit: g/cm³}
    # ... other mechanical properties
  
  laser_material_interaction:
    laserDamageThreshold: {value: 2.5, unit: J/cm², min: 1.0, max: 5.0}
    thermalShockResistance: {value: 1.2, unit: MW/m, min: 0.8, max: 1.8}
    absorptivity: {value: 0.15, unit: dimensionless}
    reflectivity: {value: 0.85, unit: dimensionless}
    # ... other laser interaction properties
```

### ❌ MISSING in alabaster-settings.yaml:
```yaml
common_issues:
  - symptom: "Specific observable problem"
    causes: ["Root cause 1", "Root cause 2", "Root cause 3"]
    solutions:
      - "Specific action to fix (with parameters)"
      - "Alternative solution if first fails"
      - "Third option for edge cases"
    verification: "How to confirm the fix worked"
    prevention: "How to avoid this issue in future"
```

### ❌ MISSING in alabaster-laser-cleaning.yaml:
```yaml
laser_material_interaction:
  ablationThreshold:
    value: 1.5  # J/cm² - energy needed to remove contaminants
    unit: J/cm²
    min: 0.8
    max: 2.5
    source: ai_research
```

---

## Required Additions

### 1. ADD TO SETTINGS YAML: `common_issues` Array

Generate 4-6 material-specific troubleshooting entries following this structure:

```yaml
common_issues:
  # Issue 1: Most common problem for this material
  - symptom: "[Observable problem the operator sees]"
    causes:
      - "[Primary root cause with physics explanation]"
      - "[Secondary cause - often related to parameters]"
      - "[Environmental or setup issue]"
    solutions:
      - "[First solution with specific parameter changes]"
      - "[Alternative approach if first doesn't work]"
      - "[Last resort or complementary action]"
    verification: "[How to measure/confirm success]"
    prevention: "[Proactive steps to avoid recurrence]"
  
  # Issue 2: Damage or safety concern
  - symptom: "[What damage looks like]"
    causes:
      - "[Physics of damage mechanism]"
      - "[Parameter that exceeded threshold]"
      - "[Material-specific vulnerability]"
    solutions:
      - "[Reduce power/energy by X%]"
      - "[Change scan pattern or speed]"
      - "[Add cooling or modify timing]"
    verification: "[Inspection method or test]"
    prevention: "[Conservative parameter starting point]"
  
  # Issue 3: Incomplete cleaning
  - symptom: "[What incomplete cleaning looks like]"
    causes:
      - "[Insufficient energy delivery]"
      - "[Wrong wavelength/absorption issue]"
      - "[Contaminant-specific challenge]"
    solutions:
      - "[Increase energy approach 1]"
      - "[Multiple pass strategy]"
      - "[Combined laser + chemical approach]"
    verification: "[Visual or analytical test]"
    prevention: "[Pre-assessment recommendations]"
  
  # Issue 4-6: Additional material-specific issues
  # - Surface finish problems
  # - Color changes
  # - Structural integrity concerns
  # - Residue redeposition
  # - Environmental challenges (humidity, temperature)
```

**Guidelines for common_issues generation:**

**Symptom** should be:
- Observable without special equipment (visual, tactile)
- Specific to this material's behavior
- Worded as operator would describe it

**Causes** should explain:
- Physics/chemistry of why it happens
- Which parameters contribute
- Material properties that make it susceptible

**Solutions** must include:
- Specific parameter values or percentages (e.g., "Reduce power from 100W to 70W")
- Priority order (try this first, then this)
- Multiple approaches for different situations

**Verification** should specify:
- Visual inspection criteria
- Measurement methods if needed
- Acceptable ranges

**Prevention** should recommend:
- Starting parameters (conservative)
- Pre-process checks
- Environmental controls

---

### 2. ADD TO MATERIALS YAML: `ablationThreshold`

Add to the `laser_material_interaction` section:

```yaml
laser_material_interaction:
  ablationThreshold:
    value: [CALCULATE based on material type]
    unit: J/cm²
    min: [value * 0.6]
    max: [value * 1.5]
    source: ai_research
```

**Ablation Threshold Guidelines by Material Category:**

| Category | Material Type | Typical Range (J/cm²) | Reasoning |
|----------|--------------|----------------------|-----------|
| **Metal - Ferrous** | Steel, Iron | 3-6 | High melting point, oxide layer |
| **Metal - Non-Ferrous** | Aluminum, Copper | 1.5-4 | Lower melting point, high conductivity |
| **Metal - Precious** | Gold, Silver | 2-5 | Excellent conductivity, tarnish layer |
| **Wood - Hardwood** | Oak, Maple | 0.8-1.5 | Dense structure, chars at 250°C |
| **Wood - Softwood** | Pine, Cedar | 0.6-1.2 | Less dense, resinous, lower char point |
| **Plastic - Thermoplastic** | ABS, Acrylic | 0.5-1.5 | Low melting point (150-250°C) |
| **Plastic - Thermoset** | Epoxy, Phenolic | 1.0-2.5 | Decomposes rather than melts |
| **Composite - Carbon Fiber** | CFRP | 1.5-4 | Matrix removal vs fiber preservation |
| **Composite - Fiberglass** | GFRP | 1.0-2.5 | Resin ablation around glass fibers |
| **Stone - Natural** | Granite, Marble, Alabaster | 4-10 | Varies by mineral composition |
| **Stone - Engineered** | Concrete, Terrazzo | 3-8 | Aggregate vs binder different thresholds |
| **Ceramic - Traditional** | Porcelain, Terracotta | 5-12 | High firing temperature = robust |
| **Ceramic - Advanced** | Alumina, Zirconia | 10-20 | Extremely hard, very high threshold |
| **Glass - Standard** | Soda-lime, Borosilicate | 2-6 | Thermal shock limits before ablation |
| **Glass - Specialty** | Quartz, Sapphire | 8-30 | Exceptional hardness and stability |
| **Rubber** | EPDM, Silicone | 0.5-2 | Burns/melts easily |
| **Textile - Natural** | Cotton, Wool, Leather | 0.3-1.0 | Very delicate, chars at 230°C |
| **Textile - Synthetic** | Polyester, Nylon | 0.8-2.5 | Melts before ablating |

**Calculation Logic:**
1. If `laserDamageThreshold` exists, set `ablationThreshold = laserDamageThreshold * 0.5` (contamination removes before substrate damages)
2. If no damage threshold, use table above based on category/subcategory
3. Set `min = value * 0.6` and `max = value * 1.5` for range
4. Lower threshold = easier to clean but also easier to damage

---

## Material-Specific Considerations for common_issues

### For METALS:
- Oxide reformation (happens in minutes/seconds)
- Reflectivity challenges (polished vs oxidized)
- Thermal distortion (thin sheets)
- Sparking/spatter safety

### For WOOD:
- Charring (primary concern - occurs at 250-300°C)
- Grain direction effects (20-40% absorption variation)
- Raised grain/fuzzing from broken lignin
- Moisture content impact (must be <10%)
- Smoke generation

### For PLASTICS:
- Melting vs ablation balance (critical)
- Toxic fumes (especially PVC, polycarbonate)
- Static electricity attracting debris
- Color changes from heat
- Warping/deformation

### For COMPOSITES:
- Matrix vs fiber damage thresholds different
- Delamination risk (layers separate)
- Anisotropic properties (direction matters)
- Outgassing during heating

### For STONE:
- Thermal shock cracking (especially marble, alabaster)
- Moisture-induced spalling (explosive failure)
- Mineral heterogeneity (different absorption)
- Weathering effects (aged stone weaker)
- Heritage preservation requirements

### For CERAMICS:
- Catastrophic thermal shock (rapid failure)
- Microcracking (hard to detect)
- Glaze vs body different properties
- Porosity variation (dense vs porous)

### For GLASS:
- Extreme thermal shock sensitivity
- IR transparency (poor absorption at 1064nm)
- Subsurface damage critical
- Optical quality requirements

### For RUBBER:
- Melting/tackiness
- Toxic decomposition fumes
- Carbon black absorption effects
- Surface chemistry changes

### For TEXTILES:
- Extreme burn risk (cotton chars at 230°C)
- Color fading from heat
- Fiber strength degradation
- Melting (synthetics) vs burning (natural)

---

## Validation Checklist

Before finalizing, verify:

✅ **Settings YAML has:**
- [ ] All 9 machineSettings parameters with min/max/value/unit
- [ ] material_challenges with 3 categories (thermal, surface, contamination)
- [ ] common_issues array with 4-6 material-specific problems

✅ **Materials YAML has:**
- [ ] thermalDiffusivity (critical for ThermalAccumulation)
- [ ] thermalConductivity (affects heatmaps)
- [ ] thermalDestruction or thermalDestructionPoint (damage zones)
- [ ] laserDamageThreshold (red zones in safety heatmap)
- [ ] ablationThreshold (effectiveness zones)
- [ ] thermalShockResistance (damage scoring)

✅ **Quality checks:**
- [ ] Parameter values are realistic for material type
- [ ] Solutions include specific numeric parameters
- [ ] Causes explain the physics/chemistry
- [ ] Material-specific terminology used (not generic)
- [ ] Severity levels match actual risk (critical/high/medium)

---

## Example Output Format

```yaml
# In {material}-settings.yaml
common_issues:
  - symptom: "White ashy residue remains on surface after cleaning"
    causes:
      - "Fluence exceeds optimal range causing surface carbonization"
      - "Scan speed too slow (dwell time >50ms per spot)"
      - "Multiple passes without adequate cooling accumulate heat"
    solutions:
      - "Reduce power from 100W to 70-80W (30% reduction)"
      - "Increase scan speed from 500 mm/s to 800 mm/s"
      - "Add 5-second cooling delay between passes"
      - "Switch to crosshatch pattern to distribute heat"
    verification: "Surface should be clean with natural color, no white deposits. Test with cloth wipe - should come away clean."
    prevention: "Start with conservative parameters (70W, 800 mm/s) and increase gradually while monitoring surface. Test on scrap first."

# In {material}-laser-cleaning.yaml
laser_material_interaction:
  ablationThreshold:
    value: 1.2
    unit: J/cm²
    min: 0.8
    max: 1.8
    source: ai_research
```

---

## Priority Order
1. **CRITICAL**: Add ablationThreshold to materials YAML (needed for effectiveness heatmap)
2. **HIGH**: Add common_issues to settings YAML (completes DiagnosticCenter)
3. **MEDIUM**: Verify all thermal properties present in materials YAML
4. **LOW**: Enhance material_challenges descriptions if too generic
