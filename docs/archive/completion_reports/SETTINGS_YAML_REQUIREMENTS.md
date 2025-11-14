# Settings YAML Requirements for Full Component Functionality

## Overview
The settings pages use 4 interactive components that require specific material property data to function accurately. Without this data, components use generic defaults that may not reflect actual material behavior.

---

## Critical Material Properties Needed

### 1. Thermal Properties (for ThermalAccumulation component)
```yaml
# Location: Can be in settings file OR loaded via materialRef from materials file
thermal_properties:
  thermalDiffusivity:
    value: 0.12  # mm²/s for oak wood
    # Compare: aluminum = 97 mm²/s, steel = 4.2 mm²/s
    # Wood is 100-800x slower to dissipate heat
    
  thermalConductivity:
    value: 0.15  # W/m·K for oak
    # Critical for calculating heat spread in heatmaps
    
  thermalDestructionPoint:
    value: 523  # K (250°C) - when wood begins to char
    # Used to determine damage zones
```

### 2. Laser Damage Thresholds (for Safety & Effectiveness Heatmaps)
```yaml
laser_material_interaction:
  laserDamageThreshold:
    value: 3.5  # J/cm² for oak
    # Defines RED DANGER zones in MaterialSafetyHeatmap
    # Above this = substrate damage/charring
    
  ablationThreshold:
    value: 1.2  # J/cm² for oak
    # Defines cleaning effectiveness threshold
    # Below this = incomplete contamination removal
    
  thermalShockResistance:
    value: 150  # K for wood
    # Affects damage risk calculations
```

### 3. Parameter Criticality (for ParameterRelationships network)
```yaml
# Add to each parameter in machineSettings:
machineSettings:
  powerRange:
    criticality: high  # Options: critical, high, medium, low
    rationale: "Wood chars easily; precise power control prevents damage"
    material_interaction: 
      mechanism: "Photothermal ablation with rapid char formation"
      critical_parameter: "Energy density must stay below char threshold"
```

### 4. Material-Specific Challenges (for DiagnosticCenter)
```yaml
machineSettings:
  material_challenges:
    thermal_management:
      - challenge: "Charring and carbonization"
        severity: high
        impact: "Wood chars at 250°C, leaving black marks and structural damage"
        solutions:
          - "Use pulse mode with 2-5 second cooling between passes"
          - "Reduce power by 30-40% compared to metals"
          - "Increase scan speed to reduce dwell time"
        prevention: "Monitor surface for any discoloration; stop immediately if browning occurs"
    
    surface_characteristics:
      - challenge: "Grain direction sensitivity"
        severity: medium
        impact: "Laser absorption varies 20-40% depending on grain orientation"
        solutions:
          - "Scan parallel to grain for consistent results"
          - "Use crosshatch pattern (0° and 90°) for uniform cleaning"
        prevention: "Test on scrap piece to determine optimal scan direction"
    
    contamination_challenges:
      - challenge: "Varnish and coating removal"
        severity: medium
        impact: "Thick coatings require multiple passes and generate smoke"
        solutions:
          - "First pass: high power (80W) fast speed (1500mm/s) for bulk removal"
          - "Second pass: medium power (60W) slow speed (800mm/s) for residue"
          - "Use fume extraction to prevent redeposition"
  
  common_issues:
    - symptom: "Charring or burn marks on wood surface"
      causes:
        - "Power density too high (>3 J/cm²)"
        - "Pulse duration too long (>100ns for softwoods)"
        - "Insufficient cooling between passes"
        - "Too many passes in same location"
      solutions:
        - "Reduce power by 30-40%"
        - "Increase scan speed by 50%"
        - "Add 3-5 second cooling between passes"
        - "Limit to 2 passes maximum"
      verification: "Visual inspection under white light; wood should maintain natural color"
      prevention: "Always start with conservative parameters on test piece"
    
    - symptom: "Incomplete contamination removal from wood grain"
      causes:
        - "Energy density too low"
        - "Scan direction perpendicular to deep grain"
        - "Contaminant penetrated deep into porous structure"
      solutions:
        - "Increase power by 10-15%"
        - "Scan parallel to grain direction"
        - "Use 3 passes with crosshatch pattern (0°, 45°, 90°)"
        - "Reduce scan speed to 600mm/s for deeper penetration"
      verification: "Magnified inspection of grain valleys"
      prevention: "Pre-assess contamination depth; chemical pre-treatment for deep penetration"
    
    - symptom: "Fuzzy or raised wood fibers after cleaning"
      causes:
        - "Pulse energy breaking lignin bonds without removing fibers"
        - "Too many passes damaging surface structure"
        - "Moisture in wood expanding under laser heat"
      solutions:
        - "Light sanding with 320-grit sandpaper after cleaning"
        - "Reduce pass count to 1-2 maximum"
        - "Pre-dry wood to <10% moisture content"
      verification: "Smooth surface to touch, no raised grain"
      prevention: "Ensure wood is properly dried before laser processing"
```

