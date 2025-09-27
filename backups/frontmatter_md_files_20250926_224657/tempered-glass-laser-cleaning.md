name: Tempered Glass
category: Glass
subcategory: Tempered Glass
title: Tempered Glass Laser Cleaning
description: Laser cleaning parameters for Tempered Glass
materialProperties:
  density:
    value: 2.5
    unit: g/cm³
    confidence: 95
    description: Density of tempered soda-lime glass
    min: 2.48
    max: 2.52
  meltingPoint:
    value: 1000
    unit: °C
    confidence: 90
    description: Softening point where glass becomes workable
    min: 980
    max: 1020
  thermalConductivity:
    value: 1.0
    unit: W/m·K
    confidence: 92
    description: Low thermal conductivity typical of glass materials
    min: 0.95
    max: 1.05
  tensileStrength:
    value: 70
    unit: MPa
    confidence: 82
    description: Compressive strength after tempering process
    min: 65
    max: 75
  hardness:
    value: 6.0
    unit: Mohs
    confidence: 88
    description: Mohs hardness scale value
    min: 5.5
    max: 6.5
  youngsModulus:
    value: 72
    unit: GPa
    confidence: 95
    description: Elastic modulus of tempered glass
    min: 70
    max: 74
  thermalExpansion:
    value: 8.5
    unit: ×10⁻⁶/°C
    confidence: 88
    description: Coefficient of thermal expansion at 20-300°C
    min: 8.2
    max: 8.8
  specificHeat:
    value: 840
    unit: J/kg·K
    confidence: 85
    description: Specific heat capacity at room temperature
    min: 800
    max: 880
  flexuralStrength:
    value: 120
    unit: MPa
    confidence: 85
    description: Bending strength after tempering
    min: 110
    max: 130
  absorptionCoefficient:
    value: 0.92
    unit: cm⁻¹ at 1064nm
    confidence: 80
    description: Absorption coefficient for Nd:YAG laser wavelength
    min: 0.85
    max: 0.98
  reflectivity:
    value: 0.04
    unit: fraction
    confidence: 82
    description: Surface reflectivity at normal incidence
    min: 0.03
    max: 0.05
  refractiveIndex:
    value: 1.52
    unit: dimensionless
    confidence: 95
    description: Refractive index at 589nm wavelength
    min: 1.51
    max: 1.53
  ablationThreshold:
    value: 15
    unit: J/cm²
    confidence: 78
    description: Laser ablation threshold for nanosecond pulses
    min: 12
    max: 18
  laserDamageThreshold:
    value: 10
    unit: J/cm²
    confidence: 75
    description: Damage threshold for continuous wave lasers
    min: 8
    max: 12
  chemicalStability:
    value: High
    unit: qualitative
    confidence: 90
    description: Resistance to most chemicals except HF and strong alkalis
    min: Moderate
    max: Very High
  surfaceRoughness:
    value: 0.5
    unit: μm Ra
    confidence: 82
    description: Typical surface roughness after tempering process
    min: 0.3
    max: 0.8
applications:
- laser cleaning
- surface preparation
machineSettings:
  powerRange:
    value: 90
    unit: W
    confidence: 92
    description: Optimal average power for tempered glass surface cleaning without
      thermal damage
    min: 70
    max: 110
  wavelength:
    value: 1064
    unit: nm
    confidence: 88
    description: Near-infrared wavelength with good transmission through glass and
      absorption by contaminants
    min: null
    max: null
  spotSize:
    value: 80
    unit: μm
    confidence: 90
    description: Beam spot diameter for precise cleaning with adequate energy density
    min: 50
    max: 120
  repetitionRate:
    value: 50
    unit: kHz
    confidence: 87
    description: Repetition rate balancing cleaning efficiency and thermal management
    min: 30
    max: 100
  fluenceThreshold:
    value: 2.5
    unit: J/cm²
    confidence: 88
    description: Fluence threshold for effective contaminant removal without glass
      substrate damage
    min: 1.8
    max: 3.2
  pulseWidth:
    value: 12
    unit: ns
    confidence: 85
    description: Pulse duration optimized for controlled ablation of contaminants
    min: 8
    max: 20
  scanSpeed:
    value: 500
    unit: mm/s
    confidence: 86
    description: Optimal scanning speed for uniform cleaning coverage
    min: 300
    max: 800
  overlapRatio:
    value: 50
    unit: '%'
    confidence: 84
    description: Optimal pulse overlap for complete surface coverage without excessive
      heat accumulation
    min: 40
    max: 60
  passCount:
    value: 2
    unit: passes
    confidence: 82
    description: Number of cleaning passes for thorough contaminant removal
    min: 1
    max: 3
  energyDensity:
    value: 3.2
    unit: J/cm²
    confidence: 85
    description: Energy density optimized for contaminant ablation while preserving
      glass integrity
    min: 2.5
    max: 4.0
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
    alt: Tempered Glass surface undergoing laser cleaning showing precise contamination
      removal
    url: /images/tempered-glass-laser-cleaning-hero.jpg
  micro:
    alt: Microscopic view of Tempered Glass surface after laser cleaning showing detailed
      surface structure
    url: /images/tempered-glass-laser-cleaning-micro.jpg
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
