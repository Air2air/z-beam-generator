name: Steel
category: Metal
subcategory: Steel
title: Steel Laser Cleaning
description: Laser cleaning parameters for Steel
materialProperties:
  density:
    value: 7.85
    unit: g/cm³
    confidence: 98
    description: Typical density for carbon steel at room temperature
    min: 7.75
    max: 7.9
  meltingPoint:
    value: 1425
    unit: °C
    confidence: 95
    description: Average melting point for medium carbon steel
    min: 1370
    max: 1510
  thermalConductivity:
    value: 50
    unit: W/m·K
    confidence: 92
    description: Thermal conductivity of carbon steel at 20°C
    min: 45
    max: 60
  tensileStrength:
    value: 420
    unit: MPa
    confidence: 90
    description: Typical tensile strength for mild steel
    min: 350
    max: 550
  hardness:
    value: 120
    unit: HB
    confidence: 88
    description: Brinell hardness for annealed carbon steel
    min: 100
    max: 150
  youngsModulus:
    value: 200
    unit: GPa
    confidence: 95
    description: Young's modulus of elasticity
    min: 190
    max: 210
  thermalExpansion:
    value: 12
    unit: 10⁻⁶/°C
    confidence: 90
    description: Linear thermal expansion coefficient at 20-100°C
    min: 11
    max: 13
  specificHeat:
    value: 490
    unit: J/kg·K
    confidence: 88
    description: Specific heat capacity at room temperature
    min: 450
    max: 520
  thermalDiffusivity:
    value: 13
    unit: mm²/s
    confidence: 85
    description: Thermal diffusivity at room temperature
    min: 11
    max: 15
  reflectivity:
    value: 55
    unit: '%'
    confidence: 85
    description: Reflectivity at 1064 nm wavelength (common laser cleaning)
    min: 45
    max: 65
  absorptionCoefficient:
    value: 0.8
    unit: 10⁶/m
    confidence: 82
    description: Optical absorption coefficient at 1064 nm
    min: 0.6
    max: 1.0
  ablationThreshold:
    value: 1.2
    unit: J/cm²
    confidence: 80
    description: Laser ablation threshold for nanosecond pulses at 1064 nm
    min: 0.8
    max: 1.8
  oxidationResistance:
    value: 3
    unit: scale 1-10
    confidence: 85
    description: Relative oxidation resistance in air at elevated temperatures
    min: 2
    max: 4
  crystallineStructure:
    value: BCC/FCC
    unit: crystal system
    confidence: 95
    description: Body-centered cubic (BCC) at room temp, FCC at high temp
    min: BCC
    max: FCC
applications:
- laser cleaning
- surface preparation
machineSettings:
  powerRange:
    value: 100
    unit: W
    confidence: 92
    description: Optimal average power range for Steel surface cleaning
    min: 80
    max: 120
  wavelength:
    value: 1064
    unit: nm
    confidence: 88
    description: Near-infrared wavelength optimal for Steel absorption
    min: null
    max: null
  spotSize:
    value: 100
    unit: μm
    confidence: 84
    description: Beam spot diameter for optimal energy density
    min: 50
    max: 200
  repetitionRate:
    value: 100
    unit: kHz
    confidence: 87
    description: High repetition rate for efficient surface coverage
    min: 50
    max: 200
  pulseWidth:
    value: 10
    unit: ns
    confidence: 85
    description: Nanosecond pulse duration for controlled ablation
    min: 5
    max: 20
  scanSpeed:
    value: 1000
    unit: mm/s
    confidence: 82
    description: Scanning speed for efficient material removal
    min: 500
    max: 2000
  energyDensity:
    value: 5
    unit: J/cm²
    confidence: 89
    description: Fluence threshold for Steel contamination removal
    min: 2
    max: 8
  overlapRatio:
    value: 50
    unit: '%'
    confidence: 83
    description: Optimal pulse overlap for uniform cleaning
    min: 30
    max: 70
  passCount:
    value: 3
    unit: passes
    confidence: 81
    description: Number of passes for complete contamination removal
    min: 1
    max: 5
  laserType:
    value: Fiber Laser
    unit: N/A
    confidence: 90
    description: Recommended laser type for Steel cleaning applications
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
    alt: Steel surface undergoing laser cleaning showing precise contamination removal
    url: /images/steel-laser-cleaning-hero.jpg
  micro:
    alt: Microscopic view of Steel surface after laser cleaning showing detailed surface
      structure
    url: /images/steel-laser-cleaning-micro.jpg
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
