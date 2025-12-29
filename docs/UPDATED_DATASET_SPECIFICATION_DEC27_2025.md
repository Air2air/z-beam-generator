# Z-Beam Updated Dataset Specification

**Version**: 3.0  
**Date**: December 27, 2025  
**Status**: Current Production Format  
**Previous Version**: 2.0 (Included extensive Schema.org metadata)

---

## 🎯 Executive Summary

Z-Beam datasets have been streamlined from the comprehensive Schema.org format (v2.0) to a focused technical format (v3.0) that prioritizes:

- **Technical Data First**: Laser parameters, material properties, removal characteristics
- **Simplified Structure**: Removed Schema.org metadata overhead
- **Three Format Support**: JSON (structured), CSV (spreadsheet), TXT (human-readable)
- **Auto-Generated**: Created from frontmatter YAML sources

---

## 📊 Dataset Categories

### 1. **Materials Dataset**
**Purpose**: Laser cleaning parameters for specific materials  
**Files**: `{material-name}-material-dataset.{json|csv|txt}`  
**Location**: `public/datasets/materials/`  
**Count**: ~153 materials × 3 formats = 459 files

### 2. **Contaminants Dataset**
**Purpose**: Contaminant removal techniques and compound safety data  
**Files**: `{contaminant-name}-contamination-contaminant-dataset.{json|csv|txt}`  
**Location**: `public/datasets/contaminants/`  
**Count**: ~98 contaminants × 3 formats = 294 files

---

## 🔄 Version History: What Changed

### **Version 2.0** (Previous - Comprehensive Schema.org Format)

**Extensive Metadata Included:**
- ✅ **Schema.org Compliance**: Full `@context`, `@type`, `@id` markup
- ✅ **SEO-Optimized**: Structured data for search engines
- ✅ **Detailed Attribution**:
  - `creator`: Organization details
  - `author`: Person with job title and affiliation
  - `publisher`: Publishing organization
  - `license`: Creative Commons licensing info
- ✅ **Distribution Metadata**: Multiple download format URLs
- ✅ **Keywords**: Comprehensive keyword arrays
- ✅ **Citations**: Related materials, compounds, safety pages
- ✅ **variableMeasured**: All properties as PropertyValue objects
- ✅ **dateModified**: Last update timestamp
- ✅ **measurementTechnique**: Research methodology description

**Example Structure (v2.0):**
```json
{
  "@context": "https://schema.org",
  "@type": "Dataset",
  "@id": "https://www.z-beam.com/datasets/materials/aluminum-material-dataset#dataset",
  "identifier": "aluminum-material-dataset",
  "name": "Aluminum",
  "description": "Comprehensive laser cleaning parameters...",
  "variableMeasured": [
    {
      "@type": "PropertyValue",
      "name": "Material Characteristics: Density",
      "value": "2.7",
      "unitText": "g/cm³",
      "minValue": 0.53,
      "maxValue": 22.6
    }
  ],
  "citation": [
    {
      "@type": "CreativeWork",
      "name": "Related Material Page",
      "url": "https://www.z-beam.com/materials/..."
    }
  ],
  "distribution": [
    {
      "@type": "DataDownload",
      "encodingFormat": "application/json",
      "contentUrl": "https://www.z-beam.com/datasets/..."
    }
  ],
  "license": {
    "@type": "CreativeWork",
    "name": "Creative Commons Attribution 4.0 International",
    "url": "https://creativecommons.org/licenses/by/4.0/"
  },
  "creator": {
    "@type": "Organization",
    "name": "Z-Beam Laser Cleaning Research Lab"
  },
  "author": {
    "@type": "Person",
    "name": "Dr. John Smith",
    "jobTitle": "Senior Materials Scientist",
    "affiliation": {
      "@type": "Organization",
      "name": "Z-Beam Research"
    }
  },
  "keywords": ["aluminum", "laser cleaning", "metal"],
  "dateModified": "2025-12-27",
  "measurementTechnique": "Experimental laser ablation studies..."
}
```

### **Version 3.0** (Current - Streamlined Technical Format)

