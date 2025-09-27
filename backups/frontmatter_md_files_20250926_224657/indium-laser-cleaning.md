name: Indium
category: Metal
subcategory: Indium
title: Indium Laser Cleaning
description: Laser cleaning parameters for Indium
materialProperties:
  density:
    value: 7.31
    unit: g/cm³
    confidence: 98
    description: Density of pure indium at 20°C
    min: 7.28
    max: 7.31
  meltingPoint:
    value: 156.6
    unit: °C
    confidence: 97
    description: Melting point of pure indium
    min: 156.4
    max: 156.8
  thermalConductivity:
    value: 81.8
    unit: W/m·K
    confidence: 92
    description: Thermal conductivity at 300K
    min: 80.0
    max: 83.0
  tensileStrength:
    value: 2.5
    unit: MPa
    confidence: 85
    description: Ultimate tensile strength of pure indium
    min: 1.5
    max: 4.0
  hardness:
    value: 0.9
    unit: HB
    confidence: 89
    description: Brinell hardness of pure indium
    min: 0.8
    max: 1.0
  youngsModulus:
    value: 11
    unit: GPa
    confidence: 87
    description: Young's modulus of elasticity
    min: 10
    max: 12
  thermalExpansion:
    value: 32.1
    unit: ×10⁻⁶/K
    confidence: 90
    description: Linear thermal expansion coefficient at 25°C
    min: 31.5
    max: 33.0
  thermalDiffusivity:
    value: 0.44
    unit: cm²/s
    confidence: 88
    description: Thermal diffusivity at room temperature
    min: 0.42
    max: 0.46
  specificHeat:
    value: 0.233
    unit: J/g·K
    confidence: 91
    description: Specific heat capacity at 25°C
    min: 0.23
    max: 0.235
  absorptionCoefficient:
    value: 6.5
    unit: ×10⁵ cm⁻¹
    confidence: 82
    description: Approximate absorption coefficient for visible light (500-600 nm)
    min: 5.0
    max: 8.0
  reflectivity:
    value: 74
    unit: '%'
    confidence: 84
    description: Reflectivity at 500 nm wavelength
    min: 72
    max: 76
  ablationThreshold:
    value: 0.15
    unit: J/cm²
    confidence: 80
    description: Estimated laser ablation threshold for nanosecond pulses (1064 nm)
    min: 0.1
    max: 0.25
  crystallineStructure:
    value: Tetragonal
    unit: none
    confidence: 95
    description: Crystal structure (body-centered tetragonal)
    min: n/a
    max: n/a
  oxidationResistance:
    value: Low
    unit: qualitative
    confidence: 88
    description: Forms thin oxide layer but oxidizes slowly in air
    min: n/a
    max: n/a
applications:
- laser cleaning
- surface preparation
machineSettings:
  powerRange:
    value: 15
    unit: W
    confidence: 90
    description: Optimal average power for Indium oxide removal without substrate
      damage
    min: 8
    max: 25
  wavelength:
    value: 1064
    unit: nm
    confidence: 88
    description: Near-IR wavelength with good absorption in Indium oxide layers
    min: 532
    max: 1064
  spotSize:
    value: 50
    unit: μm
    confidence: 82
    description: Beam spot diameter for precise oxide removal
    min: 30
    max: 100
  repetitionRate:
    value: 20
    unit: kHz
    confidence: 87
    description: Optimal repetition rate for efficient cleaning coverage
    min: 10
    max: 50
  pulseWidth:
    value: 100
    unit: ns
    confidence: 85
    description: Nanosecond pulse duration for controlled oxide ablation
    min: 50
    max: 200
  scanSpeed:
    value: 500
    unit: mm/s
    confidence: 84
    description: Optimal scanning speed for uniform cleaning
    min: 200
    max: 1000
  fluenceThreshold:
    value: 1.2
    unit: J/cm²
    confidence: 89
    description: Minimum fluence required for Indium oxide ablation
    min: 0.8
    max: 2.5
  overlapRatio:
    value: 50
    unit: '%'
    confidence: 83
    description: Optimal pulse overlap for complete surface coverage
    min: 30
    max: 70
  passCount:
    value: 1
    unit: passes
    confidence: 91
    description: Single pass typically sufficient for thin oxide layers
    min: 1
    max: 3
