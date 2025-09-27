name: Hastelloy
category: Metal
subcategory: Hastelloy
title: Hastelloy Laser Cleaning
description: Laser cleaning parameters for Hastelloy
materialProperties:
  density:
    value: 8.89
    unit: g/cm³
    confidence: 95
    description: Density of Hastelloy C-276 at room temperature
    min: 8.85
    max: 8.92
  meltingPoint:
    value: 1370
    unit: °C
    confidence: 90
    description: Solidus temperature for Hastelloy C-276
    min: 1325
    max: 1370
  thermalConductivity:
    value: 11.1
    unit: W/m·K
    confidence: 88
    description: Thermal conductivity at 20°C for Hastelloy C-276
    min: 10.5
    max: 12.0
  tensileStrength:
    value: 790
    unit: MPa
    confidence: 92
    description: Room temperature tensile strength (annealed condition)
    min: 760
    max: 830
  hardness:
    value: 220
    unit: HV
    confidence: 88
    description: Vickers hardness in annealed condition
    min: 200
    max: 240
  youngsModulus:
    value: 205
    unit: GPa
    confidence: 90
    description: Elastic modulus at room temperature
    min: 200
    max: 210
  thermalExpansion:
    value: 11.2
    unit: μm/m·°C
    confidence: 85
    description: Coefficient of thermal expansion (20-100°C)
    min: 10.8
    max: 11.6
  specificHeat:
    value: 427
    unit: J/kg·K
    confidence: 82
    description: Specific heat capacity at 20°C
    min: 410
    max: 440
  absorptionCoefficient:
    value: 0.65
    unit: dimensionless
    confidence: 75
    description: Estimated absorption coefficient for Nd:YAG laser (1064 nm)
    min: 0.55
    max: 0.75
  reflectivity:
    value: 0.35
    unit: dimensionless
    confidence: 78
    description: Estimated reflectivity for infrared lasers
    min: 0.25
    max: 0.45
  ablationThreshold:
    value: 2.5
    unit: J/cm²
    confidence: 80
    description: Estimated laser ablation threshold for nanosecond pulses
    min: 1.8
    max: 3.2
  oxidationResistance:
    value: Excellent
    unit: qualitative
    confidence: 85
    description: Resistance to oxidation at high temperatures
    min: Good
    max: Excellent
  corrosionResistance:
    value: Outstanding
    unit: qualitative
    confidence: 95
    description: Exceptional resistance to pitting, crevice corrosion, and stress
      corrosion cracking
    min: Excellent
    max: Outstanding
  crystallineStructure:
    value: FCC
    unit: crystal system
    confidence: 98
    description: Face-centered cubic austenitic structure
    min: FCC
    max: FCC
applications:
- laser cleaning
- surface preparation
machineSettings:
  powerRange:
    value: 100
    unit: W
    confidence: 92
    description: Optimal average power for Hastelloy surface cleaning without substrate
      damage
    min: 80
    max: 120
  wavelength:
    value: 1064
    unit: nm
    confidence: 88
    description: Near-infrared wavelength optimized for Hastelloy absorption characteristics
    min: 1030
    max: 1070
  spotSize:
    value: 50
    unit: μm
    confidence: 84
    description: Beam spot diameter for precise cleaning control
    min: 30
    max: 100
  repetitionRate:
    value: 100
    unit: kHz
    confidence: 87
    description: High repetition rate for efficient cleaning coverage
    min: 50
    max: 200
  pulseWidth:
    value: 10
    unit: ns
    confidence: 85
    description: Nanosecond pulse duration for controlled ablation of surface contaminants
    min: 5
    max: 20
  scanSpeed:
    value: 1000
    unit: mm/s
    confidence: 86
    description: Optimal scanning speed for uniform surface treatment
    min: 500
    max: 2000
  fluence:
    value: 5
    unit: J/cm²
    confidence: 90
    description: Energy density threshold for effective contaminant removal
    min: 3
    max: 8
  overlapRatio:
    value: 50
    unit: '%'
    confidence: 83
    description: Optimal pulse overlap for complete surface coverage
    min: 40
    max: 70
  passCount:
    value: 3
    unit: passes
    confidence: 85
    description: Number of cleaning passes for thorough contaminant removal
    min: 1
    max: 5
  laserType:
    value: Nd:YAG
    unit: n/a
    confidence: 89
    description: Fiber laser recommended for Hastelloy cleaning applications
    min: null
    max: null
author_object:
  id: 1
  name: Yi-Chun Lin
  sex: f
  title: Ph.D.
  country: Taiwan
  expertise: Laser Materials Processing
  image: /images/author/yi-chun-lin.jpg
images:
  hero:
    alt: Hastelloy surface undergoing laser cleaning showing precise contamination
      removal
    url: /images/hastelloy-laser-cleaning-hero.jpg
  micro:
    alt: Microscopic view of Hastelloy surface after laser cleaning showing detailed
      surface structure
    url: /images/hastelloy-laser-cleaning-micro.jpg
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
author_id: 1
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
