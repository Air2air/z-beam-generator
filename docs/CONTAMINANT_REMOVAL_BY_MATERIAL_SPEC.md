# Contaminant Removal by Material Specification

**Version**: 1.0.0  
**Date**: December 20, 2025  
**Status**: Ready for Implementation  
**Target**: Contaminant Frontmatter Generator  
**Priority**: High - Critical user value gap

---

## 🎯 **Objective**

Add `removal_by_material` data to all 98 contaminant frontmatter files, providing material-specific laser removal parameters, efficiency metrics, and safety guidance for each contaminant-material combination.

## 📊 **Current State**

**Problem**: Contaminants frontmatter only has:
- ✅ Visual identification (11 material categories)
- ✅ Safety data (PPE, ventilation, fumes)
- ❌ **NO removal parameters** for specific materials
- ❌ **NO material compatibility** guidance
- ❌ **NO success indicators** for removal

**Impact**: Users can't answer: *"How do I remove [contaminant] from [material]?"*

**Gap Grade**: F (0/98 contaminants have removal guidance)

---

## 🏗️ **Data Structure**

### Top-Level Addition

Add new `removal_by_material` field to contaminant frontmatter:

```yaml
# frontmatter/contaminants/{contaminant-name}.yaml

removal_by_material:
  aluminum_bronze:
    laser_parameters:
      wavelength:
        value: 1064
        unit: nm
        range: [1050, 1080]
        recommended: 1064
      power:
        value: 80
        unit: W
        range: [60, 100]
        recommended: 80
      scan_speed:
        value: 400
        unit: mm/s
        range: [300, 500]
        recommended: 400
      pulse_width:
        value: 10
        unit: ns
        range: [8, 15]
      repetition_rate:
        value: 50
        unit: kHz
        range: [30, 80]
      energy_density:
        value: 2.5
        unit: J/cm²
        range: [1.5, 3.5]
      spot_size:
        value: 50
        unit: μm
        range: [30, 100]
      pass_count:
        value: 2
        range: [1, 4]
      overlap_ratio:
        value: 50
        unit: '%'
        range: [30, 70]
    
    removal_characteristics:
      primary_mechanism: thermal_ablation  # or photochemical, mechanical_stress, vaporization
      secondary_mechanisms:
        - photochemical
        - plasma_formation
      removal_efficiency:
        single_pass: 0.75  # 0.0-1.0 (75% removal per pass)
        optimal_passes: 2
        diminishing_returns_after: 4
        typical_time_per_cm2: 3.5  # seconds
      surface_quality_after_removal:
        roughness_change: minimal  # minimal, slight, moderate, significant
        discoloration_risk: low  # low, moderate, high
        substrate_damage_risk: low  # low, moderate, high
        residual_contamination: none  # none, trace, moderate
    
    compatibility:
      recommended: true  # Can this contaminant be effectively removed from this material?
      success_rate: 0.92  # 0.0-1.0 (92% success rate)
      difficulty: moderate  # easy, moderate, difficult, extreme
      substrate_warnings:
        - Monitor for heat accumulation on thin sections
        - May require protective cooling for substrates <2mm thick
      process_limitations:
        - Not effective on heavily oxidized substrates
        - Requires pre-cleaning if organic oils present
    
    safety_considerations:
      material_specific_hazards:
        - Copper vapor release at high power (>100W)
        - Beryllium alloy requires enhanced PPE
      recommended_ppe:
        respiratory: P100  # Upgrade from base contaminant PPE if needed
        eye_protection: OD7+ at 1064nm
        skin_protection: heat_resistant_gloves
      ventilation_requirements:
        minimum_air_changes_per_hour: 12  # May differ from base contaminant
        extraction_velocity_m_s: 0.6
        filtration_notes: HEPA + activated carbon for metal vapors
      fume_warnings:
        - Increased particulate generation on porous substrates
        - Metal oxide fumes require monitoring
    
    optimization_tips:
      - Start at lower power (60W) and increase gradually
      - Use multiple passes rather than single high-energy pass
      - Allow 2-3 seconds between passes for cooling
      - Check surface temperature with IR thermometer
    
    success_indicators:
      visual:
        - Restored base metal luster
        - Uniform surface appearance
        - No visible residue
      measurement:
        - Surface reflectance >85% of clean baseline
        - Roughness Ra <2.0 μm increase
        - No detectable contamination via XRF/EDS
      failure_signs:
        - Discoloration (overheating)
        - Surface pitting (excessive energy)
        - Incomplete removal (insufficient energy)
  
  stainless_steel_304:
    # Same structure repeated for each material
    laser_parameters: {...}
    removal_characteristics: {...}
    compatibility: {...}
    safety_considerations: {...}
    optimization_tips: [...]
    success_indicators: {...}
```

