name: Bronze
category: Metal
subcategory: Bronze
title: Bronze Laser Cleaning
description: Laser cleaning parameters for Bronze
materialProperties:
  density:
    value: 8.7
    unit: g/cm³
    confidence: 95
    description: Typical density for tin bronze alloys (Cu-10%Sn)
    min: 8.5
    max: 8.9
  meltingPoint:
    value: 950
    unit: °C
    confidence: 90
    description: Melting range for common bronze compositions
    min: 850
    max: 1050
  thermalConductivity:
    value: 75
    unit: W/m·K
    confidence: 88
    description: Thermal conductivity at room temperature
    min: 65
    max: 85
  tensileStrength:
    value: 350
    unit: MPa
    confidence: 88
    description: Typical tensile strength for wrought bronze
    min: 300
    max: 450
  hardness:
    value: 85
    unit: HB
    confidence: 85
    description: Brinell hardness for typical bronze compositions
    min: 70
    max: 100
  youngsModulus:
    value: 110
    unit: GPa
    confidence: 90
    description: Elastic modulus of bronze alloys
    min: 100
    max: 120
  thermalExpansion:
    value: 18.5
    unit: 10⁻⁶/°C
    confidence: 85
    description: Coefficient of thermal expansion (20-300°C)
    min: 17.0
    max: 20.0
  thermalDiffusivity:
    value: 0.25
    unit: cm²/s
    confidence: 82
    description: Thermal diffusivity at room temperature
    min: 0.22
    max: 0.28
  specificHeat:
    value: 380
    unit: J/kg·K
    confidence: 85
    description: Specific heat capacity at room temperature
    min: 370
    max: 390
  absorptionCoefficient:
    value: 0.65
    unit: dimensionless
    confidence: 80
    description: Absorption coefficient for near-infrared lasers (1064 nm)
    min: 0.55
    max: 0.75
  reflectivity:
    value: 0.35
    unit: dimensionless
    confidence: 82
    description: Reflectivity at 1064 nm wavelength
    min: 0.25
    max: 0.45
  ablationThreshold:
    value: 1.2
    unit: J/cm²
    confidence: 78
    description: Laser ablation threshold for nanosecond pulses
    min: 0.8
    max: 1.6
  oxidationResistance:
    value: High
    unit: qualitative
    confidence: 90
    description: Natural oxidation resistance due to protective patina formation
    min: Medium
    max: Very High
  corrosionResistance:
    value: Excellent
    unit: qualitative
    confidence: 92
    description: Resistance to atmospheric and seawater corrosion
    min: Good
    max: Excellent
  crystallineStructure:
    value: α-phase solid solution
    unit: crystal structure
    confidence: 95
    description: Face-centered cubic (FCC) structure with tin in solid solution
    min: α-phase
    max: α+δ eutectoid
  surfaceRoughness:
    value: 0.8
    unit: μm Ra
    confidence: 80
    description: Typical as-machined surface roughness
    min: 0.4
    max: 1.5
applications:
- laser cleaning
- surface preparation
machineSettings:
  powerRange:
    value: 100
    unit: W
    confidence: 92
    description: Optimal average power for Bronze oxide removal without substrate
      damage
    min: 80
    max: 120
  wavelength:
    value: 1064
    unit: nm
    confidence: 88
    description: Near-IR wavelength with good Bronze absorption for thermal cleaning
    min: 532
    max: 1064
  spotSize:
    value: 100
    unit: μm
    confidence: 84
    description: Beam spot diameter for optimal energy density on Bronze surface
    min: 50
    max: 200
  repetitionRate:
    value: 100
    unit: kHz
    confidence: 87
    description: High repetition rate for efficient surface cleaning with thermal
      accumulation control
    min: 50
    max: 200
  pulseWidth:
    value: 10
    unit: ns
    confidence: 85
    description: Nanosecond pulse duration for controlled thermal ablation of contaminants
    min: 5
    max: 20
  scanSpeed:
    value: 1000
    unit: mm/s
    confidence: 82
    description: Optimal scanning speed for uniform cleaning coverage
    min: 500
    max: 2000
  overlapRatio:
    value: 50
    unit: '%'
    confidence: 83
    description: Beam overlap percentage for complete surface treatment
    min: 30
    max: 70
  passCount:
    value: 3
    unit: passes
    confidence: 86
    description: Number of cleaning passes for thorough contaminant removal
    min: 1
    max: 5
  energyDensity:
    value: 12.7
    unit: J/cm²
    confidence: 89
    description: Fluence threshold for effective Bronze cleaning without melting
    min: 8
    max: 15
  laserType:
    value: Nd:YAG
    unit: n/a
    confidence: 90
    description: Recommended laser type for Bronze cleaning applications
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
    alt: Bronze surface undergoing laser cleaning showing precise contamination removal
    url: /images/bronze-laser-cleaning-hero.jpg
  micro:
    alt: Microscopic view of Bronze surface after laser cleaning showing detailed
      surface structure
    url: /images/bronze-laser-cleaning-micro.jpg
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
