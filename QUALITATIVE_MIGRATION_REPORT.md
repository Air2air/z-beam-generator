# Qualitative Properties Migration Report

**Date**: 2025-10-17 11:29:41


============================================================
QUALITATIVE PROPERTIES MIGRATION REPORT
============================================================

📊 Materials Migrated: 2

Materials updated:
  • Cast Iron
  • Tool Steel

📋 Properties Migrated: 2

Properties moved to materialCharacteristics:
  • thermalDestructionType → thermal_behavior
  • toxicity → safety_handling

============================================================

## Qualitative Properties Defined

- **thermalDestructionType** (thermal_behavior): Primary mechanism by which material thermally degrades under laser energy
  - Allowed values: melting, decomposition, sublimation, vaporization, oxidation, charring, pyrolysis
- **thermalStability** (thermal_behavior): Overall thermal stability classification
  - Allowed values: poor, fair, good, excellent
- **heatTreatmentResponse** (thermal_behavior): Material response to heat treatment processes
  - Allowed values: hardenable, non-hardenable, age-hardenable, precipitation-hardenable
- **toxicity** (safety_handling): Toxicity level for safety and handling considerations
  - Allowed values: None, Low, Medium, High, Extreme
- **flammability** (safety_handling): Flammability classification
  - Allowed values: non-flammable, low, moderate, high, extremely-flammable
- **reactivity** (safety_handling): Chemical reactivity classification
  - Allowed values: stable, low, moderate, high, explosive
- **corrosivityLevel** (safety_handling): Corrosivity level for handling and storage
  - Allowed values: non-corrosive, mildly-corrosive, corrosive, highly-corrosive
- **color** (physical_appearance): Primary visual color of material in natural state
  - Allowed values: silver, gray, black, bronze, copper, gold, white, red, blue, green, yellow, brown, purple, orange
- **surfaceFinish** (physical_appearance): Surface finish characteristic
  - Allowed values: polished, brushed, matte, rough, oxidized, textured, smooth
- **transparency** (physical_appearance): Light transmission characteristic
  - Allowed values: opaque, translucent, transparent, semi-transparent
- **luster** (physical_appearance): Surface luster or shine characteristic
  - Allowed values: metallic, vitreous, resinous, pearly, silky, greasy, dull
- **crystalStructure** (material_classification): Crystal lattice structure type
  - Allowed values: FCC, BCC, HCP, amorphous, cubic, hexagonal, tetragonal, orthorhombic, monoclinic, triclinic
- **microstructure** (material_classification): Microscopic structural organization
  - Allowed values: single-phase, multi-phase, composite, layered, cellular, porous
- **processingMethod** (material_classification): Primary manufacturing or processing method
  - Allowed values: cast, forged, machined, sintered, additive, extruded, rolled, stamped, molded
- **grainSize** (material_classification): Grain size classification
  - Allowed values: ultrafine, fine, medium, coarse, very-coarse