**Focused on Technical Data:**
- ✅ **Direct Property Access**: Nested object structure
- ✅ **No Schema.org Overhead**: Removed metadata layers
- ✅ **Simplified JSON**: Easier programmatic access
- ✅ **TXT Format**: Human-readable with clear sections
- ❌ **Removed**: citations, distribution, keywords, license details
- ❌ **Removed**: variableMeasured array wrapper
- ❌ **Removed**: @type PropertyValue wrappers
- ⚠️ **Minimal Metadata**: Only name, description, version remain

**Example Structure (v3.0):**
```json
{
  "@context": "https://schema.org",
  "@type": "Dataset",
  "@id": "https://www.z-beam.com/datasets/materials/aluminum-material-dataset#dataset",
  "identifier": "aluminum-material-dataset",
  "name": "Aluminum",
  "description": "TEST description...",
  "material": {
    "machineSettings": {
      "laserPower": {
        "min": 50,
        "max": 500,
        "value": 100,
        "unit": "W"
      }
    },
    "materialProperties": {
      "density": {
        "value": 2.7,
        "unit": "g/cm³",
        "min": 0.53,
        "max": 22.6
      }
    }
  },
  "version": "2.0",
  "creator": {
    "@type": "Organization",
    "name": "Z-Beam Laser Cleaning Research Lab"
  },
  "publisher": {
    "@type": "Organization",
    "name": "Z-Beam Laser Cleaning Research Lab"
  }
}
```

---

## 📋 Current Dataset Structure (v3.0)

### **Materials Dataset Structure**

#### **TXT Format** (Human-Readable)
```
DATASET: Aluminum Laser Cleaning Parameters
================================================================================

DESCRIPTION:


MACHINE SETTINGS:
--------------------------------------------------------------------------------
  powerRange: 100 W (range: 1.0-120 W)
  wavelength: 1064 nm (range: 355-10640 nm)
  spotSize: 50 μm (range: 0.1-500 μm)
  repetitionRate: 50 kHz (range: 1-200 kHz)
  energyDensity: 5.1 J/cm² (range: 0.1-20.0 J/cm²)
  pulseWidth: 10 ns (range: 0.1-1000 ns)
  scanSpeed: 500 mm/s (range: 10-5000 mm/s)
  passCount: 3 passes (range: 1-10 passes)
  overlapRatio: 50 % (range: 10-90 %)

MATERIAL PROPERTIES:
--------------------------------------------------------------------------------

Laser-Material Interaction:
  thermalConductivity: 237.0 W/(m·K) (range: 7.0-430 W/(m·K))
  thermalExpansion: 23.1 ×10^{-6}/K (range: 0.5-33 ×10^{-6}/K)
  absorptionCoefficient: 1.2 ×10^7 m^{-1}
  ablationThreshold: 2.5 J/cm² (range: 2.0-8.0 J/cm²)
  laserDamageThreshold: 1.8 J/cm² (range: 0.1-20.0 J/cm²)

Material Characteristics:
  density: 2.7 g/cm³ (range: 0.53-22.6 g/cm³)
  porosity: 0 % (max: 15.0 %)
  surfaceRoughness: 0.8 μm (range: 0.4-150 μm)
  tensileStrength: 90.0 MPa (range: 3.0-3000.0 MPa)
  youngsModulus: 70.0 GPa (range: 5-600 GPa)
  hardness: 0.2744 GPa (range: 0.5-3500 GPa)
```

