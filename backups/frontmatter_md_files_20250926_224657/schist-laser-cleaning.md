name: Schist
category: Stone
subcategory: Schist
title: Schist Laser Cleaning
description: Laser cleaning parameters for Schist
materialProperties:
  density:
    value: 2.75
    unit: g/cm³
    confidence: 85
    description: Average density of schist rocks, varies with mineral composition
    min: 2.6
    max: 2.9
  meltingPoint:
    value: 1250
    unit: °C
    confidence: 80
    description: Approximate melting temperature range for schist minerals
    min: 1100
    max: 1400
  thermalConductivity:
    value: 2.8
    unit: W/m·K
    confidence: 82
    description: Thermal conductivity of typical schist at room temperature
    min: 2.2
    max: 3.4
  hardness:
    value: 5.5
    unit: Mohs
    confidence: 88
    description: Average hardness on Mohs scale, depends on mineral content
    min: 3.0
    max: 7.0
  youngsModulus:
    value: 65
    unit: GPa
    confidence: 85
    description: Elastic modulus parallel to foliation planes
    min: 45
    max: 85
  thermalExpansion:
    value: 8.5
    unit: 10⁻⁶/°C
    confidence: 78
    description: Coefficient of thermal expansion for schist
    min: 7.0
    max: 10.0
  specificHeat:
    value: 0.85
    unit: J/g·K
    confidence: 83
    description: Specific heat capacity at room temperature
    min: 0.75
    max: 0.95
  compressiveStrength:
    value: 150
    unit: MPa
    confidence: 82
    description: Uniaxial compressive strength perpendicular to foliation
    min: 80
    max: 220
  absorptionCoefficient:
    value: 0.65
    unit: dimensionless
    confidence: 75
    description: Average absorption coefficient for visible to near-IR wavelengths
    min: 0.4
    max: 0.8
  ablationThreshold:
    value: 2.5
    unit: J/cm²
    confidence: 70
    description: Approximate laser ablation threshold for 1064 nm wavelength
    min: 1.8
    max: 3.5
  porosity:
    value: 2.5
    unit: '%'
    confidence: 80
    description: Typical porosity range for intact schist
    min: 1.0
    max: 5.0
  surfaceRoughness:
    value: 8.2
    unit: μm Ra
    confidence: 78
    description: Average surface roughness of natural schist surfaces
    min: 5.0
    max: 15.0
applications:
- laser cleaning
- surface preparation
machineSettings:
  powerRange:
    value: 100
    unit: W
    confidence: 92
    description: Optimal power range for Schist cleaning without thermal damage
    min: 80
    max: 120
  wavelength:
    value: 1064
    unit: nm
    confidence: 88
    description: Near-IR wavelength optimized for Schist mineral absorption
    min: 532
    max: 1064
  spotSize:
    value: 100
    unit: μm
    confidence: 90
    description: Beam spot diameter for precise cleaning control
    min: 50
    max: 200
  repetitionRate:
    value: 50
    unit: kHz
    confidence: 87
    description: Optimal repetition rate for efficient cleaning with thermal management
    min: 20
    max: 100
  pulseWidth:
    value: 10
    unit: ns
    confidence: 85
    description: Nanosecond pulse width for controlled ablation of surface contaminants
    min: 5
    max: 20
  scanSpeed:
    value: 500
    unit: mm/s
    confidence: 84
    description: Optimal scanning speed for uniform cleaning coverage
    min: 200
    max: 1000
  fluenceThreshold:
    value: 2.5
    unit: J/cm²
    confidence: 89
    description: Fluence threshold for effective contaminant removal from Schist surface
    min: 1.5
    max: 4.0
  overlapRatio:
    value: 50
    unit: '%'
    confidence: 86
    description: Optimal beam overlap for complete surface coverage
    min: 30
    max: 70
  passCount:
    value: 3
    unit: passes
    confidence: 88
    description: Recommended number of passes for thorough cleaning
    min: 1
    max: 5
  laserType:
    value: Nd:YAG
    unit: n/a
    confidence: 90
    description: Recommended laser type for Schist cleaning applications
    min: null
    max: null
author_object:
  id: 3
  name: Ikmanda Roswati
  sex: m
  title: Ph.D.
  country: Indonesia
  expertise: Ultrafast Laser Physics and Material Interactions
  image: /images/author/ikmanda-roswati.jpg
images:
  hero:
    alt: Schist surface undergoing laser cleaning showing precise contamination removal
    url: /images/schist-laser-cleaning-hero.jpg
  micro:
    alt: Microscopic view of Schist surface after laser cleaning showing detailed
      surface structure
    url: /images/schist-laser-cleaning-micro.jpg
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
author_id: 3
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
