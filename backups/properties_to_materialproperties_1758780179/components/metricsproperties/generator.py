#!/usr/bin/env python3
"""
Metrics Properties Component Generator

Generates material properties metrics cards using frontmatter extraction.
Integrated with the modular component architecture.
"""

from pathlib import Path
from typing import Dict, Optional
import yaml

from generators.hybrid_generator import HybridComponentGenerator
from generators.component_generators import ComponentResult
from utils.file_ops.frontmatter_loader import load_frontmatter_data
from utils.core.material_name_resolver import get_material_name_resolver


class MetricsPropertiesComponentGenerator(HybridComponentGenerator):
    """Generator for material properties metrics components using frontmatter data and API when needed"""

    def __init__(self):
        super().__init__("metricsproperties")
        
    def _build_prompt(
        self,
        material_name: str,
        material_data: Dict,
        author_info: Optional[Dict] = None,
        frontmatter_data: Optional[Dict] = None,
        schema_fields: Optional[Dict] = None,
    ) -> str:
        """
        Build prompt using both material data and frontmatter data.
        """
        # FAIL-FAST: Category must be present
        if frontmatter_data:
            if not frontmatter_data.get("category"):
                raise ValueError(f"Category missing from frontmatter for {material_name} - fail-fast requires explicit categorization")
            category = frontmatter_data["category"]
        elif not material_data.get("category"):
            raise ValueError(f"Category missing from material data for {material_name} - fail-fast requires explicit categorization")
        else:
            category = material_data["category"]
            
        # Get material properties from material data or frontmatter
        material_properties = {}
        
        # Common property names to extract
        property_fields = [
            "density", "meltingPoint", "thermalConductivity", "tensileStrength", 
            "youngsModulus", "thermalExpansion", "hardness", "specificHeat"
        ]
        
        for prop in property_fields:
            if prop in material_data:
                material_properties[prop] = material_data[prop]
        
        if frontmatter_data and frontmatter_data.get("properties"):
            material_properties.update(frontmatter_data["properties"])
            
        # FAIL-FAST: Some properties must be present
        if not material_properties:
            raise ValueError(f"Material properties missing for {material_name} - fail-fast requires explicit property data")
        
        author_name = author_info.get("name", "Z-Beam Engineering Team") if author_info else "Z-Beam Engineering Team"
        
        # Get material name resolver for consistent name handling
        resolver = get_material_name_resolver()
        canonical_name = resolver.resolve_canonical_name(material_name)
        if not canonical_name:
            raise ValueError(f"Material '{material_name}' not found in materials.yaml - fail-fast requires valid material names")
        
        material_name_title = resolver.get_display_name(material_name)
        
        # Build properties summary for prompt
        properties_summary = []
        for prop, value in material_properties.items():
            if isinstance(value, dict) and "value" in value and "unit" in value:
                properties_summary.append(f"- {prop}: {value['value']} {value['unit']}")
            else:
                properties_summary.append(f"- {prop}: {value}")
        
        properties_text = "\n".join(properties_summary) if properties_summary else "No properties provided"
        
        return f"""Generate a comprehensive material properties metrics card for {material_name_title} laser cleaning.

MATERIAL DETAILS:
- Name: {material_name_title}
- Category: {category}
- Author: {author_name}

MATERIAL PROPERTIES:
{properties_text}

Generate a structured YAML output that includes:
1. A properties section with key material characteristics
2. Each property should have: value, unit, min, max, description, priority
3. Priority levels: 1 (most important), 2 (important), 3 (supplementary)
4. Include technical descriptions for each property
5. Ensure units are properly formatted (g/cm³, °C, W/m·K, MPa, GPa, μm/m·K, etc.)

Key properties to include:
- density (material density in g/cm³)
- meltingPoint (melting temperature in °C)
- thermalConductivity (heat conduction in W/m·K)
- tensileStrength (tensile strength in MPa)
- youngsModulus (stiffness in GPa)
- thermalExpansion (expansion coefficient in μm/m·K)

Your output should be STRICTLY in YAML format.
Do NOT generate explanatory text - ONLY the YAML data structure.
"""
        
    def generate(
        self,
        material_name: str,
        material_data: Dict,
        api_client=None,
        author_info: Optional[Dict] = None,
        frontmatter_data: Optional[Dict] = None,
        schema_fields: Optional[Dict] = None,
    ) -> ComponentResult:
        """
        Generate component content using both frontmatter data and API when in hybrid mode.
        Will automatically load frontmatter data from file if not provided.
        """
        # If no frontmatter data was provided, try to load it from file
        if frontmatter_data is None:
            frontmatter_data = load_frontmatter_data(material_name)
            if not frontmatter_data:
                return ComponentResult(
                    component_type=self.component_type,
                    content="",
                    success=False,
                    error_message="No frontmatter data available",
                )
        
        # Determine if we should use API based on configuration
        from utils.component_mode import should_use_api
        use_api = should_use_api(self.component_type, api_client)
        
        # Use the structured frontmatter data as a base
        try:
            # First, extract basic metrics from frontmatter
            base_content = self._extract_from_frontmatter(material_name, frontmatter_data, material_data)
            
            # Then, if in hybrid mode, use API to enhance the descriptions
            if use_api:
                print(f"Generating {self.component_type} for {material_name} in hybrid mode with API enhancement")
                enhanced_content = self._enhance_with_api(
                    material_name=material_name,
                    material_data=material_data,
                    api_client=api_client,
                    author_info=author_info,
                    frontmatter_data=frontmatter_data,
                    base_content=base_content
                )
                
                return ComponentResult(
                    component_type=self.component_type,
                    content=enhanced_content,
                    success=True,
                )
            else:
                print(f"Generating {self.component_type} for {material_name} in static mode")
                return ComponentResult(
                    component_type=self.component_type,
                    content=base_content,
                    success=True,
                )
        except Exception as e:
            # Fall back to parent implementation if direct extraction fails
            return super().generate(
                material_name=material_name,
                material_data=material_data,
                api_client=api_client,
                author_info=author_info,
                frontmatter_data=frontmatter_data,
                schema_fields=schema_fields,
            )

    def _extract_from_frontmatter(
        self, material_name: str, frontmatter_data: Dict, material_data: Optional[Dict] = None
    ) -> str:
        """Generate properties metrics from frontmatter using example - FAIL-FAST: Must have valid configuration"""
        
        # If material_data is not provided, get it from materials database
        if material_data is None:
            from data.materials import get_material_by_name
            material_data = get_material_by_name(material_name)
            if not material_data:
                material_data = {}  # Use empty dict if material not found
        
        # Verify example template exists for fail-fast validation
        example_path = Path(__file__).parent / "example_metricsproperties.md"
        if not example_path.exists():
            raise Exception(f"Example template missing: {example_path} - FAIL-FAST requires valid template")
        
        # Get properties from frontmatter
        properties_fm = frontmatter_data.get("properties", {})
        
        # Also check material_data for fallback properties
        properties_md = {}
        property_mappings = {
            "density": "density",
            "melting_point": "meltingPoint", 
            "thermalConductivity": "thermalConductivity",
            "tensileStrength": "tensileStrength",
            "youngsModulus": "youngsModulus",
            "thermalExpansion": "thermalExpansion",
            "hardness": "hardness",
            "specificHeat": "specificHeat"
        }
        
        for md_key, prop_key in property_mappings.items():
            if md_key in material_data:
                properties_md[prop_key] = material_data[md_key]
        
        # Merge properties, prioritizing frontmatter
        combined_properties = {}
        combined_properties.update(properties_md)
        combined_properties.update(properties_fm)
        
        # FAIL-FAST: Properties must be present
        if not combined_properties:
            raise ValueError(f"Material properties missing for {material_name} - fail-fast requires explicit property data")
        
        # Build metrics structure
        metrics_data = {"properties": {}}
        
        # Define standard parameters with their expected units and ranges
        standard_params = {
            "density": {"unit": "g/cm³", "min": 0.5, "max": 25.0, "priority": 1},
            "meltingPoint": {"unit": "°C", "min": -100, "max": 4000, "priority": 1},
            "thermalConductivity": {"unit": "W/m·K", "min": 0.1, "max": 500, "priority": 2},
            "tensileStrength": {"unit": "MPa", "min": 10, "max": 5000, "priority": 2},
            "youngsModulus": {"unit": "GPa", "min": 1, "max": 1000, "priority": 3},
            "thermalExpansion": {"unit": "μm/m·K", "min": 0.1, "max": 100, "priority": 3},
        }
        
        # Handle separate unit fields in frontmatter properties
        
        # Extract and normalize parameters from frontmatter properties
        for prop_key, prop_value in combined_properties.items():
            # Skip unit fields as they are handled separately
            if prop_key.endswith("Unit"):
                continue
                
            # Find corresponding unit field
            unit_key = f"{prop_key}Unit"
            unit_value = combined_properties.get(unit_key)
            
            if prop_key in standard_params:
                std_info = standard_params[prop_key]
                
                # Extract value - handle different formats
                if isinstance(prop_value, dict) and "value" in prop_value:
                    value = prop_value["value"]
                    unit = prop_value.get("unit", unit_value or std_info["unit"])
                    description = prop_value.get("description", f"Material {prop_key}")
                elif isinstance(prop_value, str):
                    # Try to parse different string formats
                    value = None
                    unit = unit_value or std_info["unit"]  # Use unit from separate field or default
                    
                    # Handle temperature format like "1668°C"
                    import re
                    
                    # Format 1: "value unit" (e.g., "1668°C", "4.51 g/cm³")
                    match = re.match(r'^(\d+(?:\.\d+)?)\s*(.+)$', prop_value)
                    if match:
                        value = float(match.group(1))
                        extracted_unit = match.group(2)
                        # Use extracted unit if it looks valid, otherwise use default
                        if extracted_unit and len(extracted_unit) < 20:  # Reasonable unit length
                            unit = extracted_unit
                        description = f"Material {prop_key}"
                    
                    # Format 2: "range" or simple number (e.g., "4.51", "1200-1800")
                    elif re.match(r'^(\d+(?:\.\d+)?)-?(\d+(?:\.\d+)?)?$', prop_value):
                        match = re.match(r'^(\d+(?:\.\d+)?)-?(\d+(?:\.\d+)?)?$', prop_value)
                        value = float(match.group(1))  # Take first/minimum value
                        description = f"Material {prop_key}"
                    
                    if value is None:
                        print(f"🔍 DEBUG: Failed to parse {prop_key}='{prop_value}' for {material_name}")
                        continue  # Skip unparseable values
                        
                elif isinstance(prop_value, (int, float)):
                    value = prop_value
                    unit = unit_value or std_info["unit"]
                    description = f"Material {prop_key}"
                else:
                    continue  # Skip other formats
                
                # Build the metrics entry
                metrics_data["properties"][prop_key] = {
                    "value": value,
                    "unit": unit,
                    "min": std_info["min"],
                    "max": std_info["max"],
                    "description": description,
                    "priority": std_info["priority"]
                }
        
        # Ensure we have at least some basic parameters
        if not metrics_data["properties"]:
            raise ValueError(f"No valid material properties found for {material_name} - fail-fast requires parseable property data")
        
        # Convert to YAML string
        yaml_content = yaml.dump(metrics_data, default_flow_style=False, sort_keys=False, allow_unicode=True)
        
        return yaml_content

    def _parse_example_yaml(self, example_content: str) -> Dict:
        """Parse example file to extract YAML structure - FAIL-FAST: Must succeed"""
        lines = example_content.strip().split('\n')
        yaml_lines = []
        in_yaml = False
    
        for line in lines:
            if line.strip().startswith('```yaml'):
                in_yaml = True
                continue
            elif line.strip() == '```' and in_yaml:
                break
            elif in_yaml:
                yaml_lines.append(line)
    
        if not yaml_lines:
            raise Exception("No YAML content found in example file - fail-fast architecture requires complete example structure")
        
        try:
            yaml_content = '\n'.join(yaml_lines)
            return yaml.safe_load(yaml_content)
        except Exception as e:
            raise Exception(f"Failed to parse example YAML: {e} - fail-fast architecture requires valid example file")

    def _enhance_with_api(
        self,
        material_name: str,
        material_data: Dict,
        api_client,
        author_info: Optional[Dict],
        frontmatter_data: Dict,
        base_content: str,
    ) -> str:
        """Enhance properties metrics with API-generated content"""
        print(f"\n🔍 DEBUG: Enhancing properties metrics for {material_name} with API")
        
        try:
            data = yaml.safe_load(base_content)
        except Exception as e:
            print(f"⚠️ DEBUG: Failed to parse base properties content: {e}")
            raise Exception(f"Failed to parse base properties content: {e}")
        
        # FAIL-FAST: Category must be present
        if not frontmatter_data.get("category"):
            raise ValueError(f"Category missing from frontmatter for {material_name} - fail-fast requires explicit categorization")
        category = frontmatter_data["category"]
        
        material_name_title = material_name.title()
        
        # Create a detailed prompt for the API to generate enhanced descriptions
        properties = data.get("properties", {})
        properties_list = list(properties.keys())
        
        prompt = f"""Enhance the descriptions for {material_name_title} material properties.
The material category is {category}.
The properties are: {', '.join(properties_list)}

For each property, provide a technical description that explains:
1. What the property measures
2. Why it's important for {category} laser cleaning
3. How it affects processing parameters

Format your response as YAML with keys matching the property names and values being the enhanced descriptions.
Keep descriptions concise but technical (15-30 words each).
"""
        print(f"\n🔍 DEBUG: Sending API prompt for descriptions:\n{prompt}")

        try:
            response = api_client.generate_simple(prompt)
            print(f"🔍 DEBUG: Received API response: {response.content[:100]}..." if hasattr(response, 'content') else "No response content")
            
            if not response or not hasattr(response, 'content') or not response.content.strip():
                print("⚠️ DEBUG: API returned empty response for descriptions")
                return base_content
                
            # Parse the API response
            enhanced_text = response.content.strip()
            
            try:
                enhanced_data = yaml.safe_load(enhanced_text)
                print(f"🔍 DEBUG: Parsed API response as YAML: {enhanced_data}")
                
                if isinstance(enhanced_data, dict):
                    # Update the descriptions in our data
                    for prop_key, prop_data in data.get("properties", {}).items():
                        if prop_key in enhanced_data:
                            prop_data["description"] = enhanced_data[prop_key]
                            
            except Exception as e:
                print(f"⚠️ DEBUG: Failed to parse API response as YAML: {e}")
        
            # Convert back to YAML string
            enhanced_yaml = yaml.dump(data, default_flow_style=False, sort_keys=False, allow_unicode=True)
            
            print("✅ DEBUG: Successfully enhanced properties metrics with API content")
            
            return enhanced_yaml
            
        except Exception as e:
            print(f"⚠️ DEBUG: Error enhancing with API: {e}")
            # If API enhancement fails, return the base content
            return base_content