#### **JSON Format** (Machine-Readable)
```json
{
  "@context": "https://schema.org",
  "@type": "Dataset",
  "@id": "https://www.z-beam.com/datasets/materials/aluminum-material-dataset#dataset",
  "identifier": "aluminum-material-dataset",
  "name": "Aluminum",
  "description": "Comprehensive laser cleaning parameters for aluminum surfaces...",
  
  "material": {
    "name": "Aluminum",
    "slug": "aluminum",
    "classification": {
      "category": "metals",
      "subcategory": "light-metals"
    },
    
    "machineSettings": {
      "laserPower": {
        "value": 100,
        "unit": "W",
        "min": 50,
        "max": 500,
        "description": "Typical range for industrial cleaning..."
      },
      "wavelength": {
        "value": 1064,
        "unit": "nm",
        "min": 355,
        "max": 10640
      },
      "spotSize": {
        "value": 50,
        "unit": "μm",
        "min": 0.1,
        "max": 500
      },
      "frequency": {
        "value": 50,
        "unit": "kHz",
        "min": 1,
        "max": 200
      },
      "pulseWidth": {
        "value": 10,
        "unit": "ns",
        "min": 0.1,
        "max": 1000
      },
      "scanSpeed": {
        "value": 500,
        "unit": "mm/s",
        "min": 10,
        "max": 5000
      },
      "passCount": {
        "value": 3,
        "unit": "passes",
        "min": 1,
        "max": 10
      },
      "overlapRatio": {
        "value": 50,
        "unit": "%",
        "min": 10,
        "max": 90
      }
    },
    
    "materialProperties": {
      "laserMaterialInteraction": {
        "thermalConductivity": {
          "value": 237.0,
          "unit": "W/(m·K)",
          "confidence": 92,
          "min": 7.0,
          "max": 430
        },
        "thermalExpansion": {
          "value": 23.1,
          "unit": "×10^{-6}/K",
          "confidence": 89,
          "min": 0.5,
          "max": 33
        },
        "ablationThreshold": {
          "value": 2.5,
          "unit": "J/cm²",
          "confidence": 83,
          "min": 2.0,
          "max": 8.0
        }
      },
      "materialCharacteristics": {
        "density": {
          "value": 2.7,
          "unit": "g/cm³",
          "confidence": 100,
          "min": 0.53,
          "max": 22.6
        },
        "hardness": {
          "value": 0.2744,
          "unit": "GPa",
          "confidence": 87
        }
      }
    }
  },
  
  "version": "2.0",
  "creator": {
    "@type": "Organization",
    "name": "Z-Beam Laser Cleaning Research Lab",
    "url": "https://www.z-beam.com"
  },
  "publisher": {
    "@type": "Organization",
    "name": "Z-Beam Laser Cleaning Research Lab",
    "url": "https://www.z-beam.com"
  }
}
```

#### **CSV Format** (Spreadsheet)
```csv
Property,Value,Unit,Min,Max,Confidence,Category,Subcategory
name,Aluminum,,,,,"",""
thermalConductivity,237.0,W/(m·K),7.0,430,92,laserMaterialInteraction,thermal
thermalExpansion,23.1,×10^{-6}/K,0.5,33,89,laserMaterialInteraction,thermal
ablationThreshold,2.5,J/cm²,2.0,8.0,83,laserMaterialInteraction,laser
density,2.7,g/cm³,0.53,22.6,100,materialCharacteristics,physical
hardness,0.2744,GPa,,,87,materialCharacteristics,mechanical
laserPower,100,W,50,500,,machineSettings,power
wavelength,1064,nm,355,10640,,machineSettings,optics
```

---

### **Contaminants Dataset Structure**

