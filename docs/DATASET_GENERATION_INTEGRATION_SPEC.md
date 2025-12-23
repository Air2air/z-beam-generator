# Dataset Generation Integration Specification

**Project**: z-beam-generator  
**Target**: Export datasets from Materials.yaml to z-beam project  
**Date**: December 22, 2025  
**Status**: Specification

---

## Overview

Add dataset generation capability to the z-beam-generator Python project. Datasets will be generated from the source Materials.yaml data during the frontmatter export process and written to the z-beam project's `public/datasets/materials/` directory.

---

## Architecture

### Location in z-beam-generator
```
z-beam-generator/
├── components/
│   └── frontmatter/
│       ├── core/
│       │   └── trivial_exporter.py        # Existing frontmatter exporter
│       └── exporters/
│           └── dataset_exporter.py        # NEW: Dataset export module
```

### Integration Point

The dataset exporter will be called **after successful frontmatter generation** in the existing export pipeline:

```python
# In trivial_exporter.py export flow:
1. Load Materials.yaml
2. Generate frontmatter → write to z-beam/frontmatter/materials/
3. Generate datasets → write to z-beam/public/datasets/materials/  # NEW
```

---

## Data Source

**Primary Source**: `data/materials/Materials.yaml`

The dataset exporter will receive the **same parsed material data** used for frontmatter generation, ensuring 100% consistency.

**No re-parsing** - use the already-loaded material dictionary.

---

## Output Formats

For each material, generate 3 files in `public/datasets/materials/`:

### 1. JSON Dataset (`{slug}.json`)
```json
{
  "@context": "https://schema.org",
  "@type": "Dataset",
  "name": "Aluminum Laser Cleaning Dataset",
  "description": "Comprehensive laser cleaning dataset for Aluminum...",
  "url": "https://z-beam.com/materials/metal/non-ferrous/aluminum-laser-cleaning",
  "identifier": "aluminum-laser-cleaning",
  "keywords": ["aluminum", "laser cleaning", "metal"],
  "creator": {
    "@type": "Organization",
    "name": "Z-Beam",
    "url": "https://z-beam.com"
  },
  "datePublished": "2025-12-22T23:35:14.137088Z",
  "dateModified": "2025-12-22T23:35:14.137088Z",
  "license": "https://creativecommons.org/licenses/by/4.0/",
  "distribution": [
    {
      "@type": "DataDownload",
      "encodingFormat": "application/json",
      "contentUrl": "https://z-beam.com/datasets/materials/aluminum-laser-cleaning.json"
    },
    {
      "@type": "DataDownload",
      "encodingFormat": "text/csv",
      "contentUrl": "https://z-beam.com/datasets/materials/aluminum-laser-cleaning.csv"
    },
    {
      "@type": "DataDownload",
      "encodingFormat": "text/plain",
      "contentUrl": "https://z-beam.com/datasets/materials/aluminum-laser-cleaning.txt"
    }
  ],
  "variableMeasured": [
    {
      "@type": "PropertyValue",
      "name": "density",
      "value": "2.7",
      "unitText": "g/cm³",
      "description": "Material density"
    },
    {
      "@type": "PropertyValue",
      "name": "melting_point_min",
      "value": "660",
      "unitText": "°C",
      "description": "Minimum melting point"
    }
    // ... all properties from Materials.yaml
  ],
  "citation": [
    {
      "@type": "CreativeWork",
      "name": "ANSI Z136.1 - Safe Use of Lasers",
      "identifier": "ANSI Z136.1"
    },
    {
      "@type": "CreativeWork",
      "name": "ISO 11146 - Laser beam parameters",
      "identifier": "ISO 11146"
    },
    {
      "@type": "CreativeWork",
      "name": "IEC 60825 - Safety of laser products",
      "identifier": "IEC 60825"
    }
    // At least 3 regulatory/standards citations
  ]
}
```

### 2. CSV Dataset (`{slug}.csv`)
```csv
section,property,value,unit,min,max,description
machine_settings,power,100,watts,50,150,Laser power setting
machine_settings,wavelength,1064,nm,1030,1090,Laser wavelength
machine_settings,frequency,20,kHz,10,30,Pulse frequency
machine_settings,speed,1000,mm/s,500,1500,Scan speed
properties,density,2.7,g/cm³,,,Material density
properties,melting_point,660,°C,660,660,Melting point
properties,thermal_conductivity,237,W/m·K,,,Thermal conductivity
// ... all properties in CSV format
```

**CSV Structure**:
- **Machine settings first** (power, wavelength, frequency, speed)
- **Then properties** (density, melting_point, etc.)
- Columns: section, property, value, unit, min, max, description

