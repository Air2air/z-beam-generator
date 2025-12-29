# Z-Beam Dataset Specification

**Version**: 3.0  
**Date**: December 27, 2025  
**Status**: Production Ready  
**Purpose**: High-level specification for Z-Beam's unified dataset architecture

---

## 🎯 Executive Summary

Z-Beam provides structured, machine-readable datasets for laser cleaning applications through **two consolidated dataset categories**:

1. **Materials Dataset** - Combines material properties + machine settings for laser cleaning applications
2. **Contaminants Dataset** - Combines contaminant properties + chemical compounds for materials scientists

All datasets are:
- ✅ **v3.0 Hybrid Format** - Nested objects + Schema.org + comprehensive metadata
- ✅ Schema.org compliant for SEO
- ✅ Available in 3 formats: JSON, CSV, TXT
- ✅ **Metadata included in all formats** (version, license, keywords, citations)
- ✅ **Nested material/contaminant objects** for structured data
- ✅ Quality-validated (3-tier system)
- ✅ Automatically generated from source YAML
- ✅ Integrated into JSON-LD structured data

---

## 📊 Two Dataset Categories

### Category 1: Materials Dataset

**Purpose**: Comprehensive laser cleaning data for industrial applications  
**Combines**: Material properties + Machine settings  
**Target Audience**: Laser operators, manufacturers, industrial engineers

**File Structure**:
```
public/datasets/materials/
├── aluminum-material-dataset.json
├── aluminum-material-dataset.csv
├── aluminum-material-dataset.txt
├── steel-material-dataset.json
└── ... (153 materials × 3 formats = 459 files)
```

**Naming Convention**: `{material-name}-material-dataset.{json|csv|txt}`

**Data Contents** (v3.0 Hybrid Format):
```json
{
  "@context": "https://schema.org",
  "@type": "Dataset",
  "@id": "https://www.z-beam.com/datasets/materials/aluminum-material-dataset#dataset",
  "identifier": "aluminum-material-dataset",
  "name": "Aluminum Laser Cleaning Dataset",
  "description": "Complete laser cleaning parameters and material properties...",
  
  "version": "3.0",
  "dateModified": "2025-12-27",
  
  "material": {
    "materialProperties": {
      "density": { "value": 2700, "unit": "kg/m³" },
      "thermalConductivity": { "value": 237, "unit": "W/(m·K)" },
      "absorptivity": { "value": 0.15, "unit": "dimensionless" },
      "meltingPoint": { "value": 660, "unit": "°C" }
      // ... 10+ material characteristics
    },
    
    "machineSettings": {
      "laserPower": { "min": 20, "max": 100, "unit": "W" },
      "wavelength": { "min": 1064, "max": 1064, "unit": "nm" },
      "pulseWidth": { "min": 10, "max": 200, "unit": "ns" },
      "scanSpeed": { "min": 500, "max": 2000, "unit": "mm/s" },
      "frequency": { "min": 20, "max": 100, "unit": "kHz" },
      "passCount": { "min": 1, "max": 5 },
      "overlapRatio": { "min": 30, "max": 70, "unit": "%" },
      "spotSize": { "min": 50, "max": 200, "unit": "μm" }
      // All 8 machine parameters included
    }
  },
  
  "variableMeasured": [
    { "@type": "PropertyValue", "name": "Laser Power Range" },
    { "@type": "PropertyValue", "name": "Material Density" }
    // Minimum 20 variables
  ],
  
  "citation": [
    { "@type": "CreativeWork", "name": "Industrial Laser Handbook" }
    // Minimum 3 citations
  ],
  
  "distribution": [
    { "@type": "DataDownload", "encodingFormat": "application/json" },
    { "@type": "DataDownload", "encodingFormat": "text/csv" },
    { "@type": "DataDownload", "encodingFormat": "text/plain" }
  ]
}
```

**Key Benefits**:
- **Single unified file** per material (no separate settings file)
- **Complete cleaning parameters** for immediate application
- **Material science data** for understanding laser-material interaction
- **Ready for machine learning** and process optimization

---

### Category 2: Contaminants Dataset

**Purpose**: Comprehensive contamination removal data for materials scientists  
**Combines**: Contaminant properties + Chemical compounds + Laser removal techniques  
**Target Audience**: Materials scientists, safety engineers, researchers

**Status**: ✅ IMPLEMENTED (December 27, 2025)  
**Implementation**: `shared/dataset/contaminants_dataset.py`  
**Tests**: `tests/test_contaminants_nested_structure.py` (14/14 passing)