#### **TXT Format** (Human-Readable)
```
DATASET: Algae and Lichen Growth Contamination Pattern
================================================================================

DESCRIPTION:
Algae and Lichen Growth (Chlorophyll, Polysaccharides, Minerals) is a common 
contamination pattern affecting 38 different material types.

CONTAMINANT PROPERTIES:
--------------------------------------------------------------------------------

Laser Parameters:
  beam_profile: flat_top
  fluence_range: {'max_j_cm2': 1.2, 'min_j_cm2': 0.3, 'recommended_j_cm2': 0.8}
  overlap_percentage: 50 %
  polarization: any
  pulse_duration_range: {'max_ns': 200, 'min_ns': 10, 'recommended_ns': 50}
  repetition_rate_khz: 50 kHz (range: 20-200 kHz)
  scan_speed_mm_s: 1000 mm/s (range: 500-2000 mm/s)
  spot_size_mm: 0.1 mm (range: 0.05-0.3 mm)
  wavelength_preference: 1064, 532 nm

Optical Properties:
  wavelength_1064nm: 120 cm⁻¹ (absorption)
  wavelength_355nm: 2200 cm⁻¹ (absorption)
  wavelength_532nm: 850 cm⁻¹ (absorption)
  wavelength_1064nm: 0.15 ratio (reflectivity)
  wavelength_355nm: 0.05 ratio (reflectivity)
  imaginary_part: 0.012 dimensionless
  real_part: 1.38 dimensionless
  transmission_depth: 45 μm

Thermal Properties:
  pulse_duration_100ns: 0.4 J/cm²
  pulse_duration_10ns: 0.6 J/cm²
  decomposition_temperature: 180 °C
  heat_affected_zone_depth: 15 μm
  specific_heat: 4200 J/(kg·K)
  thermal_conductivity: 0.6 W/(m·K)
  thermal_diffusivity: 0.14 mm²/s
  vaporization_temperature: 250 °C

Removal Characteristics:
  damage_risk_to_substrate: low
  primary_mechanism: thermal_ablation
  area_coverage_rate_cm2_min: 480 cm²/min
  typical_scan_speed_mm_s: 800 mm/s
  optimal_passes: 2 passes
  diminishing_returns_after: 3
  single_pass: 0.85 ratio
  color_change: no
  residual_stress: none
  roughness_increase: minimal
```

#### **JSON Format** (Machine-Readable)
```json
{
  "@context": "https://schema.org",
  "@type": "Dataset",
  "@id": "https://www.z-beam.com/datasets/contaminants/algae-growth-contamination-contaminant-dataset#dataset",
  "identifier": "algae-growth-contamination-contaminant-dataset",
  "name": "Algae and Lichen Growth",
  "description": "Algae and Lichen Growth (Chlorophyll, Polysaccharides, Minerals) biological contamination...",
  
  "contaminant": {
    "name": "Algae and Lichen Growth",
    "classification": {
      "category": "biological",
      "type": "growth"
    },
    
    "properties": {
      "composition": [
        "Chlorophyll",
        "Polysaccharides",
        "Minerals"
      ],
      "absorptionRate": {
        "wavelength_1064nm": 120,
        "wavelength_355nm": 2200,
        "wavelength_532nm": 850
      },
      "reflectivity": {
        "wavelength_1064nm": 0.15,
        "wavelength_355nm": 0.05,
        "wavelength_532nm": 0.08
      },
      "opticalProperties": {
        "imaginaryPart": 0.012,
        "realPart": 1.38,
        "transmissionDepth": {
          "value": 45,
          "unit": "μm"
        }
      },
      "thermalProperties": {
        "decompositionTemperature": {
          "value": 180,
          "unit": "°C"
        },
        "specificHeat": {
          "value": 4200,
          "unit": "J/(kg·K)"
        },
        "thermalConductivity": {
          "value": 0.6,
          "unit": "W/(m·K)"
        }
      }
    },
    
    "compounds": [
      {
        "name": "Nitrogen Oxides",
        "formula": "NOx",
        "casNumber": "Various",
        "hazardLevel": "toxic",
        "healthEffects": "Irritant effects on respiratory system...",
        "frequency": "unknown",
        "severity": "moderate"
      },
      {
        "name": "Carbon Dioxide",
        "formula": "CO₂",
        "casNumber": "124-38-9",
        "hazardLevel": "asphyxiant",
        "healthEffects": "Asphyxiant that displaces breathable air...",
        "frequency": "unknown",
        "severity": "low"
      }
    ],
    
    "removalTechniques": {
      "laserPower": {
        "min_j_cm2": 0.3,
        "max_j_cm2": 1.2,
        "recommended_j_cm2": 0.8
      },
      "wavelength": {
        "value": [1064, 532]
      },
      "pulseWidth": {
        "min_ns": 10,
        "max_ns": 200,
        "recommended_ns": 50
      },
      "scanSpeed": {
        "min": 500,
        "max": 2000,
        "recommended": 1000,
        "unit": "mm/s"
      },
      "spotSize": {
        "min": 0.05,
        "max": 0.3,
        "recommended": 0.1,
        "unit": "mm"
      },
      "frequency": {
        "min": 20,
        "max": 200,
        "recommended": 50,
        "unit": "kHz"
      },
      "removalRate": {
        "optimal_passes": 2,
        "diminishing_returns_after": 3,
        "single_pass": 0.85
      }
    }
  },
  
  "version": "2.0",
  "creator": {
    "@type": "Organization",
    "name": "Z-Beam Laser Cleaning Research Lab",
    "url": "https://www.z-beam.com"
  },
  "publisher": {
    "@type": "Organization",
    "name": "Z-Beam Laser Cleaning Research Lab",
    "url": "https://www.z-beam.com"
  }
}
```

