# Export Scripts

Scripts for exporting data from z-beam-generator to the z-beam project.

## 📊 Dataset Generation

### `generate_datasets.py` - Standalone Dataset Generation

**Purpose**: Generate Schema.org datasets in JSON/CSV/TXT formats for materials and contaminants.

**Architecture**: Loads directly from source YAML files (independent of frontmatter pipeline).

**Usage**:
```bash
# Generate all datasets (materials + contaminants)
python3 scripts/export/generate_datasets.py

# Generate materials only
python3 scripts/export/generate_datasets.py --domain materials

# Generate contaminants only
python3 scripts/export/generate_datasets.py --domain contaminants

# Dry run (preview without writing files)
python3 scripts/export/generate_datasets.py --dry-run

# Verbose logging
python3 scripts/export/generate_datasets.py --verbose
```

**Output**:
- **Materials**: `../z-beam/public/datasets/materials/{slug}-material-dataset.{json,csv,txt}` (459 files) ✅ GENERATED
- **Contaminants**: `../z-beam/public/datasets/contaminants/{slug}-contaminant-dataset.{json,csv,txt}` (294 files) ✅ GENERATED
- **Total**: 753 files (251 datasets × 3 formats)

**Naming Convention** (per DATASET_GENERATOR_SPECIFICATION.md):
- Materials: `{slug}-material-dataset.json` (e.g., `aluminum-material-dataset.json`)
- Contaminants: `{slug}-contaminant-dataset.json` (e.g., `rust-oxidation-contaminant-dataset.json`)
- **Note**: Compounds are INTEGRATED into contaminant datasets (no separate compound files)

**URL Structure** (per DATASET_GENERATOR_SPECIFICATION.md):
- Materials: `https://www.z-beam.com/datasets/materials/{slug}-material-dataset.{format}`
- Contaminants: `https://www.z-beam.com/datasets/contaminants/{slug}-contaminant-dataset.{format}`
- **@id**: Includes subdirectory + suffix + `#dataset` fragment
- **identifier**: Uses `-material-dataset` or `-contaminant-dataset` suffix

**Features**:
- ✅ Direct YAML loading via domain data loaders
- ✅ ADR 005 consolidation (materials+settings, contaminants+compounds)
- ✅ Schema.org Dataset format with full metadata
- ✅ CSV tabular format (machine settings first)
- ✅ TXT human-readable format
- ✅ Atomic writes with temp files
- ✅ Comprehensive statistics and reporting

**Performance**:
- Generation Time: ~25 seconds for all 753 files
- Success Rate: 100% (0 errors)
- Memory Usage: ~50 MB peak

**Documentation**:
- Implementation: `DATASET_GENERATION_SOURCE_YAML_IMPLEMENTATION_DEC22_2025.md`
- Session Summary: `SESSION_COMPLETE_DATASET_GENERATION_DEC22_2025.md`
- Original Spec: `docs/DATASET_GENERATION_INTEGRATION_SPEC.md`
- Tests: `tests/test_dataset_generation_source_yaml.py`

**Architecture Decision**:
Original spec called for integration with frontmatter export pipeline, but standalone approach proved simpler, faster, and more maintainable.

**Benefits**:
- 🎯 **Simpler**: Single-purpose script, clear data flow
- ⚡ **Faster**: Direct YAML loading, no intermediate processing
- 🔓 **Independent**: Can run standalone without export pipeline
- 📖 **Clearer**: Easy to understand, maintain, and extend

---

## 🔄 Future Export Scripts

Placeholder for additional export utilities.