**File Structure**:
```
public/datasets/contaminants/
├── rust-oxidation-contaminant-dataset.json
├── rust-oxidation-contaminant-dataset.csv
├── rust-oxidation-contaminant-dataset.txt
├── grease-deposits-contaminant-dataset.json
└── ... (98 contaminants × 3 formats = 294 files)
```

**Naming Convention**: `{contaminant-slug}-contaminant-dataset.{json|csv|txt}`  
**Note**: Compounds are INTEGRATED into contaminant datasets (not separate files)

**Data Contents**:
```json
{
  "@context": "https://schema.org",
  "@type": "Dataset",
  "identifier": "rust-oxidation-contaminant-dataset",
  "name": "Rust / Iron Oxide Formation Contamination Dataset",
  "description": "Contamination removal parameters and chemical composition...",
  
  "contaminant": {
    "properties": {
      "composition": ["Fe2O3", "Fe3O4", "FeO"],
      "color": "Red-brown to black",
      "texture": "Flaky or powdery surface",
      "absorptionRate": {
        "wavelength_1064nm": 850,
        "wavelength_532nm": 1200,
        "wavelength_355nm": 2500
      },
      "reflectivity": {
        "wavelength_1064nm": 0.15,
        "wavelength_532nm": 0.08,
        "wavelength_355nm": 0.03
      },
      "hazardLevel": "medium",
      "removalDifficulty": "medium"
    },
    
    "compounds": [
      {
        "id": "iron-oxide-compound",
        "name": "Iron(III) Oxide",
        "formula": "Fe2O3",
        "casNumber": "1309-37-1",
        "phase": "solid",
        "hazardLevel": "low",
        "healthEffects": "Respiratory irritant in dust form",
        "ppeRequirements": "Dust mask, safety glasses",
        "detectionMethods": "Visual inspection, XRD analysis"
      },
      {
        "id": "magnetite-compound",
        "name": "Magnetite",
        "formula": "Fe3O4",
        "casNumber": "1317-61-9",
        "phase": "solid",
        "hazardLevel": "low"
      }
    ],
    
    "removalTechniques": {
      "laserPower": {
        "min_j_cm2": 0.5,
        "max_j_cm2": 2.0,
        "recommended_j_cm2": 1.2
      },
      "wavelength": {
        "primary_nm": 1064,
        "secondary_nm": 532
      },
      "pulseWidth": {
        "min_ns": 10,
        "max_ns": 100,
        "recommended_ns": 50
      },
      "frequency": {
        "min": 20,
        "max": 80,
        "recommended": 50
      },
      "scanSpeed": {
        "min_mm_s": 500,
        "max_mm_s": 1500,
        "recommended_mm_s": 1000
      },
      "overlapRatio": {
        "value": 50
      },
      "passCount": {
        "min": 1,
        "max": 3,
        "recommended": 2
      },
      "assistGas": {
        "type": "compressed_air",
        "pressure_bar": 2.0
      }
    }
  },
  
  "variableMeasured": [
    { "@type": "PropertyValue", "name": "Composition Fe2O3" },
    { "@type": "PropertyValue", "name": "Absorption Rate 1064nm" },
    { "@type": "PropertyValue", "name": "Iron(III) Oxide Health Effects" },
    { "@type": "PropertyValue", "name": "Laser Power Minimum" },
    { "@type": "PropertyValue", "name": "Wavelength Primary" }
    // Total: ≥20 variables (properties + compounds + removal techniques)
  ],
  
  "citation": [
    { "@type": "CreativeWork", "name": "Corrosion Science Journal" }
    // Minimum 3 citations
  ],
  
  "distribution": [
    { "@type": "DataDownload", "encodingFormat": "application/json",
      "contentUrl": "https://www.z-beam.com/datasets/contaminants/rust-oxidation-contaminant-dataset.json" },
    { "@type": "DataDownload", "encodingFormat": "text/csv",
      "contentUrl": "https://www.z-beam.com/datasets/contaminants/rust-oxidation-contaminant-dataset.csv" },
    { "@type": "DataDownload", "encodingFormat": "text/plain",
      "contentUrl": "https://www.z-beam.com/datasets/contaminants/rust-oxidation-contaminant-dataset.txt" }
  ]
}
```

**Nested Structure Implementation**:

The contaminant object has **3 key sections**:

1. **`properties`** - Contaminant characteristics:
   - Composition (chemical formulas)
   - Visual appearance (color, texture)
   - Optical properties (absorption, reflectivity per wavelength)
   - Safety (hazard level, removal difficulty)

2. **`compounds`** (optional) - Chemical safety data:
   - Compound identification (name, formula, CAS number)
   - Physical properties (phase, molecular weight)
   - Health and safety (hazard level, PPE requirements)
   - Detection methods
   - **Source**: Reversed from `Compounds.yaml` → `produced_from_contaminants` relationships
   - **Note**: Only present if contaminant produces compounds

3. **`removalTechniques`** - Laser cleaning parameters:
   - All 8 machine parameters (power, wavelength, frequency, etc.)
   - Min/max/recommended values
   - Assist gas requirements
   - **Source**: Mapped from `laser_properties` in contaminants frontmatter

**Key Benefits**:
- **Unified dataset** - Properties + compounds + removal techniques in single file
- **Chemical safety data** integrated with removal parameters
- **Compound identification** for proper handling procedures
- **Hazard assessment** for workplace safety
- **Research-ready format** for scientific analysis
- **Relationship reversal** - Compounds linked to their contaminant sources

**Generation Script**: Use `scripts/generate_contaminants_using_dataset_class.py`
**Architecture Decision**: ADR 005 - Unified Contamination Dataset Architecture

---

## ✅ Quality Validation (3-Tier System)

### Tier 1: CRITICAL - 100% Required
**Machine Settings** (8 parameters must have min/max values):
- `laserPower`, `wavelength`, `spotSize`, `repetitionRate`
- `pulseWidth`, `scanSpeed`, `passCount`, `overlapRatio`

**Enforcement**: Dataset NOT generated if Tier 1 incomplete

### Tier 2: IMPORTANT - 80% Target
**Material Properties** (10 key characteristics):
- Thermal: `meltingPoint`, `thermalConductivity`, `heatCapacity`
- Optical: `absorptivity`, `reflectivity`, `emissivity`
- Mechanical: `density`, `hardness`, `tensileStrength`, `youngsModulus`

**Enforcement**: Warning logged, dataset still generated

### Tier 3: OPTIONAL - Enhanced Content
- Safety considerations
- Regulatory standards
- Application notes
- Vendor specifications

**Enforcement**: No requirements

---

## 📋 Schema.org Compliance

