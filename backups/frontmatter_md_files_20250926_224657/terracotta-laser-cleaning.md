name: Terracotta
category: Masonry
subcategory: Terracotta
title: Terracotta Laser Cleaning
description: Laser cleaning parameters for Terracotta
materialProperties:
  density:
    value: 1.8
    unit: g/cm³
    confidence: 95
    description: Bulk density of typical fired terracotta accounting for porosity
    min: 1.7
    max: 2.0
  meltingPoint:
    value: 1200
    unit: °C
    confidence: 90
    description: Approximate vitrification temperature where terracotta begins to
      melt
    min: 1150
    max: 1250
  thermalConductivity:
    value: 1.2
    unit: W/m·K
    confidence: 88
    description: Thermal conductivity at room temperature, reduced by porosity
    min: 1.0
    max: 1.4
  hardness:
    value: 4
    unit: Mohs
    confidence: 90
    description: Mohs hardness scale for fired clay ceramic
    min: 3.5
    max: 4.5
  youngsModulus:
    value: 15
    unit: GPa
    confidence: 83
    description: Elastic modulus in compression
    min: 12
    max: 18
  thermalExpansion:
    value: 5.5
    unit: 10⁻⁶/°C
    confidence: 85
    description: Coefficient of thermal expansion (20-500°C range)
    min: 4.5
    max: 6.5
  thermalDiffusivity:
    value: 0.6
    unit: mm²/s
    confidence: 82
    description: Thermal diffusivity at room temperature
    min: 0.5
    max: 0.7
  specificHeat:
    value: 900
    unit: J/kg·K
    confidence: 90
    description: Specific heat capacity at room temperature
    min: 850
    max: 950
  porosity:
    value: 15
    unit: '%'
    confidence: 92
    description: Typical open porosity percentage in fired terracotta
    min: 10
    max: 20
  waterAbsorption:
    value: 12
    unit: '%'
    confidence: 94
    description: Water absorption capacity by weight, critical for laser cleaning
    min: 8
    max: 16
  flexuralStrength:
    value: 15
    unit: MPa
    confidence: 85
    description: Modulus of rupture for typical terracotta
    min: 12
    max: 18
  compressiveStrength:
    value: 40
    unit: MPa
    confidence: 88
    description: Uniaxial compressive strength
    min: 35
    max: 45
  absorptionCoefficient:
    value: 0.7
    unit: dimensionless
    confidence: 80
    description: Approximate absorption coefficient for IR wavelengths (1064nm)
    min: 0.6
    max: 0.8
  ablationThreshold:
    value: 2.5
    unit: J/cm²
    confidence: 82
    description: Laser ablation threshold for nanosecond pulses at 1064nm
    min: 2.0
    max: 3.0
  chemicalStability:
    value: High
    unit: qualitative
    confidence: 95
    description: Resistance to atmospheric corrosion and most chemicals
    min: Moderate
    max: Very High
applications:
- laser cleaning
- surface preparation
machineSettings:
  powerRange:
    value: 40
    unit: W
    confidence: 90
    description: Optimal average power for Terracotta surface cleaning without thermal
      damage
    min: 20
    max: 80
  wavelength:
    value: 1064
    unit: nm
    confidence: 88
    description: Near-infrared wavelength optimized for Terracotta mineral absorption
    min: 532
    max: 1064
  spotSize:
    value: 200
    unit: μm
    confidence: 92
    description: Beam spot diameter for precise contamination removal
    min: 100
    max: 500
  repetitionRate:
    value: 20
    unit: kHz
    confidence: 87
    description: Repetition rate for consistent cleaning with thermal management
    min: 10
    max: 50
  pulseWidth:
    value: 100
    unit: ns
    confidence: 85
    description: Pulse duration balancing cleaning efficiency and thermal control
    min: 50
    max: 200
  scanSpeed:
    value: 500
    unit: mm/s
    confidence: 85
    description: Optimal scanning speed for uniform surface treatment
    min: 200
    max: 1000
  energyDensity:
    value: 1.5
    unit: J/cm²
    confidence: 89
    description: Fluence threshold for effective contaminant removal without substrate
      damage
    min: 0.8
    max: 3.0
  overlapRatio:
    value: 50
    unit: '%'
    confidence: 86
    description: Optimal overlap between adjacent scan lines for complete coverage
    min: 30
    max: 70
  passCount:
    value: 3
    unit: passes
    confidence: 84
    description: Number of passes for thorough cleaning with minimal thermal accumulation
    min: 1
    max: 5
  laserType:
    value: Nd:YAG
    unit: 'null'
    confidence: 90
    description: Recommended laser type for Terracotta cleaning applications
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
    alt: Terracotta surface undergoing laser cleaning showing precise contamination
      removal
    url: /images/terracotta-laser-cleaning-hero.jpg
  micro:
    alt: Microscopic view of Terracotta surface after laser cleaning showing detailed
      surface structure
    url: /images/terracotta-laser-cleaning-micro.jpg
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
