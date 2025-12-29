# Dataset Dynamic Field Detection Architecture

**Date**: December 30, 2025  
**Status**: DESIGN PROPOSAL  
**Purpose**: Enable datasets to automatically pick up new YAML fields without code changes

---

## Problem Statement

Current implementation (`scripts/export/generate_datasets.py`):
- ✅ **Already dynamically iterates** through YAML structure
- ❌ **Has hardcoded skip lists**: `if prop_name in ['label', 'description', 'percentage']: continue`
- ❌ **Has hardcoded field checks**: `if 'value' in prop_value or 'unit' in prop_value`
- ❌ **No formal Dataset abstraction** - logic embedded in generator script

**User Requirement**: "Ensure Datasets dynamically pick up new fields whenever source data yaml files are updated"

---

## Current Implementation Analysis

**File**: `scripts/export/generate_datasets.py` (852 lines)

**What Works Well**:
```python
# ✅ Already iterates dynamically through YAML
properties = material_data.get('properties', {})
for category_name, category_data in properties.items():
    for prop_name, prop_value in category_data.items():
        # Process property
```

**What Needs Improvement**:
```python
# ❌ Hardcoded skip list
if prop_name in ['label', 'description', 'percentage']:
    continue

# ❌ Hardcoded field presence check
if 'value' in prop_value or 'unit' in prop_value:
    # Process property
```

---

## Design Goals

1. **Zero Hardcoding**: No hardcoded field names or skip lists
2. **Metadata Detection**: Automatically distinguish metadata from data fields
3. **Nested Support**: Handle nested structures, arrays, objects
4. **Type Awareness**: Detect field types (string, number, range, object)
5. **Schema.org Compliance**: Generate proper PropertyValue structures
6. **Format Support**: JSON (Schema.org), CSV (tabular), TXT (human-readable)
7. **Testability**: Easy to test with new fields

---

## Proposed Architecture

### Base Dataset Class

