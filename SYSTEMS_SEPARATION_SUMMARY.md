# Systems Separation Summary
**Date**: December 30, 2025  
**Status**: Clarified and Documented

---

## Two Separate Systems

Z-Beam has **two distinct systems** that are often confused but serve completely different purposes:

### 1. 📊 Dataset Generation (Export Layer)
**Purpose**: Create Schema.org-compliant dataset files for SEO and machine readability  
**Input**: Source YAML files (`data/*/`)  
**Output**: Schema.org files (`/z-beam/public/datasets/`)  
**Formats**: JSON, CSV, TXT  
**Command**: `python3 scripts/export/generate_datasets.py`

**What it does**:
- Reads existing data from YAML files
- Extracts fields dynamically
- Generates Schema.org JSON-LD format
- Creates CSV tables and TXT summaries
- NO modification of source data

**Documentation**:
- [DATASET_SPECIFICATION.md](docs/DATASET_SPECIFICATION.md) - Complete specification
- [DATASET_REFACTORING_COMPLETE_DEC30_2025.md](DATASET_REFACTORING_COMPLETE_DEC30_2025.md) - Implementation
- [DATASET_QUALITY_IMPROVEMENT_COMPLETE_DEC30_2025.md](DATASET_QUALITY_IMPROVEMENT_COMPLETE_DEC30_2025.md) - Quality fixes

**Code Location**: `shared/dataset/`, `scripts/export/generate_datasets.py`

---

### 2. 🔧 Data Population (Data Layer)
**Purpose**: Enrich source YAML files with missing fields permanently  
**Input**: Source YAML files (`data/*/`)  
**Output**: Modified source YAML files (same location)  
**Formats**: YAML only  
**Command**: `python3 run.py --backfill --domain {domain} --generator {type}`

**What it does**:
- Populates missing descriptions in Contaminants.yaml
- Adds compound relationships
- Assigns authors
- Calculates derived fields
- MODIFIES source data files

**Documentation**:
- [docs/05-data/BACKFILL_SYSTEM_COMPLETE_DEC30_2025.md](docs/05-data/BACKFILL_SYSTEM_COMPLETE_DEC30_2025.md) - Complete system

**Code Location**: `generation/backfill/`

---

## Key Differences

| Aspect | Dataset Generation | Data Population |
|--------|-------------------|-----------------|
| **Modifies source?** | ❌ No | ✅ Yes |
| **Creates new files?** | ✅ Yes (Schema.org) | ❌ No |
| **Purpose** | SEO + machine readability | Data enrichment |
| **Frequency** | Every export | As needed |
| **Input** | YAML → Read | YAML → Read + Write |
| **Output** | JSON/CSV/TXT → Write | YAML → Modify |
| **Command** | `generate_datasets.py` | `run.py --backfill` |
| **Documentation** | `DATASET_SPECIFICATION.md` | `BACKFILL_SYSTEM_COMPLETE_DEC30_2025.md` |

---

## Common Confusion

❌ **WRONG**: "Dataset generation populates missing descriptions"  
✅ **RIGHT**: "Data population (backfill) populates missing descriptions in source YAML. Dataset generation then reads the enriched data."

❌ **WRONG**: "Backfill creates JSON dataset files"  
✅ **RIGHT**: "Dataset generation creates JSON files. Backfill modifies source YAML files."

---

## Workflow

```
1. Data Population (backfill) - Optional, as needed
   ↓
   Enriches source YAML with missing fields
   ↓
data/contaminants/Contaminants.yaml (now has descriptions)

2. Dataset Generation - Run on every export
   ↓
   Reads enriched YAML data
   ↓
public/datasets/contaminants/*.json (Schema.org files)
```

---

## CLI Commands

### Dataset Generation
```bash
# Generate all datasets (read-only, creates Schema.org files)
python3 scripts/export/generate_datasets.py

# Specific domain
python3 scripts/export/generate_datasets.py --domain contaminants

# Dry run (preview)
python3 scripts/export/generate_datasets.py --dry-run
```

### Data Population
```bash
# Populate source YAML (modifies data files)
python3 run.py --backfill --domain contaminants --generator description

# Dry run (preview changes to YAML)
python3 run.py --backfill --domain contaminants --generator description --dry-run

# All generators
python3 run.py --backfill --domain contaminants
```

---

## File Locations

### Dataset Generation
- **Code**: `shared/dataset/materials_dataset.py`, `shared/dataset/contaminants_dataset.py`
- **Script**: `scripts/export/generate_datasets.py`
- **Output**: `/Users/todddunning/Desktop/Z-Beam/z-beam/public/datasets/{domain}/`
- **Docs**: `docs/DATASET_SPECIFICATION.md`

### Data Population
- **Code**: `generation/backfill/base.py`, `generation/backfill/registry.py`
- **Generators**: `generation/backfill/description_backfill.py`
- **Config**: `generation/backfill/config/contaminants.yaml`
- **Modified Files**: `data/contaminants/Contaminants.yaml` (in place)
- **Docs**: `docs/05-data/BACKFILL_SYSTEM_COMPLETE_DEC30_2025.md`

---

## Summary

- **Dataset Generation** = Read YAML → Create Schema.org files (export layer)
- **Data Population** = Enrich YAML files with missing data (data layer)
- **These are separate systems** serving different purposes
- **Documentation now reflects this separation** clearly