---

## Research Priorities by Component Impact

### HIGH PRIORITY (Components fail or show wrong data):
1. **thermalDiffusivity** - ThermalAccumulation shows aluminum cooling rates instead of wood
2. **laserDamageThreshold** - Heatmaps show incorrect danger zones
3. **thermalDestructionPoint** - Safety calculations use wrong temperature limits

### MEDIUM PRIORITY (Components work but with generic data):
4. **material_challenges** - DiagnosticCenter shows metal-focused advice
5. **common_issues** - Troubleshooting doesn't address wood-specific problems
6. **ablationThreshold** - Effectiveness heatmap can't show optimal cleaning zones

### LOW PRIORITY (Nice visual enhancements):
7. **criticality levels** - ParameterRelationships uses default relationships
8. **rationale fields** - Missing explanatory context
9. **thermalShockResistance** - Minor factor in damage calculations

---

## Material-Specific Values to Research by Category

### METAL / Ferrous (Steel, Iron, Cast Iron)
```yaml
thermal_properties:
  thermalDiffusivity: 4.0-12.0  # mm²/s
  thermalConductivity: 15-80  # W/m·K
  thermalDestructionPoint: 1800-1900  # K (melting point)

laser_interaction:
  laserDamageThreshold: 8-15  # J/cm²
  ablationThreshold: 3-6  # J/cm²
  thermalShockResistance: 300  # K

key_challenges:
  - "Oxide layer reformation (rust returns within minutes)"
  - "High reflectivity of polished surfaces (70-90% at 1064nm)"
  - "Thermal distortion in thin sheets (<2mm)"
  - "Sparking and spatter during high-power cleaning"
```

### METAL / Non-Ferrous (Aluminum, Copper, Brass, Bronze)
```yaml
thermal_properties:
  thermalDiffusivity: 40-100  # mm²/s (aluminum highest at 97)
  thermalConductivity: 120-400  # W/m·K (copper highest)
  thermalDestructionPoint: 900-1400  # K (melting point)

laser_interaction:
  laserDamageThreshold: 5-12  # J/cm²
  ablationThreshold: 1.5-4  # J/cm²
  thermalShockResistance: 200-250  # K

key_challenges:
  - "Extremely high reflectivity (85-95% for polished aluminum/copper)"
  - "Rapid heat dissipation requires higher energy density"
  - "Native oxide reformation within seconds (especially aluminum)"
  - "Soft surfaces prone to melting at high fluence"
  - "Color change/discoloration from oxidation during processing"
```

### METAL / Precious (Gold, Silver, Platinum)
```yaml
thermal_properties:
  thermalDiffusivity: 120-175  # mm²/s (silver highest)
  thermalConductivity: 300-430  # W/m·K
  thermalDestructionPoint: 1200-2000  # K

laser_interaction:
  laserDamageThreshold: 8-20  # J/cm² (very high)
  ablationThreshold: 2-5  # J/cm²
  thermalShockResistance: 150-200  # K

key_challenges:
  - "Extreme reflectivity (>95% for polished surfaces)"
  - "High economic value requires zero-damage processing"
  - "Tarnish/sulfide layer removal without substrate damage"
  - "Very rapid heat dissipation"
  - "Surface finish critical for jewelry/optics applications"
```

