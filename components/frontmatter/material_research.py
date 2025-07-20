"""Material research submodule for dynamic material information retrieval."""

import logging
import json
import re
import os
import hashlib
import time
from typing import Dict, Any, List, Optional

# Update this import
from api import get_client

logger = logging.getLogger(__name__)

class MaterialResearcher:
    """Dynamically researches material properties and composition using AI."""
    
    def __init__(self, ai_provider: str):
        """Initialize with AI provider for research."""
        self.ai_provider = ai_provider
        # Update this line to use the new get_client function
        self.api_client = get_client(ai_provider)
        
    def research_material(self, material_name: str, schema: Dict[str, Any]) -> Dict[str, Any]:
        """Research material properties and composition based on schema requirements."""
        logger.info(f"Researching material information for: {material_name} using {self.ai_provider}")
        
        try:
            # Extract research config from schema
            research_config = schema.get("materialProfile", {}).get("generatorConfig", {}).get("research", {})
            required_fields = research_config.get("fields", ["properties", "composition", "compatibility"])
            
            # Build AI research prompt
            research_prompt = self._build_research_prompt(material_name, required_fields, schema)
            
            # Generate structured data using AI
            output_schema = self._build_output_schema(schema, research_config)
            structured_prompt = self._build_structured_prompt(research_prompt, output_schema)
            
            # Call AI API
            response = self.api_client.generate(structured_prompt)
            
            # Extract and parse JSON from response
            material_data = self._extract_json_data(response)
            
            # Normalize and validate data against schema
            material_data = self._normalize_data(material_data, schema)
            
            return material_data
            
        except Exception as e:
            logger.error(f"Error during material research: {str(e)}", exc_info=True)
            return self._generate_fallback_data(material_name)
    
    def _build_research_prompt(self, material_name: str, required_fields: List[str], schema: Dict[str, Any]) -> str:
        """Build AI research prompt based on schema and required fields."""
        prompt = f"""You are a materials science expert specializing in laser cleaning technology. 
Research and provide accurate scientific information about {material_name}.

Return the following information structured as JSON:

1. Properties: Include these physical and chemical properties with correct units:
   - Density (kg/m³)
   - Hardness (e.g., Janka hardness for wood, Mohs for minerals)
   - Thermal conductivity (W/m·K)
   - Melting/ignition point or temperature resistance (°C)
   - Porosity/permeability (if applicable)
   - Reflectivity/absorptivity for common laser wavelengths
   - Moisture content (for organic materials)
   - Elasticity/Young's modulus (GPa)
   Include any other properties specifically relevant to {material_name} for laser cleaning.

2. Composition: The correct chemical or structural composition with percentages.
   - For metals: Include main element percentages and alloy components.
   - For wood: Include structural components like cellulose, lignin, etc.
   - For stone/ceramics: Include mineral components.
   - For plastics: Include polymer base and additives.

3. Compatibility: List materials and processes compatible with {material_name}.

4. Regulatory Standards: Relevant industry standards for {material_name}.

5. LaserParameters: Recommended laser parameters for cleaning this material:
   - Wavelength ranges (nm)
   - Pulse duration ranges (ns, ps, or fs)
   - Energy density thresholds (J/cm²)
   - Recommended scanning speed

6. EnvironmentalConsiderations: Information about:
   - Sustainability aspects
   - Recycling potential
   - Environmental impact of processing
   - Hazardous byproducts during laser cleaning

The information should be scientifically accurate and include appropriate units where applicable.
Format your response as a valid JSON object only, with no explanation or other text."""

        return prompt
    
    def _build_output_schema(self, schema: Dict[str, Any], research_config: Dict[str, Any]) -> Dict[str, Any]:
        """Build schema for structured output from AI."""
        # Default output schema structure
        output_schema = {
            "type": "object",
            "properties": {
                "properties": {
                    "type": "object",
                    "description": "Physical and chemical properties of the material"
                },
                "composition": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "component": {
                                "type": "string",
                                "description": "Component name (element, compound, or structural component)"
                            },
                            "percentage": {
                                "type": "string",
                                "description": "Percentage or proportion as a string with unit"
                            },
                            "type": {
                                "type": "string",
                                "description": "Type of component (element, compound, structural)"
                            }
                        }
                    },
                    "description": "Chemical or structural composition of the material"
                },
                "compatibility": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "material": {
                                "type": "string",
                                "description": "Compatible material or process"
                            },
                            "application": {
                                "type": "string",
                                "description": "Application or use case"
                            }
                        }
                    },
                    "description": "Materials and processes compatible with this material"
                },
                "regulatoryStandards": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "code": {
                                "type": "string",
                                "description": "Standard code or identifier"
                            },
                            "description": {
                                "type": "string",
                                "description": "Description of the standard"
                            }
                        }
                    },
                    "description": "Relevant industry standards for this material"
                },
                "laserParameters": {
                    "type": "object",
                    "properties": {
                        "wavelength": {
                            "type": "string",
                            "description": "Recommended laser wavelength ranges in nm"
                        },
                        "pulseDuration": {
                            "type": "string",
                            "description": "Recommended pulse duration ranges (ns, ps, fs)"
                        },
                        "energyDensity": {
                            "type": "string",
                            "description": "Recommended energy density in J/cm²"
                        },
                        "scanningSpeed": {
                            "type": "string",
                            "description": "Recommended scanning speed"
                        }
                    },
                    "description": "Recommended laser parameters for cleaning this material"
                },
                "environmentalConsiderations": {
                    "type": "object",
                    "properties": {
                        "sustainability": {
                            "type": "string",
                            "description": "Sustainability aspects of the material"
                        },
                        "recyclingPotential": {
                            "type": "string",
                            "description": "Potential for recycling the material"
                        },
                        "processingImpact": {
                            "type": "string",
                            "description": "Environmental impact of processing"
                        },
                        "hazardousByproducts": {
                            "type": "string",
                            "description": "Hazardous byproducts during laser cleaning"
                        }
                    },
                    "description": "Environmental considerations for this material"
                }
            }
        }
        
        # Check if material schema has specific field definitions to use
        material_profile = schema.get("materialProfile", {}).get("profile", {})
        if "properties" in material_profile:
            # Use schema-defined property structure if available
            properties_schema = material_profile.get("properties", {}).get("properties", {})
            if properties_schema:
                output_schema["properties"]["properties"]["properties"] = properties_schema
                
        if "composition" in material_profile:
            # Use schema-defined composition structure if available
            composition_schema = material_profile.get("composition", {}).get("items", {}).get("properties", {})
            if composition_schema:
                output_schema["properties"]["composition"]["items"]["properties"] = composition_schema
        
        return output_schema
    
    def _build_structured_prompt(self, research_prompt: str, output_schema: Dict[str, Any]) -> str:
        """Create a prompt that requests structured output following the schema."""
        schema_json = json.dumps(output_schema, indent=2)
        
        structured_prompt = f"""{research_prompt}

Please format your response as a valid JSON object that follows this schema:

```json
{schema_json}
```
"""

        return structured_prompt

    def _extract_json_data(self, response: str) -> Dict[str, Any]:
        """Extract JSON data from AI response."""
        try:
            # Try to extract JSON from markdown code block
            json_match = re.search(r'```(?:json)?\n(.*?)\n```', response, re.DOTALL)
            if json_match:
                json_str = json_match.group(1)
                return json.loads(json_str)
            
            # Try to extract JSON with alternative code block format
            json_match = re.search(r'```(?:json)?(.+?)```', response, re.DOTALL)
            if json_match:
                json_str = json_match.group(1).strip()
                return json.loads(json_str)
                
            # Try to parse the entire response as JSON
            return json.loads(response)
            
        except json.JSONDecodeError as e:
            logger.error(f"Could not parse JSON from response: {str(e)}")
            logger.debug(f"Response snippet: {response[:200]}...")
            # Return empty dictionary if parsing fails
            return {}

    def _normalize_data(self, material_data: Dict[str, Any], schema: Dict[str, Any]) -> Dict[str, Any]:
        """Normalize and validate researched data against schema."""
        normalized_data = {}
        
        # Normalize properties
        if "properties" in material_data and isinstance(material_data["properties"], dict):
            normalized_data["properties"] = material_data["properties"]
        
        # Normalize composition
        if "composition" in material_data and isinstance(material_data["composition"], list):
            normalized_data["composition"] = []
            for item in material_data["composition"]:
                if isinstance(item, dict) and "component" in item:
                    normalized_component = {
                        "component": item["component"],
                        "percentage": item.get("percentage", "Unknown")
                    }
                    if "type" in item:
                        normalized_component["type"] = item["type"]
                    normalized_data["composition"].append(normalized_component)
                
        # Normalize compatibility
        if "compatibility" in material_data and isinstance(material_data["compatibility"], list):
            normalized_data["compatibility"] = material_data["compatibility"]
        
        # Normalize regulatory standards
        if "regulatoryStandards" in material_data and isinstance(material_data["regulatoryStandards"], list):
            normalized_data["regulatoryStandards"] = material_data["regulatoryStandards"]

        # Normalize laser parameters
        if "laserParameters" in material_data and isinstance(material_data["laserParameters"], dict):
            normalized_data["laserParameters"] = material_data["laserParameters"]
    
        # Normalize environmental considerations
        if "environmentalConsiderations" in material_data and isinstance(material_data["environmentalConsiderations"], dict):
            normalized_data["environmentalConsiderations"] = material_data["environmentalConsiderations"]
        
        # If no data was successfully extracted, log warning
        if not normalized_data:
            logger.warning(f"No valid material data could be extracted from AI response")
        
        return normalized_data

    def _normalize_properties(self, properties_data: Dict[str, Any], properties_schema: Dict[str, Any]) -> Dict[str, Any]:
        """Normalize properties data according to the schema."""
        normalized_properties = {}
        for prop_name, prop_value in properties_data.items():
            if prop_name in properties_schema:
                prop_type = properties_schema[prop_name].get("type")
                if prop_type == "number":
                    normalized_properties[prop_name] = float(prop_value)
                elif prop_type == "integer":
                    normalized_properties[prop_name] = int(prop_value)
                else:
                    normalized_properties[prop_name] = prop_value
        return normalized_properties

    def _normalize_composition(self, composition_data: List[Dict[str, Any]], composition_schema: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Normalize composition data according to the schema."""
        normalized_composition = []
        for component in composition_data:
            normalized_component = {}
            for comp_key, comp_value in component.items():
                if comp_key in composition_schema:
                    comp_type = composition_schema[comp_key].get("type")
                    if comp_type == "number":
                        normalized_component[comp_key] = float(comp_value)
                    elif comp_type == "integer":
                        normalized_component[comp_key] = int(comp_value)
                    else:
                        normalized_component[comp_key] = comp_value
            normalized_composition.append(normalized_component)
        return normalized_composition

    def _normalize_compatibility(self, compatibility_data: List[Dict[str, Any]], compatibility_schema: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Normalize compatibility data according to the schema."""
        normalized_compatibility = []
        for compat_item in compatibility_data:
            normalized_item = {}
            for compat_key, compat_value in compat_item.items():
                if compat_key in compatibility_schema:
                    compat_type = compatibility_schema[compat_key].get("type")
                    if compat_type == "number":
                        normalized_item[compat_key] = float(compat_value)
                    elif compat_type == "integer":
                        normalized_item[compat_key] = int(compat_value)
                    else:
                        normalized_item[compat_key] = compat_value
            normalized_compatibility.append(normalized_item)
        return normalized_compatibility

    def _generate_fallback_data(self, material_name: str) -> Dict[str, Any]:
        """Generate fallback data in case of research failure."""
        logger.warning(f"Using fallback data for material: {material_name}")
        return {
            "properties": {},
            "composition": [],
            "compatibility": [],
            "regulatoryStandards": []
        }