---

## 🔑 Key Data Elements

### **Materials Datasets Include:**

#### **Machine Settings** (Required)
- `laserPower` - Power range (W) with min/max/value
- `wavelength` - Operating wavelength (nm)
- `spotSize` - Beam diameter (μm)
- `frequency` - Repetition rate (kHz)
- `pulseWidth` - Pulse duration (ns)
- `scanSpeed` - Scanning velocity (mm/s)
- `passCount` - Number of cleaning passes
- `overlapRatio` - Pulse overlap percentage (%)

#### **Material Properties** (Required)
**Laser-Material Interaction:**
- `thermalConductivity` - Heat transfer (W/(m·K))
- `thermalExpansion` - Expansion coefficient (×10^{-6}/K)
- `thermalDiffusivity` - Thermal diffusion (×10^{-5} m²/s)
- `specificHeat` - Heat capacity (J/(kg·K))
- `absorptionCoefficient` - Light absorption (×10^7 m^{-1})
- `ablationThreshold` - Material removal threshold (J/cm²)
- `laserDamageThreshold` - Damage threshold (J/cm²)
- `laserReflectivity` - Surface reflectance (dimensionless)

**Material Characteristics:**
- `density` - Mass density (g/cm³)
- `porosity` - Void percentage (%)
- `surfaceRoughness` - Surface texture (μm)
- `tensileStrength` - Tensile limit (MPa)
- `youngsModulus` - Elastic modulus (GPa)
- `hardness` - Surface hardness (GPa)
- `meltingPoint` - Melting temperature (K)
- `boilingPoint` - Boiling temperature (K)

#### **Safety Data** (Optional)
- Exposure limits, protective equipment, handling procedures

---

### **Contaminants Datasets Include:**

#### **Laser Parameters** (Required)
- `beam_profile` - Beam shape (flat_top, gaussian)
- `fluence_range` - Energy density range (J/cm²)
- `pulse_duration_range` - Pulse width range (ns)
- `wavelength_preference` - Optimal wavelengths (nm)
- `scan_speed_mm_s` - Scanning speed (mm/s)
- `spot_size_mm` - Beam diameter (mm)
- `repetition_rate_khz` - Pulse frequency (kHz)
- `overlap_percentage` - Pulse overlap (%)
- `polarization` - Beam polarization (linear, circular, any)

#### **Optical Properties** (Required)
- `wavelength_1064nm` - Absorption at 1064nm (cm⁻¹)
- `wavelength_532nm` - Absorption at 532nm (cm⁻¹)
- `wavelength_355nm` - Absorption at 355nm (cm⁻¹)
- `reflectivity` - Reflectance ratios per wavelength
- `imaginary_part` - Complex refractive index imaginary
- `real_part` - Complex refractive index real
- `transmission_depth` - Light penetration depth (μm)

#### **Thermal Properties** (Required)
- `decomposition_temperature` - Breakdown temp (°C)
- `vaporization_temperature` - Evaporation temp (°C)
- `specific_heat` - Heat capacity (J/(kg·K))
- `thermal_conductivity` - Heat transfer (W/(m·K))
- `thermal_diffusivity` - Thermal diffusion (mm²/s)
- `heat_affected_zone_depth` - HAZ depth (μm)
- `pulse_duration_100ns` - Threshold at 100ns (J/cm²)
- `pulse_duration_10ns` - Threshold at 10ns (J/cm²)

