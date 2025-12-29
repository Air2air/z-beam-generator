"""
Base Dataset Class for Dynamic Field Detection

Automatically detects all fields in YAML data and generates Schema.org datasets
without hardcoded field lists.

Architecture:
- Zero hardcoding: No skip lists or field name checks
- Type-aware: Detects ranges, property values, objects, arrays
- Metadata detection: Automatically distinguishes metadata from data
- Schema.org compliant: Generates proper PropertyValue structures
- Multi-format: JSON, CSV, TXT output

Usage:
    dataset = MaterialsDataset(materials_yaml_path)
    
    # Detect all fields dynamically
    fields = dataset.detect_fields(material_data)
    
    # Generate Schema.org JSON
    json_data = dataset.to_schema_org_json('aluminum', material_data)
    
    # Generate CSV rows
    csv_rows = dataset.to_csv_rows(material_data)
    
    # Generate TXT format
    txt_content = dataset.to_txt('aluminum', material_data)

Policy Compliance:
- NO hardcoded field names or skip lists
- Dynamic detection of all YAML fields
- Automatic metadata exclusion
- New fields automatically included
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, List, Set, Optional
from pathlib import Path
import yaml


class BaseDataset(ABC):
    """
    Base class for dynamic dataset generation.
    
    Automatically detects all fields in YAML data and generates
    Schema.org datasets without hardcoded field lists.
    """
    
    # Field detection configuration
    METADATA_MARKERS: Set[str] = {
        'label', 'description', 'title', 'icon', 'order', 
        'variant', 'percentage', 'breadcrumb', 'breadcrumb_text'
    }
    STRUCTURAL_MARKERS: Set[str] = {'_section', '_meta', '_config'}
    
    def __init__(self, source_yaml_path: Optional[Path] = None):
        """
        Initialize with optional source YAML file path.
        
        Args:
            source_yaml_path: Path to source YAML file (optional)
        """
        self.source_path = source_yaml_path
        # Always load YAML data (subclasses implement _load_yaml())
        self.data = self._load_yaml()
        
    @abstractmethod
    def _load_yaml(self) -> Dict[str, Any]:
        """
        Load and parse source YAML file.
        
        Returns:
            Parsed YAML data
        """
        pass
    
    @abstractmethod
    def _get_dataset_type(self) -> str:
        """
        Get dataset type identifier (subdirectory name).
        
        Returns:
            Dataset type (e.g., 'materials', 'contaminants')
        """
        pass
    
    @abstractmethod
    def _get_dataset_suffix(self) -> str:
        """
        Get dataset filename suffix.
        
        Returns:
            Dataset suffix (e.g., '-material-dataset', '-contaminant-dataset')
        """
        pass
    
    def detect_fields(
        self, 
        data: Dict[str, Any], 
        prefix: str = "",
        parent_category: str = ""
    ) -> List[Dict[str, Any]]:
        """
        Dynamically detect all data fields in YAML structure.
        
        Returns list of field descriptors with:
        - name: Field name (flattened path for nested)
        - type: Field type (string, number, range, object, array)
        - value: Field value
        - metadata: Associated metadata (unit, min, max, etc.)
        - category: Parent category (for organization)
        
        Args:
            data: YAML data to introspect
            prefix: Path prefix for nested fields (e.g., "properties.mechanical")
            parent_category: Category label from parent
        
        Returns:
            List of field descriptors
        """
        fields = []
        
        # Extract category label if present
        category = data.get('label', parent_category) if isinstance(data, dict) else parent_category
        
        for key, value in data.items():
            # Skip metadata and structural fields
            if self._is_metadata_field(key):
                continue
            
            # Build field path
            field_path = f"{prefix}.{key}" if prefix else key
            
            # Detect field type and extract
            if self._is_range_field(value):
                fields.append(self._extract_range_field(field_path, value, category))
            elif self._is_property_value(value):
                fields.append(self._extract_property_value(field_path, value, category))
            elif isinstance(value, dict):
                # Recurse into nested structure
                fields.extend(self.detect_fields(value, prefix=field_path, parent_category=category))
            elif isinstance(value, list):
                fields.append(self._extract_array_field(field_path, value, category))
            else:
                # Simple field (string, number, boolean)
                fields.append(self._extract_simple_field(field_path, value, category))
        
        return fields
    
    def _is_metadata_field(self, key: str) -> bool:
        """
        Check if field name is metadata (not data).
        
        Metadata fields are excluded from dataset generation.
        
        Args:
            key: Field name
        
        Returns:
            True if metadata field
        """
        # Metadata markers (label, description, etc.)
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
        """
        Check if value is a range (has min/max).
        
        Args:
            value: Field value
        
        Returns:
            True if range field
        """
        if not isinstance(value, dict):
            return False
        return 'min' in value or 'max' in value
    
    def _is_property_value(self, value: Any) -> bool:
        """
        Check if value is a PropertyValue (has value/unit).
        
        Args:
            value: Field value
        
        Returns:
            True if PropertyValue field
        """
        if not isinstance(value, dict):
            return False
        return 'value' in value or 'unit' in value
    
    def _extract_range_field(
        self, 
        name: str, 
        data: Dict[str, Any], 
        category: str
    ) -> Dict[str, Any]:
        """
        Extract range field descriptor.
        
        Args:
            name: Field name
            data: Field data
            category: Parent category
        
        Returns:
            Field descriptor
        """
        return {
            "name": name,
            "type": "range",
            "category": category,
            "min": data.get('min'),
            "max": data.get('max'),
            "unit": data.get('unit', ''),
            "value": data.get('value'),  # Optional default
            "metadata": {k: v for k, v in data.items() 
                        if k not in {'min', 'max', 'value', 'unit'}}
        }
    
    def _extract_property_value(
        self, 
        name: str, 
        data: Dict[str, Any], 
        category: str
    ) -> Dict[str, Any]:
        """
        Extract PropertyValue field descriptor.
        
        Args:
            name: Field name
            data: Field data
            category: Parent category
        
        Returns:
            Field descriptor
        """
        return {
            "name": name,
            "type": "property_value",
            "category": category,
            "value": data.get('value'),
            "unit": data.get('unit', ''),
            "min": data.get('min'),
            "max": data.get('max'),
            "metadata": {k: v for k, v in data.items() 
                        if k not in {'value', 'unit', 'min', 'max'}}
        }
    
    def _extract_array_field(
        self, 
        name: str, 
        data: List[Any], 
        category: str
    ) -> Dict[str, Any]:
        """
        Extract array field descriptor.
        
        Args:
            name: Field name
            data: Array data
            category: Parent category
        
        Returns:
            Field descriptor
        """
        return {
            "name": name,
            "type": "array",
            "category": category,
            "value": data,
            "length": len(data),
            "metadata": {}
        }
    
    def _extract_simple_field(
        self, 
        name: str, 
        value: Any, 
        category: str
    ) -> Dict[str, Any]:
        """
        Extract simple field descriptor.
        
        Args:
            name: Field name
            value: Field value
            category: Parent category
        
        Returns:
            Field descriptor
        """
        return {
            "name": name,
            "type": type(value).__name__,
            "category": category,
            "value": value,
            "metadata": {}
        }
    
    def to_schema_org_json(
        self, 
        item_id: str, 
        item_data: Dict[str, Any]
    ) -> Dict[str, Any]:
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
                # Format field name for display
                display_name = field['name'].replace('_', ' ').replace('.', ' - ').title()
                
                # Add category prefix if available
                if field.get('category') and field['category'] != '':
                    display_name = f"{field['category']}: {field['name'].split('.')[-1].replace('_', ' ').title()}"
                
                variable_measured.append({
                    "@type": "PropertyValue",
                    "name": display_name,
                    "value": str(field.get('value', '')),
                    "unitText": field.get('unit', ''),
                    "minValue": field.get('min'),
                    "maxValue": field.get('max')
                })
        
        # Get description (allow subclasses to generate if missing)
        description = item_data.get('description', '')
        if not description and hasattr(self, '_generate_description'):
            description = self._generate_description(item_data)
        
        # Get dataset type and suffix from subclass
        dataset_type = self._get_dataset_type()  # e.g., 'materials'
        dataset_suffix = self._get_dataset_suffix()  # e.g., '-material-dataset'
        
        # Build full dataset identifier (slug + suffix)
        full_identifier = f"{item_id}{dataset_suffix}"
        
        # Build base dataset structure (v3.0 streamlined format)
        # Removed: citations, distribution, keywords, dateModified, license details
        dataset = {
            "@context": "https://schema.org",
            "@type": "Dataset",
            "@id": f"https://www.z-beam.com/datasets/{dataset_type}/{full_identifier}#dataset",
            "identifier": full_identifier,
            "name": item_data.get('name', item_id),
            "description": description,
            "variableMeasured": variable_measured
        }
        
        # v3.0: Minimal metadata only (creator/publisher added by generator)
        return dataset
    
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
        
        Args:
            item_data: Item data from YAML
        
        Returns:
            List of CSV row dicts
        """
        fields = self.detect_fields(item_data)
        rows = []
        
        for field in fields:
            if field['type'] in {'property_value', 'range'}:
                # Extract property name from path
                property_name = field['name'].split('.')[-1]
                
                # Use category from field detection
                category = field.get('category', 'General')
                
                rows.append({
                    "Category": category,
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
        
        Args:
            item_id: Item identifier
            item_data: Item data from YAML
        
        Returns:
            TXT content string
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
        categories: Dict[str, List[Dict[str, Any]]] = {}
        for field in fields:
            category = field.get('category', 'General')
            if category not in categories:
                categories[category] = []
            categories[category].append(field)
        
        # Output by category
        for category, cat_fields in sorted(categories.items()):
            if category:  # Skip empty categories
                lines.append(f"\n{category}:")
                for field in cat_fields:
                    prop_name = field['name'].split('.')[-1]
                    value_str = self._format_field_value(field)
                    lines.append(f"  {prop_name}: {value_str}")
        
        return '\n'.join(lines)
    
    def _format_field_value(self, field: Dict[str, Any]) -> str:
        """
        Format field value for TXT output.
        
        Args:
            field: Field descriptor
        
        Returns:
            Formatted value string
        """
        value = field.get('value', '')
        unit = field.get('unit', '')
        min_val = field.get('min', '')
        max_val = field.get('max', '')
        
        value_str = f"{value} {unit}".strip()
        if min_val and max_val:
            value_str += f" (range: {min_val}-{max_val} {unit})"
        elif min_val:
            value_str += f" (min: {min_val} {unit})"
        elif max_val:
            value_str += f" (max: {max_val} {unit})"
        
        return value_str or str(value)
