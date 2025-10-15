# Systematic Data Architecture Proposal

## Executive Summary

Proposal for restructuring the `/data` folder to create a modular, maintainable, and scalable database system for materialProperties and machineSettings using normalized YAML files.

---

## Current State Analysis

### Current Structure
```
data/
├── Materials.yaml          # 122 materials, ~15,000 lines, monolithic
├── Categories.yaml         # Application types, standards, metrics
└── materials.py           # Python loader
```

### Current Issues
1. **Monolithic File**: Single 15,000-line file difficult to maintain
2. **No Standardization**: Property definitions scattered across materials
3. **Duplication**: Same property descriptions repeated 122 times
4. **Hard to Update**: Changing a property definition requires 122 edits
5. **No Validation**: No central schema for property types
6. **Discovery Difficult**: Hard to find which materials have which properties

---

## Proposed Architecture

### 1. Normalized Database Structure

```
data/
├── Materials.yaml                    # Master index (SIMPLE)
├── Categories.yaml                   # Existing - unchanged
├── materials.py                      # Enhanced loader
│
├── properties/                       # Property Definitions (REFERENCE)
│   ├── material_properties.yaml     # All materialProperty schemas
│   ├── machine_settings.yaml        # All machineSetting schemas
│   └── README.md                    # Documentation
│
├── values/                          # Actual Values (DATA)
│   ├── metals/
│   │   ├── aluminum.yaml
│   │   ├── copper.yaml
│   │   ├── gold.yaml
│   │   └── ...
│   ├── ceramics/
│   │   ├── alumina.yaml
│   │   ├── silicon-carbide.yaml
│   │   └── ...
│   ├── polymers/
│   │   ├── polycarbonate.yaml
│   │   └── ...
│   ├── composites/
│   │   └── ...
│   └── stones/
│       └── ...
│
└── templates/                       # Templates (HELPERS)
    ├── new_material_template.yaml
    ├── property_template.yaml
    └── validation_rules.yaml
```

---

## Detailed Design

### 2. Property Definitions (Reference Schema)

**File: `data/properties/material_properties.yaml`**

```yaml
# Material Properties Schema - Single Source of Truth
# Each property defined once, referenced by all materials

properties:
  density:
    displayName: "Density"
    description: "Mass per unit volume of the material"
    unit: "g/cm³"
    category: "physical"
    typical_range: [0.1, 20.0]
    required: true
    validation:
      type: "numeric"
      min: 0.01
      max: 25.0
    common_materials:
      - metals: [2.0, 20.0]
      - polymers: [0.8, 2.0]
      - ceramics: [2.0, 6.0]
    measurement_methods:
      - "Archimedes principle"
      - "Pycnometry"
    sources:
      - "NIST"
      - "MatWeb"
      - "ASM Handbook"
  
  meltingPoint:
    displayName: "Melting Point"
    description: "Temperature at which material transitions from solid to liquid"
    unit: "°C"
    category: "thermal"
    typical_range: [-200, 3500]
    required: true
    validation:
      type: "numeric"
      min: -273
      max: 4000
    notes: "Some ceramics decompose rather than melt"
    measurement_methods:
      - "DSC (Differential Scanning Calorimetry)"
      - "TGA (Thermogravimetric Analysis)"
    sources:
      - "NIST"
      - "CRC Handbook"
  
  thermalConductivity:
    displayName: "Thermal Conductivity"
    description: "Ability to conduct heat through the material"
    unit: "W/m·K"
    category: "thermal"
    typical_range: [0.1, 500]
    required: false
    validation:
      type: "numeric"
      min: 0.01
      max: 600
    common_materials:
      - metals: [50, 400]
      - polymers: [0.1, 0.5]
      - ceramics: [1, 50]
    laser_relevance: "Critical for heat dissipation during laser cleaning"
  
  # ... all other properties defined here
```

**File: `data/properties/machine_settings.yaml`**