#### **Removal Characteristics** (Required)
- `primary_mechanism` - Removal method (thermal_ablation, photomechanical, etc.)
- `optimal_passes` - Best number of passes
- `diminishing_returns_after` - When efficiency drops
- `single_pass` - First pass efficiency ratio
- `area_coverage_rate_cm2_min` - Cleaning speed (cm²/min)
- `typical_scan_speed_mm_s` - Standard scan speed (mm/s)
- `damage_risk_to_substrate` - Risk level (low, medium, high)
- `color_change` - Substrate color change (yes/no)
- `residual_stress` - Induced stress (none, minimal, moderate)
- `roughness_increase` - Surface roughness change

#### **Compounds** (Required Array)
Each compound entry includes:
- `name` - Chemical name
- `formula` - Chemical formula
- `casNumber` - CAS registry number
- `hazardLevel` - Hazard classification (toxic, irritant, asphyxiant, etc.)
- `healthEffects` - Health impact description (truncated to ~150 chars)
- `frequency` - Occurrence frequency (common, rare, unknown)
- `severity` - Impact severity (low, moderate, high)

---

## 📦 Data Sources & Generation

### **Source Files**
All datasets are **auto-generated** from frontmatter YAML files:
- Materials: `frontmatter/materials/{material-name}.yaml`
- Contaminants: `frontmatter/contaminants/{contaminant-name}.yaml`

### **Generation Process**
1. Frontmatter YAML parsed
2. Data validated against schemas
3. Three formats generated simultaneously:
   - **JSON**: Full structured data
   - **CSV**: Flattened tabular format
   - **TXT**: Human-readable sections
4. Files written to `public/datasets/`

### **Schema Validation**
- Materials: `schemas/dataset-material.json`
- Contaminants: `schemas/dataset-contaminant.json`

---

## 🎨 Format Specifications

### **JSON Format**
- **Encoding**: UTF-8
- **Indentation**: 2 spaces
- **Structure**: Nested objects for logical grouping
- **Null Handling**: `null` for missing values
- **Arrays**: Used for lists (compounds, wavelengths)

### **CSV Format**
- **Encoding**: UTF-8
- **Delimiter**: Comma (`,`)
- **Quote Character**: Double quote (`"`)
- **Headers**: First row contains column names
- **Flatten Strategy**: Nested objects converted to dot notation
- **Array Handling**: Multiple rows for array items OR JSON string

### **TXT Format**
- **Encoding**: UTF-8
- **Section Separators**: 
  - Main title: `====` (80 chars)
  - Subsections: `----` (80 chars)
- **Indentation**: 2 spaces for nested properties
- **Value Format**: `{key}: {value} {unit}`
- **Range Format**: `(range: {min}-{max})`

---

## 📈 Data Quality & Confidence

### **Confidence Scores**
Many properties include confidence scores (0-100):
- **90-100**: High confidence (measured/well-documented)
- **70-89**: Medium confidence (calculated/estimated)
- **50-69**: Low confidence (approximated)
- **<50**: Very low confidence (placeholder)

### **Data Sources**
Properties may include `source` attribute:
- `measured` - Experimental data
- `calculated` - Computed from other properties
- `ai_research` - AI-generated research
- `literature` - Published research papers
- `manufacturer` - Equipment specifications

---

## 🚀 Usage Examples

### **JavaScript/TypeScript**
```typescript
// Load material dataset
const response = await fetch('/datasets/materials/aluminum-material-dataset.json');
const data = await response.json();

// Access machine settings
const laserPower = data.material.machineSettings.laserPower.value; // 100
const unit = data.material.machineSettings.laserPower.unit; // "W"
const range = `${data.material.machineSettings.laserPower.min}-${data.material.machineSettings.laserPower.max}`;

// Access properties
const density = data.material.materialProperties.materialCharacteristics.density.value;
const thermalCond = data.material.materialProperties.laserMaterialInteraction.thermalConductivity.value;
```