author_object:
  id: 4
  name: Todd Dunning
  sex: m
  title: MA
  country: United States (California)
  expertise: Optical Materials for Laser Systems
  image: /images/author/todd-dunning.jpg
images:
  hero:
    alt: Indium surface undergoing laser cleaning showing precise contamination removal
    url: /images/indium-laser-cleaning-hero.jpg
  micro:
    alt: Microscopic view of Indium surface after laser cleaning showing detailed
      surface structure
    url: /images/indium-laser-cleaning-micro.jpg
environmentalImpact:
- benefit: Chemical Waste Elimination
  description: Eliminates hazardous chemical waste streams
  applicableIndustries:
  - Semiconductor
  - Electronics
  - Medical
  - Nuclear
  quantifiedBenefits: Up to 100% reduction in chemical cleaning agents
  sustainabilityBenefit: ''
- benefit: Water Usage Reduction
  description: Dry process requires no water
  applicableIndustries: []
  quantifiedBenefits: ''
  sustainabilityBenefit: Significant water conservation in industrial processes
- benefit: Energy Efficiency
  description: Focused energy delivery with minimal waste heat
  applicableIndustries: []
  quantifiedBenefits: ''
  sustainabilityBenefit: ''
- benefit: Air Quality Improvement
  description: Eliminates volatile organic compounds from chemical cleaning
  applicableIndustries: []
  quantifiedBenefits: ''
  sustainabilityBenefit: ''
author_id: 4
applicationTypes:
- type: Precision Cleaning
  description: High-precision removal of microscopic contaminants and residues
  industries:
  - Semiconductor
  - MEMS
  - Optics
  - Medical Devices
  qualityMetrics:
  - Particle count reduction
  - Surface roughness maintenance
  - Chemical purity
  typicalTolerances: Sub-micron accuracy with minimal substrate impact
  objectives: []
- type: Surface Preparation
  description: Preparation of surfaces for bonding, coating, or further processing
  industries:
  - Aerospace
  - Automotive
  - Manufacturing
  - Construction
  qualityMetrics:
  - Surface energy
  - Cleanliness level
  - Roughness profile
  typicalTolerances: ''
  objectives:
  - Adhesion enhancement
  - Contamination removal
  - Surface activation
- type: Restoration Cleaning
  description: Gentle removal of accumulated contamination while preserving original
    material
  industries:
  - Cultural Heritage
  - Architecture
  - Art Conservation
  - Historical Restoration
  qualityMetrics: []
  typicalTolerances: ''
  objectives: []
- type: Contamination Removal
  description: General removal of unwanted surface deposits and contaminants
  industries:
  - Manufacturing
  - Marine
  - Oil & Gas
  - Power Generation
  qualityMetrics: []
  typicalTolerances: ''
  objectives: []
outcomeMetrics:
- metric: Contaminant Removal Efficiency
  description: Percentage of target contaminants successfully removed from surface
  measurementMethods:
  - Before/after microscopy
  - Chemical analysis
  - Mass spectrometry
  typicalRanges: 95-99.9% depending on application and material
  factorsAffecting:
  - Contamination type
  - Adhesion strength
  - Surface geometry
  units: []
- metric: Processing Speed
  description: Rate of surface area processed per unit time
  measurementMethods: []
  typicalRanges: ''
  factorsAffecting: []
  units:
  - m²/h
  - cm²/min
  - mm²/s
- metric: Surface Quality Preservation
  description: Maintenance of original surface characteristics after cleaning
  measurementMethods: []
  typicalRanges: ''
  factorsAffecting: []
  units: []
- metric: Thermal Damage Avoidance
  description: Prevention of heat-related material alterations during cleaning
  measurementMethods: []
  typicalRanges: ''
  factorsAffecting: []
  units: []
