name: Onyx
category: Stone
subcategory: Onyx
title: Onyx Laser Cleaning
description: Laser cleaning parameters for Onyx
materialProperties:
  density:
    value: 1.2
    unit: g/cm³
    confidence: 95
    description: Density of Markforged Onyx material (Nylon with chopped carbon fiber)
    min: 1.18
    max: 1.22
  meltingPoint:
    value: 180
    unit: °C
    confidence: 90
    description: Glass transition/melting range for nylon-based composite
    min: 175
    max: 185
  thermalConductivity:
    value: 0.25
    unit: W/m·K
    confidence: 88
    description: Thermal conductivity of carbon fiber reinforced nylon
    min: 0.22
    max: 0.28
  tensileStrength:
    value: 40
    unit: MPa
    confidence: 92
    description: Ultimate tensile strength (XY orientation)
    min: 38
    max: 42
  hardness:
    value: 75
    unit: Shore D
    confidence: 85
    description: Hardness on Shore D scale
    min: 72
    max: 78
  youngsModulus:
    value: 2.4
    unit: GPa
    confidence: 90
    description: Elastic modulus in tensile loading
    min: 2.2
    max: 2.6
  thermalExpansion:
    value: 60
    unit: μm/m·°C
    confidence: 85
    description: Coefficient of thermal expansion along print direction
    min: 55
    max: 65
  specificHeat:
    value: 1500
    unit: J/kg·K
    confidence: 82
    description: Specific heat capacity at room temperature
    min: 1450
    max: 1550
  absorptionCoefficient:
    value: 0.85
    unit: dimensionless
    confidence: 88
    description: Laser absorption coefficient for near-IR wavelengths (1064nm)
    min: 0.8
    max: 0.9
  ablationThreshold:
    value: 1.5
    unit: J/cm²
    confidence: 82
    description: Minimum fluence for material removal with nanosecond pulses
    min: 1.2
    max: 1.8
  porosity:
    value: 2.5
    unit: '%'
    confidence: 80
    description: Typical porosity in FDM-printed parts
    min: 1.5
    max: 4.0
  surfaceRoughness:
    value: 8.5
    unit: μm Ra
    confidence: 85
    description: As-printed surface roughness typical for FDM process
    min: 7.0
    max: 10.0
applications:
- laser cleaning
- surface preparation
machineSettings:
  powerRange:
    value: 100
    unit: W
    confidence: 92
    description: Optimal power range for Onyx cleaning without thermal damage
    min: 80
    max: 120
  wavelength:
    value: 1064
    unit: nm
    confidence: 88
    description: Near-IR wavelength optimized for Onyx mineral absorption
    min: 1030
    max: 1080
  spotSize:
    value: 100
    unit: μm
    confidence: 90
    description: Optimal spot size for precision cleaning
    min: 50
    max: 200
  repetitionRate:
    value: 100
    unit: kHz
    confidence: 87
    description: High repetition rate for efficient cleaning coverage
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
    value: 500
    unit: mm/s
    confidence: 84
    description: Scan speed for efficient material removal
    min: 300
    max: 800
  energyDensity:
    value: 12.7
    unit: J/cm²
    confidence: 89
    description: Fluence threshold for effective Onyx cleaning
    min: 8.0
    max: 15.0
  overlapRatio:
    value: 50
    unit: '%'
    confidence: 86
    description: Optimal overlap for uniform cleaning coverage
    min: 40
    max: 60
  passCount:
    value: 3
    unit: passes
    confidence: 88
    description: Number of passes for complete contaminant removal
    min: 2
    max: 5
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
    alt: Onyx surface undergoing laser cleaning showing precise contamination removal
    url: /images/onyx-laser-cleaning-hero.jpg
  micro:
    alt: Microscopic view of Onyx surface after laser cleaning showing detailed surface
      structure
    url: /images/onyx-laser-cleaning-micro.jpg
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