All datasets include:
- ✅ **≥20 variableMeasured** entries (enforced by JSON schema)
- ✅ **≥3 citations** with proper CreativeWork attribution
- ✅ **3 distribution formats** (JSON, CSV, TXT) with contentUrl
- ✅ **license, creator, publisher** metadata
- ✅ **Metadata headers in CSV/TXT formats** ⭐ NEW (Dec 27, 2025)
  - CSV: 7 comment rows with metadata (#-prefixed lines before data)
  - TXT: Complete metadata section after title
  - Includes: version, license, keywords, citations, last modified date
- ✅ **measurementTechnique** description (≥10 characters)

**Validation**: JSON schemas enforce all requirements
- `schemas/dataset-material.json`
- `schemas/dataset-contaminant.json`

---

## 📁 File Formats

### JSON Format
**Purpose**: API consumption, machine learning, web applications  
**Features**: Complete structured data with nested objects

```json
{
  "@context": "https://schema.org",
  "@type": "Dataset",
  "name": "Aluminum Material Dataset",
  "identifier": "aluminum-material-dataset",
  "material": {
    "materialProperties": { "density": { "value": 2700, "unit": "kg/m³" } },
    "machineSettings": { "laserPower": { "min": 20, "max": 100 } }
  }
}
```

### CSV Format
**Purpose**: Spreadsheet analysis, data import, Excel compatibility  
**Features**: Flattened structure with property-value-unit columns

```csv
# Material: Aluminum
# Category: Non-Ferrous Metals
property,value,unit,min,max
density,2700,kg/m³,,
laserPower,,W,20,100
```

### TXT Format
**Purpose**: Human reading, documentation, quick reference  
**Features**: Formatted text with 80-character line width

```txt
================================================================================
MATERIAL: Aluminum Material Dataset
================================================================================
Category: Non-Ferrous Metals

MATERIAL PROPERTIES
  Density: 2700 kg/m³
  
MACHINE SETTINGS
  Laser Power: 20-100 W
```

---

## 🔄 Generation Workflow

### Automated Generation

**Materials Dataset**:
```bash
# Generate material datasets (153 materials × 3 formats = 459 files)
npm run datasets:generate
```

**Contaminants + Compounds Dataset**:
```bash
# Generate unified contaminant/compound datasets (132 datasets × 3 formats = 396 files)
npx ts-node scripts/generate-contaminant-datasets.ts
```

**Quality & Validation**:
```bash
# Quality validation report
npm run datasets:quality

# Check synchronization with frontmatter
npm run datasets:check
```

### Source Data
- **Materials**: `data/materials/Materials.yaml` (153 materials)
- **Settings**: `data/settings/Settings.yaml` (153 settings)
- **Contaminants**: `data/contaminants/Contaminants.yaml` (98 contaminants)
- **Compounds**: `data/compounds/Compounds.yaml` (34 compounds)

**Note**: Datasets are generated from source YAML data files in the `data/` directory, NOT from frontmatter. Frontmatter files are exported output for the website, while source YAML files are the single source of truth.

### Generation Status (Dec 27, 2025)
- ✅ **Materials**: GENERATED - 459 files (153 × 3 formats)
  - Script: `python3 scripts/export/generate_datasets.py --domain materials`
  - Source: `data/materials/Materials.yaml` + `data/settings/Settings.yaml`
  - Each material includes both properties AND machine settings (unified)
  - Compliance: DATASET_GENERATOR_SPECIFICATION.md ✅
- ✅ **Contaminants**: GENERATED - 294 files (98 × 3 formats)
  - Script: `python3 scripts/export/generate_datasets.py --domain contaminants`
  - Source: `data/contaminants/Contaminants.yaml` + `data/compounds/Compounds.yaml`
  - Compounds INTEGRATED into contaminant datasets (no separate files)
  - Output directory: `public/datasets/contaminants/` (unified)
  - Compliance: DATASET_GENERATOR_SPECIFICATION.md ✅
- **Total Generated**: 753 files (459 materials + 294 contaminants)

**Generation Command**:
```bash
python3 scripts/export/generate_datasets.py  # Generate all
python3 scripts/export/generate_datasets.py --domain materials  # Materials only
python3 scripts/export/generate_datasets.py --domain contaminants  # Contaminants only
```

---

## 🎯 Current Metrics

**Materials Dataset**:
- Total materials: 153
- Files to generate: 459 (153 × 3 formats)
- Each dataset includes: Material properties + Machine settings (unified)
- Schema validation: 100% compliance enforced

**Contaminants Dataset**:
- Total contaminants: 98
- Total compounds: 34 (integrated into contaminant datasets)
- Total datasets: 98 (compounds are NOT separate files)
- Files generated: 294 (98 × 3 formats)
- Output directory: `public/datasets/contaminants/` (unified)
- Schema validation: 100% compliance enforced

**Grand Total**: 753 files generated (459 materials + 294 contaminants)

---

## 🔌 Integration Points

### SEO System
- Datasets embedded as JSON-LD structured data on all material/contaminant pages
- Enhances search engine understanding
- Enables rich snippets in search results
- Validates through `scripts/validation/seo/validate-seo-infrastructure.js`

### Source Data Sync
- Datasets generated from source YAML files in `data/` directory
- Source data is the single source of truth for all datasets
- Frontmatter is exported output (for website), NOT source for datasets
- Status check: `npm run datasets:check`

### API Endpoints

**Note**: All contaminant datasets (with integrated compounds) are served from `/datasets/contaminants/` directory. Compounds are NOT separate files - they are integrated into contaminant datasets as a `compounds` array.
- `https://www.z-beam.com/datasets/materials/{name}-material-dataset.json`
- `https://www.z-beam.com/datasets/contaminants/{name}-contaminant-dataset.json`

---

## 🚀 Architecture Benefits

### For Materials Dataset
**Before**: 2 separate exporters creating duplicate files
- `components/frontmatter/exporters/dataset_exporter.py` → `aluminum-laser-cleaning.json` (metadata-rich, minimal data)
- `scripts/export/generate_datasets.py` → `aluminum-material-dataset.json` (data-rich, minimal metadata)
- **Problem**: Duplicates (306 JSON files instead of 153), conflicting naming, incomplete content

**After**: 1 consolidated exporter with comprehensive format
- `/datasets/materials/aluminum-material-dataset.json` (metadata + structured data)
- **URL**: `https://www.z-beam.com/datasets/materials/aluminum-material-dataset.json`
- **@id**: `https://www.z-beam.com/datasets/materials/aluminum-material-dataset#dataset`
- **Benefits**: No duplicates, comprehensive metadata + data, consistent naming, 50% file reduction

### For Contaminants Dataset
**Before**: 2 separate file types (contaminants + compounds)
- `/datasets/contaminants/rust-oxidation-contamination.json`
- `/datasets/compounds/iron-oxide-compound.json` (separate system)
- **Problem**: Related chemical data disconnected from contamination data

**After**: Unified structure with proper naming
- `/datasets/contaminants/rust-oxidation-contaminant-dataset.json` (includes compounds array)
  - **URL**: `https://www.z-beam.com/datasets/contaminants/rust-oxidation-contaminant-dataset.json`
  - **@id**: `https://www.z-beam.com/datasets/contaminants/rust-oxidation-contaminant-dataset#dataset`
- `/datasets/contaminants/grease-deposits-contaminant-dataset.json` (includes compounds array)
  - **URL**: `https://www.z-beam.com/datasets/contaminants/grease-deposits-contaminant-dataset.json`
  - **@id**: `https://www.z-beam.com/datasets/contaminants/grease-deposits-contaminant-dataset#dataset`
- **Benefits**: Chemical safety integrated, complete research data, no duplicate compound files, proper URLs

---

## 📖 Related Documentation

### Core Documentation
- `docs/01-core/DATASET_ARCHITECTURE.md` - Technical architecture
- `docs/01-core/DATASET_QUALITY_POLICY.md` - Quality standards
- `docs/01-core/DATASET_SEO_POLICY.md` - SEO integration
- `docs/adr/005-dataset-consolidation.md` - Architecture decision

### Schemas
- `schemas/dataset-material.json` - JSON schema for materials
- `schemas/dataset-contaminant.json` - JSON schema for contaminants
- `schemas/frontmatter-v5.0.0.json` - Frontmatter source schema
 (materials)
- `scripts/generate-contaminant-datasets.ts` - **Unified contaminant + compound generator** ✅ Updated Dec 26, 2025
- `scripts/datasets/merge-datasets.js` - Dataset consolidation utilities
- `scripts/generate-contaminant-datasets.ts` - Contaminant generator
- `scripts/datasets/merge-datasets.js` - Dataset consolidation

### Tests
- `tests/datasets/dataset-architecture.test.ts` - Architecture compliance
- `tests/datasets/quality-policy.test.ts` - Quality validation

---Implementation Status & Future Enhancements

### Phase 1: Compound Integration ✅ COMPLETE (Dec 26, 2025)
**Status**: Script updated, ready for backend generation  
**Completed**: 
1. ✅ Updated `scripts/generate-contaminant-datasets.ts` to process compounds
2. ✅ Script generates 396 files (132 datasets × 3 formats)
3. ✅ Unified output directory: `public/datasets/contaminants/`
4. ✅ Compounds treated as specialized contaminants for materials scientists

**Backend Command**: `npx ts-node scripts/generate-contaminant-datasets.ts`data into contaminant datasets where applicable

**Timeline**: 1-2 days

### Phase 2: Enhanced Relationships (Priority: MEDIUM)
- Link materials to compatible contaminants
- Cross-reference compounds in contamination datasets
- Material compatibility matrices

**Timeline**: 1 week

### Phase 3: Dataset API Endpoints (Priority: LOW)
- RESTful API for programmatic access
- Real-time dataset queries
- Batch download capabilities

**Timeline**: 2-3 weeks

---

## ✅ Success Criteria

**A dataset is considered complete when**:
1. ✅ All Tier 1 parameters have min/max values (8/8)
2. ✅ ≥80% Tier 2 properties present (8/10 minimum)
3. ✅ ≥20 variableMeasured entries
4. ✅ ≥3 valid citations with CreativeWork schema
5. ✅ 3 distribution formats available (JSON, CSV, TXT)
6. ✅ JSON schema validation passes
7. ✅ Embedded in page JSON-LD structured data
8. ✅ Listed on `/datasets` public catalog page

**System is healthy when**:
- All tests passing (`npm run test:datasets`)
- Zero schema validation errors
- Frontmatter sync status: UP TO DATE
- SEO validation score: A+ (95+/100)

---1  
**Status**: Production Ready  
**Generation Scripts**:
- Materials: `npm run datasets:generate` ✅ Operational
- Contaminants + Compounds: `npx ts-node scripts/generate-contaminant-datasets.ts` ✅ Ready for backend execution
**Last Updated**: December 26, 2025  
**Version**: 2.0  
**Status**: Production Ready (Materials complete, Compounds pending)