```yaml
# Machine Settings Schema - Single Source of Truth
# Laser parameter definitions for all materials

settings:
  powerRange:
    displayName: "Power Range"
    description: "Optimal laser average power for surface cleaning"
    unit: "W"
    category: "power"
    typical_range: [10, 500]
    required: true
    validation:
      type: "numeric"
      min: 1
      max: 1000
    common_ranges:
      - delicate: [10, 50]
      - standard: [50, 150]
      - heavy_duty: [150, 500]
    safety_notes: "Must not exceed material damage threshold"
  
  wavelength:
    displayName: "Wavelength"
    description: "Laser wavelength optimized for material absorption"
    unit: "nm"
    category: "optical"
    typical_range: [355, 1064]
    required: true
    validation:
      type: "numeric"
      min: 200
      max: 2000
    common_values:
      - UV: 355
      - Green: 532
      - Near-IR: 1064
    laser_relevance: "Material absorption depends critically on wavelength"
  
  # ... all other settings defined here
```

---

### 3. Material Value Files (Actual Data)

**File: `data/values/metals/aluminum.yaml`**

```yaml
# Aluminum Material Data
# References: property definitions in data/properties/

metadata:
  name: "Aluminum"
  category: "metal"
  subcategory: "Aluminum"
  commonNames: ["Aluminium", "Al"]
  casNumber: "7429-90-5"
  lastUpdated: "2025-10-02"
  dataQuality: "high"
  verifiedBy: "AI Research 2025"

materialProperties:
  # Simple format - just values, definitions come from properties/material_properties.yaml
  density:
    value: 2.70
    min: 2.33
    max: 7.13
    confidence: 98
    source: "ai_research"
    notes: "Pure aluminum at room temperature"
  
  meltingPoint:
    value: 660
    confidence: 99
    source: "ai_research"
    notes: "Pure aluminum melting point"
  
  thermalConductivity:
    value: 237
    min: 0.2
    max: 156
    confidence: 95
    source: "ai_research"
  
  hardness:
    value: 30
    unit: "HB"  # Override default unit if needed
    min: 2
    max: 9.5
    confidence: 92
    source: "ai_research"
  
  # ... other properties

machineSettings:
  # Simple format - just values, definitions come from properties/machine_settings.yaml
  powerRange:
    value: 100
    min: 50
    max: 200
    confidence: 95
    source: "ai_research"
  
  wavelength:
    value: 1064
    min: 532
    max: 1064
    confidence: 90
    source: "ai_research"
  
  # ... other settings

# Optional: Material-specific metadata
industryTags:
  - aerospace
  - automotive
  - packaging

applications:
  - "Aerospace component restoration"
  - "Automotive part cleaning"
  - "Food packaging preparation"
```

---

### 4. Master Index (Simple Reference)

**File: `data/Materials.yaml`** (Simplified)

```yaml
# Materials Master Index
# Links to individual material files in data/values/

materials:
  Aluminum:
    file: "values/metals/aluminum.yaml"
    category: "metal"
    status: "active"
    verified: true
  
  Copper:
    file: "values/metals/copper.yaml"
    category: "metal"
    status: "active"
    verified: true
  
  "Silicon Carbide":
    file: "values/ceramics/silicon-carbide.yaml"
    category: "ceramic"
    status: "active"
    verified: true
  
  # ... 122 materials indexed here
```

---

## Implementation Benefits

### 1. **Maintainability**
- ✅ Property definitions in one place
- ✅ Update property description → affects all materials
- ✅ Easy to add new properties
- ✅ Clear separation of concerns

### 2. **Data Quality**
- ✅ Consistent property definitions
- ✅ Validation rules enforced
- ✅ Type checking at load time
- ✅ Range validation automatic

### 3. **Scalability**
- ✅ Add 100 materials? Just 100 new small files
- ✅ Easy to parallelize data collection
- ✅ Individual files can be worked on independently
- ✅ Git-friendly (small file changes)

### 4. **Discovery**
```python
# Easy queries
materials_with_high_thermal_conductivity = find_materials(
    property="thermalConductivity",
    min_value=100
)

materials_needing_uv_laser = find_materials(
    setting="wavelength",
    value=355
)
```

### 5. **Data Entry**
```bash
# Create new material from template
cp data/templates/new_material_template.yaml data/values/metals/titanium.yaml

# Fill in only the values - definitions already exist!
```

---

## Enhanced Loader Implementation

**File: `data/materials.py`** (Enhanced)

