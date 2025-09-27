name: Crown Glass
category: Glass
subcategory: Crown Glass
title: Crown Glass Laser Cleaning
description: Laser cleaning parameters for Crown Glass
materialProperties:
  density:
    value: 2.52
    unit: g/cm³
    confidence: 95
    description: Typical density for borosilicate crown glass
    min: 2.48
    max: 2.56
  meltingPoint:
    value: 1400
    unit: °C
    confidence: 90
    description: Softening/melting temperature range
    min: 1350
    max: 1450
  thermalConductivity:
    value: 1.1
    unit: W/m·K
    confidence: 92
    description: Low thermal conductivity typical of glass materials
    min: 1.0
    max: 1.2
  hardness:
    value: 6.0
    unit: Mohs
    confidence: 88
    description: Mohs hardness scale
    min: 5.5
    max: 6.5
  youngsModulus:
    value: 72
    unit: GPa
    confidence: 95
    description: Elastic modulus of crown glass
    min: 70
    max: 74
  thermalExpansion:
    value: 8.5
    unit: ×10⁻⁶/°C
    confidence: 88
    description: Coefficient of thermal expansion at 20-300°C
    min: 8.0
    max: 9.0
  thermalDiffusivity:
    value: 0.65
    unit: mm²/s
    confidence: 85
    description: Thermal diffusivity at room temperature
    min: 0.6
    max: 0.7
  specificHeat:
    value: 750
    unit: J/kg·K
    confidence: 90
    description: Specific heat capacity at room temperature
    min: 720
    max: 780
  flexuralStrength:
    value: 70
    unit: MPa
    confidence: 85
    description: Bending strength of pristine glass
    min: 60
    max: 80
  refractiveIndex:
    value: 1.523
    unit: n/a
    confidence: 98
    description: Refractive index at 589 nm (sodium D-line)
    min: 1.52
    max: 1.526
  absorptionCoefficient:
    value: 0.001
    unit: cm⁻¹
    confidence: 82
    description: Absorption coefficient at 1064 nm (typical laser wavelength)
    min: 0.0005
    max: 0.002
  reflectivity:
    value: 4.2
    unit: '%'
    confidence: 90
    description: Surface reflectivity at normal incidence (1064 nm)
    min: 4.0
    max: 4.5
  ablationThreshold:
    value: 5.0
    unit: J/cm²
    confidence: 80
    description: Laser ablation threshold for nanosecond pulses at 1064 nm
    min: 3.0
    max: 8.0
  laserDamageThreshold:
    value: 15
    unit: J/cm²
    confidence: 82
    description: Bulk laser damage threshold for short pulses
    min: 10
    max: 20
  chemicalStability:
    value: 8.5
    unit: scale 1-10
    confidence: 85
    description: Resistance to water and mild chemical attack
    min: 8.0
    max: 9.0
  surfaceRoughness:
    value: 0.5
    unit: nm RMS
    confidence: 88
    description: Typical polished surface roughness
    min: 0.3
    max: 1.0
applications:
- laser cleaning
- surface preparation
machineSettings:
  powerRange:
    value: 15
    unit: W
    confidence: 90
    description: Average power for effective contaminant removal without substrate
      damage
    min: 8
    max: 25
  wavelength:
    value: 1064
    unit: nm
    confidence: 89
    description: Near-IR wavelength for moderate Crown Glass absorption and contaminant
      removal
    min: 532
    max: 1064
  spotSize:
    value: 50
    unit: μm
    confidence: 92
    description: Beam spot diameter for precise cleaning resolution
    min: 30
    max: 100
  repetitionRate:
    value: 20
    unit: kHz
    confidence: 87
    description: Optimal repetition rate for efficient cleaning with thermal management
    min: 10
    max: 50
  fluenceThreshold:
    value: 1.2
    unit: J/cm²
    confidence: 88
    description: Threshold fluence for contaminant ablation while preserving Crown
      Glass substrate
    min: 0.8
    max: 2.0
  pulseWidth:
    value: 10
    unit: ns
    confidence: 85
    description: Nanosecond pulse duration for controlled thermal interaction
    min: 5
    max: 20
  scanSpeed:
    value: 500
    unit: mm/s
    confidence: 85
    description: Optimal scanning speed for uniform cleaning coverage
    min: 200
    max: 1000
  overlapRatio:
    value: 50
    unit: '%'
    confidence: 86
    description: Optimal pulse overlap for uniform cleaning without excessive heat
      accumulation
    min: 30
    max: 70
  passCount:
    value: 2
    unit: passes
    confidence: 84
    description: Recommended number of passes for complete contaminant removal
    min: 1
    max: 4
  energyDensity:
    value: 6.1
    unit: J/cm²
    confidence: 88
    description: Calculated energy density based on spot size and pulse energy
    min: 3.0
    max: 10.0
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
    alt: Crown Glass surface undergoing laser cleaning showing precise contamination
      removal
    url: /images/crown-glass-laser-cleaning-hero.jpg
  micro:
    alt: Microscopic view of Crown Glass surface after laser cleaning showing detailed
      surface structure
    url: /images/crown-glass-laser-cleaning-micro.jpg
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
