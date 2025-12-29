# Dataset Generator Specification
**Date**: December 27, 2025  
**Status**: Current Specification

## File Naming Convention

### Materials
- **Pattern**: `{slug}-material-dataset.{format}`
- **Formats**: `json`, `csv`, `txt`
- **Example**: `aluminum-material-dataset.json`

### Contaminants/Compounds
- **Pattern**: `{slug}-contaminant-dataset.{format}`
- **Formats**: `json`, `csv`, `txt`
- **Example**: `adhesive-residue-contamination-contaminant-dataset.json`

## File Locations

### Public Directory Structure
```
public/
├── datasets/
│   ├── materials/
│   │   ├── {slug}-material-dataset.json
│   │   ├── {slug}-material-dataset.csv
│   │   └── {slug}-material-dataset.txt
│   └── contaminants/
│       ├── {slug}-contaminant-dataset.json
│       ├── {slug}-contaminant-dataset.csv
│       └── {slug}-contaminant-dataset.txt
```

### URL Paths
- **Materials**: `https://www.z-beam.com/datasets/materials/{slug}-material-dataset.{format}`
- **Contaminants**: `https://www.z-beam.com/datasets/contaminants/{slug}-contaminant-dataset.{format}`

## JSON-LD Structure Requirements

### @id Pattern
- **Materials**: `https://www.z-beam.com/datasets/materials/{slug}-material-dataset#dataset`
- **Contaminants**: `https://www.z-beam.com/datasets/contaminants/{slug}-contaminant-dataset#dataset`

### Distribution ContentURL Pattern

**CRITICAL**: The `distribution` array MUST use the full path including the type subdirectory.

#### Materials Example
```json
{
  "@context": "https://schema.org",
  "@type": "Dataset",
  "@id": "https://www.z-beam.com/datasets/materials/aluminum-material-dataset#dataset",
  "identifier": "aluminum-material-dataset",
  "name": "Aluminum",
  "distribution": [
    {
      "@type": "DataDownload",
      "encodingFormat": "application/json",
      "contentUrl": "https://www.z-beam.com/datasets/materials/aluminum-material-dataset.json"
    },
    {
      "@type": "DataDownload",
      "encodingFormat": "text/csv",
      "contentUrl": "https://www.z-beam.com/datasets/materials/aluminum-material-dataset.csv"
    },
    {
      "@type": "DataDownload",
      "encodingFormat": "text/plain",
      "contentUrl": "https://www.z-beam.com/datasets/materials/aluminum-material-dataset.txt"
    }
  ]
}
```

#### Contaminants Example
```json
{
  "@context": "https://schema.org",
  "@type": "Dataset",
  "@id": "https://www.z-beam.com/datasets/contaminants/adhesive-residue-contamination-contaminant-dataset#dataset",
  "identifier": "adhesive-residue-contamination-contaminant-dataset",
  "name": "Adhesive Residue Contamination",
  "distribution": [
    {
      "@type": "DataDownload",
      "encodingFormat": "application/json",
      "contentUrl": "https://www.z-beam.com/datasets/contaminants/adhesive-residue-contamination-contaminant-dataset.json"
    },
    {
      "@type": "DataDownload",
      "encodingFormat": "text/csv",
      "contentUrl": "https://www.z-beam.com/datasets/contaminants/adhesive-residue-contamination-contaminant-dataset.csv"
    },
    {
      "@type": "DataDownload",
      "encodingFormat": "text/plain",
      "contentUrl": "https://www.z-beam.com/datasets/contaminants/adhesive-residue-contamination-contaminant-dataset.txt"
    }
  ]
}
```

## Generator Implementation Guidelines

### Path Construction

```typescript
// Material datasets
const materialSlug = getMaterialSlug(); // e.g., "aluminum"
const datasetSlug = `${materialSlug}-material-dataset`;
const baseUrl = "https://www.z-beam.com/datasets/materials";
const fullUrl = `${baseUrl}/${datasetSlug}`;

// File paths
const jsonFile = `public/datasets/materials/${datasetSlug}.json`;
const csvFile = `public/datasets/materials/${datasetSlug}.csv`;
const txtFile = `public/datasets/materials/${datasetSlug}.txt`;

// Distribution URLs
const distribution = [
  { contentUrl: `${fullUrl}.json` },
  { contentUrl: `${fullUrl}.csv` },
  { contentUrl: `${fullUrl}.txt` }
];
```