### 3. Text Dataset (`{slug}.txt`)
```
LASER CLEANING DATASET: ALUMINUM
=================================
Generated: 2025-12-22T23:35:14Z
Material ID: aluminum-laser-cleaning
Category: Metal

MACHINE SETTINGS
----------------
Power: 100 watts (range: 50-150)
Wavelength: 1064 nm (range: 1030-1090)
Frequency: 20 kHz (range: 10-30)
Speed: 1000 mm/s (range: 500-1500)

MATERIAL PROPERTIES
-------------------
Density: 2.7 g/cm³
Melting Point: 660°C
Thermal Conductivity: 237 W/m·K
...

DESCRIPTION
-----------
[Full material description text]

SOURCE
------
Dataset: https://z-beam.com/datasets/materials/aluminum-laser-cleaning.json
Material Page: https://z-beam.com/materials/metal/non-ferrous/aluminum-laser-cleaning
```

---

## Implementation Details

### Module Structure

**File**: `components/frontmatter/exporters/dataset_exporter.py`

```python
class DatasetExporter:
    """Export material datasets in JSON/CSV/TXT formats"""
    
    def __init__(self, z_beam_path: str):
        """
        Args:
            z_beam_path: Absolute path to z-beam project root
        """
        self.z_beam_path = Path(z_beam_path)
        self.output_dir = self.z_beam_path / "public" / "datasets" / "materials"
        self.site_config = self._load_site_config()
        self.stats = {"generated": 0, "skipped": 0, "errors": 0}
    
    def export_material(self, material_data: dict, slug: str) -> bool:
        """
        Export a single material to all formats
        
        Args:
            material_data: Parsed material dict from Materials.yaml
            slug: Material slug (e.g., "aluminum-laser-cleaning")
            
        Returns:
            True if successful, False otherwise
        """
        try:
            self._export_json(material_data, slug)
            self._export_csv(material_data, slug)
            self._export_txt(material_data, slug)
            self.stats["generated"] += 1
            return True
        except Exception as e:
            self.stats["errors"] += 1
            print(f"❌ Error exporting {slug}: {e}")
            return False
    
    def _export_json(self, material_data: dict, slug: str):
        """Generate Schema.org Dataset JSON"""
        # Build Schema.org structure
        # Include variableMeasured array for all properties
        # Include citation array (min 3 regulatory standards)
        pass
    
    def _export_csv(self, material_data: dict, slug: str):
        """Generate CSV with machine settings + properties"""
        # Machine settings first (power, wavelength, frequency, speed)
        # Then all properties (density, melting_point, etc.)
        pass
    
    def _export_txt(self, material_data: dict, slug: str):
        """Generate human-readable text format"""
        pass
    
    def print_summary(self):
        """Print export statistics"""
        print(f"\n{'='*60}")
        print("DATASET EXPORT SUMMARY")
        print(f"{'='*60}")
        print(f"✅ Generated: {self.stats['generated']} materials")
        print(f"⏭️  Skipped:   {self.stats['skipped']}")
        print(f"❌ Errors:    {self.stats['errors']}")
        print(f"{'='*60}\n")
```

### Integration in trivial_exporter.py

```python
# Add to TrivialExporter class:

def __init__(self, ...):
    # Existing init
    self.dataset_exporter = None  # Lazy init

def export_materials(self, z_beam_path: str):
    """Export materials to z-beam project"""
    # Existing frontmatter export logic...
    
    # After successful frontmatter export:
    self._export_datasets(z_beam_path)

def _export_datasets(self, z_beam_path: str):
    """Export datasets for all materials"""
    from components.frontmatter.exporters.dataset_exporter import DatasetExporter
    
    if not self.dataset_exporter:
        self.dataset_exporter = DatasetExporter(z_beam_path)
    
    print("\n📦 Generating datasets...")
    
    for slug, material_data in self.materials.items():
        self.dataset_exporter.export_material(material_data, slug)
    
    self.dataset_exporter.print_summary()
```

---

## Data Mapping

### From Materials.yaml to Dataset

**Source Structure** (Materials.yaml):
```yaml
aluminum-laser-cleaning:
  name: Aluminum
  category: metal
  properties:
    density: 2.7
    melting_point: 660
    # ... more properties
  machine_settings:
    power: 100
    wavelength: 1064
    # ... more settings
  description: "..."
  micro: "..."
```

**Target Structure** (JSON Dataset):
- `name` → Dataset name (with "Laser Cleaning Dataset" appended)
- `description` → Dataset description
- `properties.*` → variableMeasured array
- `machine_settings.*` → variableMeasured array (separate from properties)
- `datePublished`, `dateModified` → from frontmatter
- `url` → constructed from `full_path`

