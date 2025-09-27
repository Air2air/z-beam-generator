name: Cedar
category: Wood
subcategory: Cedar
title: Cedar Laser Cleaning
description: Laser cleaning parameters for Cedar
materialProperties:
  density:
    value: 0.37
    unit: g/cm³
    confidence: 95
    description: Average density of Western Red Cedar at 12% moisture content
    min: 0.31
    max: 0.42
  meltingPoint:
    value: 380
    unit: °C
    confidence: 85
    description: Approximate pyrolysis/charring temperature of cedar wood
    min: 350
    max: 400
  thermalConductivity:
    value: 0.09
    unit: W/m·K
    confidence: 90
    description: Thermal conductivity perpendicular to grain at room temperature
    min: 0.08
    max: 0.11
  tensileStrength:
    value: 75
    unit: MPa
    confidence: 90
    description: Tensile strength parallel to grain
    min: 65
    max: 85
  hardness:
    value: 2.0
    unit: kN
    confidence: 85
    description: Janka hardness test result for side hardness
    min: 1.6
    max: 2.4
  youngsModulus:
    value: 7.6
    unit: GPa
    confidence: 88
    description: Modulus of elasticity parallel to grain
    min: 6.8
    max: 8.4
  thermalExpansion:
    value: 3.4
    unit: μm/m·°C
    confidence: 88
    description: Coefficient of thermal expansion tangential to grain
    min: 2.8
    max: 4.0
  specificHeat:
    value: 1380
    unit: J/kg·K
    confidence: 92
    description: Specific heat capacity at room temperature
    min: 1300
    max: 1450
  absorptionCoefficient:
    value: 0.85
    unit: dimensionless
    confidence: 82
    description: Estimated absorption coefficient for near-infrared wavelengths (1064nm)
    min: 0.75
    max: 0.92
  ablationThreshold:
    value: 0.8
    unit: J/cm²
    confidence: 80
    description: Estimated laser ablation threshold for 1064nm wavelength
    min: 0.5
    max: 1.2
  porosity:
    value: 65
    unit: '%'
    confidence: 92
    description: Typical porosity of cedar wood structure
    min: 60
    max: 70
  surfaceRoughness:
    value: 15
    unit: μm Ra
    confidence: 85
    description: Average surface roughness of planed cedar wood
    min: 10
    max: 25
applications:
- laser cleaning
- surface preparation
machineSettings:
  powerRange:
    value: 40
    unit: W
    confidence: 90
    description: Optimal average power for cedar surface cleaning without charring
    min: 20
    max: 60
  wavelength:
    value: 1064
    unit: nm
    confidence: 88
    description: Near-IR wavelength for optimal cedar absorption with minimal penetration
      depth
    min: 532
    max: 1064
  spotSize:
    value: 100
    unit: μm
    confidence: 82
    description: Beam spot diameter for precise cedar surface treatment
    min: 50
    max: 200
  repetitionRate:
    value: 20
    unit: kHz
    confidence: 87
    description: Optimal repetition rate for efficient cedar cleaning with thermal
      management
    min: 10
    max: 50
  pulseWidth:
    value: 100
    unit: ns
    confidence: 85
    description: Short pulse duration for controlled ablation of surface contaminants
    min: 50
    max: 200
  scanSpeed:
    value: 500
    unit: mm/s
    confidence: 84
    description: Optimal scanning speed for uniform cedar cleaning coverage
    min: 200
    max: 1000
  fluenceThreshold:
    value: 2.5
    unit: J/cm²
    confidence: 89
    description: Fluence threshold for effective cedar surface cleaning without substrate
      damage
    min: 1.5
    max: 4.0
  overlapRatio:
    value: 50
    unit: '%'
    confidence: 83
    description: Optimal beam overlap for uniform cedar surface treatment
    min: 30
    max: 70
  passCount:
    value: 2
    unit: passes
    confidence: 86
    description: Recommended number of passes for complete cedar surface cleaning
    min: 1
    max: 4
  laserType:
    value: Fiber Laser
    unit: N/A
    confidence: 90
    description: Recommended laser type for cedar cleaning applications
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
    alt: Cedar surface undergoing laser cleaning showing precise contamination removal
    url: /images/cedar-laser-cleaning-hero.jpg
  micro:
    alt: Microscopic view of Cedar surface after laser cleaning showing detailed surface
      structure
    url: /images/cedar-laser-cleaning-micro.jpg
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
