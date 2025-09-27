name: Iron
category: Metal
subcategory: Iron
title: Iron Laser Cleaning
description: Laser cleaning parameters for Iron
materialProperties:
  density:
    value: 7.87
    unit: g/cm³
    confidence: 98
    description: Density of pure iron at room temperature (20°C)
    min: 7.85
    max: 7.9
  meltingPoint:
    value: 1538
    unit: °C
    confidence: 97
    description: Melting point of pure iron
    min: 1535
    max: 1540
  thermalConductivity:
    value: 80.2
    unit: W/m·K
    confidence: 92
    description: Thermal conductivity of pure iron at 20°C
    min: 78.0
    max: 82.5
  tensileStrength:
    value: 210
    unit: MPa
    confidence: 85
    description: Ultimate tensile strength of pure annealed iron
    min: 180
    max: 250
  hardness:
    value: 60
    unit: HV
    confidence: 82
    description: Vickers hardness of pure annealed iron
    min: 50
    max: 70
  youngsModulus:
    value: 211
    unit: GPa
    confidence: 95
    description: Young's modulus of elasticity
    min: 208
    max: 214
  thermalExpansion:
    value: 11.8
    unit: μm/m·K
    confidence: 90
    description: Linear thermal expansion coefficient (20-100°C)
    min: 11.5
    max: 12.1
  specificHeat:
    value: 449
    unit: J/kg·K
    confidence: 88
    description: Specific heat capacity at room temperature
    min: 440
    max: 460
  thermalDiffusivity:
    value: 23.1
    unit: mm²/s
    confidence: 85
    description: Thermal diffusivity at 20°C
    min: 22.0
    max: 24.5
  absorptionCoefficient:
    value: 0.65
    unit: dimensionless
    confidence: 80
    description: Absorption coefficient for 1064nm Nd:YAG laser
    min: 0.6
    max: 0.7
  reflectivity:
    value: 0.35
    unit: dimensionless
    confidence: 82
    description: Reflectivity at 1064nm wavelength
    min: 0.3
    max: 0.4
  ablationThreshold:
    value: 1.2
    unit: J/cm²
    confidence: 78
    description: Laser ablation threshold for nanosecond pulses at 1064nm
    min: 0.8
    max: 1.6
  oxidationResistance:
    value: 0.1
    unit: mm/year
    confidence: 85
    description: Oxidation rate in dry air at room temperature
    min: 0.05
    max: 0.15
  crystallineStructure:
    value: BCC
    unit: none
    confidence: 98
    description: Body-centered cubic structure (alpha-iron) at room temperature
    min: BCC
    max: BCC
  electricalResistivity:
    value: 9.71
    unit: μΩ·cm
    confidence: 90
    description: Electrical resistivity at 20°C
    min: 9.6
    max: 9.8
applications:
- laser cleaning
- surface preparation
machineSettings:
  powerRange:
    value: 100
    unit: W
    confidence: 92
    description: Optimal average power for Iron oxide removal without substrate damage
    min: 80
    max: 120
  wavelength:
    value: 1064
    unit: nm
    confidence: 88
    description: Near-IR wavelength with good Iron absorption for oxide layer removal
    min: 1030
    max: 1070
  spotSize:
    value: 100
    unit: μm
    confidence: 84
    description: Optimal spot diameter for balancing cleaning efficiency and resolution
    min: 50
    max: 200
  repetitionRate:
    value: 100
    unit: kHz
    confidence: 87
    description: High repetition rate for efficient surface coverage and oxide removal
    min: 50
    max: 200
  pulseWidth:
    value: 10
    unit: ns
    confidence: 85
    description: Nanosecond pulse duration for efficient oxide ablation with minimal
      thermal diffusion
    min: 5
    max: 20
  scanSpeed:
    value: 1000
    unit: mm/s
    confidence: 86
    description: Optimal scanning speed for uniform oxide removal
    min: 500
    max: 2000
  fluenceThreshold:
    value: 2.5
    unit: J/cm²
    confidence: 89
    description: Threshold fluence for effective Iron oxide removal
    min: 1.5
    max: 4.0
  overlapRatio:
    value: 70
    unit: '%'
    confidence: 83
    description: Optimal pulse overlap for uniform cleaning coverage
    min: 50
    max: 85
  passCount:
    value: 3
    unit: passes
    confidence: 82
    description: Typical number of passes required for complete oxide removal
    min: 1
    max: 5
  laserType:
    value: Nd:YAG
    unit: n/a
    confidence: 90
    description: Fiber laser preferred for Iron cleaning applications
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
    alt: Iron surface undergoing laser cleaning showing precise contamination removal
    url: /images/iron-laser-cleaning-hero.jpg
  micro:
    alt: Microscopic view of Iron surface after laser cleaning showing detailed surface
      structure
    url: /images/iron-laser-cleaning-micro.jpg
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
