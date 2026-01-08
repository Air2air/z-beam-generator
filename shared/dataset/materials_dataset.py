"""
Materials Dataset with Dynamic Field Detection

Automatically detects all fields from Materials.yaml including:
- Material properties (nested by category)
- Machine settings (merged from Settings.yaml per ADR 005)
- Any new fields added to YAML

Policy Compliance:
- NO hardcoded field names
- Automatic detection of all YAML fields
- ADR 005: Materials + Settings unified dataset
"""

from pathlib import Path
from typing import Dict, Any, List
import sys

# Add project root to path
project_root = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(project_root))

from shared.dataset.base_dataset import BaseDataset
from domains.materials.data_loader_v2 import MaterialsDataLoader
from shared.exceptions import DataError
import logging

logger = logging.getLogger(__name__)


class MaterialsDataset(BaseDataset):
    """
    Materials dataset with machine settings merged (ADR 005).
    
    Automatically detects all fields from Materials.yaml including:
    - Material properties (nested by category)
    - Machine settings (merged from Settings.yaml)
    - Any new fields added to YAML
    
    Usage:
        dataset = MaterialsDataset()
        
        # Get single material
        material_data = dataset.get_material('aluminum')
        
        # Detect fields dynamically
        fields = dataset.detect_fields(material_data)
        
        # Generate Schema.org JSON
        json_data = dataset.to_schema_org_json('aluminum', material_data)
        
        # Generate CSV
        csv_rows = dataset.to_csv_rows(material_data)
        
        # Generate TXT
        txt_content = dataset.to_txt('aluminum', material_data)
    """
    
    def __init__(self, source_yaml_path: Path = None):
        """
        Initialize materials dataset.
        
        Args:
            source_yaml_path: Optional path to Materials.yaml
        """
        # Initialize loader BEFORE calling super().__init__
        self.loader = MaterialsDataLoader()
        # Call parent __init__ which will call _load_yaml()
        super().__init__(source_yaml_path)
    
    def _load_yaml(self) -> Dict[str, Any]:
        """
        Load Materials.yaml with machineSettings merged (for dataset generation).
        
        Returns:
            Parsed materials data with machineSettings from Settings.yaml
        """
        return self.loader.load_materials(include_machine_settings=True)
    
    def _get_dataset_type(self) -> str:
        """Return dataset type for materials."""
        return "materials"
    
    def _get_dataset_suffix(self) -> str:
        """Return dataset suffix for materials."""
        return "-material-dataset"
    
    def get_material(self, slug: str) -> Dict[str, Any]:
        """
        Get material data by slug.
        
        Args:
            slug: Material slug (with or without -laser-cleaning suffix)
        
        Returns:
            Material data dict
        
        Raises:
            KeyError: If material not found
        """
        materials = self.data.get('materials', {})
        
        # Try with suffix
        full_slug = slug if slug.endswith('-laser-cleaning') else f"{slug}-laser-cleaning"
        if full_slug in materials:
            return materials[full_slug]
        
        # Try without suffix
        if slug in materials:
            return materials[slug]
        
        raise KeyError(f"Material not found: {slug}")
    
    def get_all_materials(self) -> Dict[str, Dict[str, Any]]:
        """
        Get all materials.
        
        Returns:
            Dict of slug -> material data
        """
        return self.data.get('materials', {})
    
    def get_base_slug(self, full_slug: str) -> str:
        """
        Extract base slug from full slug.
        
        Args:
            full_slug: Full slug (e.g., 'aluminum-laser-cleaning')
        
        Returns:
            Base slug (e.g., 'aluminum')
        """
        return full_slug.replace('-laser-cleaning', '')
    
    def _generate_description(self, item_data: Dict[str, Any]) -> str:
        """
        Generate description from material data.
        
        Uses page_description field (replaces deprecated root-level description).
        
        Args:
            item_data: Material data
        
        Returns:
            Description string
        """
        # Use page_description field (current standard)
        if 'page_description' in item_data:
            return item_data['page_description']
        
        # Fallback: generate from material properties
        name = item_data.get('name', 'Material')
        category = item_data.get('category', '')
        subcategory = item_data.get('subcategory', '')
        
        parts = [f"{name} is a"]
        if subcategory:
            parts.append(f"{subcategory} {category}")
        elif category:
            parts.append(category)
        else:
            parts.append("material")
        
        parts.append("suitable for laser cleaning applications.")
        
        return ' '.join(parts)
    
    def _build_material_object(self, item_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Build nested material object per DATASET_SPECIFICATION.md.
        
        Creates structure with:
        - materialProperties: All material characteristics
        - machineSettings: Laser machine parameters (8 core parameters)
        
        Args:
            item_data: Material data
        
        Returns:
            Nested material object
        """
        return {
            'materialProperties': self._extract_material_properties(item_data),
            'machineSettings': self._extract_machine_settings(item_data)
        }
    
    def _extract_material_properties(self, item_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extract material properties from properties section.
        
        Args:
            item_data: Material data
        
        Returns:
            Dict of property_name -> {value, unit, etc.}
        """
        properties = {}
        properties_section = item_data.get('properties', {})
        
        for category_name, category_data in properties_section.items():
            if not isinstance(category_data, dict):
                continue
            
            # Extract all properties in this category
            for prop_name, prop_value in category_data.items():
                # Skip metadata fields
                if prop_name in {'label', 'description', 'title', '_section'}:
                    continue
                
                # Handle structured property values
                if isinstance(prop_value, dict) and 'value' in prop_value:
                    properties[prop_name] = prop_value
                elif isinstance(prop_value, (int, float, str)):
                    properties[prop_name] = {'value': prop_value}
        
        return properties
    
    def _extract_machine_settings(self, item_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extract machine settings (8 core parameters per DATASET_SPECIFICATION.md).
        
        Maps to specification names (handles both camelCase and snake_case):
        - power/powerRange -> laserPower
        - wavelength -> wavelength
        - spotSize/spot_size -> spotSize
        - repetitionRate/repetition_rate -> frequency
        - pulseWidth/pulse_width -> pulseWidth
        - scanSpeed/scan_speed -> scanSpeed
        - passCount/pass_count -> passCount
        - overlapRatio/overlap_ratio -> overlapRatio
        
        Args:
            item_data: Material data
        
        Returns:
            Dict of machine parameters with min/max/value/unit
        """
        machine_settings = item_data.get('machine_settings', {})
        if not machine_settings:
            logger.warning(f"No machine_settings found for {item_data.get('name', 'material')}")
            return {}
        
        # Map YAML keys to specification keys (try multiple variants)
        # Settings.yaml already uses correct camelCase names (laserPower, frequency, etc.)
        key_mapping = {
            'laserPower': ['laserPower', 'power', 'powerRange'],  # Try direct match first
            'wavelength': ['wavelength'],
            'spotSize': ['spotSize', 'spot_size'],
            'frequency': ['frequency', 'repetitionRate', 'repetition_rate'],  # Try direct match first
            'pulseWidth': ['pulseWidth', 'pulse_width'],
            'scanSpeed': ['scanSpeed', 'scan_speed'],
            'passCount': ['passCount', 'pass_count'],
            'overlapRatio': ['overlapRatio', 'overlap_ratio']
        }
        
        mapped_settings = {}
        for spec_key, yaml_keys in key_mapping.items():
            # Try each variant until we find one
            for yaml_key in yaml_keys:
                if yaml_key in machine_settings:
                    mapped_settings[spec_key] = machine_settings[yaml_key]
                    break
        
        return mapped_settings
    
    def to_schema_org_json(self, item_id: str, item_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate Schema.org Dataset JSON with nested material object.
        
        Per DATASET_SPECIFICATION.md:
        - Includes nested 'material' object with materialProperties + machineSettings
        - Includes machine parameters in variableMeasured
        - Enforces Tier 1: 8 machine parameters required
        
        Args:
            item_id: Material identifier
            item_data: Material data
        
        Returns:
            Schema.org Dataset structure
        
        Raises:
            ValueError: If Tier 1 requirements not met
        """
        # Build nested material object (per spec)
        material_object = self._build_material_object(item_data)
        
        # Validate Tier 1 requirements (8 machine parameters)
        self._validate_tier1_requirements(material_object)
        
        # Get base dataset structure from parent
        dataset = super().to_schema_org_json(item_id, item_data)
        
        # Add nested material object (per specification)
        dataset['material'] = material_object
        
        # Add machine parameters to variableMeasured
        machine_settings = material_object.get('machineSettings', {})
        for param_name, param_data in machine_settings.items():
            if isinstance(param_data, dict):
                dataset['variableMeasured'].append({
                    '@type': 'PropertyValue',
                    'name': f"Laser {param_name.replace('laser', '').replace('Power', 'Power')}",
                    'value': param_data.get('value'),
                    'minValue': param_data.get('min'),
                    'maxValue': param_data.get('max'),
                    'unitText': param_data.get('unit', '')
                })
        
        return dataset
    
    def _validate_tier1_requirements(self, material_object: Dict[str, Any]) -> None:
        """
        Validate Tier 1 requirements (per DATASET_SPECIFICATION.md lines 178-182).
        
        Tier 1: 8 machine parameters MUST have min/max values:
        - laserPower, wavelength, spotSize, frequency
        - pulseWidth, scanSpeed, passCount, overlapRatio
        
        Args:
            material_object: Nested material object
        
        Raises:
            DataError: If Tier 1 requirements not met
        """
        required_params = [
            'laserPower', 'wavelength', 'spotSize', 'frequency',
            'pulseWidth', 'scanSpeed', 'passCount', 'overlapRatio'
        ]
        
        settings = material_object.get('machineSettings', {})
        
        for param in required_params:
            if param not in settings:
                raise DataError(
                    f"Tier 1 violation: Missing required machine parameter '{param}'",
                    fix=f"Add '{param}' to machine_settings in Materials.yaml",
                    doc_link="docs/05-data/DATASET_SPECIFICATION.md",
                    context={"missing_parameter": param, "tier": 1}
                )
            
            param_data = settings[param]
            if not isinstance(param_data, dict):
                raise DataError(
                    f"Tier 1 violation: Parameter '{param}' must be a dict with min/max",
                    fix=f"Change '{param}' to dict format with min/max values",
                    doc_link="docs/05-data/DATASET_SPECIFICATION.md",
                    context={"parameter": param, "current_type": type(param_data).__name__}
                )
            
            if 'min' not in param_data or 'max' not in param_data:
                raise DataError(
                    f"Tier 1 violation: Parameter '{param}' missing min/max values",
                    fix=f"Add 'min' and 'max' fields to '{param}' in machine_settings",
                    doc_link="docs/05-data/DATASET_SPECIFICATION.md",
                    context={"parameter": param, "has_min": 'min' in param_data, "has_max": 'max' in param_data}
                )
    
    def to_csv_rows(self, item_data: Dict[str, Any], metadata: Dict[str, Any] = None) -> List[Dict[str, str]]:
        """
        Generate CSV rows with machine settings FIRST (per ADR 005).
        Now includes metadata as comment rows.
        
        Args:
            item_data: Material data
            metadata: Optional metadata dict (version, keywords, license, etc.)
        
        Returns:
            List of CSV row dicts with metadata comments and data
        """
        rows = []
        
        # Add metadata as comment rows (if provided)
        if metadata:
            rows.append({
                "Category": f"# Dataset Version: {metadata.get('version', '3.0')}",
                "Property": "",
                "Value": "",
                "Unit": "",
                "Min": "",
                "Max": ""
            })
            rows.append({
                "Category": f"# Dataset: {metadata.get('name', 'Unknown')}",
                "Property": "",
                "Value": "",
                "Unit": "",
                "Min": "",
                "Max": ""
            })
            rows.append({
                "Category": f"# License: {metadata.get('license', 'CC BY 4.0')} ({metadata.get('license_url', '')})",
                "Property": "",
                "Value": "",
                "Unit": "",
                "Min": "",
                "Max": ""
            })
            rows.append({
                "Category": f"# Keywords: {', '.join(metadata.get('keywords', [])[:5])}",
                "Property": "",
                "Value": "",
                "Unit": "",
                "Min": "",
                "Max": ""
            })
            rows.append({
                "Category": f"# Last Modified: {metadata.get('dateModified', '')}",
                "Property": "",
                "Value": "",
                "Unit": "",
                "Min": "",
                "Max": ""
            })
            rows.append({
                "Category": f"# Citations: {', '.join(metadata.get('citation', []))}",
                "Property": "",
                "Value": "",
                "Unit": "",
                "Min": "",
                "Max": ""
            })
            rows.append({
                "Category": "#",
                "Property": "",
                "Value": "",
                "Unit": "",
                "Min": "",
                "Max": ""
            })
        
        # Machine settings FIRST (ADR 005 requirement)
        machine_settings = item_data.get('machine_settings', {})
        if machine_settings:
            for param_name, param_value in machine_settings.items():
                if isinstance(param_value, dict):
                    rows.append({
                        "Category": "Machine Setting",
                        "Property": param_name.replace('_', ' ').title(),
                        "Value": str(param_value.get('value', '')),
                        "Unit": param_value.get('unit', ''),
                        "Min": str(param_value.get('min', '')),
                        "Max": str(param_value.get('max', ''))
                    })
        
        # Material properties (detected dynamically)
        fields = self.detect_fields(item_data)
        for field in fields:
            if field['type'] in {'property_value', 'range'}:
                # Skip machine_settings (already added above)
                if 'machine_settings' in field['name']:
                    continue
                
                property_name = field['name'].split('.')[-1]
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
    
    def to_txt(self, item_id: str, item_data: Dict[str, Any], metadata: Dict[str, Any] = None) -> str:
        """
        Generate TXT format with machine settings section FIRST (per ADR 005).
        Now includes metadata header block.
        
        Args:
            item_id: Material slug
            item_data: Material data
            metadata: Optional metadata dict (version, keywords, license, etc.)
        
        Returns:
            TXT content string
        """
        lines = [
            f"DATASET: {item_data.get('name', item_id)} Laser Cleaning Parameters",
            "=" * 80
        ]
        
        # Add metadata header (if provided)
        if metadata:
            lines.extend([
                "",
                "METADATA:",
                "-" * 80,
                f"Version: {metadata.get('version', '3.0')}",
                f"License: {metadata.get('license', 'CC BY 4.0')}",
                f"License URL: {metadata.get('license_url', '')}",
                f"Last Modified: {metadata.get('dateModified', '')}",
                f"Keywords: {', '.join(metadata.get('keywords', []))}",
                f"Citations: {', '.join(metadata.get('citation', []))}",
                ""
            ])
        
        lines.extend([
            "",
            "DESCRIPTION:",
            item_data.get('description', ''),
            "",
            "MACHINE SETTINGS:",
            "-" * 80
        ])
        
        # Machine settings FIRST (ADR 005 requirement)
        machine_settings = item_data.get('machine_settings', {})
        if machine_settings:
            for param_name, param_value in machine_settings.items():
                if isinstance(param_value, dict):
                    value_str = self._format_field_value({
                        'value': param_value.get('value'),
                        'unit': param_value.get('unit', ''),
                        'min': param_value.get('min'),
                        'max': param_value.get('max')
                    })
                    lines.append(f"  {param_name}: {value_str}")
        else:
            lines.append("  (No machine settings available)")
        
        lines.extend(["", "MATERIAL PROPERTIES:", "-" * 80])
        
        # Material properties (detected dynamically, grouped by category)
        fields = self.detect_fields(item_data)
        categories: Dict[str, List[Dict[str, Any]]] = {}
        
        for field in fields:
            # Skip machine_settings (already added above)
            if 'machine_settings' in field['name']:
                continue
            
            category = field.get('category', 'General')
            if category not in categories:
                categories[category] = []
            categories[category].append(field)
        
        # Output by category
        for category, cat_fields in sorted(categories.items()):
            if category and cat_fields:
                lines.append(f"\n{category}:")
                for field in cat_fields:
                    prop_name = field['name'].split('.')[-1]
                    value_str = self._format_field_value(field)
                    lines.append(f"  {prop_name}: {value_str}")
        
        return '\n'.join(lines)
