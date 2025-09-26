#!/usr/bin/env python3
"""
Dynamic Property Integration Service

Integrates the dynamic material property research system with frontmatter generation
to provide comprehensive property data when materials lack stored properties.

This service bridges the gap between the Material Property Research System 
and the frontmatter generator, ensuring all materials get appropriate properties
based on their category and laser processing requirements.
"""

import logging
import sys
from pathlib import Path
from typing import Dict, List, Optional, Any

# Add project root to path for imports
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

try:
    from research.material_property_research_system import MaterialPropertyResearchSystem
    DYNAMIC_RESEARCH_AVAILABLE = True
    logger = logging.getLogger(__name__)
    logger.info("Dynamic Property Research System available")
except ImportError as e:
    DYNAMIC_RESEARCH_AVAILABLE = False
    MaterialPropertyResearchSystem = None
    logger = logging.getLogger(__name__)
    logger.warning(f"Dynamic Property Research System not available: {e}")


class DynamicPropertyIntegration:
    """Integrates dynamic property research with frontmatter generation"""
    
    def __init__(self):
        self.research_system = None
        if DYNAMIC_RESEARCH_AVAILABLE:
            try:
                self.research_system = MaterialPropertyResearchSystem()
                logger.info("Dynamic Property Research System initialized successfully")
            except Exception as e:
                logger.error(f"Failed to initialize Dynamic Property Research System: {e}")
                self.research_system = None
    
    def enhance_material_properties(self, material_name: str, existing_properties: Dict, material_data: Dict) -> Dict:
        """
        Enhance material properties using dynamic research system.
        
        Args:
            material_name: Name of the material
            existing_properties: Currently available properties from materials.yaml
            material_data: Full material data from materials.yaml
            
        Returns:
            Enhanced properties dictionary with researched properties
        """
        if not self.research_system:
            logger.warning("Dynamic research system not available - returning existing properties")
            return existing_properties
            
        try:
            # Get dynamic recommendations
            recommendations = self.research_system.get_recommended_properties_for_material(material_name)
            
            if 'error' in recommendations:
                logger.warning(f"No recommendations available for {material_name}: {recommendations['error']}")
                return existing_properties
            
            # Start with existing properties
            enhanced_properties = existing_properties.copy()
            
            # Add priority properties (top 5) with realistic values for the material
            priority_properties = recommendations.get('priority_properties', [])
            
            for prop_info in priority_properties[:8]:  # Get top 8 priority properties
                prop_name = prop_info['name']
                
                # Convert research system property names to frontmatter property names
                frontmatter_prop_name = self._convert_property_name(prop_name)
                
                # Only add if not already present
                if frontmatter_prop_name not in enhanced_properties:
                    # Generate realistic value for this material/property combination
                    property_data = self._generate_property_data(
                        material_name, 
                        material_data.get('category', 'unknown'),
                        prop_info
                    )
                    
                    if property_data:
                        enhanced_properties.update(property_data)
                        logger.debug(f"Added dynamic property {prop_name} -> {frontmatter_prop_name} for {material_name}")
            
            # Log enhancement summary
            added_count = len(enhanced_properties) - len(existing_properties)
            if added_count > 0:
                logger.info(f"Enhanced {material_name} with {added_count} dynamic properties "
                           f"(total: {len(enhanced_properties)})")
            
            return enhanced_properties
            
        except Exception as e:
            logger.error(f"Error enhancing properties for {material_name}: {e}")
            return existing_properties
    
    def _convert_property_name(self, research_prop_name: str) -> str:
        """Convert research system property names to frontmatter property names"""
        conversion_map = {
            'density': 'density',
            'thermal_conductivity': 'thermalConductivity',
            'melting_point': 'meltingPoint',
            'specific_heat': 'specificHeat',
            'hardness': 'hardness',
            'tensile_strength': 'tensileStrength',
            'youngs_modulus': 'youngsModulus',
            'thermal_expansion': 'thermalExpansion',
            'laser_absorption': 'laserAbsorption',
            'reflectivity': 'reflectivity',
            'thermal_shock_resistance': 'thermalShockResistance',
            'electrical_conductivity': 'electricalConductivity',
            'surface_roughness': 'surfaceRoughness',
            'corrosion_resistance': 'corrosionResistance',
            'glass_transition_temperature': 'glassTg'
        }
        return conversion_map.get(research_prop_name, research_prop_name)
    
    def _generate_property_data(self, material_name: str, category: str, prop_info: Dict) -> Optional[Dict]:
        """
        Generate realistic property data for a specific material.
        
        Args:
            material_name: Name of the material
            category: Material category (ceramic, metal, etc.)
            prop_info: Property information from research system
            
        Returns:
            Dictionary with property value, unit, and ranges if applicable
        """
        try:
            prop_name = prop_info['name']
            frontmatter_prop_name = self._convert_property_name(prop_name)
            typical_range = prop_info.get('typical_range', {})
            units = prop_info.get('units', [])
            
            # Get primary unit (first in list)
            primary_unit = units[0] if units else ''
            
            property_data = {}
            
            # Generate realistic values based on material and property
            if typical_range and 'min' in typical_range and 'max' in typical_range:
                min_val = typical_range['min']
                max_val = typical_range['max']
                
                # Generate a realistic value within the range
                # For most properties, use a value closer to the middle-lower range
                if prop_name == 'density':
                    value = self._generate_density_value(material_name, category, min_val, max_val)
                elif prop_name == 'thermal_conductivity':
                    value = self._generate_thermal_conductivity_value(material_name, category, min_val, max_val)
                elif prop_name == 'melting_point':
                    value = self._generate_melting_point_value(material_name, category, min_val, max_val)
                elif prop_name == 'hardness':
                    value = self._generate_hardness_value(material_name, category, min_val, max_val)
                else:
                    # Default: use middle of range
                    value = round((min_val + max_val) / 2, 2)
                
                # Add the main property value
                property_data[frontmatter_prop_name] = value
                
                # Add unit
                if primary_unit:
                    property_data[f'{frontmatter_prop_name}Unit'] = primary_unit
                
                # Add min/max ranges for important properties
                if prop_info.get('laser_relevance', 0) >= 0.8:
                    property_data[f'{frontmatter_prop_name}Min'] = min_val
                    property_data[f'{frontmatter_prop_name}Max'] = max_val
                
                return property_data
            
            # For qualitative properties (like corrosion_resistance), provide descriptive values
            elif prop_name == 'corrosion_resistance':
                resistance_rating = self._generate_corrosion_resistance(material_name, category)
                if resistance_rating:
                    property_data[frontmatter_prop_name] = resistance_rating
                    return property_data
            
            return None
            
        except Exception as e:
            logger.error(f"Error generating property data for {prop_name}: {e}")
            return None
    
    def _generate_density_value(self, material_name: str, category: str, min_val: float, max_val: float) -> float:
        """Generate realistic density values for specific materials"""
        # Material-specific density knowledge
        density_map = {
            'zirconia': 6.05,  # ZrO2 typical density
            'alumina': 3.95,   # Al2O3 typical density  
            'silicon nitride': 3.20,  # Si3N4 typical density
            'aluminum': 2.70,   # Al typical density
            'steel': 7.85,     # Steel typical density
            'titanium': 4.51,  # Ti typical density
            'copper': 8.96,    # Cu typical density
        }
        
        material_lower = material_name.lower()
        for key, density in density_map.items():
            if key in material_lower:
                return density
        
        # Category-based estimates
        if category == 'ceramic':
            return round(min_val + (max_val - min_val) * 0.3, 2)  # Lower end for most ceramics
        elif category == 'metal':
            return round(min_val + (max_val - min_val) * 0.4, 2)  # Mid-range for metals
        else:
            return round((min_val + max_val) / 2, 2)
    
    def _generate_thermal_conductivity_value(self, material_name: str, category: str, min_val: float, max_val: float) -> float:
        """Generate realistic thermal conductivity values"""
        material_lower = material_name.lower()
        
        # Material-specific thermal conductivity
        if 'zirconia' in material_lower:
            return 2.0  # ZrO2 typical thermal conductivity
        elif 'alumina' in material_lower:
            return 30.0  # Al2O3 typical thermal conductivity
        elif 'silicon nitride' in material_lower:
            return 85.0  # Si3N4 typical thermal conductivity
        elif 'aluminum' in material_lower:
            return 237.0  # Al typical thermal conductivity
        elif 'copper' in material_lower:
            return 401.0  # Cu typical thermal conductivity
        
        # Category defaults
        if category == 'ceramic':
            return round(min_val + (max_val - min_val) * 0.1, 1)  # Lower end for ceramics
        elif category == 'metal':
            return round(min_val + (max_val - min_val) * 0.6, 1)  # Higher end for metals
        else:
            return round((min_val + max_val) / 2, 1)
    
    def _generate_melting_point_value(self, material_name: str, category: str, min_val: float, max_val: float) -> float:
        """Generate realistic melting point values"""
        material_lower = material_name.lower()
        
        # Material-specific melting points
        melting_points = {
            'zirconia': 2715,    # ZrO2
            'alumina': 2072,     # Al2O3  
            'silicon nitride': 1900,  # Si3N4 (decomposes)
            'aluminum': 660,     # Al
            'copper': 1085,      # Cu
            'titanium': 1668,    # Ti
            'steel': 1500,       # Steel (average)
        }
        
        for key, melting_point in melting_points.items():
            if key in material_lower:
                return melting_point
        
        # Category-based estimates
        if category == 'ceramic':
            return round(min_val + (max_val - min_val) * 0.7, 0)  # Higher end for ceramics
        elif category == 'metal':
            return round(min_val + (max_val - min_val) * 0.5, 0)  # Mid-range for metals
        else:
            return round((min_val + max_val) / 2, 0)
    
    def _generate_hardness_value(self, material_name: str, category: str, min_val: float, max_val: float) -> float:
        """Generate realistic hardness values"""
        material_lower = material_name.lower()
        
        if category == 'ceramic':
            # Ceramics are typically very hard (Mohs scale)
            if 'zirconia' in material_lower:
                return 8.5  # Mohs
            elif 'alumina' in material_lower:
                return 9.0  # Mohs
            elif 'silicon nitride' in material_lower:
                return 9.2  # Mohs
            return round(min_val + (max_val - min_val) * 0.8, 1)  # High end for ceramics
        
        elif category == 'metal':
            # Metals typically mid-range hardness
            return round(min_val + (max_val - min_val) * 0.4, 0)
        
        return round((min_val + max_val) / 2, 1)
    
    def _generate_corrosion_resistance(self, material_name: str, category: str) -> Optional[str]:
        """Generate qualitative corrosion resistance ratings"""
        material_lower = material_name.lower()
        
        if category == 'ceramic':
            return "Excellent"  # Most ceramics have excellent corrosion resistance
        elif 'stainless' in material_lower:
            return "Excellent"
        elif 'aluminum' in material_lower:
            return "Good"
        elif 'titanium' in material_lower:
            return "Excellent"
        elif 'steel' in material_lower:
            return "Fair"
        elif 'copper' in material_lower:
            return "Good"
        
        return None


def enhance_frontmatter_properties(material_name: str, existing_properties: Dict, material_data: Dict) -> Dict:
    """
    Convenience function to enhance properties using dynamic research.
    
    Args:
        material_name: Name of the material
        existing_properties: Current properties from materials.yaml
        material_data: Full material data
        
    Returns:
        Enhanced properties dictionary
    """
    integrator = DynamicPropertyIntegration()
    return integrator.enhance_material_properties(material_name, existing_properties, material_data)


if __name__ == '__main__':
    # Test the integration
    integrator = DynamicPropertyIntegration()
    
    # Test with Zirconia
    print("Testing Dynamic Property Integration with Zirconia:")
    enhanced = integrator.enhance_material_properties("Zirconia", {}, {"category": "ceramic"})
    
    print(f"Enhanced properties for Zirconia: {len(enhanced)} properties")
    for prop, value in enhanced.items():
        print(f"  {prop}: {value}")