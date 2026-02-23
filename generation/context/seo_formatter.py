"""
SEO Context Formatter

Formats material data for SEO prompt templates.
Provides all the context needed to generate spec-compliant page titles and meta descriptions.

The formatter extracts:
- Material properties (reflectivity, absorption, thermal conductivity, etc.)
- Laser interaction characteristics (wavelength, power range, challenges)
- Common contaminants
- Applications
- Machine settings summary

Data flows:
  Materials.yaml → SEOContextFormatter → Formatted context dict → SEO prompt template
"""

from typing import Dict, Any, List, Optional
import logging

logger = logging.getLogger(__name__)


class SEOContextFormatter:
    """Formats material data for SEO generation."""

    @staticmethod
    def _require_key(data: Dict[str, Any], key: str, context: str) -> Any:
        if key not in data:
            raise KeyError(f"Missing required key '{key}' in {context}")
        return data[key]

    @staticmethod
    def _extract_property_value(all_props: Dict[str, Any], key: str) -> Any:
        if key not in all_props:
            raise KeyError(f"Missing required property '{key}'")

        value = all_props[key]
        if isinstance(value, dict):
            if 'value' not in value:
                raise KeyError(f"Property '{key}' missing required key 'value'")
            return value['value']
        return value
    
    @staticmethod
    def enrich_material_for_seo(item_data: Dict[str, Any], identifier: str) -> Dict[str, str]:
        """
        Extract all data needed for material SEO generation.
        
        Args:
            item_data: Material data from Materials.yaml
            identifier: Material identifier (e.g., "aluminum-laser-cleaning")
            
        Returns:
            Dict with formatted context for SEO prompt placeholders
        """
        # Extract basic info
        material_name = SEOContextFormatter._require_key(item_data, 'name', f"item_data for {identifier}")
        category = SEOContextFormatter._require_key(item_data, 'category', f"item_data for {identifier}")
        subcategory = SEOContextFormatter._require_key(item_data, 'subcategory', f"item_data for {identifier}")
        
        # Get full path (already in data)
        full_path = SEOContextFormatter._require_key(item_data, 'full_path', f"item_data for {identifier}")
        
        # Extract properties - navigate nested structure
        properties = SEOContextFormatter._require_key(item_data, 'properties', f"item_data for {identifier}")
        if not isinstance(properties, dict):
            raise TypeError(f"Key 'properties' must be a dict for {identifier}")
        
        # Get all properties from nested categories
        all_props = {}
        for cat_name, cat_data in properties.items():
            if isinstance(cat_data, dict):
                for prop_name, prop_val in cat_data.items():
                    if prop_name not in ['label', 'description']:  # Skip metadata
                        all_props[prop_name] = prop_val
        
        # Extract specific properties
        reflectivity = SEOContextFormatter._extract_property_value(all_props, 'reflectivity')
        absorption = SEOContextFormatter._extract_property_value(all_props, 'absorption')
        thermal_conductivity = SEOContextFormatter._extract_property_value(all_props, 'thermal_conductivity')
        melting_point = SEOContextFormatter._extract_property_value(all_props, 'melting_point')
        density = SEOContextFormatter._extract_property_value(all_props, 'density')
        
        # Format properties context using all flattened properties
        properties_context = SEOContextFormatter._format_properties_list(all_props)
        
        # Extract laser characteristics from flattened properties
        wavelength = SEOContextFormatter._extract_property_value(all_props, 'optimal_wavelength')
        
        # Try different power property names
        power_min = SEOContextFormatter._extract_property_value(all_props, 'power_min')
        power_max = SEOContextFormatter._extract_property_value(all_props, 'power_max')
        if 'power_range' in all_props:
            power_range = all_props['power_range']
            if isinstance(power_range, dict):
                if 'min' not in power_range or 'max' not in power_range:
                    raise KeyError("Property 'power_range' must contain 'min' and 'max'")
                power_min = power_range['min']
                power_max = power_range['max']

        primary_challenge = SEOContextFormatter._extract_property_value(all_props, 'primary_challenge')
        damage_risk = SEOContextFormatter._extract_property_value(all_props, 'damage_risk')
        
        laser_context = SEOContextFormatter._format_laser_context(all_props)
        
        # Extract contaminants
        contaminants = SEOContextFormatter._require_key(item_data, 'common_contaminants', f"item_data for {identifier}")
        if not isinstance(contaminants, list):
            raise TypeError(f"Key 'common_contaminants' must be a list for {identifier}")
        contaminants_list = SEOContextFormatter._format_contaminants_list(contaminants)
        
        # Extract applications
        applications = SEOContextFormatter._require_key(item_data, 'applications', f"item_data for {identifier}")
        if not isinstance(applications, list):
            raise TypeError(f"Key 'applications' must be a list for {identifier}")
        applications_list = SEOContextFormatter._format_applications_list(applications)
        
        # Settings summary
        settings_context = SEOContextFormatter._format_settings_summary(item_data)
        
        return {
            'material_name': material_name,
            'category': category,
            'subcategory': subcategory,
            'full_path': full_path,
            'properties_context': properties_context,
            'reflectivity': str(reflectivity),
            'absorption': str(absorption),
            'thermal_conductivity': str(thermal_conductivity),
            'melting_point': str(melting_point),
            'density': str(density),
            'laser_context': laser_context,
            'wavelength': str(wavelength),
            'power_min': str(power_min),
            'power_max': str(power_max),
            'primary_challenge': primary_challenge,
            'damage_risk': damage_risk,
            'contaminants_list': contaminants_list,
            'applications_list': applications_list,
            'settings_context': settings_context,
        }
    
    @staticmethod
    def _format_properties_list(properties: Dict) -> str:
        """Format properties into readable list."""
        if not properties:
            return "No specific properties data available"
        
        lines = []
        for key, data in properties.items():
            if isinstance(data, dict) and 'value' in data:
                name = key.replace('_', ' ').title()
                value = data['value']
                unit = data['unit'] if 'unit' in data else ''
                lines.append(f"- {name}: {value} {unit}".strip())
        
        return '\n'.join(lines) if lines else "Properties data available"
    
    @staticmethod
    def _format_laser_context(laser_char: Dict) -> str:
        """Format laser characteristics into readable context."""
        if not laser_char:
            return "Standard laser cleaning parameters apply"
        
        lines = []
        for key, data in laser_char.items():
            if isinstance(data, dict):
                name = key.replace('_', ' ').title()
                if 'value' in data:
                    value = data['value']
                    unit = data['unit'] if 'unit' in data else ''
                    lines.append(f"- {name}: {value} {unit}".strip())
                elif 'min' in data and 'max' in data:
                    lines.append(f"- {name}: {data['min']}-{data['max']}")
        
        return '\n'.join(lines) if lines else "Laser interaction data available"
    
    @staticmethod
    def _format_contaminants_list(contaminants: List) -> str:
        """Format contaminants list."""
        if not contaminants:
            raise ValueError("Contaminants list is empty")
        
        # Handle list of strings or list of dicts
        items = []
        for cont in contaminants:
            if isinstance(cont, str):
                items.append(f"- {cont}")
            elif isinstance(cont, dict):
                if 'name' in cont:
                    name = cont['name']
                elif 'type' in cont:
                    name = cont['type']
                else:
                    raise KeyError("Contaminant entry must contain 'name' or 'type'")
                items.append(f"- {name}")
        
        if not items:
            raise ValueError("No valid contaminant entries found")
        return '\n'.join(items)
    
    @staticmethod
    def _format_applications_list(applications: List) -> str:
        """Format applications list."""
        if not applications:
            raise ValueError("Applications list is empty")
        
        # Handle list of strings or list of dicts
        items = []
        for app in applications:
            if isinstance(app, str):
                items.append(f"- {app}")
            elif isinstance(app, dict):
                if 'name' in app:
                    name = app['name']
                elif 'industry' in app:
                    name = app['industry']
                else:
                    raise KeyError("Application entry must contain 'name' or 'industry'")
                items.append(f"- {name}")
        
        if not items:
            raise ValueError("No valid application entries found")
        return '\n'.join(items)
    
    @staticmethod
    def _format_settings_summary(item_data: Dict) -> str:
        """Format machine settings summary."""
        settings = SEOContextFormatter._require_key(item_data, 'machine_settings', 'item_data')
        if not isinstance(settings, dict):
            raise TypeError("Key 'machine_settings' must be a dictionary")
        if not settings:
            raise ValueError("Machine settings are empty")
        
        lines = []
        for key, data in settings.items():
            if isinstance(data, dict):
                name = key.replace('_', ' ').title()
                if 'value' in data:
                    value = data['value']
                    unit = data['unit'] if 'unit' in data else ''
                    lines.append(f"- {name}: {value} {unit}".strip())
                elif 'min' in data and 'max' in data:
                    lines.append(f"- {name}: {data['min']}-{data['max']}")
        
        if not lines:
            raise ValueError("No valid machine setting entries found")
        return '\n'.join(lines)
