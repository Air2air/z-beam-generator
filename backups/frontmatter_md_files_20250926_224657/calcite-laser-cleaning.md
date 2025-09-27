name: Calcite
category: Stone
subcategory: Calcite
title: Calcite Laser Cleaning
description: Laser cleaning parameters for Calcite
materialProperties:
  density:
    value: 2.71
    unit: g/cm³
    confidence: 98
    description: Density of pure calcite at room temperature
    min: 2.69
    max: 2.73
  meltingPoint:
    value: 1339
    unit: °C
    confidence: 90
    description: Melting point with decomposition to CaO and CO₂
    min: 1320
    max: 1350
  thermalConductivity:
    value: 3.2
    unit: W/m·K
    confidence: 85
    description: Thermal conductivity parallel to c-axis at 25°C
    min: 2.8
    max: 3.6
  hardness:
    value: 3.0
    unit: Mohs
    confidence: 95
    description: Mohs hardness scale - reference mineral for hardness 3
    min: 2.8
    max: 3.2
  youngsModulus:
    value: 75
    unit: GPa
    confidence: 82
    description: Young's modulus for single crystal calcite
    min: 70
    max: 80
  thermalExpansion:
    value: 25
    unit: ×10⁻⁶/°C
    confidence: 88
    description: Coefficient of thermal expansion parallel to c-axis
    min: 23
    max: 27
  specificHeat:
    value: 0.82
    unit: J/g·K
    confidence: 92
    description: Specific heat capacity at room temperature
    min: 0.8
    max: 0.84
  refractiveIndex:
    value: 1.658
    unit: dimensionless
    confidence: 96
    description: Ordinary refractive index (nₒ) at 589 nm
    min: 1.656
    max: 1.66
  absorptionCoefficient:
    value: 0.05
    unit: cm⁻¹
    confidence: 85
    description: Absorption coefficient at 1064 nm (Nd:YAG laser wavelength)
    min: 0.03
    max: 0.08
  ablationThreshold:
    value: 2.5
    unit: J/cm²
    confidence: 80
    description: Approximate ablation threshold for nanosecond pulses at 1064 nm
    min: 1.8
    max: 3.5
  chemicalStability:
    value: Low
    unit: qualitative
    confidence: 95
    description: Highly soluble in acids, reacts with weak acids including carbonic
      acid
    min: N/A
    max: N/A
  crystallineStructure:
    value: Rhombohedral
    unit: crystal system
    confidence: 98
    description: Trigonal crystal system, space group R3̄c
    min: N/A
    max: N/A
applications:
- laser cleaning
- surface preparation
machineSettings:
  powerRange:
    value: 15
    unit: W
    confidence: 90
    description: Optimal average power for Calcite surface cleaning without thermal
      damage
    min: 8
    max: 25
  wavelength:
    value: 1064
    unit: nm
    confidence: 88
    description: Near-IR wavelength with good Calcite absorption for controlled ablation
    min: 532
    max: 1064
  spotSize:
    value: 100
    unit: μm
    confidence: 92
    description: Beam spot diameter for precise cleaning control on Calcite surfaces
    min: 50
    max: 200
  repetitionRate:
    value: 20
    unit: kHz
    confidence: 87
    description: Optimal repetition rate for efficient cleaning with adequate cooling
      between pulses
    min: 10
    max: 50
  pulseWidth:
    value: 15
    unit: ns
    confidence: 85
    description: Nanosecond pulse duration for efficient contaminant removal with
      minimal substrate damage
    min: 10
    max: 30
  scanSpeed:
    value: 500
    unit: mm/s
    confidence: 84
    description: Optimal scanning speed for uniform cleaning coverage
    min: 200
    max: 1000
  fluenceThreshold:
    value: 1.2
    unit: J/cm²
    confidence: 89
    description: Threshold fluence for effective contaminant removal from Calcite
    min: 0.8
    max: 2.0
  overlapRatio:
    value: 50
    unit: '%'
    confidence: 86
    description: Optimal pulse overlap for uniform cleaning without excessive energy
      deposition
    min: 30
    max: 70
  passCount:
    value: 2
    unit: passes
    confidence: 88
    description: Recommended number of passes for complete contaminant removal
    min: 1
    max: 4
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
    alt: Calcite surface undergoing laser cleaning showing precise contamination removal
    url: /images/calcite-laser-cleaning-hero.jpg
  micro:
    alt: Microscopic view of Calcite surface after laser cleaning showing detailed
      surface structure
    url: /images/calcite-laser-cleaning-micro.jpg
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