---

## 📋 **Field Definitions**

### `laser_parameters` (REQUIRED)

Core laser settings for removal from this specific material.

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `wavelength` | object | YES | Laser wavelength (355, 532, 1064, 10640 nm typical) |
| `power` | object | YES | Average laser power in Watts |
| `scan_speed` | object | YES | Beam travel speed in mm/s |
| `pulse_width` | object | YES | Pulse duration in ns (nanoseconds) |
| `repetition_rate` | object | YES | Pulse frequency in kHz |
| `energy_density` | object | YES | Fluence in J/cm² |
| `spot_size` | object | YES | Beam diameter in μm |
| `pass_count` | object | YES | Recommended number of cleaning passes |
| `overlap_ratio` | object | YES | Beam overlap percentage |

Each parameter object contains:
```yaml
value: 1064        # Recommended value
unit: nm           # Unit of measurement
range: [1050, 1080]  # Min/max acceptable range
```

### `removal_characteristics` (REQUIRED)

Performance metrics and removal behavior.

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `primary_mechanism` | string | YES | thermal_ablation, photochemical, mechanical_stress, vaporization |
| `secondary_mechanisms` | array | NO | Additional removal mechanisms |
| `removal_efficiency` | object | YES | Per-pass efficiency, optimal passes, timing |
| `surface_quality_after_removal` | object | YES | Roughness, discoloration, damage, residue |

### `compatibility` (REQUIRED)

Material-contaminant compatibility assessment.

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `recommended` | boolean | YES | Can this contaminant be effectively removed? |
| `success_rate` | float | YES | 0.0-1.0 (e.g., 0.92 = 92% success) |
| `difficulty` | string | YES | easy, moderate, difficult, extreme |
| `substrate_warnings` | array | NO | Material-specific cautions |
| `process_limitations` | array | NO | Known limitations or prerequisites |

### `safety_considerations` (REQUIRED)

Material-specific safety requirements (adds to base contaminant safety).

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `material_specific_hazards` | array | YES | Hazards unique to this material-contaminant combo |
| `recommended_ppe` | object | NO | PPE upgrades from base requirements |
| `ventilation_requirements` | object | NO | Enhanced ventilation if needed |
| `fume_warnings` | array | NO | Material-specific fume considerations |

### `optimization_tips` (RECOMMENDED)

Array of practical guidance strings for best results.

### `success_indicators` (REQUIRED)

How to verify successful removal.

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `visual` | array | YES | Visual inspection criteria |
| `measurement` | array | NO | Quantitative verification methods |
| `failure_signs` | array | YES | Signs of unsuccessful removal |

---

## 🎯 **Material Coverage Requirements**

### Priority Tier 1: Common Industrial Materials (20 materials)
**Must include for ALL 98 contaminants:**

**Metals:**
- Aluminum (6061-T6 alloy typical)
- Stainless Steel (304, 316)
- Carbon Steel (1018, 1045)
- Copper
- Brass
- Titanium (Grade 5)
- Bronze (Aluminum Bronze)

**Non-Metals:**
- Concrete
- Stone (Granite, Marble, Limestone)
- Glass (Borosilicate, Soda-lime)
- Wood (Pine, Oak, Maple)
- Plastic (ABS, Acrylic, Polycarbonate)
- Rubber (EPDM, Nitrile)
- Ceramic (Alumina)

### Priority Tier 2: Specialized Materials (30 materials)
**Include where applicable (60%+ of contaminants):**

- Alloy steels (Tool steel, High-speed steel)
- Non-ferrous alloys (Inconel, Hastelloy, Monel)
- Composites (Carbon fiber, Fiberglass)
- Specialty ceramics (Silicon carbide, Silicon nitride)
- Semiconductor materials (Silicon, GaAs)
- Rare earth materials

### Priority Tier 3: Niche Materials (50+ materials)
**Include where specifically relevant:**

- Exotic alloys
- Specialty coatings
- Advanced composites
- Custom formulations

### Incompatible Materials

If a material CANNOT effectively clean a contaminant, include entry with:
```yaml
removal_by_material:
  polystyrene:
    compatibility:
      recommended: false
      success_rate: 0.0
      difficulty: impossible
      substrate_warnings:
        - Laser energy causes substrate melting before contaminant removal
        - Not recommended - use chemical or mechanical methods instead
    laser_parameters: null
    removal_characteristics: null
```