```python
from abc import ABC, abstractmethod
from typing import Dict, Any, List, Set
from pathlib import Path

class BaseDataset(ABC):
    """
    Base class for dynamic dataset generation.
    
    Automatically detects all fields in YAML data and generates
    Schema.org datasets without hardcoded field lists.
    """
    
    # Field detection configuration
    METADATA_MARKERS = {'label', 'description', 'title', 'icon', 'order', 'variant'}
    STRUCTURAL_MARKERS = {'_section', '_meta', '_config'}
    
    def __init__(self, source_yaml_path: Path):
        """Initialize with source YAML file path"""
        self.source_path = source_yaml_path
        self.data = self._load_yaml()
        
    @abstractmethod
    def _load_yaml(self) -> Dict[str, Any]:
        """Load and parse source YAML file"""
        pass
    
    def detect_fields(self, data: Dict[str, Any], prefix: str = "") -> List[Dict[str, Any]]:
        """
        Dynamically detect all data fields in YAML structure.
        
        Returns list of field descriptors with:
        - name: Field name (flattened path for nested)
        - type: Field type (string, number, range, object, array)
        - value: Field value
        - metadata: Associated metadata (unit, min, max, etc.)
        
        Args:
            data: YAML data to introspect
            prefix: Path prefix for nested fields (e.g., "properties.mechanical")
        
        Returns:
            List of field descriptors
        """
        fields = []
        
        for key, value in data.items():
            # Skip metadata and structural fields
            if self._is_metadata_field(key):
                continue
            
            # Build field path
            field_path = f"{prefix}.{key}" if prefix else key
            
            # Detect field type and extract
            if self._is_range_field(value):
                fields.append(self._extract_range_field(field_path, value))
            elif self._is_property_value(value):
                fields.append(self._extract_property_value(field_path, value))
            elif isinstance(value, dict):
                # Recurse into nested structure
                fields.extend(self.detect_fields(value, prefix=field_path))
            elif isinstance(value, list):
                fields.append(self._extract_array_field(field_path, value))
            else:
                fields.append(self._extract_simple_field(field_path, value))
        
        return fields
    
    def _is_metadata_field(self, key: str) -> bool:
        """Check if field name is metadata (not data)"""
        # Metadata markers
        if key in self.METADATA_MARKERS:
            return True
        # Structural markers (prefixed with _)
        if key.startswith('_'):
            return True
        # Section metadata (ends with _section)
        if key.endswith('_section'):
            return True
        return False
    
    def _is_range_field(self, value: Any) -> bool:
        """Check if value is a range (has min/max)"""
        if not isinstance(value, dict):
            return False
        return 'min' in value or 'max' in value
    
    def _is_property_value(self, value: Any) -> bool:
        """Check if value is a PropertyValue (has value/unit)"""
        if not isinstance(value, dict):
            return False
        return 'value' in value or 'unit' in value
    
    def _extract_range_field(self, name: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Extract range field descriptor"""
        return {
            "name": name,
            "type": "range",
            "min": data.get('min'),
            "max": data.get('max'),
            "unit": data.get('unit', ''),
            "value": data.get('value'),  # Optional default
            "metadata": {k: v for k, v in data.items() if k not in {'min', 'max', 'value', 'unit'}}
        }
    
    def _extract_property_value(self, name: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Extract PropertyValue field descriptor"""
        return {
            "name": name,
            "type": "property_value",
            "value": data.get('value'),
            "unit": data.get('unit', ''),
            "min": data.get('min'),
            "max": data.get('max'),
            "metadata": {k: v for k, v in data.items() if k not in {'value', 'unit', 'min', 'max'}}
        }
    
    def _extract_array_field(self, name: str, data: List[Any]) -> Dict[str, Any]:
        """Extract array field descriptor"""
        return {
            "name": name,
            "type": "array",
            "value": data,
            "length": len(data),
            "metadata": {}
        }
    
    def _extract_simple_field(self, name: str, value: Any) -> Dict[str, Any]:
        """Extract simple field descriptor"""
        return {
            "name": name,
            "type": type(value).__name__,
            "value": value,
            "metadata": {}
        }
    
    def to_schema_org_json(self, item_id: str, item_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate Schema.org Dataset JSON with dynamic field detection.
        
        Args:
            item_id: Item identifier
            item_data: Item data from YAML
        
        Returns:
            Schema.org Dataset structure
        """
        # Detect all fields dynamically
        fields = self.detect_fields(item_data)
        
        # Build variableMeasured array
        variable_measured = []
        for field in fields:
            if field['type'] in {'property_value', 'range'}:
                variable_measured.append({
                    "@type": "PropertyValue",
                    "name": field['name'].replace('_', ' ').replace('.', ' - ').title(),
                    "value": str(field.get('value', '')),
                    "unitText": field.get('unit', ''),
                    "minValue": field.get('min'),
                    "maxValue": field.get('max')
                })
        
        # Build base dataset structure
        return {
            "@context": "https://schema.org",
            "@type": "Dataset",
            "@id": f"https://www.z-beam.com/datasets/{item_id}",
            "name": item_data.get('name', item_id),
            "description": item_data.get('description', ''),
            "variableMeasured": variable_measured,
            "keywords": self._extract_keywords(item_data),
            "dateModified": item_data.get('updated_at', ''),
            "license": "https://creativecommons.org/licenses/by/4.0/"
        }
    
    def to_csv_rows(self, item_data: Dict[str, Any]) -> List[Dict[str, str]]:
        """
        Generate CSV rows with dynamic field detection.
        
        Returns list of row dicts with columns:
        - Category
        - Property
        - Value
        - Unit
        - Min
        - Max
        """
        fields = self.detect_fields(item_data)
        rows = []
        
        for field in fields:
            if field['type'] in {'property_value', 'range'}:
                # Extract category from path (e.g., "properties.mechanical.hardness" → "mechanical")
                parts = field['name'].split('.')
                category = parts[-2] if len(parts) > 1 else 'General'
                property_name = parts[-1]
                
                rows.append({
                    "Category": category.replace('_', ' ').title(),
                    "Property": property_name.replace('_', ' ').title(),
                    "Value": str(field.get('value', '')),
                    "Unit": field.get('unit', ''),
                    "Min": str(field.get('min', '')),
                    "Max": str(field.get('max', ''))
                })
        
        return rows
    
    def to_txt(self, item_id: str, item_data: Dict[str, Any]) -> str:
        """
        Generate human-readable TXT format with dynamic field detection.
        """
        lines = [
            f"DATASET: {item_data.get('name', item_id)}",
            "=" * 80,
            "",
            "DESCRIPTION:",
            item_data.get('description', ''),
            "",
            "FIELDS:",
            "-" * 80
        ]
        
        fields = self.detect_fields(item_data)
        
        # Group by category
        categories = {}
        for field in fields:
            parts = field['name'].split('.')
            category = parts[-2] if len(parts) > 1 else 'General'
            if category not in categories:
                categories[category] = []
            categories[category].append(field)
        
        # Output by category
        for category, cat_fields in categories.items():
            lines.append(f"\n{category.replace('_', ' ').title()}:")
            for field in cat_fields:
                prop_name = field['name'].split('.')[-1]
                value_str = self._format_field_value(field)
                lines.append(f"  {prop_name}: {value_str}")
        
        return '\n'.join(lines)
    
    def _format_field_value(self, field: Dict[str, Any]) -> str:
        """Format field value for TXT output"""
        value = field.get('value', '')
        unit = field.get('unit', '')
        min_val = field.get('min', '')
        max_val = field.get('max', '')
        
        value_str = f"{value} {unit}".strip()
        if min_val and max_val:
            value_str += f" (range: {min_val}-{max_val} {unit})"
        
        return value_str
    
    @abstractmethod
    def _extract_keywords(self, item_data: Dict[str, Any]) -> List[str]:
        """Extract keywords for dataset (domain-specific)"""
        pass
```

