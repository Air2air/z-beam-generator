#!/usr/bin/env python3
"""
Dynamic Property Generator with Web Research Integration

Integrates the Material Property Research System with web research capabilities
to populate comprehensive material properties for frontmatter generation.
"""

import sys
import re
import asyncio
from typing import Dict, List, Optional
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

# Import after path setup
# Try to import research system separately
try:
    from research.material_property_research_system import MaterialPropertyResearchSystem
    print("DEBUG: Successfully imported MaterialPropertyResearchSystem")
except ImportError as e:
    print(f"Research system import error: {e}")
    MaterialPropertyResearchSystem = None

# Try to import API components separately
try:
    from api.client_manager import ClientManager
    from api.config import APIConfig
    print("DEBUG: Successfully imported API components")
except ImportError as e:
    print(f"API components import warning: {e}")
    ClientManager = None
    APIConfig = None


class DynamicPropertyGenerator:
    """Generates material properties through research and web search"""
    
    def __init__(self):
        if MaterialPropertyResearchSystem:
            self.research_system = MaterialPropertyResearchSystem()
        else:
            self.research_system = None
        
        # API manager for web research (optional)
        self.api_manager = None
        try:
            if ClientManager and APIConfig:
                self.api_manager = ClientManager(APIConfig())
        except Exception as e:
            print(f"API manager initialization failed: {e}")
            self.api_manager = None
        
    def generate_properties_for_material(self, material_name: str, existing_data: Dict = None) -> Dict:
        """
        Generate comprehensive material properties by combining:
        1. Existing data from materials.yaml
        2. Dynamic property research recommendations  
        3. Web research for actual values
        """
        
        # Get property recommendations from research system
        if not self.research_system:
            return self._generate_basic_properties(existing_data or {})
            
        recommendations = self.research_system.get_recommended_properties_for_material(material_name)
        print(f"DEBUG: Research system found {recommendations.get('total_recommended', 0)} properties for {material_name}")
        
        if 'error' in recommendations:
            return self._generate_basic_properties(existing_data or {})
        
        # Start with existing properties
        properties = {}
        if existing_data:
            properties.update(self._extract_existing_properties(existing_data))
        
        # Research and populate missing recommended properties
        recommended_props = recommendations.get('recommended_properties', [])[:5]  # Top 5
        print(f"DEBUG: Processing {len(recommended_props)} recommended properties")
        
        for prop_rec in recommended_props:
            prop_name = prop_rec['name']
            print(f"DEBUG: Checking property {prop_name}")
            if not self._has_property(properties, prop_name):
                # Research the actual value for this material and property
                researched_value = self._research_property_value(
                    material_name, 
                    prop_name, 
                    prop_rec
                )
                if researched_value:
                    properties.update(researched_value)
                    print(f"DEBUG: Added property {prop_name}")
                else:
                    print(f"DEBUG: Failed to research property {prop_name}")
            else:
                print(f"DEBUG: Property {prop_name} already exists")
        
        return properties
    
    def _generate_basic_properties(self, existing_data):
        """Generate basic properties without research system."""
        print("DEBUG: Generating basic properties without research system")
        
        # Return common properties based on material type or existing data
        basic_properties = {}
        
        # Add any existing numeric properties that have proper structure
        for key, value in existing_data.items():
            if isinstance(value, dict) and ('value' in value or 'min' in value or 'max' in value):
                basic_properties[key] = value
                
        return basic_properties
    
    def _extract_existing_properties(self, material_data: Dict) -> Dict:
        """Extract existing properties from materials.yaml data"""
        properties = {}
        
        # Standard property mappings
        property_mappings = {
            'density': 'density',
            'thermal_conductivity': 'thermalConductivity', 
            'tensile_strength': 'tensileStrength',
            'youngs_modulus': 'youngsModulus',
            'hardness': 'hardness',
            'melting_point': 'meltingPoint',
            'specific_heat': 'specificHeat'
        }
        
        for yaml_key, prop_key in property_mappings.items():
            if yaml_key in material_data:
                material_value = material_data[yaml_key]
                numeric_value = self._extract_numeric_only(material_value)
                if numeric_value is not None:
                    properties[prop_key] = numeric_value
                    # Add unit separately
                    unit = self._extract_unit(material_value)
                    if unit:
                        properties[f'{prop_key}Unit'] = unit
                    # Add ranges if present
                    self._add_property_ranges_from_value(properties, material_value, prop_key)
        
        return properties
    
    def _has_property(self, properties: Dict, prop_name: str) -> bool:
        """Check if property already exists in properties dict"""
        property_mappings = {
            'density': 'density',
            'thermal_conductivity': 'thermalConductivity',
            'tensile_strength': 'tensileStrength', 
            'youngs_modulus': 'youngsModulus',
            'hardness': 'hardness',
            'melting_point': 'meltingPoint',
            'specific_heat': 'specificHeat',
            'laser_absorption': 'laserAbsorption',
            'reflectivity': 'reflectivity',
            'thermal_expansion': 'thermalExpansion'
        }
        
        mapped_name = property_mappings.get(prop_name, prop_name)
        return mapped_name in properties
    
    def _research_property_value(self, material_name: str, property_name: str, property_rec: Dict) -> Optional[Dict]:
        """Research actual property value using web search"""
        
        try:
            # Create search query for this material and property
            common_names = property_rec.get('common_names', [property_name])
            
            search_queries = [
                f"{material_name} {property_name} value",
                f"{material_name} {common_names[0]}" if common_names else f"{material_name} {property_name}",
                f"{material_name} material properties {property_name}"
            ]
            
            # Research the property value
            researched_data = self._perform_web_research(search_queries, material_name, property_name, property_rec)
            
            if researched_data:
                return researched_data
                
        except Exception as e:
            print(f"Research failed for {material_name} {property_name}: {str(e)}")
        
        # Fallback to typical range if research fails
        return self._generate_fallback_property(property_name, property_rec)
    
    def _perform_web_research(self, queries: List[str], material_name: str, property_name: str, property_rec: Dict) -> Optional[Dict]:
        """Perform actual web research using AI API"""
        
        try:
            # Create a research prompt
            research_prompt = f"""
            Research the {property_name} ({', '.join(property_rec.get('common_names', []))}) for {material_name}.
            
            Property details:
            - Description: {property_rec.get('description', '')}
            - Typical units: {', '.join(property_rec.get('units', []))}
            - Typical range: {property_rec.get('typical_range', {})}
            - Industry standards: {', '.join(property_rec.get('industry_standards', []))}
            
            Please provide:
            1. The typical value for {material_name}
            2. The unit of measurement
            3. Any typical range (min-max) if applicable
            
            Format the response as:
            Value: [number]
            Unit: [unit]
            Range: [min]-[max] (if applicable)
            Source: [brief source reference]
            
            Focus on reliable engineering sources like CRC Handbook, ASM Materials Database, or manufacturer specifications.
            """
            
            # Get response from API
            try:
                client = self.api_manager.get_client('perplexity')  # Use Perplexity for research
                if client:
                    response = client.chat.completions.create(
                        model="llama-3.1-sonar-small-128k-online",
                        messages=[{"role": "user", "content": research_prompt}],
                        temperature=0.1,  # Low temperature for factual research
                        max_tokens=500
                    )
                    
                    if response and response.choices:
                        research_result = response.choices[0].message.content
                        return self._parse_research_result(research_result, property_name, property_rec)
                        
            except Exception as api_error:
                print(f"API research failed: {str(api_error)}")
                
        except Exception as e:
            print(f"Web research failed: {str(e)}")
        
        return None
    
    def _parse_research_result(self, research_text: str, property_name: str, property_rec: Dict) -> Optional[Dict]:
        """Parse the research result and extract property data"""
        
        try:
            properties = {}
            
            # Extract value
            value_match = re.search(r'Value:\s*([0-9.]+)', research_text, re.IGNORECASE)
            if value_match:
                value = float(value_match.group(1))
                
                # Map property name to frontmatter key
                property_mappings = {
                    'density': 'density',
                    'thermal_conductivity': 'thermalConductivity',
                    'tensile_strength': 'tensileStrength', 
                    'youngs_modulus': 'youngsModulus',
                    'hardness': 'hardness',
                    'melting_point': 'meltingPoint',
                    'specific_heat': 'specificHeat',
                    'laser_absorption': 'laserAbsorption',
                    'reflectivity': 'reflectivity',
                    'thermal_expansion': 'thermalExpansion'
                }
                
                prop_key = property_mappings.get(property_name, property_name)
                properties[prop_key] = value
                
                # Extract unit
                unit_match = re.search(r'Unit:\s*([^\n\r]+)', research_text, re.IGNORECASE)
                if unit_match:
                    unit = unit_match.group(1).strip()
                    properties[f'{prop_key}Unit'] = unit
                
                # Extract range
                range_match = re.search(r'Range:\s*([0-9.]+)\s*[-–—]\s*([0-9.]+)', research_text, re.IGNORECASE)
                if range_match:
                    min_val = float(range_match.group(1))
                    max_val = float(range_match.group(2))
                    properties[f'{prop_key}Min'] = min_val
                    properties[f'{prop_key}Max'] = max_val
                
                return properties
                
        except Exception as e:
            print(f"Failed to parse research result: {str(e)}")
        
        return None
    
    def _generate_fallback_property(self, property_name: str, property_rec: Dict) -> Optional[Dict]:
        """Generate fallback property value from typical ranges"""
        
        typical_range = property_rec.get('typical_range', {})
        if not typical_range:
            return None
        
        try:
            min_val = typical_range.get('min')
            max_val = typical_range.get('max')
            
            if min_val is not None and max_val is not None:
                # Use middle of range as typical value
                typical_value = (min_val + max_val) / 2
                
                property_mappings = {
                    'density': 'density',
                    'thermal_conductivity': 'thermalConductivity',
                    'tensile_strength': 'tensileStrength', 
                    'youngs_modulus': 'youngsModulus',
                    'hardness': 'hardness',
                    'melting_point': 'meltingPoint',
                    'specific_heat': 'specificHeat',
                    'laser_absorption': 'laserAbsorption',
                    'reflectivity': 'reflectivity',
                    'thermal_expansion': 'thermalExpansion'
                }
                
                prop_key = property_mappings.get(property_name, property_name)
                properties = {
                    prop_key: typical_value,
                    f'{prop_key}Min': min_val,
                    f'{prop_key}Max': max_val
                }
                
                # Add typical unit
                units = property_rec.get('units', [])
                if units:
                    properties[f'{prop_key}Unit'] = units[0]
                
                return properties
                
        except Exception as e:
            print(f"Failed to generate fallback property: {str(e)}")
        
        return None
    
    def _generate_basic_properties(self, existing_data: Dict) -> Dict:
        """Generate basic properties from existing data only"""
        return self._extract_existing_properties(existing_data)
    
    def _extract_numeric_only(self, value):
        """Extract numeric value from a string that may contain units"""
        if isinstance(value, (int, float)):
            return value
        
        if isinstance(value, str):
            import re
            match = re.match(r'^(-?\d+(?:\.\d+)?)', value.strip())
            if match:
                numeric_str = match.group(1)
                try:
                    if '.' in numeric_str:
                        return float(numeric_str)
                    else:
                        return int(numeric_str)
                except ValueError:
                    return None
        
        return None
    
    def _extract_unit(self, value_with_unit: str) -> str:
        """Extract unit from a string like '7.8-8.9 g/cm³'"""
        if not isinstance(value_with_unit, str):
            return ""
        
        import re
        unit_match = re.search(r'([a-zA-Z/°×·⁻⁰¹²³⁴⁵⁶⁷⁸⁹]+)$', value_with_unit.strip())
        return unit_match.group(1) if unit_match else ""
    
    def _add_property_ranges_from_value(self, properties: Dict, value_str: str, prop_key: str):
        """Extract min/max ranges from values like '7.8-8.9 g/cm³'"""
        if not isinstance(value_str, str):
            return
            
        import re
        range_match = re.search(r'(\d+(?:\.\d+)?)\s*[-–—]\s*(\d+(?:\.\d+)?)', value_str)
        if range_match:
            min_val = float(range_match.group(1))
            max_val = float(range_match.group(2))
            properties[f'{prop_key}Min'] = min_val
            properties[f'{prop_key}Max'] = max_val


# Standalone testing function
async def test_dynamic_property_generator():
    """Test the dynamic property generator"""
    generator = DynamicPropertyGenerator()
    
    # Test with Zirconia (ceramic with no existing properties)
    print("🧪 Testing Dynamic Property Generation for Zirconia")
    print("=" * 50)
    
    zirconia_properties = generator.generate_properties_for_material("Zirconia")
    
    print(f"Generated {len(zirconia_properties)} properties:")
    for key, value in zirconia_properties.items():
        print(f"  {key}: {value}")
    
    print("\n" + "=" * 50)


if __name__ == '__main__':
    # Run test
    asyncio.run(test_dynamic_property_generator())