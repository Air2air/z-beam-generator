name: Sandstone
category: Stone
subcategory: Sandstone
title: Sandstone Laser Cleaning
description: Laser cleaning parameters for Sandstone
materialProperties:
  density:
    value: 2.32
    unit: g/cm³
    confidence: 95
    description: Bulk density of typical sandstone with moderate porosity
    min: 2.0
    max: 2.65
  meltingPoint:
    value: 1710
    unit: °C
    confidence: 90
    description: Approximate melting point of quartz (primary constituent)
    min: 1650
    max: 1750
  thermalConductivity:
    value: 2.5
    unit: W/m·K
    confidence: 88
    description: Thermal conductivity at room temperature, varies with mineral composition
    min: 1.5
    max: 4.0
  tensileStrength:
    value: 4.5
    unit: MPa
    confidence: 87
    description: Indirect tensile strength (Brazilian test)
    min: 1.0
    max: 10.0
  hardness:
    value: 6.5
    unit: Mohs
    confidence: 92
    description: Mohs hardness scale, primarily determined by quartz content
    min: 6.0
    max: 7.0
  youngsModulus:
    value: 15
    unit: GPa
    confidence: 88
    description: Elastic modulus in compression
    min: 5
    max: 30
  thermalExpansion:
    value: 12.0
    unit: 10⁻⁶/°C
    confidence: 85
    description: Coefficient of thermal expansion (20-100°C range)
    min: 8.0
    max: 15.0
  specificHeat:
    value: 920
    unit: J/kg·K
    confidence: 92
    description: Specific heat capacity at room temperature
    min: 800
    max: 1000
  thermalDiffusivity:
    value: 1.17
    unit: mm²/s
    confidence: 86
    description: Thermal diffusivity calculated from conductivity, density, and specific
      heat
    min: 0.8
    max: 1.5
  porosity:
    value: 15
    unit: '%'
    confidence: 94
    description: Typical porosity range affecting laser absorption and cleaning efficiency
    min: 5
    max: 30
  compressiveStrength:
    value: 70
    unit: MPa
    confidence: 89
    description: Uniaxial compressive strength, varies significantly with cementation
    min: 20
    max: 170
  absorptionCoefficient:
    value: 0.85
    unit: dimensionless
    confidence: 82
    description: Optical absorption coefficient for common laser wavelengths (1064nm)
    min: 0.7
    max: 0.95
  ablationThreshold:
    value: 1.2
    unit: J/cm²
    confidence: 80
    description: Laser ablation threshold for nanosecond pulses at 1064nm
    min: 0.8
    max: 2.0
  surfaceRoughness:
    value: 12.5
    unit: μm Ra
    confidence: 85
    description: Typical surface roughness of cut sandstone surfaces
    min: 5.0
    max: 25.0
applications:
- laser cleaning
- surface preparation
machineSettings:
  powerRange:
    value: 100
    unit: W
    confidence: 92
    description: Optimal average power range for Sandstone cleaning without thermal
      damage
    min: 80
    max: 120
  wavelength:
    value: 1064
    unit: nm
    confidence: 88
    description: Near-infrared wavelength optimized for Sandstone mineral absorption
    min: 1030
    max: 1080
  spotSize:
    value: 100
    unit: μm
    confidence: 90
    description: Optimal beam diameter for precision cleaning of Sandstone surface
      features
    min: 50
    max: 200
  repetitionRate:
    value: 100
    unit: kHz
    confidence: 87
    description: High repetition rate for efficient cleaning with minimal thermal
      accumulation
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
    value: 500
    unit: mm/s
    confidence: 84
    description: Scanning speed balancing cleaning efficiency and surface preservation
    min: 300
    max: 800
  fluenceThreshold:
    value: 2.5
    unit: J/cm²
    confidence: 89
    description: Threshold fluence for effective contaminant removal without damaging
      Sandstone substrate
    min: 1.5
    max: 4.0
  overlapRatio:
    value: 70
    unit: '%'
    confidence: 86
    description: Optimal pulse overlap for uniform cleaning coverage
    min: 60
    max: 80
  passCount:
    value: 3
    unit: passes
    confidence: 83
    description: Recommended number of passes for thorough cleaning without excessive
      exposure
    min: 2
    max: 5
  energyDensity:
    value: 3.2
    unit: J/cm²
    confidence: 88
    description: Optimal energy density for Sandstone cleaning applications
    min: 2.0
    max: 5.0
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
    alt: Sandstone surface undergoing laser cleaning showing precise contamination
      removal
    url: /images/sandstone-laser-cleaning-hero.jpg
  micro:
    alt: Microscopic view of Sandstone surface after laser cleaning showing detailed
      surface structure
    url: /images/sandstone-laser-cleaning-micro.jpg
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
