name: Travertine
category: Stone
subcategory: Travertine
title: Travertine Laser Cleaning
description: Laser cleaning parameters for Travertine
materialProperties:
  density:
    value: 2.4
    unit: g/cm³
    confidence: 95
    description: Bulk density of typical travertine stone
    min: 2.3
    max: 2.6
  meltingPoint:
    value: 825
    unit: °C
    confidence: 90
    description: Decomposition temperature of calcium carbonate to calcium oxide
    min: 800
    max: 850
  thermalConductivity:
    value: 2.3
    unit: W/m·K
    confidence: 88
    description: Thermal conductivity at room temperature
    min: 2.1
    max: 2.5
  hardness:
    value: 3.0
    unit: Mohs
    confidence: 95
    description: Mohs hardness scale (calcite-based mineral)
    min: 2.5
    max: 3.5
  youngsModulus:
    value: 40
    unit: GPa
    confidence: 88
    description: Elastic modulus in compression
    min: 35
    max: 45
  thermalExpansion:
    value: 8.0
    unit: 10⁻⁶/°C
    confidence: 85
    description: Coefficient of thermal expansion
    min: 7.5
    max: 8.5
  specificHeat:
    value: 0.84
    unit: kJ/kg·K
    confidence: 90
    description: Specific heat capacity at room temperature
    min: 0.8
    max: 0.88
  thermalDiffusivity:
    value: 1.14
    unit: 10⁻⁶ m²/s
    confidence: 85
    description: Thermal diffusivity calculated from conductivity, density, and specific
      heat
    min: 1.0
    max: 1.3
  compressiveStrength:
    value: 80
    unit: MPa
    confidence: 92
    description: Uniaxial compressive strength
    min: 60
    max: 100
  flexuralStrength:
    value: 15
    unit: MPa
    confidence: 85
    description: Modulus of rupture
    min: 10
    max: 20
  absorptionCoefficient:
    value: 0.85
    unit: dimensionless
    confidence: 82
    description: Estimated absorption coefficient for IR wavelengths (1064 nm)
    min: 0.75
    max: 0.95
  reflectivity:
    value: 0.15
    unit: dimensionless
    confidence: 80
    description: Reflectivity at common laser wavelengths
    min: 0.1
    max: 0.2
  ablationThreshold:
    value: 2.5
    unit: J/cm²
    confidence: 82
    description: Estimated laser ablation threshold for nanosecond pulses
    min: 1.5
    max: 3.5
  porosity:
    value: 12
    unit: '%'
    confidence: 90
    description: Typical porosity range for travertine
    min: 5
    max: 20
  chemicalStability:
    value: Moderate
    unit: qualitative
    confidence: 88
    description: Susceptible to acid attack but stable in alkaline conditions
    min: Poor in acidic environments
    max: Excellent in neutral/alkaline conditions
applications:
- laser cleaning
- surface preparation
machineSettings:
  powerRange:
    value: 90
    unit: W
    confidence: 92
    description: Optimal average power for Travertine surface cleaning without thermal
      damage
    min: 70
    max: 110
  wavelength:
    value: 1064
    unit: nm
    confidence: 88
    description: Near-infrared wavelength optimized for Travertine mineral absorption
    min: 1030
    max: 1080
  spotSize:
    value: 100
    unit: μm
    confidence: 90
    description: Beam spot diameter for precise cleaning control on Travertine surface
    min: 80
    max: 150
  repetitionRate:
    value: 50
    unit: kHz
    confidence: 87
    description: Optimal repetition rate for efficient cleaning with thermal management
    min: 30
    max: 100
  pulseWidth:
    value: 12
    unit: ns
    confidence: 85
    description: Nanosecond pulse duration for controlled ablation of surface contaminants
    min: 8
    max: 20
  scanSpeed:
    value: 500
    unit: mm/s
    confidence: 84
    description: Optimal scanning speed for uniform cleaning coverage
    min: 300
    max: 800
  fluenceThreshold:
    value: 2.5
    unit: J/cm²
    confidence: 89
    description: Minimum fluence required for effective contaminant removal from Travertine
    min: 1.8
    max: 4.0
  overlapRatio:
    value: 50
    unit: '%'
    confidence: 86
    description: Optimal beam overlap for complete surface coverage without over-processing
    min: 40
    max: 60
  passCount:
    value: 3
    unit: passes
    confidence: 88
    description: Recommended number of passes for thorough cleaning of Travertine
      surfaces
    min: 2
    max: 5
  energyDensity:
    value: 8.5
    unit: J/cm²
    confidence: 91
    description: Optimal energy density for Travertine cleaning without substrate
      damage
    min: 6.0
    max: 12.0
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
    alt: Travertine surface undergoing laser cleaning showing precise contamination
      removal
    url: /images/travertine-laser-cleaning-hero.jpg
  micro:
    alt: Microscopic view of Travertine surface after laser cleaning showing detailed
      surface structure
    url: /images/travertine-laser-cleaning-micro.jpg
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
