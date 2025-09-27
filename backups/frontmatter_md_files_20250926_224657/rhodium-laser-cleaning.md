name: Rhodium
category: Metal
subcategory: Rhodium
title: Rhodium Laser Cleaning
description: Laser cleaning parameters for Rhodium
materialProperties:
  density:
    value: 12.41
    unit: g/cm³
    confidence: 98
    description: Density of pure rhodium at 20°C
    min: 12.4
    max: 12.42
  meltingPoint:
    value: 1964
    unit: °C
    confidence: 97
    description: Melting point of pure rhodium
    min: 1960
    max: 1968
  thermalConductivity:
    value: 150
    unit: W/m·K
    confidence: 92
    description: Thermal conductivity at room temperature
    min: 145
    max: 155
  hardness:
    value: 110
    unit: HV
    confidence: 89
    description: Vickers hardness of annealed rhodium
    min: 100
    max: 120
  youngsModulus:
    value: 380
    unit: GPa
    confidence: 93
    description: Young's modulus of elasticity
    min: 375
    max: 385
  thermalExpansion:
    value: 8.2
    unit: ×10⁻⁶/K
    confidence: 90
    description: Coefficient of linear thermal expansion (20-100°C)
    min: 8.0
    max: 8.4
  thermalDiffusivity:
    value: 0.38
    unit: cm²/s
    confidence: 88
    description: Thermal diffusivity at room temperature
    min: 0.35
    max: 0.41
  specificHeat:
    value: 0.242
    unit: J/g·K
    confidence: 91
    description: Specific heat capacity at 25°C
    min: 0.24
    max: 0.244
  reflectivity:
    value: 78
    unit: '%'
    confidence: 85
    description: Optical reflectivity at 1064 nm (common laser wavelength)
    min: 75
    max: 80
  absorptionCoefficient:
    value: 5.8
    unit: ×10⁵ cm⁻¹
    confidence: 82
    description: Absorption coefficient at 1064 nm wavelength
    min: 5.5
    max: 6.1
  ablationThreshold:
    value: 1.2
    unit: J/cm²
    confidence: 80
    description: Estimated laser ablation threshold for nanosecond pulses at 1064
      nm
    min: 0.8
    max: 1.5
  crystallineStructure:
    value: FCC
    unit: '-'
    confidence: 99
    description: Face-centered cubic crystal structure
    min: '-'
    max: '-'
  oxidationResistance:
    value: Excellent
    unit: '-'
    confidence: 95
    description: Highly resistant to oxidation up to 600°C
    min: '-'
    max: '-'
  corrosionResistance:
    value: Exceptional
    unit: '-'
    confidence: 96
    description: Resistant to most acids, aqua regia, and corrosive environments
    min: '-'
    max: '-'
applications:
- laser cleaning
- surface preparation
machineSettings:
  powerRange:
    value: 45
    unit: W
    confidence: 90
    description: Optimal average power for Rhodium surface cleaning without thermal
      damage
    min: 30
    max: 60
  wavelength:
    value: 1064
    unit: nm
    confidence: 88
    description: Near-IR wavelength optimized for Rhodium's moderate reflectivity
      and thermal conductivity
    min: 532
    max: 1064
  spotSize:
    value: 80
    unit: μm
    confidence: 89
    description: Beam spot diameter for precise cleaning control on Rhodium surfaces
    min: 50
    max: 150
  repetitionRate:
    value: 50
    unit: kHz
    confidence: 87
    description: Optimal repetition rate for efficient cleaning with thermal management
    min: 20
    max: 100
  pulseWidth:
    value: 15
    unit: ns
    confidence: 85
    description: Nanosecond pulse duration for controlled ablation of surface contaminants
    min: 10
    max: 30
  scanSpeed:
    value: 500
    unit: mm/s
    confidence: 86
    description: Optimal scanning speed for uniform cleaning coverage
    min: 200
    max: 1000
  fluenceThreshold:
    value: 2.5
    unit: J/cm²
    confidence: 91
    description: Fluence threshold for effective contaminant removal without substrate
      damage
    min: 1.5
    max: 4.0
  overlapRatio:
    value: 70
    unit: '%'
    confidence: 84
    description: Optimal pulse overlap for uniform cleaning results
    min: 50
    max: 85
  passCount:
    value: 3
    unit: passes
    confidence: 88
    description: Recommended number of passes for complete contaminant removal
    min: 1
    max: 5
author_object:
  id: 2
  name: Alessandro Moretti
  sex: m
  title: Ph.D.
  country: Italy
  expertise: Laser-Based Additive Manufacturing
  image: /images/author/alessandro-moretti.jpg
images:
  hero:
    alt: Rhodium surface undergoing laser cleaning showing precise contamination removal
    url: /images/rhodium-laser-cleaning-hero.jpg
  micro:
    alt: Microscopic view of Rhodium surface after laser cleaning showing detailed
      surface structure
    url: /images/rhodium-laser-cleaning-micro.jpg
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
author_id: 2
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
