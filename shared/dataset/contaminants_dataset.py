"""
Contaminants Dataset with Dynamic Field Detection

Automatically detects all fields from Contaminants.yaml including:
- Contaminant pattern data
- Related compounds (merged from Compounds.yaml per ADR 005)
- Any new fields added to YAML

Policy Compliance:
- NO hardcoded field names
- Automatic detection of all YAML fields
- ADR 005: Contaminants + Compounds merged dataset
"""

from pathlib import Path
from typing import Dict, Any, List
import sys

# Add project root to path
project_root = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(project_root))

from shared.dataset.base_dataset import BaseDataset
from domains.contaminants.data_loader_v2 import ContaminantsDataLoader
from domains.compounds.data_loader_v2 import CompoundsDataLoader


class ContaminantsDataset(BaseDataset):
    """
    Contaminants dataset with compounds merged (ADR 005).
    
    Automatically detects all fields from Contaminants.yaml including:
    - Contaminant pattern data
    - Related compounds (merged from Compounds.yaml)
    - Any new fields added to YAML
    
    Usage:
        dataset = ContaminantsDataset()
        
        # Get single contaminant
        pattern_data = dataset.get_contaminant('rust')
        
        # Merge compound data (ADR 005)
        enriched_data = dataset.merge_compounds(pattern_data)
        
        # Detect fields dynamically
        fields = dataset.detect_fields(enriched_data)
        
        # Generate Schema.org JSON
        json_data = dataset.to_schema_org_json('rust', enriched_data)
        
        # Generate CSV
        csv_rows = dataset.to_csv_rows(enriched_data)
        
        # Generate TXT
        txt_content = dataset.to_txt('rust', enriched_data)
    """
    
    def __init__(self, source_yaml_path: Path = None):
        """
        Initialize contaminants dataset.
        
        Args:
            source_yaml_path: Optional path to Contaminants.yaml
        """
        # Initialize loaders BEFORE calling super().__init__
        self.contaminants_loader = ContaminantsDataLoader()
        self.compounds_loader = CompoundsDataLoader()
        
        # Load compounds data for merging
        compounds_data = self.compounds_loader.load_compounds()
        self.compounds = compounds_data.get('compounds', {})
        
        # Call parent __init__ which will call _load_yaml()
        super().__init__(source_yaml_path)
    
    def _load_yaml(self) -> Dict[str, Any]:
        """
        Load Contaminants.yaml.
        
        Returns:
            Parsed contaminants data
        """
        return self.contaminants_loader.load_patterns()
    
    def _get_dataset_type(self) -> str:
        """Return dataset type for contaminants."""
        return "contaminants"
    
    def _get_dataset_suffix(self) -> str:
        """Return dataset suffix for contaminants."""
        return "-contaminant-dataset"
    
    def get_contaminant(self, pattern_id: str) -> Dict[str, Any]:
        """
        Get contaminant pattern data by ID.
        
        Args:
            pattern_id: Contaminant pattern ID
        
        Returns:
            Contaminant data dict
        
        Raises:
            KeyError: If contaminant not found
        """
        if pattern_id not in self.data:
            raise KeyError(f"Contaminant not found: {pattern_id}")
        
        return self.data[pattern_id]
    
    def get_all_contaminants(self) -> Dict[str, Dict[str, Any]]:
        """
        Get all contaminants.
        
        Returns:
            Dict of pattern_id -> contaminant data
        """
        return self.data
    
    def _extract_laser_properties_fields(self, item_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Extract fields from laser_properties relationship.
        
        Laser properties contain rich technical data including:
        - optical_properties: absorption, reflectivity, refractive_index
        - thermal_properties: melting_point, ablation_threshold, etc.
        - laser_parameters: fluence, pulse_duration, scan_speed ranges
        - removal_characteristics: efficiency, process_speed, damage_risk
        
        Args:
            item_data: Contaminant data
        
        Returns:
            List of field descriptors compatible with detect_fields format
        """
        fields = []
        
        # Get laser_properties from relationships
        relationships = item_data.get('relationships', {})
        laser_props = relationships.get('laser_properties', {})
        laser_items = laser_props.get('items', [])
        
        if not laser_items:
            return fields
        
        # Use first laser_properties item
        laser_data = laser_items[0]
        
        # Extract optical properties
        optical = laser_data.get('optical_properties', {})
        for prop_name, prop_value in optical.items():
            if isinstance(prop_value, dict):
                # Nested dict (e.g., absorption_coefficient with wavelengths)
                for sub_key, sub_value in prop_value.items():
                    fields.append({
                        "name": f"optical.{prop_name}.{sub_key}",
                        "type": "property_value",
                        "category": "Optical Properties",
                        "value": sub_value,
                        "unit": self._get_unit_for_property(prop_name),
                        "min": None,
                        "max": None,
                        "metadata": {}
                    })
            else:
                # Simple value
                fields.append({
                    "name": f"optical.{prop_name}",
                    "type": "property_value",
                    "category": "Optical Properties",
                    "value": prop_value,
                    "unit": self._get_unit_for_property(prop_name),
                    "min": None,
                    "max": None,
                    "metadata": {}
                })
        
        # Extract thermal properties
        thermal = laser_data.get('thermal_properties', {})
        for prop_name, prop_value in thermal.items():
            if isinstance(prop_value, dict):
                # Nested dict with ranges
                for sub_key, sub_value in prop_value.items():
                    fields.append({
                        "name": f"thermal.{prop_name}.{sub_key}",
                        "type": "property_value",
                        "category": "Thermal Properties",
                        "value": sub_value,
                        "unit": self._get_unit_for_property(prop_name),
                        "min": None,
                        "max": None,
                        "metadata": {}
                    })
            else:
                fields.append({
                    "name": f"thermal.{prop_name}",
                    "type": "property_value",
                    "category": "Thermal Properties",
                    "value": prop_value,
                    "unit": self._get_unit_for_property(prop_name),
                    "min": None,
                    "max": None,
                    "metadata": {}
                })
        
        # Extract laser parameters (often have min/max/recommended)
        laser_params = laser_data.get('laser_parameters', {})
        for param_name, param_value in laser_params.items():
            if isinstance(param_value, dict) and ('min' in param_value or 'max' in param_value):
                # Range parameter
                fields.append({
                    "name": f"laser_parameters.{param_name}",
                    "type": "range",
                    "category": "Laser Parameters",
                    "value": param_value.get('recommended'),
                    "min": param_value.get('min'),
                    "max": param_value.get('max'),
                    "unit": self._get_unit_for_property(param_name),
                    "metadata": {}
                })
            elif isinstance(param_value, list):
                # List value (e.g., wavelength_preference)
                fields.append({
                    "name": f"laser_parameters.{param_name}",
                    "type": "property_value",
                    "category": "Laser Parameters",
                    "value": ', '.join(str(v) for v in param_value),
                    "unit": self._get_unit_for_property(param_name),
                    "min": None,
                    "max": None,
                    "metadata": {}
                })
            else:
                # Simple value
                fields.append({
                    "name": f"laser_parameters.{param_name}",
                    "type": "property_value",
                    "category": "Laser Parameters",
                    "value": param_value,
                    "unit": self._get_unit_for_property(param_name),
                    "min": None,
                    "max": None,
                    "metadata": {}
                })
        
        # Extract removal characteristics
        removal = laser_data.get('removal_characteristics', {})
        for prop_name, prop_value in removal.items():
            if isinstance(prop_value, dict):
                # Nested dict with sub-properties
                for sub_key, sub_value in prop_value.items():
                    # Skip complex nested objects
                    if not isinstance(sub_value, (list, dict)):
                        fields.append({
                            "name": f"removal.{prop_name}.{sub_key}",
                            "type": "property_value",
                            "category": "Removal Characteristics",
                            "value": sub_value,
                            "unit": self._get_unit_for_property(sub_key),
                            "min": None,
                            "max": None,
                            "metadata": {}
                        })
            elif not isinstance(prop_value, (list, dict)):
                # Simple value (skip complex arrays/objects)
                fields.append({
                    "name": f"removal.{prop_name}",
                    "type": "property_value",
                    "category": "Removal Characteristics",
                    "value": prop_value,
                    "unit": self._get_unit_for_property(prop_name),
                    "min": None,
                    "max": None,
                    "metadata": {}
                })
        
        return fields
    
    def _get_unit_for_property(self, prop_name: str) -> str:
        """
        Get appropriate unit for a property name.
        
        Args:
            prop_name: Property name
        
        Returns:
            Unit string
        """
        unit_map = {
            'absorption_coefficient': 'cm⁻¹',
            'reflectivity': 'ratio',
            'refractive_index': 'dimensionless',
            'transmission_depth': 'μm',
            'melting_point': '°C',
            'decomposition_temperature': '°C',
            'vaporization_temperature': '°C',
            'ablation_threshold': 'J/cm²',
            'heat_affected_zone_depth': 'μm',
            'specific_heat': 'J/(kg·K)',
            'thermal_conductivity': 'W/(m·K)',
            'thermal_diffusivity': 'mm²/s',
            'fluence_range': 'J/cm²',
            'pulse_duration_range': 'ns',
            'repetition_rate_khz': 'kHz',
            'scan_speed_mm_s': 'mm/s',
            'spot_size_mm': 'mm',
            'overlap_percentage': '%',
            'wavelength_preference': 'nm',
            'removal_efficiency': 'ratio',
            'single_pass': 'ratio',
            'optimal_passes': 'passes',
            'area_coverage_rate_cm2_min': 'cm²/min',
            'typical_scan_speed_mm_s': 'mm/s'
        }
        
        # Find matching unit
        for key, unit in unit_map.items():
            if key in prop_name:
                return unit
        
        return ''
    
    def _generate_description(self, item_data: Dict[str, Any]) -> str:
        """
        Generate description from contaminant data.
        
        Uses composition, category, and visual characteristics to create
        a meaningful description when none exists.
        
        Args:
            item_data: Contaminant data
        
        Returns:
            Generated description string
        """
        # Return existing description if present
        if item_data.get('description'):
            return item_data['description']
        
        # Build description from available data
        parts = []
        
        # Add name and composition
        name = item_data.get('name', 'Contamination')
        composition = item_data.get('composition', [])
        if composition:
            comp_str = ', '.join(composition) if isinstance(composition, list) else str(composition)
            parts.append(f"{name} ({comp_str}) is a common contamination pattern in laser cleaning.")
        else:
            parts.append(f"{name} is a common contamination pattern in laser cleaning.")
        
        # Add category info
        category = item_data.get('category', '')
        subcategory = item_data.get('subcategory', '')
        if category:
            cat_str = f"{category}/{subcategory}" if subcategory else category
            parts.append(f"This {cat_str} contamination affects surface integrity and requires specialized removal techniques.")
        
        # Add material compatibility info
        valid_materials = item_data.get('valid_materials', [])
        if valid_materials and len(valid_materials) > 0:
            count = len(valid_materials)
            parts.append(f"Commonly found on {count} different material types including metals, composites, and specialized substrates.")
        
        return ' '.join(parts)
    
    def detect_fields(
        self, 
        data: Dict[str, Any], 
        prefix: str = "",
        parent_category: str = ""
    ) -> List[Dict[str, Any]]:
        """
        Detect all data fields including laser_properties from relationships.
        
        Overrides base class to add extraction of laser_properties which contains
        rich technical data not in the standard YAML structure.
        
        Args:
            data: Contaminant data
            prefix: Path prefix for nested fields
            parent_category: Category label from parent
        
        Returns:
            List of field descriptors
        """
        # Get base fields from standard YAML structure
        fields = super().detect_fields(data, prefix, parent_category)
        
        # Add laser properties fields from relationships
        laser_fields = self._extract_laser_properties_fields(data)
        fields.extend(laser_fields)
        
        return fields
    
    def _generate_citations(self, item_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Generate citations from relationships.
        
        Creates citations for:
        - affects_materials: Materials this contaminant appears on
        - produces_compounds: Hazardous compounds generated
        - regulatory_standards: Safety standards
        
        Args:
            item_data: Contaminant data
        
        Returns:
            List of Schema.org CreativeWork citations
        """
        citations = []
        relationships = item_data.get('relationships', {})
        
        # Add material citations (limit to 5 most common)
        # Note: affects_materials is at root level of relationships
        affects_materials = relationships.get('affects_materials', {})
        material_items = affects_materials.get('items', [])
        
        # Sort by frequency if available, take top 5
        sorted_materials = sorted(
            material_items,
            key=lambda x: {'very_common': 3, 'common': 2, 'uncommon': 1}.get(
                x.get('frequency', 'uncommon') if isinstance(x, dict) else 'uncommon',
                1
            ),
            reverse=True
        )
        
        for item in sorted_materials[:5]:  # Top 5 materials
            if isinstance(item, dict) and 'id' in item:
                material_id = item['id']
                # Convert ID to name (remove -laser-cleaning suffix)
                name = material_id.replace('-laser-cleaning', '').replace('-', ' ').title()
                citations.append({
                    "@type": "CreativeWork",
                    "name": f"{name} Laser Cleaning",
                    "url": f"https://www.z-beam.com/materials/{material_id}"
                })
        
        # Add compound citations if produces_compounds exists
        produces_compounds = relationships.get('produces_compounds', {})
        compound_items = produces_compounds.get('items', [])
        for item in compound_items[:3]:  # Top 3 compounds
            if isinstance(item, dict) and 'id' in item:
                compound_id = item['id']
                name = compound_id.replace('-compound', '').replace('-', ' ').title()
                citations.append({
                    "@type": "CreativeWork",
                    "name": f"{name} Hazardous Compound",
                    "url": f"https://www.z-beam.com/compounds/{compound_id}"
                })
        
        # Add regulatory standards (also at root level)
        regulatory = relationships.get('regulatory_standards', {})
        regulatory_items = regulatory.get('items', [])
        for item in regulatory_items[:2]:  # Top 2 standards
            if isinstance(item, dict):
                standard_id = item.get('id', '')
                standard_type = item.get('type', 'regulatory_standards')
                if standard_id:
                    name = standard_id.replace('-', ' ').upper()
                    citations.append({
                        "@type": "CreativeWork",
                        "name": name,
                        "url": f"https://www.z-beam.com/safety/{standard_type}/{standard_id}"
                    })
        
        return citations
    
    def merge_compounds(self, contaminant_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Merge compound data into contaminant (ADR 005).
        
        Uses reverse relationship lookup: searches Compounds.yaml for compounds
        that are produced_from this contaminant.
        
        Args:
            contaminant_data: Contaminant pattern data
        
        Returns:
            Enriched contaminant data with compounds merged
        """
        enriched = contaminant_data.copy()
        
        # Extract compounds using the same method as JSON generation
        # This uses reverse relationship lookup from Compounds.yaml
        compounds_array = self._extract_compounds_from_relationships(contaminant_data)
        
        # Add compounds array to contaminant data
        if compounds_array:
            enriched['compounds'] = compounds_array
        
        return enriched
    
    def to_csv_rows(self, item_data: Dict[str, Any], metadata: Dict[str, Any] = None) -> List[Dict[str, str]]:
        """
        Generate CSV rows with compounds section (per ADR 005).
        Now includes metadata as comment rows.
        
        Args:
            item_data: Contaminant data (with compounds merged)
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
        
        # Contaminant properties (detected dynamically)
        fields = self.detect_fields(item_data)
        for field in fields:
            if field['type'] in {'property_value', 'range'}:
                # Skip compounds (handled separately below)
                if 'compounds' in field['name']:
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
        
        # Compounds section (ADR 005 requirement)
        compounds = item_data.get('compounds', [])
        if compounds:
            for compound in compounds:
                if isinstance(compound, dict):
                    # Add compound identification
                    rows.append({
                        "Category": "Compound",
                        "Property": "Name",
                        "Value": compound.get('name', ''),
                        "Unit": "",
                        "Min": "",
                        "Max": ""
                    })
                    if 'formula' in compound:
                        rows.append({
                            "Category": "Compound",
                            "Property": "Formula",
                            "Value": compound.get('formula', ''),
                            "Unit": "",
                            "Min": "",
                            "Max": ""
                        })
                    if 'cas_number' in compound:
                        rows.append({
                            "Category": "Compound",
                            "Property": "CAS Number",
                            "Value": compound.get('cas_number', ''),
                            "Unit": "",
                            "Min": "",
                            "Max": ""
                        })
        
        return rows
    
    def to_txt(self, item_id: str, item_data: Dict[str, Any], metadata: Dict[str, Any] = None) -> str:
        """
        Generate TXT format with compounds section (per ADR 005).
        Now includes metadata header block.
        
        Args:
            item_id: Contaminant pattern ID
            item_data: Contaminant data (with compounds merged)
            metadata: Optional metadata dict (version, keywords, license, etc.)
        
        Returns:
            TXT content string
        """
        lines = [
            f"DATASET: {item_data.get('name', item_id)} Contamination Pattern",
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
            "CONTAMINANT PROPERTIES:",
            "-" * 80
        ])
        
        # Contaminant properties (detected dynamically, grouped by category)
        fields = self.detect_fields(item_data)
        categories: Dict[str, List[Dict[str, Any]]] = {}
        
        for field in fields:
            # Skip compounds (handled separately below)
            if 'compounds' in field['name']:
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
        
        # Compounds section (ADR 005 requirement)
        compounds = item_data.get('compounds', [])
        if compounds:
            lines.extend(["", "RELATED COMPOUNDS:", "-" * 80])
            for idx, compound in enumerate(compounds, 1):
                if isinstance(compound, dict):
                    lines.append(f"\nCompound {idx}: {compound.get('name', 'Unknown')}")
                    if 'formula' in compound:
                        lines.append(f"  Formula: {compound['formula']}")
                    if 'cas_number' in compound:
                        lines.append(f"  CAS Number: {compound['cas_number']}")
                    if 'composition' in compound:
                        lines.append(f"  Composition: {compound['composition']}")
                    if 'safety' in compound:
                        lines.append(f"  Safety: {compound['safety']}")
        
        return '\n'.join(lines)
    
    def _build_contaminant_object(self, item_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Build nested contaminant object per DATASET_SPECIFICATION.md.
        
        Structure:
        {
            "properties": {...contaminant properties...},
            "compounds": [{...compound objects...}],
            "removalTechniques": {...laser parameters...}
        }
        
        Args:
            item_data: Contaminant data with relationships
        
        Returns:
            Nested contaminant object
        """
        contaminant_obj = {}
        
        # Extract contaminant properties
        properties = self._extract_contaminant_properties(item_data)
        if properties:
            contaminant_obj['properties'] = properties
        
        # Extract compounds from relationships
        compounds = self._extract_compounds_from_relationships(item_data)
        if compounds:
            contaminant_obj['compounds'] = compounds
        
        # Extract removal techniques (laser parameters)
        removal_techniques = self._extract_removal_techniques(item_data)
        if removal_techniques:
            contaminant_obj['removalTechniques'] = removal_techniques
        
        return contaminant_obj
    
    def _extract_contaminant_properties(self, item_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extract contaminant properties (composition, absorption, hazard level, etc.).
        
        Args:
            item_data: Contaminant data
        
        Returns:
            Dict of contaminant properties
        """
        properties = {}
        
        # Extract composition (top-level field)
        if 'composition' in item_data:
            properties['composition'] = item_data['composition']
        
        # Extract from visual_characteristics relationship
        relationships = item_data.get('relationships', {})
        visual_chars = relationships.get('visual_characteristics', {})
        visual_items = visual_chars.get('items', [])
        
        if visual_items:
            visual_data = visual_items[0]
            
            # Extract visual properties
            if 'appearance' in visual_data:
                appearance = visual_data['appearance']
                if 'color' in appearance:
                    properties['color'] = appearance['color']
                if 'texture' in appearance:
                    properties['texture'] = appearance['texture']
                if 'thickness' in appearance:
                    properties['thickness'] = appearance['thickness']
        
        # Extract from optical_properties in laser_properties
        laser_props = relationships.get('laser_properties', {})
        laser_items = laser_props.get('items', [])
        
        if laser_items:
            laser_data = laser_items[0]
            
            # Extract optical properties
            optical = laser_data.get('optical_properties', {})
            if 'absorption_coefficient' in optical:
                properties['absorptionRate'] = optical['absorption_coefficient']
            if 'reflectivity' in optical:
                properties['reflectivity'] = optical['reflectivity']
        
        # Extract from safety relationship
        safety_rel = relationships.get('safety', {})
        safety_items = safety_rel.get('items', [])
        
        if safety_items:
            safety_data = safety_items[0]
            
            if 'hazard_assessment' in safety_data:
                hazard = safety_data['hazard_assessment']
                if 'overall_risk_level' in hazard:
                    properties['hazardLevel'] = hazard['overall_risk_level']
        
        # Extract removal difficulty from technical relationship
        technical_rel = relationships.get('technical', {})
        technical_items = technical_rel.get('items', [])
        
        if technical_items:
            technical_data = technical_items[0]
            
            if 'removal_difficulty' in technical_data:
                properties['removalDifficulty'] = technical_data['removal_difficulty']
        
        return properties
    
    def _extract_compounds_from_relationships(self, item_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Extract compounds from produced_from_contaminants relationships in Compounds.yaml.
        
        Reverses the relationship: Compounds → contaminant becomes Contaminant → compounds
        
        Args:
            item_data: Contaminant data
        
        Returns:
            List of compound objects
        """
        compounds_array = []
        contaminant_id = item_data.get('id', '')
        
        if not contaminant_id:
            return compounds_array
        
        # Search all compounds for those that reference this contaminant
        for compound_id, compound_data in self.compounds.items():
            relationships = compound_data.get('relationships', {})
            produced_from = relationships.get('produced_from_contaminants', {})
            items = produced_from.get('items', [])
            
            # Check if this compound is produced from current contaminant
            for item in items:
                if isinstance(item, dict) and item.get('id') == contaminant_id:
                    # Add compound to array
                    compound_obj = {
                        'name': compound_data.get('name', ''),
                        'formula': compound_data.get('chemical_formula', ''),
                        'casNumber': compound_data.get('cas_number', ''),
                        'hazardLevel': compound_data.get('hazard_class', ''),
                        'healthEffects': compound_data.get('health_effects', '')[:200] + '...' if compound_data.get('health_effects') else ''
                    }
                    
                    # Add frequency and severity from relationship
                    compound_obj['frequency'] = item.get('frequency', 'unknown')
                    compound_obj['severity'] = item.get('severity', 'unknown')
                    
                    compounds_array.append(compound_obj)
                    break  # Found match, move to next compound
        
        return compounds_array
    
    def _extract_removal_techniques(self, item_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extract laser removal parameters from relationships.
        
        Args:
            item_data: Contaminant data
        
        Returns:
            Dict of removal technique parameters
        """
        removal_techniques = {}
        
        # Get laser_properties from relationships
        relationships = item_data.get('relationships', {})
        laser_props = relationships.get('laser_properties', {})
        laser_items = laser_props.get('items', [])
        
        if not laser_items:
            return removal_techniques
        
        # Use first laser_properties item
        laser_data = laser_items[0]
        
        # Extract laser parameters with actual field names
        laser_params = laser_data.get('laser_parameters', {})
        
        # Map actual YAML fields to specification fields
        field_mapping = {
            'fluence_range': 'laserPower',
            'wavelength_preference': 'wavelength',
            'pulse_duration_range': 'pulseWidth',
            'scan_speed_mm_s': 'scanSpeed',
            'spot_size_mm': 'spotSize',
            'repetition_rate_khz': 'frequency',
            'overlap_percentage': 'overlapRatio'
        }
        
        for yaml_key, spec_key in field_mapping.items():
            if yaml_key in laser_params:
                value = laser_params[yaml_key]
                if isinstance(value, dict):
                    # Already has min/max structure
                    removal_techniques[spec_key] = value
                else:
                    # Convert to value dict
                    removal_techniques[spec_key] = {'value': value}
        
        # Extract removal characteristics
        removal_chars = laser_data.get('removal_characteristics', {})
        
        # Extract efficiency
        if 'removal_efficiency' in removal_chars:
            eff = removal_chars['removal_efficiency']
            if isinstance(eff, dict):
                removal_techniques['removalRate'] = eff
            else:
                removal_techniques['removalRate'] = {'value': eff, 'unit': '%'}
        
        # Extract pass count (from context or default)
        if 'pass_count' in laser_params:
            passes = laser_params['pass_count']
            removal_techniques['passCount'] = passes if isinstance(passes, dict) else {'value': passes}
        
        return removal_techniques
    
    def _to_camel_case(self, snake_str: str) -> str:
        """
        Convert snake_case to camelCase.
        
        Args:
            snake_str: Snake case string
        
        Returns:
            Camel case string
        """
        components = snake_str.split('_')
        return components[0] + ''.join(x.title() for x in components[1:])
    
    def to_schema_org_json(self, item_id: str, item_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate Schema.org Dataset JSON with nested contaminant object.
        
        Per DATASET_SPECIFICATION.md:
        - Includes nested 'contaminant' object with properties + compounds + removalTechniques
        - Includes compound information in variableMeasured
        
        Args:
            item_id: Contaminant identifier
            item_data: Contaminant data
        
        Returns:
            Schema.org Dataset structure
        """
        # Build nested contaminant object (per spec)
        contaminant_object = self._build_contaminant_object(item_data)
        
        # Get base dataset structure from parent
        dataset = super().to_schema_org_json(item_id, item_data)
        
        # Add nested contaminant object (per specification)
        dataset['contaminant'] = contaminant_object
        
        # Add compound information to variableMeasured
        compounds = contaminant_object.get('compounds', [])
        for compound in compounds:
            if isinstance(compound, dict) and 'name' in compound:
                dataset['variableMeasured'].append({
                    '@type': 'PropertyValue',
                    'name': f"Compound: {compound['name']}",
                    'value': compound.get('formula', ''),
                    'description': compound.get('healthEffects', '')
                })
        
        # Add removal technique parameters to variableMeasured
        removal_techniques = contaminant_object.get('removalTechniques', {})
        for param_name, param_data in removal_techniques.items():
            if isinstance(param_data, dict):
                dataset['variableMeasured'].append({
                    '@type': 'PropertyValue',
                    'name': f"Removal {param_name}",
                    'value': param_data.get('value'),
                    'minValue': param_data.get('min'),
                    'maxValue': param_data.get('max'),
                    'unitText': param_data.get('unit', '')
                })
        
        return dataset