---

## Configuration

### Site Configuration
Load from `z-beam/site-config.json`:
```json
{
  "site": {
    "domain": "https://z-beam.com",
    "name": "Z-Beam"
  }
}
```

### Output Paths
```python
JSON: z-beam/public/datasets/materials/{slug}.json
CSV:  z-beam/public/datasets/materials/{slug}.csv
TXT:  z-beam/public/datasets/materials/{slug}.txt
```

---

## Testing Strategy

### Unit Tests
```python
# tests/test_dataset_exporter.py

def test_json_export():
    """Test JSON dataset generation"""
    material_data = load_sample_material()
    exporter = DatasetExporter("/path/to/z-beam")
    
    exporter._export_json(material_data, "aluminum-laser-cleaning")
    
    # Verify JSON structure
    json_path = Path("/path/to/z-beam/public/datasets/materials/aluminum-laser-cleaning.json")
    assert json_path.exists()
    
    data = json.loads(json_path.read_text())
    assert data["@type"] == "Dataset"
    assert "variableMeasured" in data
    assert len(data["citation"]) >= 3

def test_csv_export():
    """Test CSV dataset generation"""
    # Test CSV structure, machine settings first, then properties

def test_txt_export():
    """Test text dataset generation"""
    # Test human-readable format
```

### Integration Test
```bash
# Run full export pipeline
cd z-beam-generator
python3 run.py --deploy

# Verify datasets exist
ls z-beam/public/datasets/materials/*.json | wc -l  # Should be 153
```

---

## Error Handling

```python
# Fail-fast on critical errors:
- Missing Materials.yaml → raise FileNotFoundError
- Invalid z-beam path → raise ValueError
- Cannot create output directory → raise PermissionError

# Graceful degradation per-material:
- Missing property → skip that property
- Invalid value → log warning, continue
- Export failure → increment error count, continue to next material
```

---

## Performance Expectations

- **Dataset Generation**: ~2-5 seconds for 153 materials
- **Single-pass**: Use already-parsed material data (no re-parsing)
- **Atomic writes**: Write to temp file, then rename (avoid partial writes)

---

## Success Criteria

✅ All 153 materials generate 3 files each (459 total files)  
✅ JSON passes Schema.org Dataset validation  
✅ CSV opens correctly in Excel/Google Sheets  
✅ TXT is human-readable  
✅ Export completes in <5 seconds  
✅ Zero data inconsistency between frontmatter and datasets  
✅ Integration with existing `--deploy` command  

---

## Migration from Current Approach

**Current**: TypeScript re-parses YAML files  
**New**: Python uses source Materials.yaml data

**Migration Steps**:
1. Build DatasetExporter in z-beam-generator
2. Integrate with trivial_exporter.py
3. Test with sample materials
4. Run full export and compare outputs
5. Deprecate TypeScript dataset generation
6. Remove `scripts/generate-datasets.ts` from z-beam
7. Update package.json to remove old commands

---

## Command Usage

```bash
# In z-beam-generator project:
python3 run.py --deploy

# Output:
# ... frontmatter generation ...
# 📦 Generating datasets...
# ✅ Generated: 153 materials
# ⏭️  Skipped:   0
# ❌ Errors:    0
```

---

## Dependencies

**z-beam-generator** (add to requirements.txt):
```
pyyaml>=6.0
```

**No new dependencies** - uses only Python stdlib + existing PyYAML

---

## File Size Estimates

Per material:
- JSON: ~8-15 KB (with full Schema.org structure)
- CSV: ~2-5 KB (tabular data)
- TXT: ~3-8 KB (human-readable)

Total for 153 materials:
- JSON: ~1.8 MB
- CSV: ~0.6 MB  
- TXT: ~0.9 MB
- **Total: ~3.3 MB**

---

## Next Steps

1. Create `components/frontmatter/exporters/` directory
2. Implement `dataset_exporter.py` module
3. Add integration point in `trivial_exporter.py`
4. Write unit tests
5. Test with sample materials
6. Run full export
7. Compare outputs with TypeScript version
8. Update documentation
9. Deprecate TypeScript approach

---

## Questions for Implementation

- [ ] Should datasets be versioned (e.g., include schema_version)?
- [ ] Should we compress large JSON files (gzip)?
- [ ] Do we need a master index file (all-materials.json)?
- [ ] Should citation array be configurable or hardcoded?
- [ ] Handle missing properties gracefully or fail?

---

**Status**: Ready for implementation  
**Priority**: High (eliminates data inconsistency risk)  
**Estimated Effort**: 4-6 hours
