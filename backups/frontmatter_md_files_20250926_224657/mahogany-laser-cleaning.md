name: Mahogany
category: Wood
subcategory: Mahogany
title: Mahogany Laser Cleaning
description: Laser cleaning parameters for Mahogany
materialProperties:
  density:
    value: 0.64
    unit: g/cm³
    confidence: 95
    description: Average density of mahogany at 12% moisture content
    min: 0.53
    max: 0.85
  meltingPoint:
    value: 350
    unit: °C
    confidence: 85
    description: Approximate pyrolysis/charring temperature before complete decomposition
    min: 300
    max: 400
  thermalConductivity:
    value: 0.12
    unit: W/m·K
    confidence: 90
    description: Thermal conductivity perpendicular to grain at room temperature
    min: 0.1
    max: 0.14
  tensileStrength:
    value: 85
    unit: MPa
    confidence: 90
    description: Tensile strength parallel to grain
    min: 70
    max: 100
  hardness:
    value: 4.2
    unit: kN
    confidence: 88
    description: Janka hardness test result
    min: 3.8
    max: 4.6
  youngsModulus:
    value: 9.7
    unit: GPa
    confidence: 92
    description: Modulus of elasticity parallel to grain
    min: 8.5
    max: 11.0
  thermalExpansion:
    value: 3.5
    unit: 10^-6/°C
    confidence: 88
    description: Coefficient of thermal expansion parallel to grain
    min: 3.0
    max: 4.0
  specificHeat:
    value: 1700
    unit: J/kg·K
    confidence: 92
    description: Specific heat capacity at room temperature
    min: 1600
    max: 1800
  absorptionCoefficient:
    value: 0.75
    unit: dimensionless
    confidence: 85
    description: Estimated absorption coefficient for near-infrared lasers (1064 nm)
    min: 0.65
    max: 0.85
  ablationThreshold:
    value: 1.2
    unit: J/cm²
    confidence: 82
    description: Estimated laser ablation threshold for nanosecond pulses at 1064
      nm
    min: 0.8
    max: 1.6
  porosity:
    value: 45
    unit: '%'
    confidence: 90
    description: Typical porosity range for mahogany wood structure
    min: 40
    max: 50
  moistureContent:
    value: 12
    unit: '%'
    confidence: 95
    description: Equilibrium moisture content at standard conditions
    min: 8
    max: 15
applications:
- laser cleaning
- surface preparation
machineSettings:
  powerRange:
    value: 40
    unit: W
    confidence: 90
    description: Optimal average power for Mahogany surface cleaning without charring
    min: 20
    max: 60
  wavelength:
    value: 1064
    unit: nm
    confidence: 91
    description: Near-IR wavelength optimized for Mahogany absorption
    min: null
    max: null
  spotSize:
    value: 100
    unit: μm
    confidence: 92
    description: Optimal beam diameter for precision cleaning
    min: 50
    max: 200
  repetitionRate:
    value: 50
    unit: kHz
    confidence: 87
    description: Optimal repetition rate for efficient cleaning coverage
    min: 20
    max: 100
  fluenceThreshold:
    value: 0.8
    unit: J/cm²
    confidence: 88
    description: Minimum fluence required for effective contaminant removal
    min: 0.5
    max: 1.2
  pulseWidth:
    value: 15
    unit: ns
    confidence: 85
    description: Optimal pulse duration for controlled material removal
    min: 10
    max: 30
  scanSpeed:
    value: 500
    unit: mm/s
    confidence: 89
    description: Optimal scanning speed for uniform cleaning
    min: 200
    max: 1000
  overlapRatio:
    value: 50
    unit: '%'
    confidence: 86
    description: Optimal pulse overlap for complete surface coverage
    min: 30
    max: 70
  passCount:
    value: 2
    unit: passes
    confidence: 88
    description: Recommended number of passes for thorough cleaning
    min: 1
    max: 4
  energyDensity:
    value: 1.5
    unit: J/cm²
    confidence: 85
    description: Optimal energy density for controlled material interaction
    min: 0.8
    max: 2.5
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
    alt: Mahogany surface undergoing laser cleaning showing precise contamination
      removal
    url: /images/mahogany-laser-cleaning-hero.jpg
  micro:
    alt: Microscopic view of Mahogany surface after laser cleaning showing detailed
      surface structure
    url: /images/mahogany-laser-cleaning-micro.jpg
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
