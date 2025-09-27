name: Porphyry
category: Stone
subcategory: Porphyry
title: Porphyry Laser Cleaning
description: Laser cleaning parameters for Porphyry
materialProperties:
  density:
    value: 2.65
    unit: g/cm³
    confidence: 95
    description: Bulk density of porphyry rock with typical mineral composition
    min: 2.6
    max: 2.75
  meltingPoint:
    value: 1200
    unit: °C
    confidence: 85
    description: Approximate melting temperature range for porphyry composition
    min: 950
    max: 1300
  thermalConductivity:
    value: 2.9
    unit: W/m·K
    confidence: 88
    description: Thermal conductivity at room temperature
    min: 2.5
    max: 3.3
  hardness:
    value: 6.5
    unit: Mohs
    confidence: 92
    description: Mohs hardness scale for porphyry (feldspar-dominated)
    min: 6.0
    max: 7.0
  youngsModulus:
    value: 60
    unit: GPa
    confidence: 85
    description: Elastic modulus in compression
    min: 50
    max: 70
  thermalExpansion:
    value: 7.2
    unit: 10⁻⁶/°C
    confidence: 82
    description: Coefficient of linear thermal expansion
    min: 6.5
    max: 8.0
  specificHeat:
    value: 0.84
    unit: kJ/kg·K
    confidence: 90
    description: Specific heat capacity at room temperature
    min: 0.8
    max: 0.88
  compressiveStrength:
    value: 180
    unit: MPa
    confidence: 88
    description: Uniaxial compressive strength
    min: 150
    max: 220
  absorptionCoefficient:
    value: 0.85
    unit: dimensionless
    confidence: 80
    description: Optical absorption coefficient for common laser wavelengths (1064
      nm)
    min: 0.75
    max: 0.92
  reflectivity:
    value: 0.15
    unit: dimensionless
    confidence: 82
    description: Surface reflectivity at 1064 nm wavelength
    min: 0.1
    max: 0.2
  ablationThreshold:
    value: 2.5
    unit: J/cm²
    confidence: 80
    description: Laser ablation threshold for nanosecond pulses at 1064 nm
    min: 1.8
    max: 3.5
  porosity:
    value: 2.5
    unit: '%'
    confidence: 90
    description: Typical porosity range for dense porphyry
    min: 1.0
    max: 5.0
applications:
- laser cleaning
- surface preparation
machineSettings:
  powerRange:
    value: 90
    unit: W
    confidence: 92
    description: Optimal average power for Porphyry surface cleaning without thermal
      damage
    min: 70
    max: 110
  wavelength:
    value: 1064
    unit: nm
    confidence: 88
    description: Near-infrared wavelength optimized for Porphyry mineral absorption
    min: 532
    max: 1064
  spotSize:
    value: 100
    unit: μm
    confidence: 90
    description: Beam spot diameter for precise cleaning of Porphyry surface features
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
    value: 15
    unit: ns
    confidence: 85
    description: Nanosecond pulse duration for controlled ablation of surface contaminants
    min: 8
    max: 25
  scanSpeed:
    value: 500
    unit: mm/s
    confidence: 84
    description: Optimal scanning speed for uniform cleaning coverage
    min: 300
    max: 800
  fluenceThreshold:
    value: 2.5
    unit: J/cm²
    confidence: 89
    description: Threshold fluence for effective contaminant removal from Porphyry
    min: 1.8
    max: 3.5
  overlapRatio:
    value: 50
    unit: '%'
    confidence: 86
    description: Optimal beam overlap for complete surface coverage without over-processing
    min: 40
    max: 60
  passCount:
    value: 3
    unit: passes
    confidence: 83
    description: Recommended number of passes for thorough cleaning
    min: 2
    max: 5
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
    alt: Porphyry surface undergoing laser cleaning showing precise contamination
      removal
    url: /images/porphyry-laser-cleaning-hero.jpg
  micro:
    alt: Microscopic view of Porphyry surface after laser cleaning showing detailed
      surface structure
    url: /images/porphyry-laser-cleaning-micro.jpg
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