---

## 🔧 **Generation Strategy**

### Phase 1: Foundation Data (Week 1)
1. Create base parameter sets for 20 Tier 1 materials × 98 contaminants = **1,960 entries**
2. Use intelligent defaults based on:
   - Material properties (thermal, optical, mechanical)
   - Contaminant properties (composition, bonding strength)
   - Existing settings frontmatter data
   - Literature/standards (ANSI Z136, IEC 60825)

### Phase 2: Refinement (Week 2)
3. Add Tier 2 materials (30 materials × 60 relevant contaminants = **1,800 entries**)
4. Validate against known successful combinations
5. Flag uncertain combinations for expert review

### Phase 3: Specialization (Week 3)
6. Add Tier 3 materials where specifically relevant (**~500 entries**)
7. Mark incompatible material-contaminant pairs
8. Add optimization tips and success indicators

### Phase 4: Validation (Week 4)
9. Cross-reference with settings frontmatter machine_settings
10. Ensure wavelength/power ranges are consistent
11. Validate safety escalations make sense
12. Expert review of high-risk combinations

**Total Entries**: ~4,000-5,000 material-contaminant combinations

---

## 🧮 **Data Generation Logic**

### Step 1: Base Parameter Calculation

For each material-contaminant pair:

1. **Load material properties** from materials frontmatter:
   - Thermal conductivity, melting point, reflectivity
   - Absorption coefficient at common wavelengths
   
2. **Load contaminant properties**:
   - Composition, bonding type, thickness range
   - Decomposition/ablation threshold
   
3. **Calculate base parameters**:
   ```python
   # Wavelength selection
   if material.category == "metal":
       wavelength = 1064  # Near-IR for metals
   elif material.high_absorption_UV:
       wavelength = 355   # UV for organics/polymers
   else:
       wavelength = 532   # Visible green
   
   # Power calculation
   ablation_threshold = contaminant.ablation_threshold_j_cm2
   safety_margin = 1.3  # 30% above threshold
   energy_density = ablation_threshold * safety_margin
   
   # Spot size from material
   spot_size = material.typical_spot_size_um
   
   # Calculate power
   power = (energy_density * spot_size^2 * repetition_rate) / 1000
   
   # Scan speed based on material thermal properties
   thermal_diffusivity = material.thermal_diffusivity_mm2_s
   scan_speed = min(thermal_diffusivity * 10, 1000)  # Cap at 1000 mm/s
   ```

4. **Set ranges** (±20-30% from base value)

### Step 2: Removal Efficiency Estimation

```python
# Single-pass efficiency based on bonding strength
bonding_strength = contaminant.adhesion_strength_mpa
if bonding_strength < 5:
    single_pass_efficiency = 0.85  # Weak bond
elif bonding_strength < 15:
    single_pass_efficiency = 0.70  # Moderate bond
else:
    single_pass_efficiency = 0.55  # Strong bond

# Optimal passes
optimal_passes = math.ceil(1 / single_pass_efficiency)
```

### Step 3: Compatibility Assessment

```python
# Check if combination is feasible
substrate_damage_temp = material.degradation_temperature_c
contaminant_removal_temp = contaminant.ablation_temperature_c

if contaminant_removal_temp > substrate_damage_temp:
    recommended = False
    difficulty = "impossible"
    success_rate = 0.0
elif material.category == "plastic" and contaminant.requires_high_energy:
    recommended = False
    difficulty = "extreme"
    success_rate = 0.2
else:
    recommended = True
    difficulty = calculate_difficulty(...)
    success_rate = estimate_success_rate(...)
```

### Step 4: Safety Escalation

```python
# Inherit base contaminant safety, escalate if needed
if material.generates_toxic_fumes:
    ppe.respiratory = "PAPR"  # Upgrade from P100
    ventilation.ach += 5      # Add 5 ACH

if material.thermal_conductivity < 50:  # Poor conductor
    substrate_warnings.append("Risk of heat accumulation - use pulsed approach")
```

---

## ✅ **Validation Rules**

### Required Field Validation

```yaml
# Every material entry MUST have:
- laser_parameters (all 9 sub-fields)
- removal_characteristics.removal_efficiency
- removal_characteristics.surface_quality_after_removal
- compatibility.recommended
- compatibility.success_rate
- compatibility.difficulty
- safety_considerations.material_specific_hazards
- success_indicators.visual
- success_indicators.failure_signs
```

### Value Range Validation

