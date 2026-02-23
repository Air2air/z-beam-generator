"""
Property Selector - Identifies Distinctive Properties for Materials

Selects properties that best distinguish each material from others in its category,
ensuring section descriptions have unique factual grounding.

Algorithm: Compare property values against category statistics to identify outliers.
"""

import logging
from typing import Dict, List, Any, Optional, Tuple
from statistics import mean, stdev

logger = logging.getLogger(__name__)


class PropertySelector:
    """
    Selects distinctive properties for materials to drive varied section descriptions.
    
    Strategy:
    1. Load all materials in same category
    2. Calculate statistical distributions (mean, stdev) for each property
    3. Compute z-score for target material's properties
    4. Return top N properties with highest |z-score| (most distinctive)
    
    This ensures each material's description focuses on what makes IT unique.
    """
    
    def __init__(self, data_loader=None):
        """
        Initialize property selector.
        
        Args:
            data_loader: MaterialsDataLoader instance (optional, will create if needed)
        """
        self.data_loader = data_loader
        if not self.data_loader:
            from shared.data.loader_factory import create_data_loader
            self.data_loader = create_data_loader('materials')
        
        self._category_stats_cache = {}  # Cache category statistics
    
    def select_distinctive_properties(
        self,
        material_name: str,
        section_type: str,
        count: int = 3
    ) -> List[Dict[str, Any]]:
        """
        Select most distinctive properties for this material and section type.
        
        Args:
            material_name: Material identifier (e.g., 'aluminum-laser-cleaning')
            section_type: Section type determines property pool:
                - 'materialCharacteristics': Physical/mechanical properties
                - 'laserMaterialInteraction': Optical/thermal properties
                - 'other': All properties
            count: Number of properties to select (default: 3)
            
        Returns:
            List of property dicts with {name, value, unit, distinctiveness_score}
            Sorted by distinctiveness (most distinctive first)
        """
        # Load material data
        materials_data = self.data_loader.load_materials()
        
        if material_name not in materials_data:
            logger.warning(f"Material '{material_name}' not found")
            return []
        
        material = materials_data[material_name]
        if 'category' not in material:
            raise KeyError(f"Material '{material_name}' missing required key: 'category'")
        category = material['category']
        
        # Get property pool for this section type
        property_pool = self._get_property_pool_for_section(section_type)
        
        # Calculate category statistics (cached)
        category_stats = self._get_category_statistics(category, property_pool)
        
        # Extract material properties
        material_properties = self._extract_properties(material, property_pool)
        
        if not material_properties:
            logger.warning(f"No properties found for {material_name}")
            return []
        
        # Calculate distinctiveness scores
        scored_properties = []
        for prop_name, prop_data in material_properties.items():
            if prop_name not in category_stats:
                continue  # Skip if no category baseline
            
            if 'value' not in prop_data:
                raise KeyError(f"Property '{prop_name}' missing required key: 'value'")
            value = prop_data['value']
            if value is None:
                continue
            
            try:
                value_numeric = float(value)
            except (ValueError, TypeError):
                continue  # Skip non-numeric properties
            
            stats = category_stats[prop_name]
            
            # Calculate z-score (measure of how unusual this value is)
            z_score = 0.0
            if stats['stdev'] > 0:
                z_score = abs((value_numeric - stats['mean']) / stats['stdev'])
            
            scored_properties.append({
                'name': prop_name,
                'value': value,
                'unit': prop_data['unit'] if 'unit' in prop_data else '',
                'distinctiveness_score': z_score,
                'category_mean': stats['mean'],
                'category_range': f"{stats['min']:.2f}-{stats['max']:.2f}"
            })
        
        # Sort by distinctiveness (highest z-score first)
        scored_properties.sort(key=lambda p: p['distinctiveness_score'], reverse=True)
        
        # Return top N
        selected = scored_properties[:count]
        
        logger.info(f"Selected {len(selected)} distinctive properties for {material_name}.{section_type}")
        for prop in selected:
            logger.info(f"  - {prop['name']}: {prop['value']} {prop['unit']} (z-score: {prop['distinctiveness_score']:.2f})")
        
        return selected
    
    def _get_property_pool_for_section(self, section_type: str) -> List[str]:
        """
        Get property names relevant to this section type.
        
        Args:
            section_type: Section type identifier
            
        Returns:
            List of property names to consider
        """
        if section_type == 'materialCharacteristics_description':
            # Physical and mechanical properties
            return [
                'density', 'tensile_strength', 'hardness', 'yield_strength',
                'surface_roughness', 'thermal_expansion', 'porosity',
                'elastic_modulus', 'compressive_strength'
            ]
        elif section_type == 'laserMaterialInteraction_description':
            # Optical and thermal properties
            return [
                'thermal_conductivity', 'melting_point', 'boiling_point',
                'specific_heat', 'thermal_diffusivity', 'emissivity',
                'absorption_1064nm', 'reflectivity', 'ablation_threshold'
            ]
        else:
            # All properties
            return [
                'density', 'tensile_strength', 'hardness', 'thermal_conductivity',
                'melting_point', 'boiling_point', 'surface_roughness',
                'thermal_expansion', 'specific_heat', 'absorption_1064nm'
            ]
    
    def _extract_properties(self, material: Dict, property_names: List[str]) -> Dict[str, Dict]:
        """
        Extract property values from material data structure.
        
        Args:
            material: Material data dict
            property_names: List of property names to extract
            
        Returns:
            Dict mapping property name to {value, unit}
        """
        properties = {}
        
        # Navigate nested structure: properties.materialCharacteristics.{prop}
        if 'properties' not in material:
            raise KeyError("Material missing required key: 'properties'")
        material_props = material['properties']
        if not isinstance(material_props, dict):
            raise TypeError("Material key 'properties' must be a dictionary")
        if 'materialCharacteristics' not in material_props:
            raise KeyError("Material properties missing required key: 'materialCharacteristics'")
        material_chars = material_props['materialCharacteristics']
        if not isinstance(material_chars, dict):
            raise TypeError("Material properties.materialCharacteristics must be a dictionary")
        
        for prop_name in property_names:
            if prop_name in material_chars:
                prop_data = material_chars[prop_name]
                if isinstance(prop_data, dict):
                    if 'value' not in prop_data:
                        raise KeyError(f"Property '{prop_name}' missing required key: 'value'")
                    properties[prop_name] = {
                        'value': prop_data['value'],
                        'unit': prop_data['unit'] if 'unit' in prop_data else ''
                    }
        
        return properties
    
    def _get_category_statistics(self, category: str, property_names: List[str]) -> Dict[str, Dict]:
        """
        Calculate statistical distribution for properties across all materials in category.
        
        Args:
            category: Material category (e.g., 'metals', 'ceramics')
            property_names: List of property names to analyze
            
        Returns:
            Dict mapping property name to {mean, stdev, min, max, count}
        """
        cache_key = f"{category}:{','.join(sorted(property_names))}"
        
        if cache_key in self._category_stats_cache:
            return self._category_stats_cache[cache_key]
        
        # Load all materials
        materials_data = self.data_loader.load_materials()
        
        # Filter to category
        category_materials = {
            name: data for name, data in materials_data.items()
            if isinstance(data, dict) and 'category' in data and data['category'] == category
        }
        
        if not category_materials:
            logger.warning(f"No materials found for category '{category}'")
            return {}
        
        # Collect property values across category
        property_values = {prop_name: [] for prop_name in property_names}
        
        for material_name, material_data in category_materials.items():
            props = self._extract_properties(material_data, property_names)
            for prop_name, prop_data in props.items():
                if 'value' not in prop_data:
                    raise KeyError(f"Extracted property '{prop_name}' missing required key: 'value'")
                value = prop_data['value']
                if value is not None:
                    try:
                        property_values[prop_name].append(float(value))
                    except (ValueError, TypeError):
                        pass  # Skip non-numeric
        
        # Calculate statistics
        stats = {}
        for prop_name, values in property_values.items():
            if len(values) < 2:
                continue  # Need at least 2 values for stdev
            
            stats[prop_name] = {
                'mean': mean(values),
                'stdev': stdev(values) if len(values) > 1 else 0.0,
                'min': min(values),
                'max': max(values),
                'count': len(values)
            }
        
        # Cache results
        self._category_stats_cache[cache_key] = stats
        
        logger.debug(f"Calculated statistics for {len(stats)} properties in category '{category}'")
        
        return stats
    
    def format_properties_for_prompt(
        self,
        properties: List[Dict[str, Any]],
        include_comparison: bool = True
    ) -> str:
        """
        Format selected properties as prompt-friendly text.
        
        Args:
            properties: List of property dicts from select_distinctive_properties()
            include_comparison: If True, include category comparison context
            
        Returns:
            Formatted string for prompt injection
        """
        if not properties:
            return "No distinctive properties available."
        
        lines = []
        for prop in properties:
            name_display = prop['name'].replace('_', ' ').title()
            value_str = f"{prop['value']} {prop['unit']}".strip()
            
            if include_comparison and prop['distinctiveness_score'] > 1.0:
                # High distinctiveness - add comparison
                lines.append(
                    f"- {name_display}: {value_str} "
                    f"(significantly {'higher' if float(prop['value']) > prop['category_mean'] else 'lower'} "
                    f"than category average of {prop['category_mean']:.2f})"
                )
            else:
                # Standard formatting
                lines.append(f"- {name_display}: {value_str}")
        
        return "\n".join(lines)
