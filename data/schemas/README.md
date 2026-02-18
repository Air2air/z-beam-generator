# Z-Beam Dataset Schema Consolidation

**Date**: February 16, 2026  
**Version**: 2.1.0

## Schema Architecture

The dataset schemas have been consolidated from separate files into a base + extension pattern to eliminate duplication and improve maintainability.

### New Structure (v2.0)

```
data/schemas/
├── dataset-base.json                      # Shared foundation (124 lines)
├── dataset-material-extension.json        # Material-specific (extends base)
├── dataset-contaminant-extension.json     # Contaminant-specific (extends base)
├── frontmatter.json                       # Frontmatter validation
├── FrontmatterFieldOrder.yaml             # Field ordering
├── section_display_schema.yaml            # Section metadata
└── archive/
    ├── dataset-material.json              # Archived (376 lines)
    └── dataset-contaminant.json           # Archived (505 lines)
```

### Benefits

1. **Reduced Duplication**: ~90% shared structure now in base schema
2. **Easier Maintenance**: Update shared fields once in base
3. **Consistent Structure**: All datasets follow same core pattern
4. **Extensible**: Easy to add new domain schemas (settings, compounds)
5. **Standards Compliant**: Uses JSON Schema `$ref` and `allOf` for composition

## Schema Details

### Base Schema (`dataset-base.json`)

**Shared across all domains:**
- Schema.org metadata (@context, @type)
- Required fields (identifier, name, description, license, creator, publisher)
- Optional metadata (datePublished, dateModified, measurementTechnique)
- Schema.org requirements (variableMeasured, citation, distribution)
- SEO fields (keywords, spatialCoverage, temporalCoverage)

**Common definitions:**
- `measuredValue`: Physical measurements with value/unit/description
- `parameterRange`: Min/max ranges for machine parameters
- `exposureRoute`: Health effects exposure routes
- `toxicityValue`: Toxicology data format
- `exposureLimit`: OSHA/NIOSH/ACGIH exposure limits

### Material Extension (`dataset-material-extension.json`)

**Extends base with:**
- Material-specific identifier pattern (`*-material-dataset`)
- `material` object containing:
  - `materialProperties`: Physical/thermal/optical/mechanical characteristics (22 properties)
  - `machineSettings`: 8 Tier 1 CRITICAL laser parameters + 2 optional
  - `industryApplications`: Sector usage
  - `regulatoryStandards`: Applicable standards
  - `commonContaminants`: Typical contamination

**Material properties include:**
- Thermal: density, melting/boiling point, conductivity, specific heat, expansion, diffusivity
- Optical: absorption, reflectivity, absorptivity, emissivity
- Mechanical: tensile strength, Young's modulus, hardness, porosity, surface roughness
- Laser interaction: ablation threshold, damage threshold
- Durability: corrosion/oxidation resistance
- Electrical: conductivity, resistivity

### Contaminant Extension (`dataset-contaminant-extension.json`)

**Extends base with:**
- Contaminant-specific identifier pattern (`*-contaminant-dataset`)
- `contaminant` object containing:
  - `category`: Contamination type (15 categories)
  - `subcategory`: Specific classification
  - `properties`: Visual appearance by material, composition, hazard/removal difficulty
  - `removalTechniques`: Laser cleaning parameters (power, wavelength, fluence, passes, rate)
  - `compounds`: Chemical safety data (CAS numbers, health effects, PPE, exposure limits)
  - `validMaterials`: Affected materials
  - `regulatoryStandards`: Safety/handling standards

**Compound safety includes:**
- Chemical identification: name, formula, CAS number, molecular weight, phase
- Hazard classification: level (low/medium/high/severe), class (toxic/irritant/etc)
- Health effects: exposure routes, acute/chronic effects, toxicology data, carcinogenicity
- Safety requirements: PPE, detection methods, first aid, exposure limits (OSHA/NIOSH/ACGIH)
- Environmental impact: aquatic toxicity, biodegradability, atmospheric fate, reportable releases

## Usage

### Validation

Validate datasets against the appropriate extension schema (which automatically includes base):

```bash
# Validate material dataset
ajv validate -s data/schemas/dataset-material-extension.json -d path/to/material-dataset.json

# Validate contaminant dataset
ajv validate -s data/schemas/dataset-contaminant-extension.json -d path/to/contaminant-dataset.json
```

### Schema References

Both extension schemas reference the base schema:

```json
{
  "allOf": [
    {"$ref": "dataset-base.json"},
    {"type": "object", "required": ["material"], ...}
  ]
}
```

Definitions from base can be referenced in extensions:

```json
"density": {"$ref": "dataset-base.json#/definitions/measuredValue"}
```

## Migration Impact

**Code changes required:** NONE

The dataset generation script (`scripts/export/generate_datasets.py`) dynamically generates datasets from source YAML data. It doesn't validate against schemas during generation, so the consolidation has zero impact on generation logic.

**Schema validation (if used):** Update validation calls to use extension schemas:
- `dataset-material.json` → `dataset-material-extension.json`
- `dataset-contaminant.json` → `dataset-contaminant-extension.json`

## Future Extensions

Adding new domain schemas (settings, compounds) is straightforward:

1. Create `dataset-{domain}-extension.json`
2. Extend `dataset-base.json` using `allOf`
3. Add domain-specific identifier pattern
4. Define domain-specific required fields and properties
5. Reuse base definitions via `$ref`

## Version History

- **v2.1.0** (Feb 16, 2026): Frontmatter schema update to explicitly allow `page_description` while preserving legacy `_description` field deprecation for all other fields
- **v2.0.0** (Jan 13, 2026): Consolidated into base + extensions architecture
- **v1.0.0** (Dec 26, 2025): Separate material and contaminant schemas

## Related Documentation

- Dataset Generation: `scripts/DATASET_GENERATION_GUIDE.md`
- Export README: `scripts/export/README.md`
- Schema.org Documentation: https://schema.org/Dataset
- JSON Schema Specification: https://json-schema.org/