```yaml
# Laser parameters must be physically realistic:
wavelength: [355, 532, 1064, 10640]  # Common laser wavelengths
power: [1, 500]  # 1W to 500W
scan_speed: [10, 5000]  # mm/s
pulse_width: [0.1, 1000]  # nanoseconds
repetition_rate: [1, 500]  # kHz
energy_density: [0.1, 50]  # J/cm²
spot_size: [10, 500]  # μm
pass_count: [1, 10]
overlap_ratio: [0, 90]  # %

# Success rate must be realistic:
success_rate: [0.0, 1.0]  # 0-100%
single_pass_efficiency: [0.0, 1.0]
```

### Consistency Validation

```yaml
# Cross-field validation:
- If recommended == false, success_rate should be < 0.3
- If difficulty == "impossible", recommended should be false
- If single_pass_efficiency > 0.9, optimal_passes should be 1
- wavelength must match material absorption characteristics
- power must be sufficient for energy_density at given spot_size
```

---

## 📊 **Example: Complete Entry**

```yaml
# frontmatter/contaminants/rust-scale-contamination.yaml

removal_by_material:
  stainless_steel_304:
    laser_parameters:
      wavelength: {value: 1064, unit: nm, range: [1050, 1080]}
      power: {value: 100, unit: W, range: [80, 150]}
      scan_speed: {value: 500, unit: mm/s, range: [300, 800]}
      pulse_width: {value: 10, unit: ns, range: [8, 20]}
      repetition_rate: {value: 50, unit: kHz, range: [30, 100]}
      energy_density: {value: 3.0, unit: J/cm², range: [2.0, 4.5]}
      spot_size: {value: 50, unit: μm, range: [30, 100]}
      pass_count: {value: 2, range: [1, 3]}
      overlap_ratio: {value: 50, unit: '%', range: [30, 70]}
    
    removal_characteristics:
      primary_mechanism: thermal_ablation
      secondary_mechanisms: [photochemical, plasma_formation]
      removal_efficiency:
        single_pass: 0.80
        optimal_passes: 2
        diminishing_returns_after: 4
        typical_time_per_cm2: 2.8
      surface_quality_after_removal:
        roughness_change: minimal
        discoloration_risk: low
        substrate_damage_risk: low
        residual_contamination: none
    
    compatibility:
      recommended: true
      success_rate: 0.95
      difficulty: easy
      substrate_warnings:
        - Passivation layer may be affected - may require re-passivation
      process_limitations:
        - Heavy scale (>1mm) may require mechanical pre-removal
    
    safety_considerations:
      material_specific_hazards:
        - Iron oxide particulates in fume stream
        - Chromium oxide at high power (monitor Cr(VI))
      recommended_ppe:
        respiratory: P100
        eye_protection: OD7+ at 1064nm
      ventilation_requirements:
        minimum_air_changes_per_hour: 12
        extraction_velocity_m_s: 0.6
        filtration_notes: HEPA required for metal oxide particulates
      fume_warnings:
        - Monitor for hexavalent chromium with Cr(VI) detector
        - Higher particulate generation than on carbon steel
    
    optimization_tips:
      - Use overlapping passes for uniform removal
      - Allow substrate to cool between passes (3-5 seconds)
      - Check passivation layer integrity post-cleaning
      - Consider citric acid passivation after laser cleaning
    
    success_indicators:
      visual:
        - Restored satin finish (not mirror-polished)
        - Uniform gray appearance
        - No rust discoloration
      measurement:
        - Surface roughness Ra <1.5 μm increase
        - Passivation test shows protective layer intact
        - XRF shows no residual iron oxide peaks
      failure_signs:
        - Yellow/brown discoloration (incomplete removal)
        - Rainbow tinting (overheating, passivation damage)
        - Pitting or surface roughness >3 μm Ra
  
  aluminum_6061:
    laser_parameters:
      wavelength: {value: 1064, unit: nm, range: [1050, 1080]}
      power: {value: 60, unit: W, range: [40, 100]}
      scan_speed: {value: 800, unit: mm/s, range: [500, 1200]}
      pulse_width: {value: 15, unit: ns, range: [10, 25]}
      repetition_rate: {value: 60, unit: kHz, range: [40, 100]}
      energy_density: {value: 1.8, unit: J/cm², range: [1.2, 2.8]}
      spot_size: {value: 60, unit: μm, range: [40, 100]}
      pass_count: {value: 1, range: [1, 2]}
      overlap_ratio: {value: 40, unit: '%', range: [20, 60]}
    
    removal_characteristics:
      primary_mechanism: thermal_ablation
      secondary_mechanisms: [photochemical]
      removal_efficiency:
        single_pass: 0.90
        optimal_passes: 1
        diminishing_returns_after: 2
        typical_time_per_cm2: 1.8
      surface_quality_after_removal:
        roughness_change: minimal
        discoloration_risk: moderate
        substrate_damage_risk: moderate
        residual_contamination: trace
    
    compatibility:
      recommended: true
      success_rate: 0.85
      difficulty: moderate
      substrate_warnings:
        - High thermal conductivity requires careful power management
        - Anodized coating (if present) will be removed with rust
        - May expose bare aluminum requiring re-anodizing
      process_limitations:
        - Not effective on heavily pitted surfaces
        - Substrate must be >2mm thick to avoid warping
    
    safety_considerations:
      material_specific_hazards:
        - Aluminum oxide particulates (less hazardous than iron oxide)
        - Risk of substrate reflectivity increasing mid-process
      recommended_ppe:
        respiratory: N95
        eye_protection: OD6+ at 1064nm
      ventilation_requirements:
        minimum_air_changes_per_hour: 8
        extraction_velocity_m_s: 0.5
      fume_warnings:
        - Lower particulate generation than on ferrous metals
    
    optimization_tips:
      - Use lower power than for steel (aluminum more reflective)
      - Single fast pass preferred over multiple slow passes
      - Monitor for surface oxidation post-cleaning
      - Consider protective coating application after cleaning
    
    success_indicators:
      visual:
        - Bright metallic aluminum finish
        - No rust discoloration
        - Uniform surface appearance
      measurement:
        - Surface reflectance >75% at 1064nm
        - No iron detected via XRF
        - Roughness Ra <1.0 μm increase
      failure_signs:
        - Gray discoloration (overheating, oxide formation)
        - Surface melting or deformation
        - Incomplete rust removal in pitted areas
```