```python
#!/usr/bin/env python3
"""Enhanced Materials Database Loader with Validation"""

import yaml
from pathlib import Path
from typing import Dict, List, Optional
from functools import lru_cache

class MaterialsDatabase:
    def __init__(self, data_dir: Path = None):
        self.data_dir = data_dir or Path(__file__).parent
        self.property_schemas = self._load_property_schemas()
        self.setting_schemas = self._load_setting_schemas()
        self.materials_index = self._load_materials_index()
    
    def _load_property_schemas(self) -> Dict:
        """Load property definitions (reference schema)"""
        schema_file = self.data_dir / "properties" / "material_properties.yaml"
        with open(schema_file) as f:
            return yaml.safe_load(f)['properties']
    
    def _load_setting_schemas(self) -> Dict:
        """Load machine setting definitions (reference schema)"""
        schema_file = self.data_dir / "properties" / "machine_settings.yaml"
        with open(schema_file) as f:
            return yaml.safe_load(f)['settings']
    
    def _load_materials_index(self) -> Dict:
        """Load materials master index"""
        index_file = self.data_dir / "Materials.yaml"
        with open(index_file) as f:
            return yaml.safe_load(f)['materials']
    
    @lru_cache(maxsize=200)
    def load_material(self, name: str) -> Dict:
        """Load and validate a single material"""
        if name not in self.materials_index:
            raise ValueError(f"Material {name} not found in index")
        
        # Load material data file
        material_info = self.materials_index[name]
        material_file = self.data_dir / material_info['file']
        
        with open(material_file) as f:
            material_data = yaml.safe_load(f)
        
        # Enrich with property schemas
        enriched = self._enrich_with_schemas(material_data)
        
        # Validate
        self._validate_material(name, enriched)
        
        return enriched
    
    def _enrich_with_schemas(self, material_data: Dict) -> Dict:
        """Add property definitions to material values"""
        enriched = material_data.copy()
        
        # Add property metadata
        if 'materialProperties' in enriched:
            for prop_name, prop_value in enriched['materialProperties'].items():
                if prop_name in self.property_schemas:
                    schema = self.property_schemas[prop_name]
                    prop_value['schema'] = {
                        'displayName': schema['displayName'],
                        'description': schema['description'],
                        'unit': schema.get('unit', prop_value.get('unit')),
                        'category': schema['category']
                    }
        
        # Add setting metadata
        if 'machineSettings' in enriched:
            for setting_name, setting_value in enriched['machineSettings'].items():
                if setting_name in self.setting_schemas:
                    schema = self.setting_schemas[setting_name]
                    setting_value['schema'] = {
                        'displayName': schema['displayName'],
                        'description': schema['description'],
                        'unit': schema.get('unit', setting_value.get('unit')),
                        'category': schema['category']
                    }
        
        return enriched
    
    def _validate_material(self, name: str, material_data: Dict):
        """Validate material data against schemas"""
        errors = []
        
        # Validate properties
        for prop_name, prop_data in material_data.get('materialProperties', {}).items():
            if prop_name in self.property_schemas:
                schema = self.property_schemas[prop_name]
                value = prop_data.get('value')
                
                # Type validation
                if schema['validation']['type'] == 'numeric':
                    if not isinstance(value, (int, float)):
                        errors.append(f"{name}.{prop_name}: value must be numeric, got {type(value)}")
                    
                    # Range validation
                    min_val = schema['validation'].get('min')
                    max_val = schema['validation'].get('max')
                    if min_val and value < min_val:
                        errors.append(f"{name}.{prop_name}: value {value} below minimum {min_val}")
                    if max_val and value > max_val:
                        errors.append(f"{name}.{prop_name}: value {value} above maximum {max_val}")
        
        if errors:
            raise ValueError(f"Validation errors for {name}:\n" + "\n".join(errors))
    
    def load_all_materials(self) -> Dict:
        """Load all materials efficiently"""
        return {name: self.load_material(name) for name in self.materials_index.keys()}
    
    def find_materials(self, **filters) -> List[str]:
        """Find materials matching criteria"""
        # property="density", min_value=5.0
        # category="metal"
        # etc.
        matching = []
        
        for name in self.materials_index.keys():
            material = self.load_material(name)
            
            if self._matches_filters(material, filters):
                matching.append(name)
        
        return matching
    
    def _matches_filters(self, material: Dict, filters: Dict) -> bool:
        """Check if material matches filter criteria"""
        # Implementation of filter matching logic
        for key, value in filters.items():
            if key == "category":
                if material.get('metadata', {}).get('category') != value:
                    return False
            elif key == "property":
                prop_name = filters.get('property')
                min_val = filters.get('min_value')
                max_val = filters.get('max_value')
                
                if prop_name in material.get('materialProperties', {}):
                    prop_value = material['materialProperties'][prop_name].get('value')
                    if min_val and prop_value < min_val:
                        return False
                    if max_val and prop_value > max_val:
                        return False
                else:
                    return False
        
        return True

# Backward compatibility function
@lru_cache(maxsize=1)
def load_materials() -> Dict:
    """Load materials in legacy format for backward compatibility"""
    db = MaterialsDatabase()
    all_materials = db.load_all_materials()
    
    # Convert to legacy format
    legacy_format = {
        'materials': {}
    }
    
    for name, material in all_materials.items():
        legacy_format['materials'][name] = {
            'name': name,
            'category': material.get('metadata', {}).get('category', 'Unknown'),
            'materialProperties': material.get('materialProperties', {}),
            'machineSettings': material.get('machineSettings', {})
        }
    
    return legacy_format
```