```typescript
// Contaminant datasets
const contaminantSlug = getContaminantSlug(); // e.g., "adhesive-residue-contamination"
const datasetSlug = `${contaminantSlug}-contaminant-dataset`;
const baseUrl = "https://www.z-beam.com/datasets/contaminants";
const fullUrl = `${baseUrl}/${datasetSlug}`;

// File paths
const jsonFile = `public/datasets/contaminants/${datasetSlug}.json`;
const csvFile = `public/datasets/contaminants/${datasetSlug}.csv`;
const txtFile = `public/datasets/contaminants/${datasetSlug}.txt`;

// Distribution URLs
const distribution = [
  { contentUrl: `${fullUrl}.json` },
  { contentUrl: `${fullUrl}.csv` },
  { contentUrl: `${fullUrl}.txt` }
];
```

## Validation Checklist

Before generating datasets, verify:

- [ ] File naming uses `-material-dataset` or `-contaminant-dataset` suffix
- [ ] Files are placed in correct subdirectory (`materials/` or `contaminants/`)
- [ ] JSON-LD `@id` includes full path with subdirectory
- [ ] JSON-LD `identifier` matches filename (without extension)
- [ ] All three `distribution.contentUrl` values include subdirectory path
- [ ] All three `distribution.contentUrl` values use the `-material-dataset` or `-contaminant-dataset` suffix
- [ ] URLs match actual file locations in public folder

## Common Mistakes to Avoid

### ❌ INCORRECT: Missing subdirectory in contentUrl
```json
{
  "contentUrl": "https://www.z-beam.com/datasets/aluminum-material-dataset.json"
}
```

### ✅ CORRECT: Includes materials/ subdirectory
```json
{
  "contentUrl": "https://www.z-beam.com/datasets/materials/aluminum-material-dataset.json"
}
```

### ❌ INCORRECT: Missing suffix in filename
```json
{
  "contentUrl": "https://www.z-beam.com/datasets/materials/aluminum.json"
}
```

### ✅ CORRECT: Includes -material-dataset suffix
```json
{
  "contentUrl": "https://www.z-beam.com/datasets/materials/aluminum-material-dataset.json"
}
```

### ❌ DEPRECATED: Old dual-format approach (pre-Dec 27, 2025)
```json
{
  "contentUrl": "https://www.z-beam.com/datasets/materials/aluminum-laser-cleaning.json"
}
```
**Issue**: This was the old DatasetExporter format (metadata-rich, minimal data). Created duplicates.

### ✅ CORRECT: Consolidated format (Dec 27, 2025+)
```json
{
  "contentUrl": "https://www.z-beam.com/datasets/materials/aluminum-material-dataset.json"
}
```
**Benefits**: Single comprehensive format with metadata + structured data, no duplicates.

## Testing Dataset URLs

Verify generated datasets are accessible:

### Materials
```bash
# Check file exists
ls public/datasets/materials/aluminum-material-dataset.json

# Verify URL structure in JSON
grep "contentUrl" public/datasets/materials/aluminum-material-dataset.json

# Expected output:
# "contentUrl": "https://www.z-beam.com/datasets/materials/aluminum-material-dataset.json"
# "contentUrl": "https://www.z-beam.com/datasets/materials/aluminum-material-dataset.csv"
# "contentUrl": "https://www.z-beam.com/datasets/materials/aluminum-material-dataset.txt"
```

### Contaminants
```bash
# Check file exists
ls public/datasets/contaminants/adhesive-residue-contamination-contaminant-dataset.json

# Verify URL structure in JSON
grep "contentUrl" public/datasets/contaminants/adhesive-residue-contamination-contaminant-dataset.json

# Expected output:
# "contentUrl": "https://www.z-beam.com/datasets/contaminants/adhesive-residue-contamination-contaminant-dataset.json"
# "contentUrl": "https://www.z-beam.com/datasets/contaminants/adhesive-residue-contamination-contaminant-dataset.csv"
# "contentUrl": "https://www.z-beam.com/datasets/contaminants/adhesive-residue-contamination-contaminant-dataset.txt"
```

## Related Documentation

- [DATASET_SPECIFICATION.md](./DATASET_SPECIFICATION.md) - Complete dataset structure and schema
- [docs/04-reference/datasets.md](./04-reference/datasets.md) - User-facing dataset documentation
- [docs/deployment/POST_DEPLOYMENT_VALIDATION.md](./deployment/POST_DEPLOYMENT_VALIDATION.md) - Deployment validation procedures
