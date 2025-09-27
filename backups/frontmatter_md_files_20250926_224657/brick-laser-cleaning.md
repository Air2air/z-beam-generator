name: Brick
category: Masonry
subcategory: Brick
title: Brick Laser Cleaning
description: Laser cleaning parameters for Brick
materialProperties:
  density:
    value: 2.0
    unit: g/cm³
    confidence: 95
    description: Typical density of fired clay brick
    min: 1.6
    max: 2.4
  meltingPoint:
    value: 1600
    unit: °C
    confidence: 90
    description: Approximate melting point of fired clay brick components
    min: 1500
    max: 1700
  thermalConductivity:
    value: 0.72
    unit: W/m·K
    confidence: 92
    description: Thermal conductivity of common brick at room temperature
    min: 0.6
    max: 1.0
  hardness:
    value: 4.5
    unit: Mohs
    confidence: 85
    description: Mohs hardness scale for fired clay brick
    min: 3.5
    max: 5.5
  youngsModulus:
    value: 20
    unit: GPa
    confidence: 88
    description: Elastic modulus of fired clay brick
    min: 15
    max: 30
  thermalExpansion:
    value: 5.5
    unit: ×10⁻⁶/°C
    confidence: 88
    description: Coefficient of thermal expansion for fired clay brick
    min: 4.0
    max: 7.0
  specificHeat:
    value: 840
    unit: J/kg·K
    confidence: 85
    description: Specific heat capacity at room temperature
    min: 800
    max: 900
  thermalDiffusivity:
    value: 0.43
    unit: mm²/s
    confidence: 82
    description: Thermal diffusivity calculated from thermal properties
    min: 0.35
    max: 0.55
  compressiveStrength:
    value: 35
    unit: MPa
    confidence: 94
    description: Typical compressive strength of standard brick
    min: 20
    max: 70
  absorptionCoefficient:
    value: 0.85
    unit: dimensionless
    confidence: 90
    description: Optical absorption coefficient for common laser wavelengths (1064
      nm)
    min: 0.7
    max: 0.95
  reflectivity:
    value: 0.15
    unit: dimensionless
    confidence: 87
    description: Surface reflectivity at common laser wavelengths
    min: 0.05
    max: 0.3
  ablationThreshold:
    value: 1.2
    unit: J/cm²
    confidence: 82
    description: Laser ablation threshold for nanosecond pulses at 1064 nm
    min: 0.8
    max: 2.0
  porosity:
    value: 25
    unit: '%'
    confidence: 92
    description: Typical porosity of fired clay brick
    min: 15
    max: 35
  waterAbsorption:
    value: 12
    unit: '%'
    confidence: 90
    description: Water absorption capacity by weight
    min: 8
    max: 20
applications:
- laser cleaning
- surface preparation
machineSettings:
  powerRange:
    value: 100
    unit: W
    confidence: 92
    description: Optimal average power for brick surface cleaning without thermal
      damage
    min: 80
    max: 120
  wavelength:
    value: 1064
    unit: nm
    confidence: 88
    description: Near-infrared wavelength for optimal brick absorption and contamination
      removal
    min: 1030
    max: 1070
  spotSize:
    value: 100
    unit: μm
    confidence: 84
    description: Beam spot diameter for precise cleaning control on brick surfaces
    min: 50
    max: 200
  repetitionRate:
    value: 20
    unit: kHz
    confidence: 87
    description: Optimal repetition rate for efficient cleaning coverage and thermal
      management
    min: 10
    max: 50
  pulseWidth:
    value: 10
    unit: ns
    confidence: 85
    description: Nanosecond pulse duration for effective contaminant ablation with
      minimal substrate heating
    min: 5
    max: 20
  scanSpeed:
    value: 500
    unit: mm/s
    confidence: 86
    description: Optimal scanning speed for uniform cleaning efficiency
    min: 200
    max: 1000
  fluenceThreshold:
    value: 2.5
    unit: J/cm²
    confidence: 89
    description: Minimum fluence required for effective contaminant removal from brick
    min: 1.5
    max: 4.0
  overlapRatio:
    value: 50
    unit: '%'
    confidence: 83
    description: Optimal pulse overlap for uniform cleaning coverage
    min: 30
    max: 70
  passCount:
    value: 2
    unit: passes
    confidence: 85
    description: Recommended number of passes for thorough cleaning
    min: 1
    max: 4
  laserType:
    value: Nd:YAG
    unit: n/a
    confidence: 90
    description: Fiber laser type recommended for brick cleaning applications
    min: null
    max: null
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
    alt: Brick surface undergoing laser cleaning showing precise contamination removal
    url: /images/brick-laser-cleaning-hero.jpg
  micro:
    alt: Microscopic view of Brick surface after laser cleaning showing detailed surface
      structure
    url: /images/brick-laser-cleaning-micro.jpg
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
