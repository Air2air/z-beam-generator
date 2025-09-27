name: Brass
category: Metal
subcategory: Brass
title: Brass Laser Cleaning
description: Laser cleaning parameters for Brass
materialProperties:
  density:
    value: 8.5
    unit: g/cm³
    confidence: 95
    description: Typical density for common brass alloys (60-70% Cu)
    min: 8.4
    max: 8.7
  meltingPoint:
    value: 930
    unit: °C
    confidence: 90
    description: Average melting point for common brass compositions
    min: 900
    max: 960
  thermalConductivity:
    value: 120
    unit: W/m·K
    confidence: 88
    description: Thermal conductivity of typical brass alloys
    min: 110
    max: 130
  tensileStrength:
    value: 340
    unit: MPa
    confidence: 88
    description: Typical tensile strength for annealed brass
    min: 300
    max: 400
  hardness:
    value: 75
    unit: HV
    confidence: 85
    description: Vickers hardness for typical brass compositions
    min: 65
    max: 85
  youngsModulus:
    value: 100
    unit: GPa
    confidence: 90
    description: Elastic modulus of brass alloys
    min: 95
    max: 105
  thermalExpansion:
    value: 19.0
    unit: 10⁻⁶/°C
    confidence: 85
    description: Coefficient of thermal expansion at 20-100°C
    min: 18.0
    max: 20.0
  thermalDiffusivity:
    value: 35.0
    unit: mm²/s
    confidence: 82
    description: Thermal diffusivity at room temperature
    min: 32.0
    max: 38.0
  specificHeat:
    value: 380
    unit: J/kg·K
    confidence: 85
    description: Specific heat capacity at room temperature
    min: 370
    max: 390
  reflectivity:
    value: 65
    unit: '%'
    confidence: 82
    description: Average reflectivity in visible to near-IR range
    min: 60
    max: 70
  absorptionCoefficient:
    value: 0.8
    unit: 10⁶/m
    confidence: 80
    description: Optical absorption coefficient at 1064nm wavelength
    min: 0.7
    max: 0.9
  ablationThreshold:
    value: 1.2
    unit: J/cm²
    confidence: 78
    description: Laser ablation threshold for nanosecond pulses at 1064nm
    min: 0.8
    max: 1.5
  oxidationResistance:
    value: Good
    unit: Qualitative
    confidence: 85
    description: Resistance to atmospheric oxidation and tarnishing
    min: Moderate
    max: Excellent
  corrosionResistance:
    value: Moderate
    unit: Qualitative
    confidence: 82
    description: General corrosion resistance in various environments
    min: Fair
    max: Good
  crystallineStructure:
    value: FCC
    unit: Crystal System
    confidence: 95
    description: Face-centered cubic structure typical for alpha-brass
    min: Alpha Phase
    max: Alpha+Beta Phase
  surfaceRoughness:
    value: 0.4
    unit: μm Ra
    confidence: 80
    description: Typical surface roughness for machined brass surfaces
    min: 0.2
    max: 0.8
applications:
- laser cleaning
- surface preparation
machineSettings:
  powerRange:
    value: 100
    unit: W
    confidence: 92
    description: Optimal average power for Brass oxide removal without substrate damage
    min: 80
    max: 120
  wavelength:
    value: 1064
    unit: nm
    confidence: 88
    description: Near-IR wavelength for optimal Brass absorption and thermal processing
    min: 1030
    max: 1070
  spotSize:
    value: 50
    unit: μm
    confidence: 84
    description: Beam spot diameter for precise cleaning resolution
    min: 30
    max: 100
  repetitionRate:
    value: 100
    unit: kHz
    confidence: 87
    description: High repetition rate for efficient cleaning with thermal management
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
    value: 1000
    unit: mm/s
    confidence: 86
    description: Optimal scanning speed for uniform cleaning coverage
    min: 500
    max: 2000
  fluenceThreshold:
    value: 2.5
    unit: J/cm²
    confidence: 89
    description: Minimum fluence required for effective Brass surface cleaning
    min: 1.5
    max: 4.0
  overlapRatio:
    value: 50
    unit: '%'
    confidence: 83
    description: Optimal beam overlap for uniform cleaning without excessive heat
      accumulation
    min: 30
    max: 70
  passCount:
    value: 3
    unit: passes
    confidence: 82
    description: Recommended number of passes for complete contaminant removal
    min: 1
    max: 5
  laserType:
    value: Fiber Laser
    unit: N/A
    confidence: 90
    description: Recommended laser type for Brass cleaning applications
    min: null
    max: null
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
    alt: Brass surface undergoing laser cleaning showing precise contamination removal
    url: /images/brass-laser-cleaning-hero.jpg
  micro:
    alt: Microscopic view of Brass surface after laser cleaning showing detailed surface
      structure
    url: /images/brass-laser-cleaning-micro.jpg
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