### **Python**
```python
import json

# Load contaminant dataset
with open('public/datasets/contaminants/algae-growth-contamination-contaminant-dataset.json') as f:
    data = json.load(f)

# Access laser parameters
fluence = data['contaminant']['removalTechniques']['laserPower']['recommended_j_cm2']
wavelengths = data['contaminant']['removalTechniques']['wavelength']['value']

# Access compounds
for compound in data['contaminant']['compounds']:
    print(f"{compound['name']} ({compound['formula']}): {compound['hazardLevel']}")
```

### **Excel/Google Sheets**
1. Open CSV file directly
2. Data → Text to Columns (if needed)
3. Apply filters to headers
4. Sort/pivot as needed

---

## 🔍 Schema Validation Rules

### **Materials Schema** (`schemas/dataset-material.json`)

#### **Required Top-Level Fields**
- `@context` - Must be `"https://schema.org"`
- `@type` - Must be `"Dataset"`
- `@id` - Must match pattern: `https://www.z-beam.com/materials/{name}#dataset`
- `name` - Material name (3+ chars)
- `description` - Description (50+ chars)
- `material` - Material data object

#### **Required material.machineSettings Fields**
- `powerRange` - parameterValue object
- `wavelength` - parameterValue object
- `spotSize` - parameterValue object
- `repetitionRate` - parameterValue object
- `pulseWidth` - parameterValue object
- `scanSpeed` - parameterValue object

#### **Required material.materialProperties Fields**
- Must have at least 1 property group
- Each property group contains multiple property objects
- Each property: `{value, unit, min?, max?, confidence?, source?}`

---

### **Contaminants Schema** (`schemas/dataset-contaminant.json`)

#### **Required Top-Level Fields**
- `@context` - Must be `"https://schema.org"`
- `@type` - Must be `"Dataset"`
- `@id` - Must match pattern: `https://www.z-beam.com/contaminants/{name}#dataset`
- `name` - Contaminant name (3+ chars)
- `description` - Description (50+ chars)
- `contaminant` - Contaminant data object

#### **Required contaminant Fields**
- `name` - Contaminant name
- `classification` - Category/type object
- `properties` - Properties object (minProperties: 1)
- `removalTechniques` - Removal data object

#### **Required contaminant.compounds Array**
Each compound must have:
- `formula` - Chemical formula
- `name` - Compound name
- `hazards` - Array of hazard strings (optional in current version)

---

## 📊 Metadata Comparison Table

| **Metadata Element** | **v2.0 (Previous)** | **v3.0 (Current)** | **Notes** |
|---------------------|---------------------|-------------------|-----------|
| `@context` | ✅ Schema.org | ✅ Schema.org | Retained |
| `@type` | ✅ Dataset | ✅ Dataset | Retained |
| `@id` | ✅ Full URL | ✅ Full URL | Retained |
| `identifier` | ✅ Included | ✅ Included | Retained |
| `name` | ✅ Full name | ✅ Full name | Retained |
| `description` | ✅ Rich text | ⚠️ Minimal/TEST | Degraded |
| `variableMeasured` | ✅ PropertyValue array | ❌ Removed | Flattened to nested objects |
| `citation` | ✅ Related pages array | ❌ Removed | SEO metadata gone |
| `distribution` | ✅ 3 download URLs | ❌ Removed | Format links gone |
| `keywords` | ✅ Comprehensive array | ❌ Removed | SEO terms gone |
| `dateModified` | ✅ ISO date | ❌ Removed | Update tracking lost |
| `license` | ✅ CC-BY-4.0 details | ❌ Removed | Licensing unclear |
| `measurementTechnique` | ✅ Methodology text | ❌ Removed | Research context lost |
| `creator` | ✅ Organization details | ✅ Basic org | Simplified |
| `author` | ✅ Person + affiliation | ❌ Removed | Attribution lost |
| `publisher` | ✅ Organization details | ✅ Basic org | Simplified |
| `version` | ❌ Not included | ✅ "2.0" | Added but inconsistent |

---

## ⚠️ Breaking Changes from v2.0

