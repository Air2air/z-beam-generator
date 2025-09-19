# 📋 **FRONTMATTER FIELD ORDERING PROPOSAL**

## 🎯 **Logical Organization for Optimal Readability**

### **Proposed Field Order**

```yaml
---
# === 1. BASIC IDENTIFICATION ===
name: [material-name]
category: [material-category]

# === 2. CONTENT METADATA ===
title: [SEO title]
headline: [descriptive headline]
description: [technical overview]
keywords: [comma-separated keywords]

# === 3. CHEMICAL CLASSIFICATION ===
chemicalProperties:
  symbol: [chemical symbol]
  formula: [chemical formula]
  materialType: [metal/ceramic/polymer/composite]

# === 4. MATERIAL PROPERTIES (Grouped) ===
properties:
  # DENSITY GROUP
  density: [value with unit]
  densityNumeric: [numeric value]
  densityUnit: [unit]
  densityMin: [min value with unit]
  densityMinNumeric: [numeric min]
  densityMinUnit: [unit]
  densityMax: [max value with unit]
  densityMaxNumeric: [numeric max]
  densityMaxUnit: [unit]
  densityPercentile: [unitless percentile]
  
  # MELTING POINT GROUP
  meltingPoint: [value with unit]
  meltingPointNumeric: [numeric value]
  meltingPointUnit: [unit]
  meltingMin: [min value with unit]
  meltingMinNumeric: [numeric min]
  meltingMinUnit: [unit]
  meltingMax: [max value with unit]
  meltingMaxNumeric: [numeric max]
  meltingMaxUnit: [unit]
  meltingPercentile: [unitless percentile]
  
  # THERMAL CONDUCTIVITY GROUP
  thermalConductivity: [value with unit]
  thermalConductivityNumeric: [numeric value]
  thermalConductivityUnit: [unit]
  thermalMin: [min value with unit]
  thermalMinNumeric: [numeric min]
  thermalMinUnit: [unit]
  thermalMax: [max value with unit]
  thermalMaxNumeric: [numeric max]
  thermalMaxUnit: [unit]
  thermalPercentile: [unitless percentile]
  
  # TENSILE STRENGTH GROUP
  tensileStrength: [value with unit]
  tensileStrengthNumeric: [numeric value]
  tensileStrengthUnit: [unit]
  tensileMin: [min value with unit]
  tensileMinNumeric: [numeric min]
  tensileMinUnit: [unit]
  tensileMax: [max value with unit]
  tensileMaxNumeric: [numeric max]
  tensileMaxUnit: [unit]
  tensilePercentile: [unitless percentile]
  
  # HARDNESS GROUP
  hardness: [value with unit]
  hardnessNumeric: [numeric value]
  hardnessUnit: [unit]
  hardnessMin: [min value with unit]
  hardnessMinNumeric: [numeric min]
  hardnessMinUnit: [unit]
  hardnessMax: [max value with unit]
  hardnessMaxNumeric: [numeric max]
  hardnessMaxUnit: [unit]
  hardnessPercentile: [unitless percentile]
  
  # YOUNG'S MODULUS GROUP
  youngsModulus: [value with unit]
  youngsModulusNumeric: [numeric value]
  youngsModulusUnit: [unit]
  modulusMin: [min value with unit]
  modulusMinNumeric: [numeric min]
  modulusMinUnit: [unit]
  modulusMax: [max value with unit]
  modulusMaxNumeric: [numeric max]
  modulusMaxUnit: [unit]
  modulusPercentile: [unitless percentile]
  
  # LASER-SPECIFIC PROPERTIES
  laserType: [laser type]
  wavelength: [optimal wavelength]
  fluenceRange: [fluence range]
  chemicalFormula: [formula]

# === 5. MATERIAL COMPOSITION ===
composition:
- [primary component with percentage]
- [secondary components]

# === 6. LASER MACHINE SETTINGS (Grouped) ===
machineSettings:
  # POWER RANGE GROUP
  powerRange: [value with unit]
  powerRangeNumeric: [numeric value]
  powerRangeUnit: [unit]
  powerRangeMin: [min value with unit]
  powerRangeMinNumeric: [numeric min]
  powerRangeMinUnit: [unit]
  powerRangeMax: [max value with unit]
  powerRangeMaxNumeric: [numeric max]
  powerRangeMaxUnit: [unit]
  
  # PULSE DURATION GROUP
  pulseDuration: [value with unit]
  pulseDurationNumeric: [numeric value]
  pulseDurationUnit: [unit]
  pulseDurationMin: [min value with unit]
  pulseDurationMinNumeric: [numeric min]
  pulseDurationMinUnit: [unit]
  pulseDurationMax: [max value with unit]
  pulseDurationMaxNumeric: [numeric max]
  pulseDurationMaxUnit: [unit]
  
  # WAVELENGTH GROUP
  wavelength: [value with unit and options]
  wavelengthNumeric: [numeric value]
  wavelengthUnit: [unit]
  wavelengthMin: [min value with unit]
  wavelengthMinNumeric: [numeric min]
  wavelengthMinUnit: [unit]
  wavelengthMax: [max value with unit]
  wavelengthMaxNumeric: [numeric max]
  wavelengthMaxUnit: [unit]
  
  # SPOT SIZE GROUP
  spotSize: [value with unit]
  spotSizeNumeric: [numeric value]
  spotSizeUnit: [unit]
  spotSizeMin: [min value with unit]
  spotSizeMinNumeric: [numeric min]
  spotSizeMinUnit: [unit]
  spotSizeMax: [max value with unit]
  spotSizeMaxNumeric: [numeric max]
  spotSizeMaxUnit: [unit]
  
  # REPETITION RATE GROUP
  repetitionRate: [value with unit]
  repetitionRateNumeric: [numeric value]
  repetitionRateUnit: [unit]
  repetitionRateMin: [min value with unit]
  repetitionRateMinNumeric: [numeric min]
  repetitionRateMinUnit: [unit]
  repetitionRateMax: [max value with unit]
  repetitionRateMaxNumeric: [numeric max]
  repetitionRateMaxUnit: [unit]
  
  # FLUENCE RANGE GROUP
  fluenceRange: [value with unit]
  fluenceRangeNumeric: [numeric value]
  fluenceRangeUnit: [unit]
  fluenceRangeMin: [min value with unit]
  fluenceRangeMinNumeric: [numeric min]
  fluenceRangeMinUnit: [unit]
  fluenceRangeMax: [max value with unit]
  fluenceRangeMaxNumeric: [numeric max]
  fluenceRangeMaxUnit: [unit]
  
  # SCANNING SPEED GROUP
  scanningSpeed: [value with unit]
  scanningSpeedNumeric: [numeric value]
  scanningSpeedUnit: [unit]
  scanningSpeedMin: [min value with unit]
  scanningSpeedMinNumeric: [numeric min]
  scanningSpeedMinUnit: [unit]
  scanningSpeedMax: [max value with unit]
  scanningSpeedMaxNumeric: [numeric max]
  scanningSpeedMaxUnit: [unit]
  
  # BEAM AND SAFETY SETTINGS
  beamProfile: [beam profile type]
  beamProfileOptions: [array of options]
  safetyClass: [safety classification]

# === 7. APPLICATIONS ===
applications:
- industry: [industry name]
  detail: [specific application details]

# === 8. COMPATIBILITY ===
compatibility:
- [compatible material 1]
- [compatible material 2]

# === 9. REGULATORY STANDARDS ===
regulatoryStandards: [relevant standards]

# === 10. AUTHOR INFORMATION ===
author: [author name]
author_object:
  id: [author ID]
  name: [full name]
  sex: [m/f]
  title: [academic/professional title]
  country: [country/region]
  expertise: [area of expertise]
  image: [author image path]

# === 11. VISUAL ASSETS ===
images:
  hero:
    alt: [hero image description]
    url: [hero image path]
  micro:
    alt: [microscopic image description]
    url: [microscopic image path]

# === 12. IMPACT METRICS ===
environmentalImpact:
- benefit: [environmental benefit]
  description: [detailed description]

outcomes:
- result: [measurable outcome]
  metric: [specific metric/measurement]
---
```

