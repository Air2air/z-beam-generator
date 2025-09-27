name: Quartzite
category: Stone
subcategory: Quartzite
title: Quartzite Laser Cleaning
description: Laser cleaning parameters for Quartzite
materialProperties:
  density:
    value: 2.65
    unit: g/cm³
    confidence: 95
    description: Density of pure quartzite, varies slightly with impurities
    min: 2.6
    max: 2.7
  meltingPoint:
    value: 1670
    unit: °C
    confidence: 90
    description: Melting point of crystalline quartz (SiO₂)
    min: 1650
    max: 1710
  thermalConductivity:
    value: 7.6
    unit: W/m·K
    confidence: 88
    description: Thermal conductivity at room temperature, perpendicular to c-axis
    min: 6.5
    max: 8.5
  hardness:
    value: 7.0
    unit: Mohs
    confidence: 95
    description: Mohs hardness scale (quartz mineral hardness)
    min: 6.5
    max: 7.0
  youngsModulus:
    value: 95
    unit: GPa
    confidence: 90
    description: Young's modulus of elasticity
    min: 90
    max: 100
  thermalExpansion:
    value: 12.3
    unit: ×10⁻⁶/°C
    confidence: 85
    description: Coefficient of thermal expansion (20-100°C), parallel to c-axis
    min: 11.0
    max: 13.5
  specificHeat:
    value: 1050
    unit: J/kg·K
    confidence: 92
    description: Specific heat capacity at 25°C
    min: 1000
    max: 1100
  thermalDiffusivity:
    value: 3.1
    unit: mm²/s
    confidence: 86
    description: Thermal diffusivity at room temperature
    min: 2.8
    max: 3.4
  compressiveStrength:
    value: 300
    unit: MPa
    confidence: 85
    description: Uniaxial compressive strength
    min: 250
    max: 350
  absorptionCoefficient:
    value: 0.15
    unit: cm⁻¹
    confidence: 82
    description: Absorption coefficient at 1064 nm (Nd:YAG laser wavelength)
    min: 0.1
    max: 0.2
  reflectivity:
    value: 0.04
    unit: dimensionless
    confidence: 85
    description: Reflectivity at 1064 nm wavelength
    min: 0.03
    max: 0.05
  refractiveIndex:
    value: 1.54
    unit: dimensionless
    confidence: 95
    description: Refractive index at 589 nm (sodium D-line)
    min: 1.53
    max: 1.55
  ablationThreshold:
    value: 8.5
    unit: J/cm²
    confidence: 80
    description: Laser ablation threshold for nanosecond pulses at 1064 nm
    min: 7.0
    max: 10.0
  laserDamageThreshold:
    value: 15
    unit: J/cm²
    confidence: 82
    description: Laser-induced damage threshold for short pulses
    min: 12
    max: 18
  crystallineStructure:
    value: Trigonal
    unit: crystal system
    confidence: 98
    description: Crystal structure of quartz (α-quartz)
    min: N/A
    max: N/A
  porosity:
    value: 1.5
    unit: '%'
    confidence: 85
    description: Typical porosity of dense quartzite
    min: 0.5
    max: 3.0
  chemicalStability:
    value: Excellent
    unit: qualitative
    confidence: 90
    description: Resistance to acids (except HF) and chemical weathering
    min: N/A
    max: N/A
applications:
- laser cleaning
- surface preparation
machineSettings:
  powerRange:
    value: 100
    unit: W
    confidence: 92
    description: Optimal average power for Quartzite surface cleaning without thermal
      damage
    min: 80
    max: 120
  wavelength:
    value: 1064
    unit: nm
    confidence: 88
    description: Near-IR wavelength optimized for Quartzite absorption and minimal
      subsurface damage
    min: 1030
    max: 1080
  spotSize:
    value: 100
    unit: μm
    confidence: 84
    description: Beam spot diameter providing optimal fluence for contaminant ablation
    min: 80
    max: 150
  repetitionRate:
    value: 100
    unit: kHz
    confidence: 87
    description: High repetition rate for efficient surface coverage while maintaining
      thermal management
    min: 50
    max: 200
  pulseWidth:
    value: 10
    unit: ns
    confidence: 85
    description: Nanosecond pulse duration for effective contaminant removal with
      controlled thermal penetration
    min: 5
    max: 20
  scanSpeed:
    value: 500
    unit: mm/s
    confidence: 83
    description: Scan speed balancing cleaning efficiency and thermal accumulation
      control
    min: 300
    max: 800
  overlapRatio:
    value: 50
    unit: '%'
    confidence: 86
    description: Optimal overlap between adjacent scan lines for uniform cleaning
      coverage
    min: 40
    max: 60
  passCount:
    value: 2
    unit: passes
    confidence: 89
    description: Number of passes required for complete contaminant removal without
      substrate damage
    min: 1
    max: 3
  energyDensity:
    value: 12.7
    unit: J/cm²
    confidence: 85
    description: Fluence threshold for effective contaminant removal from Quartzite
      surface
    min: 8.0
    max: 15.0
  dwellTime:
    value: 200
    unit: μs
    confidence: 82
    description: Effective interaction time per spot location for optimal cleaning
      results
    min: 100
    max: 400
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
    alt: Quartzite surface undergoing laser cleaning showing precise contamination
      removal
    url: /images/quartzite-laser-cleaning-hero.jpg
  micro:
    alt: Microscopic view of Quartzite surface after laser cleaning showing detailed
      surface structure
    url: /images/quartzite-laser-cleaning-micro.jpg
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
