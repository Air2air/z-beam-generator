"""
SEO Data Enricher

Extracts and formats material data for SEO prompt templates.
Provides all the context needed to generate spec-compliant page titles and meta descriptions.

The enricher extracts:
- Material properties (reflectivity, absorption, thermal conductivity, etc.)
- Laser interaction characteristics (wavelength, power range, challenges)
- Common contaminants
- Applications
- Machine settings summary

Data flows:
  Materials.yaml → SEODataEnricher → Formatted context dict → SEO prompt template
"""

from typing import Dict, Any, List, Optional
import logging

logger = logging.getLogger(__name__)


class SEODataEnricher:
    """Extract and format material data for SEO generation."""
    
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
        material_name = item_data.get('name', identifier.replace('-laser-cleaning', '').replace('-', ' ').title())
        category = item_data.get('category', 'Unknown')
        subcategory = item_data.get('subcategory', '')
        
        # Get full path (already in data)
        full_path = item_data.get('full_path', f"{category} / {material_name}")
        
        # Extract properties - navigate nested structure
        properties = item_data.get('properties', {})
        
        # Get all properties from nested categories
        all_props = {}
        for cat_name, cat_data in properties.items():
            if isinstance(cat_data, dict):
                for prop_name, prop_val in cat_data.items():
                    if prop_name not in ['label', 'description']:  # Skip metadata
                        all_props[prop_name] = prop_val
        
        # Extract specific properties
        reflectivity = all_props.get('reflectivity', {}).get('value', 'N/A')
        absorption = all_props.get('absorption', {}).get('value', 'N/A')
        thermal_conductivity = all_props.get('thermal_conductivity', {}).get('value', 'N/A')
        melting_point = all_props.get('melting_point', {}).get('value', 'N/A')
        density = all_props.get('density', {}).get('value', 'N/A')
        
        # Format properties context using all flattened properties
        properties_context = SEODataEnricher._format_properties_list(all_props)
        
        # Extract laser characteristics from flattened properties
        wavelength = all_props.get('optimal_wavelength', {})
        if isinstance(wavelength, dict):
            wavelength = wavelength.get('value', 'N/A')
        
        # Try different power property names
        power_min = 'N/A'
        power_max = 'N/A'
        if 'power_min' in all_props:
            power_min = all_props['power_min'].get('value', 'N/A') if isinstance(all_props['power_min'], dict) else all_props['power_min']
        if 'power_max' in all_props:
            power_max = all_props['power_max'].get('value', 'N/A') if isinstance(all_props['power_max'], dict) else all_props['power_max']
        if 'power_range' in all_props:
            power_range = all_props['power_range']
            if isinstance(power_range, dict):
                power_min = power_range.get('min', power_min)
                power_max = power_range.get('max', power_max)
        
        primary_challenge = all_props.get('primary_challenge', 'Material-specific laser interaction challenges')
        damage_risk = all_props.get('damage_risk', 'Thermal damage, surface integrity risks')
        
        laser_context = SEODataEnricher._format_laser_context(all_props)
        
        # Extract contaminants
        contaminants = item_data.get('common_contaminants', [])
        contaminants_list = SEODataEnricher._format_contaminants_list(contaminants)
        
        # Extract applications
        applications = item_data.get('applications', [])
        applications_list = SEODataEnricher._format_applications_list(applications)
        
        # Settings summary
        settings_context = SEODataEnricher._format_settings_summary(item_data)
        
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
                unit = data.get('unit', '')
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
                    unit = data.get('unit', '')
                    lines.append(f"- {name}: {value} {unit}".strip())
                elif 'min' in data and 'max' in data:
                    lines.append(f"- {name}: {data['min']}-{data['max']}")
        
        return '\n'.join(lines) if lines else "Laser interaction data available"
    
    @staticmethod
    def _format_contaminants_list(contaminants: List) -> str:
        """Format contaminants list."""
        if not contaminants:
            return "Various industrial contaminants"
        
        # Handle list of strings or list of dicts
        items = []
        for cont in contaminants:
            if isinstance(cont, str):
                items.append(f"- {cont}")
            elif isinstance(cont, dict):
                name = cont.get('name', cont.get('type', 'Unknown'))
                items.append(f"- {name}")
        
        return '\n'.join(items) if items else "Standard contaminants"
    
    @staticmethod
    def _format_applications_list(applications: List) -> str:
        """Format applications list."""
        if not applications:
            return "Industrial cleaning applications"
        
        # Handle list of strings or list of dicts
        items = []
        for app in applications:
            if isinstance(app, str):
                items.append(f"- {app}")
            elif isinstance(app, dict):
                name = app.get('name', app.get('industry', 'Industrial'))
                items.append(f"- {name}")
        
        return '\n'.join(items) if items else "Various industrial applications"
    
    @staticmethod
    def _format_settings_summary(item_data: Dict) -> str:
        """Format machine settings summary."""
        settings = item_data.get('machine_settings', {})
        if not settings:
            return "Standard machine settings apply"
        
        lines = []
        for key, data in settings.items():
            if isinstance(data, dict):
                name = key.replace('_', ' ').title()
                if 'value' in data:
                    value = data['value']
                    unit = data.get('unit', '')
                    lines.append(f"- {name}: {value} {unit}".strip())
                elif 'min' in data and 'max' in data:
                    lines.append(f"- {name}: {data['min']}-{data['max']}")
        
        return '\n'.join(lines) if lines else "Machine settings configured"
