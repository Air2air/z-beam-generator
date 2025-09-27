name: Soapstone
category: Stone
subcategory: Soapstone
title: Soapstone Laser Cleaning
description: Laser cleaning parameters for Soapstone
materialProperties:
  density:
    value: 2.75
    unit: g/cm³
    confidence: 95
    description: Average density of soapstone (talc-rich metamorphic rock)
    min: 2.6
    max: 2.9
  meltingPoint:
    value: 1350
    unit: °C
    confidence: 85
    description: Approximate melting point considering talc decomposition at 800-900°C
    min: 1300
    max: 1400
  thermalConductivity:
    value: 6.0
    unit: W/m·K
    confidence: 90
    description: Thermal conductivity at room temperature
    min: 5.5
    max: 6.5
  hardness:
    value: 1.0
    unit: Mohs
    confidence: 95
    description: Mohs hardness scale (talc is reference mineral for hardness 1)
    min: 1.0
    max: 2.5
  youngsModulus:
    value: 50
    unit: GPa
    confidence: 82
    description: Elastic modulus - varies significantly with mineral composition
    min: 30
    max: 70
  thermalExpansion:
    value: 8.5
    unit: 10⁻⁶/°C
    confidence: 88
    description: Coefficient of thermal expansion (20-200°C range)
    min: 8.0
    max: 9.0
  specificHeat:
    value: 0.98
    unit: J/g·K
    confidence: 92
    description: Specific heat capacity at room temperature
    min: 0.95
    max: 1.02
  thermalDiffusivity:
    value: 2.2
    unit: mm²/s
    confidence: 85
    description: Thermal diffusivity calculated from conductivity, density, and specific
      heat
    min: 2.0
    max: 2.4
  compressiveStrength:
    value: 120
    unit: MPa
    confidence: 88
    description: Uniaxial compressive strength
    min: 80
    max: 160
  absorptionCoefficient:
    value: 0.85
    unit: dimensionless
    confidence: 80
    description: Estimated absorption coefficient for IR wavelengths (1064 nm)
    min: 0.75
    max: 0.92
  ablationThreshold:
    value: 2.5
    unit: J/cm²
    confidence: 78
    description: Estimated laser ablation threshold for nanosecond pulses at 1064
      nm
    min: 1.8
    max: 3.5
  porosity:
    value: 1.5
    unit: '%'
    confidence: 90
    description: Typical porosity range for dense soapstone varieties
    min: 0.5
    max: 3.0
  chemicalStability:
    value: High
    unit: qualitative
    confidence: 92
    description: Resistance to acids and alkalis - excellent chemical inertness
    min: Moderate
    max: Excellent
applications:
- laser cleaning
- surface preparation
machineSettings:
  powerRange:
    value: 40
    unit: W
    confidence: 90
    description: Optimal average power for Soapstone surface cleaning without thermal
      damage
    min: 20
    max: 80
  wavelength:
    value: 1064
    unit: nm
    confidence: 89
    description: Near-IR wavelength optimized for Soapstone mineral absorption
    min: null
    max: null
  spotSize:
    value: 100
    unit: μm
    confidence: 92
    description: Optimal beam diameter for precise cleaning control
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
    value: 1.2
    unit: J/cm²
    confidence: 88
    description: Threshold fluence for effective Soapstone contaminant removal
    min: 0.8
    max: 2.5
  pulseWidth:
    value: 15
    unit: ns
    confidence: 85
    description: Optimal pulse duration for controlled ablation of surface contaminants
    min: 8
    max: 30
  scanSpeed:
    value: 500
    unit: mm/s
    confidence: 85
    description: Optimal scanning speed for uniform cleaning results
    min: 200
    max: 1000
  overlapRatio:
    value: 50
    unit: '%'
    confidence: 88
    description: Optimal pulse overlap for complete surface coverage
    min: 30
    max: 70
  passCount:
    value: 2
    unit: passes
    confidence: 86
    description: Recommended number of passes for thorough cleaning
    min: 1
    max: 4
  energyDensity:
    value: 3.5
    unit: J/cm²
    confidence: 84
    description: Optimal energy density for contaminant removal without substrate
      damage
    min: 2.0
    max: 6.0
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
    alt: Soapstone surface undergoing laser cleaning showing precise contamination
      removal
    url: /images/soapstone-laser-cleaning-hero.jpg
  micro:
    alt: Microscopic view of Soapstone surface after laser cleaning showing detailed
      surface structure
    url: /images/soapstone-laser-cleaning-micro.jpg
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