### Domain-Specific Datasets

```python
class MaterialsDataset(BaseDataset):
    """
    Materials dataset with machine settings merged (ADR 005).
    
    Automatically detects all fields from Materials.yaml including:
    - Material properties (nested by category)
    - Machine settings (merged from Settings.yaml)
    - Any new fields added to YAML
    """
    
    def _load_yaml(self) -> Dict[str, Any]:
        """Load Materials.yaml"""
        from domains.materials.data_loader_v2 import MaterialsDataLoader
        loader = MaterialsDataLoader()
        return loader.load_materials()
    
    def _extract_keywords(self, item_data: Dict[str, Any]) -> List[str]:
        """Extract material-specific keywords"""
        keywords = [
            item_data.get('name', ''),
            "laser cleaning",
            "material properties",
            "industrial cleaning"
        ]
        
        # Add category/subcategory if present
        if 'category' in item_data:
            keywords.append(item_data['category'])
        if 'subcategory' in item_data:
            keywords.append(item_data['subcategory'])
        
        return [k for k in keywords if k]


class ContaminantsDataset(BaseDataset):
    """
    Contaminants dataset with compounds merged (ADR 005).
    
    Automatically detects all fields from Contaminants.yaml including:
    - Contaminant pattern data
    - Related compounds (merged from Compounds.yaml)
    - Any new fields added to YAML
    """
    
    def __init__(self, source_yaml_path: Path, compounds_data: Dict[str, Any]):
        """Initialize with contaminants data and compounds for merging"""
        self.compounds_data = compounds_data
        super().__init__(source_yaml_path)
    
    def _load_yaml(self) -> Dict[str, Any]:
        """Load Contaminants.yaml"""
        from domains.contaminants.data_loader_v2 import ContaminantsDataLoader
        loader = ContaminantsDataLoader()
        return loader.load_patterns()
    
    def merge_compounds(self, contaminant_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Merge compound data into contaminant (ADR 005).
        
        Dynamically detects compound fields without hardcoding.
        """
        enriched = contaminant_data.copy()
        related_compounds = contaminant_data.get('related_compounds', [])
        
        compounds_array = []
        for compound_id in related_compounds:
            if compound_id in self.compounds_data:
                compound = self.compounds_data[compound_id]
                # Detect all compound fields dynamically
                compounds_array.append(compound)
        
        enriched['compounds'] = compounds_array
        return enriched
    
    def _extract_keywords(self, item_data: Dict[str, Any]) -> List[str]:
        """Extract contaminant-specific keywords"""
        keywords = [
            item_data.get('name', ''),
            "laser cleaning",
            "contaminant removal",
            "surface cleaning"
        ]
        
        # Add category if present
        if 'category' in item_data:
            keywords.append(item_data['category'])
        
        return [k for k in keywords if k]
```

