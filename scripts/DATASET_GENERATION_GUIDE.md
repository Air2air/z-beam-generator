# Dataset Generation Guide

**Last Updated**: December 27, 2025

---

## 📊 Quick Reference

### ✅ RECOMMENDED Scripts (Use These)

| Task | Script | Output |
|------|--------|--------|
| **Generate ALL datasets** | `python3 scripts/export/generate_datasets.py` | 753 files (materials + contaminants) |
| **Generate materials only** | `python3 scripts/export/generate_datasets.py --domain materials` | 459 files (153 × 3) |
| **Generate contaminants only** | `python3 scripts/export/generate_datasets.py --domain contaminants` | 294 files (98 × 3) |

### ⚠️ DEPRECATED Scripts (Do Not Use)

| Script | Issue | Use Instead |
|--------|-------|-------------|
| `scripts/generate_all_contaminant_datasets.py` | Generates compounds as SEPARATE files (incorrect) | `scripts/export/generate_datasets.py` |
| `scripts/generate_sample_datasets.py` | Outdated, doesn't use dataset classes | `scripts/export/generate_datasets.py` |

---

## 📝 Naming Conventions

### Materials Datasets
**Pattern**: `{slug}-material-dataset.{json,csv,txt}`

**Examples**:
- `aluminum-material-dataset.json`
- `steel-material-dataset.json`
- `titanium-alloy-ti-6al-4v-material-dataset.json`

**Structure**:
```json
{
  "identifier": "aluminum-material-dataset",
  "material": {
    "materialProperties": {...},
    "machineSettings": {...}
  }
}
```

### Contaminants Datasets
**Pattern**: `{slug}-contaminant-dataset.{json,csv,txt}`

**Examples**:
- `rust-oxidation-contaminant-dataset.json`
- `grease-deposits-contaminant-dataset.json`
- `paint-residue-contaminant-dataset.json`

**Structure**:
```json
{
  "identifier": "rust-oxidation-contaminant-dataset",
  "contaminant": {
    "properties": {...},
    "compounds": [...],  // INTEGRATED (not separate files)
    "removalTechniques": {...}
  }
}
```

**⚠️ IMPORTANT**: Compounds are INTEGRATED into contaminant datasets as an array. There are NO separate compound dataset files.

---

## 🏗️ Architecture

### Unified Dataset Pattern (ADR 005)

Both domains use **nested structure** to combine related data:

| Domain | Pattern | Files |
|--------|---------|-------|
| **Materials** | `material{materialProperties, machineSettings}` | 153 × 3 = 459 |
| **Contaminants** | `contaminant{properties, compounds, removalTechniques}` | 98 × 3 = 294 |

### Data Sources

**Materials**:
- Source: `data/materials/Materials.yaml` + `data/settings/Settings.yaml`
- Class: `shared/dataset/materials_dataset.py` → `MaterialsDataset`
- Output: 153 materials × 3 formats = 459 files

**Contaminants**:
- Source: `../z-beam/frontmatter/contaminants/*.yaml` + `data/compounds/Compounds.yaml`
- Class: `shared/dataset/contaminants_dataset.py` → `ContaminantsDataset`
- Output: 98 contaminants × 3 formats = 294 files

**Relationship Reversal**:
- Compounds.yaml: `compound.produced_from_contaminants = ["rust-oxidation-contamination"]`
- Dataset: `contaminant.compounds = [{compound object}]`

---

## 📂 File Structure

```
public/datasets/
├── materials/
│   ├── aluminum-material-dataset.json
│   ├── aluminum-material-dataset.csv
│   ├── aluminum-material-dataset.txt
│   ├── steel-material-dataset.json
│   └── ... (459 files total)
│
└── contaminants/
    ├── rust-oxidation-contaminant-dataset.json
    ├── rust-oxidation-contaminant-dataset.csv
    ├── rust-oxidation-contaminant-dataset.txt
    ├── grease-deposits-contaminant-dataset.json
    └── ... (294 files total)
```

**Total**: 753 files (251 datasets × 3 formats)

---

## 🚀 Generation Commands

### Generate Everything
```bash
python3 scripts/export/generate_datasets.py
```

**Output**:
```
📊 DATASET GENERATION
════════════════════════════════════════════════════════════════════════════════

📂 Loading data...
   ✅ Loaded 153 materials
   ✅ Loaded 98 contaminants

🔧 Generating materials datasets (153 items)...
   ✅ Generated 10 datasets...
   ...
   ✅ Generated 150 datasets...

🔧 Generating contaminants datasets (98 items)...
   ✅ Generated 10 datasets...
   ...
   ✅ Generated 90 datasets...

✅ GENERATION COMPLETE
════════════════════════════════════════════════════════════════════════════════

📊 Statistics:
   • Total datasets: 251
   • Materials: 153 (459 files)
   • Contaminants: 98 (294 files)
   • Total files: 753
   • Errors: 0
   • Success rate: 100%
```

