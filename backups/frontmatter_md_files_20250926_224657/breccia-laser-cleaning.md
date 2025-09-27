name: Breccia
category: Stone
subcategory: Breccia
title: Breccia Laser Cleaning
description: Laser cleaning parameters for Breccia
materialProperties:
  density:
    value: 2.65
    unit: g/cm³
    confidence: 85
    description: Average bulk density of typical limestone-based breccia
    min: 2.4
    max: 2.9
  meltingPoint:
    value: 1250
    unit: °C
    confidence: 80
    description: Approximate melting point for carbonate-rich breccia components
    min: 1100
    max: 1400
  thermalConductivity:
    value: 2.5
    unit: W/m·K
    confidence: 82
    description: Thermal conductivity of consolidated breccia rock
    min: 1.8
    max: 3.2
  hardness:
    value: 4.5
    unit: Mohs
    confidence: 88
    description: Composite hardness on Mohs scale (varies by clast composition)
    min: 3.0
    max: 6.0
  youngsModulus:
    value: 45
    unit: GPa
    confidence: 79
    description: Elastic modulus for consolidated breccia
    min: 30
    max: 60
  thermalExpansion:
    value: 8.0
    unit: 10⁻⁶/°C
    confidence: 78
    description: Coefficient of thermal expansion for mixed mineral composition
    min: 5.0
    max: 12.0
  specificHeat:
    value: 0.84
    unit: kJ/kg·K
    confidence: 83
    description: Specific heat capacity at room temperature
    min: 0.75
    max: 0.95
  compressiveStrength:
    value: 120
    unit: MPa
    confidence: 85
    description: Uniaxial compressive strength
    min: 80
    max: 180
  porosity:
    value: 12
    unit: '%'
    confidence: 87
    description: Typical porosity range for well-cemented breccia
    min: 5
    max: 25
  absorptionCoefficient:
    value: 0.65
    unit: dimensionless
    confidence: 75
    description: Average absorption coefficient for visible to near-IR wavelengths
    min: 0.4
    max: 0.85
  ablationThreshold:
    value: 2.5
    unit: J/cm²
    confidence: 72
    description: Approximate laser ablation threshold for nanosecond pulses
    min: 1.5
    max: 4.0
  chemicalStability:
    value: Moderate
    unit: qualitative
    confidence: 82
    description: Resistance to chemical weathering and dissolution
    min: Low
    max: High
applications:
- laser cleaning
- surface preparation
machineSettings:
  powerRange:
    value: 45
    unit: W
    confidence: 90
    description: Optimal average power for Breccia surface cleaning without thermal
      damage
    min: 30
    max: 60
  wavelength:
    value: 1064
    unit: nm
    confidence: 88
    description: Near-IR wavelength optimal for mineral absorption in Breccia composition
    min: 532
    max: 1064
  spotSize:
    value: 80
    unit: μm
    confidence: 82
    description: Optimal beam diameter for precision cleaning of Breccia surface features
    min: 50
    max: 120
  repetitionRate:
    value: 50
    unit: kHz
    confidence: 87
    description: High repetition rate for uniform cleaning coverage
    min: 20
    max: 100
  pulseWidth:
    value: 15
    unit: ns
    confidence: 85
    description: Short pulse duration for efficient ablation of surface contaminants
    min: 10
    max: 25
  scanSpeed:
    value: 500
    unit: mm/s
    confidence: 84
    description: Scan speed balancing cleaning efficiency and surface preservation
    min: 300
    max: 800
  fluenceThreshold:
    value: 2.5
    unit: J/cm²
    confidence: 89
    description: Threshold fluence for effective contaminant removal from Breccia
    min: 1.5
    max: 4.0
  overlapRatio:
    value: 70
    unit: '%'
    confidence: 83
    description: Optimal overlap between adjacent laser tracks for uniform cleaning
    min: 50
    max: 85
  passCount:
    value: 3
    unit: passes
    confidence: 86
    description: Number of passes for thorough cleaning while minimizing substrate
      damage
    min: 1
    max: 5
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
    alt: Breccia surface undergoing laser cleaning showing precise contamination removal
    url: /images/breccia-laser-cleaning-hero.jpg
  micro:
    alt: Microscopic view of Breccia surface after laser cleaning showing detailed
      surface structure
    url: /images/breccia-laser-cleaning-micro.jpg
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