## 🏗️ **Organizational Principles**

### **1. Logical Flow**
- **Identification** → **Content** → **Chemistry** → **Properties** → **Machine Settings** → **Applications** → **Metadata**

### **2. Grouped Related Fields**
- All numeric/unit components grouped with their parent property
- Min/Max values immediately follow their base property
- Percentiles at the end of each property group

### **3. Hierarchical Structure**
- **Primary Properties**: Most important material characteristics first
- **Machine Settings**: Technical laser parameters grouped by type
- **Application Data**: Industry applications and compatibility
- **Metadata**: Author, images, and impact metrics last

### **4. Consistent Patterns**
- Every numerical property follows: `main → numeric → unit → min → minNumeric → minUnit → max → maxNumeric → maxUnit → percentile`
- Machine settings follow the same pattern for consistency
- Non-numerical fields (safety, beam profile) at the end of their sections

## ✅ **Benefits of This Order**

1. **🔍 Easy Scanning**: Most important info at the top
2. **📊 Grouped Data**: Related fields together for easier processing
3. **🔧 Technical Flow**: Material properties → machine settings → applications
4. **🎯 Logical Grouping**: All numeric components with their parent property
5. **📖 Readable Structure**: Clear sections with consistent patterns
6. **🔄 Maintainable**: Easy to add new properties following existing patterns

## 🚀 **Implementation**

This ordering can be implemented in the generator by:
1. **Field ordering logic** in the enhancement methods
2. **Grouped processing** for properties and machine settings
3. **Consistent patterns** across all materials
4. **Template-based generation** ensuring consistent structure

**This structure provides optimal readability while maintaining all the enhanced numeric/unit separation functionality!** 🎯