### Generate Materials Only
```bash
python3 scripts/export/generate_datasets.py --domain materials
```

### Generate Contaminants Only
```bash
python3 scripts/export/generate_datasets.py --domain contaminants
```

### Dry Run (Preview Without Writing)
```bash
python3 scripts/export/generate_datasets.py --dry-run
```

### Verbose Logging
```bash
python3 scripts/export/generate_datasets.py --verbose
```

---

## ✅ Verification

### Check File Counts
```bash
# Materials
ls -1 public/datasets/materials/*.json | wc -l  # Should be 153

# Contaminants
ls -1 public/datasets/contaminants/*.json | wc -l  # Should be 98

# Total JSON files
ls -1 public/datasets/*/*.json | wc -l  # Should be 251
```

### Verify Naming Convention
```bash
# Materials should all end with -material-dataset.json
ls public/datasets/materials/*.json | grep -v "material-dataset.json" | wc -l  # Should be 0

# Contaminants should all end with -contaminant-dataset.json
ls public/datasets/contaminants/*.json | grep -v "contaminant-dataset.json" | wc -l  # Should be 0
```

### Check for Compound Files (Should be NONE)
```bash
# Should return 0 - no separate compound files
ls public/datasets/contaminants/ | grep -c "compound"  # Should be 0
```

---

## 🧪 Testing

### Run Dataset Tests
```bash
# Test dataset generation from source YAML
pytest tests/test_dataset_generation_source_yaml.py -v

# Test contaminants nested structure
pytest tests/test_contaminants_nested_structure.py -v

# Test all dataset tests
pytest tests/test_dataset*.py -v
```

### Expected Results
- ✅ 14/14 tests passing for contaminants nested structure
- ✅ 30+ tests passing for dataset generation
- ✅ 100% success rate for file generation

---

## 📖 Documentation

### Primary Documentation
- **Specification**: `docs/DATASET_SPECIFICATION.md`
- **Implementation**: `CONTAMINANTS_COMPOUNDS_INTEGRATION_COMPLETE_DEC27_2025.md`
- **Architecture Decision**: ADR 005 (Unified Dataset Architecture)
- **Export Scripts**: `scripts/export/README.md`

### Implementation Details
- **Materials Class**: `shared/dataset/materials_dataset.py`
- **Contaminants Class**: `shared/dataset/contaminants_dataset.py`
- **Base Class**: `shared/dataset/base_dataset.py`

### Test Coverage
- **Nested Structure**: `tests/test_contaminants_nested_structure.py` (14 tests)
- **Generation**: `tests/test_dataset_generation_source_yaml.py` (30+ tests)
- **Integration**: `tests/test_dataset_generation.py`

---

## ⚠️ Common Mistakes to Avoid

### ❌ Using Deprecated Scripts
```bash
# WRONG - Generates compound files separately
python3 scripts/generate_all_contaminant_datasets.py
```

### ❌ Expecting Compound Files
```bash
# WRONG - Compounds are not separate files
ls public/datasets/contaminants/benzene-compound-contaminant-dataset.json
```

### ❌ Wrong Naming Convention
```bash
# WRONG - Missing -dataset suffix
aluminum-material.json

# WRONG - Wrong suffix
aluminum-laser-cleaning-dataset.json

# CORRECT
aluminum-material-dataset.json
```

### ✅ Correct Usage
```bash
# RIGHT - Use export script
python3 scripts/export/generate_datasets.py

# RIGHT - Verify naming
ls public/datasets/materials/*-material-dataset.json | head -3

# RIGHT - Check integrated compounds
jq '.contaminant.compounds' public/datasets/contaminants/rust-oxidation-contaminant-dataset.json
```

---

## 🔮 Future Enhancements

### Potential Additions
1. **Settings Datasets** - Separate dataset files for machine settings (not yet implemented)
2. **Batch Generation** - Parallel processing for faster generation
3. **Incremental Updates** - Only regenerate changed datasets
4. **Validation Hooks** - Pre/post generation validation
5. **Custom Formats** - XML, RDF, or other formats

### Ready for Implementation
The architecture supports easy addition of new dataset types following the same pattern:
```python
class SettingsDataset(BaseDataset):
    def to_schema_org_json(self, item_id, item_data):
        return {
            "@context": "https://schema.org",
            "@type": "Dataset",
            "setting": {
                "machineParameters": {...},
                "processingConditions": {...}
            }
        }
```

---

## 📞 Support

### Issues
- **File count wrong**: Verify you're using `scripts/export/generate_datasets.py`
- **Compound files present**: Run the deprecated script checker
- **Wrong naming**: Check slug generation in dataset classes
- **Missing data**: Verify source YAML files exist and are valid

### Getting Help
1. Check `TROUBLESHOOTING.md` in root
2. Review `docs/DATASET_SPECIFICATION.md`
3. Run tests to verify system health
4. Check git history for recent changes

---

**Last Updated**: December 27, 2025  
**Status**: ✅ Production Ready