---

## Migration Strategy

### Phase 1: Setup (Week 1)
1. Create new directory structure
2. Extract property schemas from current Materials.yaml
3. Create property definition files
4. Create templates

### Phase 2: Migration (Week 2-3)
1. Split Materials.yaml into individual files (automated script)
2. Create master index
3. Update loader with validation
4. Run comprehensive validation

### Phase 3: Testing (Week 4)
1. Test backward compatibility
2. Verify all 122 materials load correctly
3. Performance testing
4. Update documentation

### Phase 4: Enhancement (Week 5)
1. Add advanced query functions
2. Create data entry tools
3. Implement AI-powered validation
4. Create maintenance scripts

---

## Tools to Build

### 1. Migration Script
```bash
python3 scripts/migrate_to_normalized_structure.py
```

### 2. Material Creator
```bash
python3 scripts/create_material.py --name "Titanium" --category "metal"
# Creates template and opens in editor
```

### 3. Property Validator
```bash
python3 scripts/validate_all_materials.py
# Validates all materials against schemas
```

### 4. Property Adder
```bash
python3 scripts/add_property.py --name "surfaceRoughness"
# Adds new property to schema and prompts for values
```

### 5. Bulk Updater
```bash
python3 scripts/bulk_update.py --property "density" --source "NIST_2025"
# Updates source field for all density values
```

---

## Example Queries

```python
from data.materials import MaterialsDatabase

db = MaterialsDatabase()

# Find all metals with high thermal conductivity
metals = db.find_materials(
    category="metal",
    property="thermalConductivity",
    min_value=200
)

# Find materials needing UV laser
uv_materials = db.find_materials(
    setting="wavelength",
    value=355
)

# Get material with full metadata
aluminum = db.load_material("Aluminum")
print(aluminum['materialProperties']['density']['schema']['description'])
# "Mass per unit volume of the material"
```

---

## File Size Comparison

### Current
- `Materials.yaml`: 15,000 lines, 450 KB

### Proposed
- `Materials.yaml` (index): 300 lines, 10 KB
- `material_properties.yaml`: 500 lines, 20 KB
- `machine_settings.yaml`: 300 lines, 12 KB
- 122 material files: avg 150 lines each = 18,300 lines, 550 KB total
- **Total: 19,400 lines, 592 KB** (split across 125+ files)

---

## Conclusion

### Benefits
✅ **Maintainability**: Update property definitions once, affect all materials
✅ **Scalability**: Easy to add materials and properties
✅ **Quality**: Automatic validation and consistency
✅ **Discovery**: Powerful query capabilities
✅ **Collaboration**: Small files, git-friendly, parallel work possible
✅ **Documentation**: Self-documenting with schemas

### Implementation Effort
- Setup: 1 week
- Migration: 2-3 weeks
- Testing: 1 week
- **Total: 4-5 weeks**

### Recommendation
**Proceed with migration** - The long-term benefits far outweigh the short-term migration effort. The current monolithic structure will become increasingly difficult to maintain as the database grows.

---

**Next Steps:**
1. Review and approve proposal
2. Create migration script
3. Pilot with 10 materials
4. Full migration if successful
5. Deploy enhanced loader