### **Removed Elements**
1. **variableMeasured Array** - All properties were wrapped in PropertyValue objects
2. **citation Array** - Links to related materials, compounds, safety pages
3. **distribution Array** - Download URLs for JSON/CSV/TXT formats
4. **keywords Array** - SEO-optimized keyword lists
5. **dateModified** - Last update timestamp
6. **license Object** - Creative Commons license details with URL
7. **measurementTechnique String** - Research methodology description
8. **author Object** - Individual attribution with job title & affiliation

### **Simplified Elements**
1. **creator** - Reduced to name + URL only
2. **publisher** - Reduced to name + URL only
3. **description** - Often placeholder "TEST description" instead of rich content

### **Added Elements**
1. **version** - Now includes version number ("2.0")
2. **Direct nesting** - Properties nested under material/contaminant without PropertyValue wrapper

---

## 🎯 Recommendations for Future Versions

### **For v3.1 (Minor Update)**
1. ✅ **Restore Descriptions**: Replace "TEST description" with actual content
2. ✅ **Add dateModified**: Track update timestamps
3. ✅ **Add License Reference**: Simple license string or URL
4. ✅ **Version Consistency**: Ensure version field matches actual format version

### **For v4.0 (Major Update - Hybrid Approach)**
Consider **dual format generation**:

#### **Format A: Technical Dataset** (Current v3.0)
- Optimized for programmatic access
- Minimal metadata overhead
- Fast loading
- Direct property access

#### **Format B: SEO-Optimized Dataset** (Enhanced v2.0)
- Full Schema.org compliance
- Rich metadata for search engines
- Citation links for credibility
- Distribution metadata
- Keywords for discoverability

**Implementation**: Generate both simultaneously
- `{name}-dataset.json` - Technical format
- `{name}-dataset-seo.json` - SEO format
- Same TXT/CSV formats

**Benefits**:
- ✅ Technical users get streamlined data
- ✅ Search engines get rich metadata
- ✅ No breaking changes
- ✅ Backwards compatible

---

## 📝 Migration Guide

### **From v2.0 to v3.0**

#### **Code Changes Required**

**Before (v2.0):**
```javascript
// Accessing property through variableMeasured array
const densityProp = data.variableMeasured.find(
  prop => prop.name === "Material Characteristics: Density"
);
const density = parseFloat(densityProp.value);
const unit = densityProp.unitText;
```

**After (v3.0):**
```javascript
// Direct property access
const density = data.material.materialProperties.materialCharacteristics.density.value;
const unit = data.material.materialProperties.materialCharacteristics.density.unit;
```

#### **Citation Links**

**Before (v2.0):**
```javascript
// Related materials from citation array
const relatedMaterials = data.citation
  .filter(cite => cite.url.includes('/materials/'))
  .map(cite => cite.name);
```

**After (v3.0):**
```javascript
// Citations removed - implement alternative:
// 1. Query frontmatter for relationships
// 2. Use materials_affected array if available
// 3. Implement graph database queries
```

#### **Distribution URLs**

**Before (v2.0):**
```javascript
// Get download URLs from distribution array
const jsonUrl = data.distribution.find(
  d => d.encodingFormat === 'application/json'
).contentUrl;
```

**After (v3.0):**
```javascript
// Construct URLs manually
const baseUrl = 'https://www.z-beam.com/datasets';
const materialSlug = data.identifier;
const jsonUrl = `${baseUrl}/${materialSlug}.json`;
```

---

## 🔗 Related Documentation

- **Dataset Specification v2.0**: `docs/DATASET_SPECIFICATION.md`
- **Material Schema**: `schemas/dataset-material.json`
- **Contaminant Schema**: `schemas/dataset-contaminant.json`
- **Frontmatter Schema**: `schemas/frontmatter-v5.0.0.json`
- **Data Generation Guide**: `docs/FRONTMATTER_GENERATION_GUIDE.md`

---

## 📞 Questions & Support

**Created**: December 27, 2025  
**Last Updated**: December 27, 2025  
**Document Version**: 1.0  
**Dataset Version Documented**: 3.0 (Current), 2.0 (Previous Reference)

For questions about dataset structure, generation, or usage:
- Review schema files in `/schemas`
- Check frontmatter source files in `/frontmatter`
- Examine generated datasets in `/public/datasets`