---

## Implementation Strategy

### Phase 1: Create Dataset Classes
1. Create `shared/dataset/base_dataset.py` with BaseDataset
2. Create `shared/dataset/materials_dataset.py` with MaterialsDataset
3. Create `shared/dataset/contaminants_dataset.py` with ContaminantsDataset
4. Create `shared/dataset/__init__.py` with exports

### Phase 2: Update Generator Script
1. Refactor `scripts/export/generate_datasets.py` to use Dataset classes
2. Remove hardcoded field lists and skip logic
3. Use dynamic field detection throughout

### Phase 3: Fill In Test Stubs
1. Complete all TODOs in `tests/test_dataset_generation_source_yaml.py`
2. Add test: "New YAML field automatically included in dataset"
3. Add test: "Metadata fields properly excluded"
4. Add test: "Nested fields properly flattened"

### Phase 4: Verification
1. Run all tests - verify pass
2. Generate datasets for all materials/contaminants
3. Manually add new field to Materials.yaml - verify auto-included
4. Remove field - verify auto-excluded

---

## Benefits

1. **Zero Maintenance**: New fields automatically detected
2. **No Hardcoding**: No skip lists or field checks
3. **Type Aware**: Automatically detects ranges, property values, etc.
4. **Testable**: Easy to verify dynamic behavior
5. **Schema.org Compliant**: Generates proper PropertyValue structures
6. **Multi-Format**: JSON, CSV, TXT all supported

---

## Migration Path

**Current**:
```python
# Hardcoded skip list
if prop_name in ['label', 'description', 'percentage']:
    continue
```

**After**:
```python
# Automatic metadata detection
dataset = MaterialsDataset(materials_yaml_path)
fields = dataset.detect_fields(material_data)
# All data fields automatically included, metadata excluded
```

**Test Case**:
```python
def test_new_field_automatically_included():
    """When new field added to YAML, dataset includes it"""
    # Add new field to test material
    material_data['properties']['thermal']['conductivity'] = {
        'value': 50,
        'unit': 'W/mK',
        'min': 40,
        'max': 60
    }
    
    # Generate dataset
    dataset = MaterialsDataset(test_materials_path)
    fields = dataset.detect_fields(material_data)
    
    # Verify new field detected
    field_names = [f['name'] for f in fields]
    assert 'properties.thermal.conductivity' in field_names
    
    # Verify appears in all formats
    json_data = dataset.to_schema_org_json('aluminum', material_data)
    assert any('conductivity' in v['name'].lower() 
               for v in json_data['variableMeasured'])
```

---

## Success Criteria

- [ ] BaseDataset class created with dynamic field detection
- [ ] MaterialsDataset and ContaminantsDataset implemented
- [ ] Generator script refactored to use Dataset classes
- [ ] All hardcoded skip lists removed
- [ ] All hardcoded field checks removed
- [ ] All test TODOs filled in with assertions
- [ ] All tests pass
- [ ] Manual verification: Add field to YAML → appears in dataset
- [ ] Manual verification: Remove field from YAML → disappears from dataset
- [ ] Zero code changes required when YAML schema changes

---

## Future Enhancements

1. **Field Type Inference**: Automatically detect field types from values
2. **Schema Validation**: Validate detected fields against schemas
3. **Documentation Generation**: Auto-generate field documentation
4. **Change Detection**: Track field additions/removals over time
5. **Field Statistics**: Count fields, coverage, completeness