### WOOD / Hardwood (Oak, Maple, Walnut, Mahogany)
```yaml
thermal_properties:
  thermalDiffusivity: 0.10-0.15  # mm²/s (800x slower than aluminum!)
  thermalConductivity: 0.15-0.20  # W/m·K
  thermalDestructionPoint: 523-573  # K (250-300°C charring point)

laser_interaction:
  laserDamageThreshold: 2-5  # J/cm² (low - chars easily)
  ablationThreshold: 0.8-1.5  # J/cm²
  thermalShockResistance: 150  # K

key_challenges:
  - "Charring and carbonization at low temperatures (250°C)"
  - "Grain direction affects absorption 20-40%"
  - "Porous structure traps contaminants deep"
  - "Moisture content affects processing (must be <10%)"
  - "Raised grain/fuzzing from broken lignin bonds"
  - "Smoke and fume generation"
  - "Varnish/finish removal without damaging wood"
```

### WOOD / Softwood (Pine, Cedar, Spruce, Fir)
```yaml
thermal_properties:
  thermalDiffusivity: 0.08-0.12  # mm²/s (even slower than hardwood)
  thermalConductivity: 0.10-0.15  # W/m·K
  thermalDestructionPoint: 500-550  # K (chars at lower temp than hardwood)

laser_interaction:
  laserDamageThreshold: 1.5-3  # J/cm² (more delicate than hardwood)
  ablationThreshold: 0.6-1.2  # J/cm²
  thermalShockResistance: 120  # K

key_challenges:
  - "Resinous species (pine) create sticky residue"
  - "Lower char threshold than hardwoods"
  - "More pronounced raised grain after cleaning"
  - "Lighter color shows discoloration more easily"
  - "Knots have different absorption than straight grain"
```

### PLASTIC / Thermoplastic (ABS, Polycarbonate, Acrylic, PVC)
```yaml
thermal_properties:
  thermalDiffusivity: 0.08-0.15  # mm²/s
  thermalConductivity: 0.15-0.25  # W/m·K
  thermalDestructionPoint: 400-500  # K (melting/decomposition)

laser_interaction:
  laserDamageThreshold: 1-3  # J/cm² (melts easily)
  ablationThreshold: 0.5-1.5  # J/cm²
  thermalShockResistance: 80-100  # K

key_challenges:
  - "Low melting point (150-250°C)"
  - "Thermal deformation and warping"
  - "Toxic fumes (especially PVC - releases HCl)"
  - "Surface melting vs. ablation balance"
  - "Color change from thermal degradation"
  - "Static electricity attracts debris"
```

### PLASTIC / Thermoset (Epoxy, Phenolic, Polyimide)
```yaml
thermal_properties:
  thermalDiffusivity: 0.10-0.20  # mm²/s
  thermalConductivity: 0.20-0.35  # W/m·K
  thermalDestructionPoint: 500-700  # K (decomposition, doesn't melt)

laser_interaction:
  laserDamageThreshold: 2-5  # J/cm² (more robust than thermoplastics)
  ablationThreshold: 1.0-2.5  # J/cm²
  thermalShockResistance: 150-200  # K

key_challenges:
  - "Decomposition rather than melting (chars/burns)"
  - "Carbon fiber reinforcement reflects laser"
  - "Epoxy resin removal from composites"
  - "Delamination risk in layered structures"
  - "Fume generation from decomposition"
```

### COMPOSITE / Carbon Fiber
```yaml
thermal_properties:
  thermalDiffusivity: 5-25  # mm²/s (anisotropic - varies by direction)
  thermalConductivity: 10-100  # W/m·K (direction dependent)
  thermalDestructionPoint: 600-800  # K (matrix decomposition)

laser_interaction:
  laserDamageThreshold: 3-8  # J/cm²
  ablationThreshold: 1.5-4  # J/cm²
  thermalShockResistance: 200  # K

key_challenges:
  - "Anisotropic properties (fiber direction matters)"
  - "Matrix removal without fiber damage"
  - "Carbon fiber reflects IR wavelengths"
  - "Delamination between layers"
  - "Epoxy outgassing during heating"
  - "High economic value (aerospace parts)"
```