---

## 🚀 **Implementation Checklist**

### Generator Requirements

- [ ] Load existing materials frontmatter (160 files)
- [ ] Load existing contaminants frontmatter (98 files)
- [ ] Load existing settings frontmatter (153 files) for reference
- [ ] Parse material properties (thermal, optical, mechanical)
- [ ] Implement parameter calculation logic
- [ ] Implement compatibility assessment logic
- [ ] Implement safety escalation logic
- [ ] Generate 20 Tier 1 materials per contaminant (1,960 entries)
- [ ] Validate all generated entries against schema
- [ ] Flag uncertain combinations for review
- [ ] Write updated frontmatter files
- [ ] Generate validation report

### Post-Generation

- [ ] Run frontmatter validation tests
- [ ] Verify JSON Schema compliance
- [ ] Check parameter range consistency
- [ ] Expert review of high-risk combinations (toxic, explosive)
- [ ] Update contaminant datasets (public/datasets/contaminants/)
- [ ] Regenerate dataset architecture tests
- [ ] Update documentation

---

## 📖 **References**

### Data Sources
1. Existing settings frontmatter (`frontmatter/settings/*.yaml`)
2. Materials frontmatter (`frontmatter/materials/*.yaml`)
3. ANSI Z136.1 - Safe Use of Lasers
4. Laser cleaning literature (Lu, Veiko, et al.)
5. Materials science databases (MatWeb, ASM)

### Related Specifications
- `DATASET_CONSOLIDATION_SPEC.md` - Dataset architecture
- `schemas/dataset-contaminant.json` - Contaminant dataset schema
- `DATA_STORAGE_POLICY.md` - Data architecture policy

---

## ✅ **Success Metrics**

### Coverage
- ✅ 98/98 contaminants have `removal_by_material` field
- ✅ 20+ materials per contaminant (Tier 1 complete)
- ✅ 1,960+ material-contaminant combinations generated

### Quality
- ✅ 100% of entries pass schema validation
- ✅ 95%+ of parameter ranges are physically realistic
- ✅ 90%+ of entries have complete field coverage
- ✅ 0 incompatible combinations marked as `recommended: true`

### User Value
- ✅ Users can find removal guidance for common material-contaminant pairs
- ✅ Parameters are actionable (not encyclopedic ranges)
- ✅ Safety escalations are appropriate
- ✅ Success indicators are measurable

---

## 🎯 **Priority: HIGH**

**Rationale**: This data closes the critical user value gap identified in the dataset satisfaction assessment. Without this, contaminant datasets answer "what is this?" but not "how do I remove it?" - which is the primary user need.

**Timeline**: 4 weeks to complete all phases  
**Effort**: ~80 hours generator development + validation  
**Impact**: Upgrades contaminant datasets from Grade F (useless) to Grade A (actionable)
