name: Marble
category: Stone
subcategory: Marble
title: Marble Laser Cleaning
description: Laser cleaning parameters for Marble
materialProperties:
  density:
    value: 2.71
    unit: g/cm³
    confidence: 95
    description: Average density of pure calcite marble
    min: 2.6
    max: 2.85
  meltingPoint:
    value: 825
    unit: °C
    confidence: 90
    description: Decomposition temperature where CaCO3 → CaO + CO2
    min: 800
    max: 850
  thermalConductivity:
    value: 2.8
    unit: W/m·K
    confidence: 88
    description: Thermal conductivity at room temperature
    min: 2.5
    max: 3.2
  hardness:
    value: 3.0
    unit: Mohs
    confidence: 95
    description: Mohs hardness scale (calcite mineral)
    min: 2.5
    max: 3.5
  youngsModulus:
    value: 55
    unit: GPa
    confidence: 90
    description: Elastic modulus of calcite marble
    min: 40
    max: 70
  thermalExpansion:
    value: 8.0
    unit: 10⁻⁶/°C
    confidence: 85
    description: Coefficient of thermal expansion (20-100°C)
    min: 6.5
    max: 10.0
  specificHeat:
    value: 0.88
    unit: kJ/kg·K
    confidence: 92
    description: Specific heat capacity at room temperature
    min: 0.84
    max: 0.92
  thermalDiffusivity:
    value: 1.18
    unit: mm²/s
    confidence: 86
    description: Thermal diffusivity calculated from conductivity, density, and specific
      heat
    min: 1.05
    max: 1.35
  compressiveStrength:
    value: 120
    unit: MPa
    confidence: 88
    description: Uniaxial compressive strength
    min: 80
    max: 180
  absorptionCoefficient:
    value: 0.85
    unit: dimensionless
    confidence: 82
    description: Average absorption coefficient for visible to near-IR wavelengths
    min: 0.7
    max: 0.95
  ablationThreshold:
    value: 1.5
    unit: J/cm²
    confidence: 80
    description: Laser ablation threshold for nanosecond pulses at 1064nm
    min: 0.8
    max: 2.5
  porosity:
    value: 0.5
    unit: '%'
    confidence: 85
    description: Typical porosity range for high-quality marble
    min: 0.1
    max: 2.0
  chemicalStability:
    value: Low
    unit: qualitative
    confidence: 95
    description: Susceptible to acid attack and weathering
    min: N/A
    max: N/A
  crystallineStructure:
    value: Hexagonal
    unit: crystal system
    confidence: 98
    description: Calcite crystal structure (rhombohedral)
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
    description: Optimal power range for Marble cleaning without thermal damage
    min: 80
    max: 120
  wavelength:
    value: 1064
    unit: nm
    confidence: 88
    description: Near-IR wavelength optimized for Marble absorption and minimal substrate
      damage
    min: 532
    max: 1064
  spotSize:
    value: 100
    unit: μm
    confidence: 90
    description: Beam spot diameter for precise cleaning with adequate energy density
    min: 50
    max: 200
  repetitionRate:
    value: 20
    unit: kHz
    confidence: 87
    description: Optimal repetition rate for efficient cleaning while maintaining
      thermal control
    min: 10
    max: 50
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
    confidence: 85
    description: Optimal scanning speed for uniform cleaning coverage
    min: 200
    max: 1000
  fluenceThreshold:
    value: 2.5
    unit: J/cm²
    confidence: 88
    description: Energy density threshold for effective contaminant removal without
      damaging marble substrate
    min: 1.5
    max: 4.0
  overlapRatio:
    value: 50
    unit: '%'
    confidence: 83
    description: Optimal overlap between adjacent scan lines for uniform cleaning
    min: 30
    max: 70
  passCount:
    value: 3
    unit: passes
    confidence: 82
    description: Recommended number of passes for thorough cleaning of surface contaminants
    min: 1
    max: 5
  laserType:
    value: Nd:YAG
    unit: n/a
    confidence: 90
    description: Recommended laser type for marble cleaning applications
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
    alt: Marble surface undergoing laser cleaning showing precise contamination removal
    url: /images/marble-laser-cleaning-hero.jpg
  micro:
    alt: Microscopic view of Marble surface after laser cleaning showing detailed
      surface structure
    url: /images/marble-laser-cleaning-micro.jpg
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