### COMPOSITE / Fiberglass
```yaml
thermal_properties:
  thermalDiffusivity: 0.15-0.30  # mm²/s
  thermalConductivity: 0.30-0.50  # W/m·K
  thermalDestructionPoint: 550-650  # K (resin decomposition)

laser_interaction:
  laserDamageThreshold: 2-5  # J/cm²
  ablationThreshold: 1.0-2.5  # J/cm²
  thermalShockResistance: 150  # K

key_challenges:
  - "Glass fibers highly reflective"
  - "Resin removal without glass fiber damage"
  - "Layered structure prone to delamination"
  - "Gel coat vs. structural laminate cleaning"
  - "Marine applications (salt, growth, paint removal)"
```

### STONE / Natural Stone (Granite, Marble, Limestone)
```yaml
thermal_properties:
  thermalDiffusivity: 0.8-2.0  # mm²/s
  thermalConductivity: 2-4  # W/m·K
  thermalDestructionPoint: 1100-1800  # K (calcination for limestone)

laser_interaction:
  laserDamageThreshold: 10-25  # J/cm² (very robust)
  ablationThreshold: 4-10  # J/cm²
  thermalShockResistance: 300-500  # K

key_challenges:
  - "Thermal shock cracking (especially marble)"
  - "Calcination of limestone/marble (CaCO₃ → CaO)"
  - "Natural color variation affects absorption"
  - "Porous stone absorbs contaminants deep"
  - "Historical preservation requires zero damage"
  - "Salt efflorescence (white deposits) on outdoor stone"
```

### STONE / Engineered Stone (Concrete, Terrazzo, Quartz Composite)
```yaml
thermal_properties:
  thermalDiffusivity: 0.5-1.2  # mm²/s
  thermalConductivity: 1.0-2.5  # W/m·K
  thermalDestructionPoint: 800-1200  # K (cement decomposition)

laser_interaction:
  laserDamageThreshold: 8-20  # J/cm²
  ablationThreshold: 3-8  # J/cm²
  thermalShockResistance: 250-400  # K

key_challenges:
  - "Aggregate (rocks/glass) vs. binder (cement/resin) different absorption"
  - "Rebar/wire mesh reflects laser in concrete"
  - "Spalling (explosive surface fracture) from trapped moisture"
  - "Graffiti removal without color change"
  - "Efflorescence (salt deposits) on concrete"
```

### CERAMIC / Traditional Ceramic (Porcelain, Terracotta, Clay)
```yaml
thermal_properties:
  thermalDiffusivity: 0.5-1.5  # mm²/s
  thermalConductivity: 1-3  # W/m·K
  thermalDestructionPoint: 1200-1800  # K (already fired, very stable)

laser_interaction:
  laserDamageThreshold: 15-30  # J/cm² (very high)
  ablationThreshold: 5-12  # J/cm²
  thermalShockResistance: 200-400  # K (varies - porcelain high, terracotta low)

key_challenges:
  - "Thermal shock cracking (especially low-fire ceramics)"
  - "Glaze vs. body different absorption"
  - "Historical artifacts require zero damage"
  - "Color change from temperature"
  - "Porous unglazed surface traps contaminants"
```

### CERAMIC / Advanced Ceramic (Alumina, Zirconia, Silicon Carbide)
```yaml
thermal_properties:
  thermalDiffusivity: 5-20  # mm²/s (much higher than traditional)
  thermalConductivity: 20-120  # W/m·K (SiC very high)
  thermalDestructionPoint: 2300-3100  # K (extremely high)

laser_interaction:
  laserDamageThreshold: 25-50  # J/cm² (extremely robust)
  ablationThreshold: 10-20  # J/cm²
  thermalShockResistance: 500-800  # K

key_challenges:
  - "Very high reflectivity (especially polished)"
  - "Extremely hard - difficult to ablate"
  - "High economic value (precision components)"
  - "Microcracking from thermal shock"
  - "Coating removal (TiN, DLC) without substrate damage"
```

### GLASS / Standard Glass (Soda-Lime, Borosilicate)
```yaml
thermal_properties:
  thermalDiffusivity: 0.4-0.6  # mm²/s
  thermalConductivity: 0.8-1.2  # W/m·K
  thermalDestructionPoint: 800-1200  # K (softening point)

laser_interaction:
  laserDamageThreshold: 5-15  # J/cm² (thermal shock is main risk)
  ablationThreshold: 2-6  # J/cm²
  thermalShockResistance: 50-150  # K (borosilicate much better)

key_challenges:
  - "Thermal shock cracking (soda-lime very sensitive)"
  - "Transparent to IR wavelengths (poor absorption at 1064nm)"
  - "Surface coatings (AR, mirrors) have different thresholds"
  - "Contamination embedded in surface (not just on surface)"
  - "Optical quality required after cleaning"
```

### GLASS / Specialty Glass (Quartz, Sapphire, Optical Glass)
```yaml
thermal_properties:
  thermalDiffusivity: 0.8-12.0  # mm²/s (sapphire very high)
  thermalConductivity: 1.5-35  # W/m·K (sapphire 35, quartz 1.5)
  thermalDestructionPoint: 1900-2300  # K

laser_interaction:
  laserDamageThreshold: 20-80  # J/cm² (very high, especially sapphire)
  ablationThreshold: 8-30  # J/cm²
  thermalShockResistance: 800-1200  # K (quartz excellent)

key_challenges:
  - "Extreme surface quality requirements (optical applications)"
  - "Sub-surface damage detection critical"
  - "Coating damage vs. substrate damage"
  - "Extremely high economic value"
  - "UV wavelengths often required for absorption"
```

### RUBBER / Natural & Synthetic (EPDM, Neoprene, Silicone)
```yaml
thermal_properties:
  thermalDiffusivity: 0.08-0.15  # mm²/s
  thermalConductivity: 0.13-0.20  # W/m·K
  thermalDestructionPoint: 450-600  # K (decomposition)

laser_interaction:
  laserDamageThreshold: 1-4  # J/cm² (burns/melts easily)
  ablationThreshold: 0.5-2  # J/cm²
  thermalShockResistance: 100-150  # K

key_challenges:
  - "Melting vs. clean ablation difficult to control"
  - "Toxic fumes from thermal decomposition"
  - "Surface tackiness after heating"
  - "Vulcanization changes affect absorption"
  - "Carbon black filler increases absorption (black rubber)"
  - "Mold release agents and oils on surface"
```

### TEXTILE / Natural Fiber (Cotton, Wool, Leather)
```yaml
thermal_properties:
  thermalDiffusivity: 0.05-0.10  # mm²/s (very low)
  thermalConductivity: 0.05-0.10  # W/m·K
  thermalDestructionPoint: 500-550  # K (charring/burning)

laser_interaction:
  laserDamageThreshold: 1-3  # J/cm² (very delicate)
  ablationThreshold: 0.3-1.0  # J/cm²
  thermalShockResistance: 80-120  # K

key_challenges:
  - "Extreme burn/char risk (especially cotton)"
  - "Porous structure requires careful parameter control"
  - "Color fading from heat exposure"
  - "Leather shrinkage from heat"
  - "Organic dyes and finishes affected by temperature"
  - "Historical textiles require zero damage"
```

### TEXTILE / Synthetic Fiber (Polyester, Nylon, Aramid)
```yaml
thermal_properties:
  thermalDiffusivity: 0.08-0.12  # mm²/s
  thermalConductivity: 0.10-0.20  # W/m·K
  thermalDestructionPoint: 500-650  # K (aramids highest)

laser_interaction:
  laserDamageThreshold: 2-5  # J/cm² (aramids more robust)
  ablationThreshold: 0.8-2.5  # J/cm²
  thermalShockResistance: 120-200  # K

key_challenges:
  - "Melting vs. burning (depends on fiber type)"
  - "Synthetic fibers melt and fuse"
  - "Color change from heat exposure"
  - "Protective coatings (water repellent, flame retardant)"
  - "Industrial applications require fiber strength preservation"
```

---

## Implementation Notes

1. **Data can live in two places:**
   - Directly in settings YAML under `machineSettings`
   - In materials YAML, linked via `materialRef: materials/category/subcategory/material-slug`

2. **Fallback behavior:**
   - Components currently use generic defaults if data missing
   - ThermalAccumulation defaults to aluminum (97 mm²/s) - **WRONG** for most materials!
   - Heatmaps use generic thresholds
   - DiagnosticCenter generates basic metal-focused advice

3. **Priority order for Python generator:**
   - **Phase 1**: Add thermal properties (biggest accuracy impact)
     - thermalDiffusivity (critical for ThermalAccumulation)
     - thermalConductivity (affects heatmap calculations)
     - thermalDestructionPoint (defines damage zones)
   
   - **Phase 2**: Add damage thresholds (safety critical)
     - laserDamageThreshold (red zones in safety heatmap)
     - ablationThreshold (effectiveness zones)
     - thermalShockResistance (damage risk modifier)
   
   - **Phase 3**: Add material-specific challenges (user experience)
     - thermal_management challenges
     - surface_characteristics challenges
     - contamination_challenges
     - common_issues with material-specific solutions
   
   - **Phase 4**: Add parameter criticality (visual enhancement)
     - criticality levels for each parameter
     - rationale explaining material interaction
     - material_interaction mechanisms

4. **Category-specific priorities:**
   
   **METALS** (Ferrous, Non-Ferrous, Precious):
   - HIGH: Reflectivity values (affects laser coupling)
   - HIGH: Oxide reformation rates
   - MEDIUM: Thermal distortion thresholds
   
   **WOOD** (Hardwood, Softwood):
   - CRITICAL: Char temperature (250-300°C vs 660°C for aluminum!)
   - HIGH: Grain direction effects
   - HIGH: Moisture content impact
   
   **PLASTICS** (Thermoplastic, Thermoset):
   - CRITICAL: Melting point (150-250°C for most)
   - HIGH: Toxic fume warnings (especially PVC, polycarbonate)
   - MEDIUM: Static electricity considerations
   
   **COMPOSITES** (Carbon Fiber, Fiberglass):
   - HIGH: Anisotropic properties (direction matters)
   - HIGH: Matrix vs. fiber damage thresholds
   - MEDIUM: Delamination risk
   
   **STONE** (Natural, Engineered):
   - HIGH: Thermal shock sensitivity (marble!)
   - HIGH: Calcination temperature (limestone/marble)
   - MEDIUM: Moisture-related spalling (concrete)
   
   **CERAMIC** (Traditional, Advanced):
   - HIGH: Thermal shock thresholds
   - HIGH: Glaze vs. body different properties
   - MEDIUM: Microcracking detection
   
   **GLASS** (Standard, Specialty):
   - CRITICAL: Thermal shock sensitivity (soda-lime cracks easily)
   - HIGH: IR transparency (poor absorption at 1064nm)
   - HIGH: Optical quality requirements
   
   **RUBBER**:
   - HIGH: Toxic fume warnings
   - HIGH: Melting vs. ablation control
   - MEDIUM: Carbon black absorption effects
   
   **TEXTILES**:
   - CRITICAL: Extreme burn risk (cotton chars at 230°C)
   - HIGH: Color fading thresholds
   - HIGH: Fiber strength preservation

5. **Quick reference for thermal diffusivity ranges:**
   ```
   Precious metals:    120-175 mm²/s  ████████████████████
   Non-ferrous metals:  40-100 mm²/s  ██████████
   Advanced ceramics:    5-20 mm²/s   ███
   Ferrous metals:       4-12 mm²/s   ██
   Stone:                0.8-2 mm²/s  █
   Glass:                0.4-0.6 mm²/s ▌
   Plastics:             0.08-0.2 mm²/s ▎
   Wood:                 0.08-0.15 mm²/s ▎
   Textiles:             0.05-0.10 mm²/s ▏
   ```
   This 3000x range shows why material-specific data is critical!
