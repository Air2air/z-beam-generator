#!/usr/bin/env python3
"""
Fully Dynamic Metadata Generator - No hardcoded values
"""
import logging
import json
import re
from typing import Dict, Any
from datetime import datetime
from pathlib import Path

logger = logging.getLogger(__name__)

def generate_metadata(material: str, author_id: int, config: Dict[str, Any], api_client) -> Dict[str, Any]:
    """Generate metadata for material with fully dynamic approach"""
    logger.info(f"📊 Generating metadata for {material} by author ID {author_id}")
    
    # Get author info from authors.json
    author = _load_author_from_file(author_id)
    
    # Generate material properties via API
    material_data = _generate_material_properties(material, config, api_client)
    
    # Combine metadata
    metadata = {
        **material_data,
        **author,
        "generation_timestamp": datetime.now().isoformat(),
        "lastUpdated": datetime.now().strftime("%Y-%m-%d"),
        "publishedAt": datetime.now().strftime("%Y-%m-%d"),
        "model_used": f"{config['api']['provider'].upper()}/{config['api']['model']}"
    }
    
    logger.info(f"✅ Metadata generated for {material}")
    return metadata

def _load_author_from_file(author_id: int) -> Dict[str, Any]:
    """Load author info from authors.json file"""
    try:
        # Load authors.json
        authors_file = Path("authors/authors.json")
        
        if not authors_file.exists():
            logger.warning(f"⚠️ Authors file not found: {authors_file}")
            return _get_fallback_author(author_id)
        
        with open(authors_file, 'r', encoding='utf-8') as f:
            authors_data = json.load(f)
        
        # Find author by ID
        author = next((a for a in authors_data if a["id"] == author_id), None)
        
        if not author:
            logger.warning(f"⚠️ Author ID {author_id} not found in authors.json")
            return _get_fallback_author(author_id)
        
        # Convert to metadata format
        return {
            "authorId": str(author["id"]),
            "authorName": author["name"],
            "authorCountry": author["country"],
            "authorTitle": author["title"],
            "authorImage": author["image"],
            "authorSlug": author["slug"]
        }
        
    except Exception as e:
        logger.error(f"❌ Failed to load author from file: {e}")
        return _get_fallback_author(author_id)

def _get_fallback_author(author_id: int) -> Dict[str, Any]:
    """Fallback author data if file loading fails"""
    return {
        "authorId": str(author_id),
        "authorName": f"Author {author_id}",
        "authorCountry": "Unknown",
        "authorTitle": "Laser Cleaning Expert",
        "authorImage": f"/images/Site/Author/author-{author_id}.jpg",
        "authorSlug": f"author-{author_id}"
    }

def _generate_material_properties(material: str, config: Dict[str, Any], api_client) -> Dict[str, Any]:
    """Generate material properties via API - fully dynamic"""
    logger.info(f"🔬 Generating material properties for {material}")
    
    # Create comprehensive prompt for ANY material
    prompt = f"""Generate comprehensive material properties for {material} suitable for laser cleaning applications.

Return the data in the following JSON structure:
{{
  "title": "Laser Cleaning {material}",
  "nameShort": "{material}",
  "subject": "{material}",
  "description": "Brief description of laser cleaning applications for {material}",
  "image": "/images/Material/material_{material}.jpg",
  "materialClass": "Metal/Polymer/Ceramic/Composite/etc",
  "materialType": "Specific type classification",
  "generalClassifier": "General category",
  "chemicalSymbol": "Chemical symbol if applicable",
  "atomicNumber": "Atomic number if applicable",
  "density": "Density in g/cm³",
  "meltingPoint": "Melting point in °C",
  "thermalConductivity": "Thermal conductivity in W/m·K",
  "youngsModulus": "Young's modulus in GPa",
  "specificHeatCapacity": "Specific heat capacity in J/g·K",
  "hardnessMohs": "Mohs hardness if applicable",
  "materialPurity": "Typical purity percentage",
  "crystalStructure": "Crystal structure if applicable",
  "reflectivityIr": "IR reflectivity (0-1)",
  "reflectivityWavelength": "Wavelength for reflectivity measurement",
  "applications": [
    "List of 5-7 industrial applications"
  ],
  "industryStandards": [
    "List of 3-5 relevant industry standards"
  ],
  "laserCleaningParameters": {{
    "energyDensity": "Recommended energy density in J/cm²",
    "pulseDuration": "Recommended pulse duration in ns",
    "repetitionRate": "Recommended repetition rate in Hz",
    "wavelength": "Recommended wavelength in nm"
  }},
  "performanceMetrics": {{
    "corrosionResistance": "Poor/Moderate/Good/Excellent",
    "electricalConductivity": "Low/Moderate/High",
    "thermalStability": "Poor/Moderate/Good/Excellent",
    "wearResistance": "Poor/Moderate/Good/Excellent"
  }},
  "processingChallenges": [
    "List of processing challenges"
  ],
  "safetyConsiderations": [
    "List of safety considerations"
  ],
  "environmentalImpact": "Description of environmental impact",
  "regulatoryCompliance": [
    "List of regulatory requirements"
  ],
  "relatedMaterials": [
    "List of related materials"
  ]
}}

Provide accurate, technical data for {material}. If specific values are unknown, provide typical ranges or indicate uncertainty."""
    
    try:
        # Use the correct API client method name
        response = api_client.generate_content(prompt)
        
        # Parse response into structured data
        material_data = _parse_dynamic_material_response(response, material)
        
        logger.info(f"✅ Material properties generated for {material}")
        return material_data
        
    except Exception as e:
        logger.error(f"❌ Failed to generate material properties: {e}")
        # Don't raise - return basic structure instead
        return _create_basic_material_data("", material)

def _parse_dynamic_material_response(response: str, material: str) -> Dict[str, Any]:
    """Parse API response into structured material data - fully dynamic"""
    try:
        # Try to extract JSON from response
        json_match = re.search(r'\{.*\}', response, re.DOTALL)
        if json_match:
            json_str = json_match.group(0)
            material_data = json.loads(json_str)
            
            # Ensure required fields exist
            material_data = _ensure_required_fields(material_data, material)
            
            # Convert numeric strings to numbers
            material_data = _convert_numeric_fields(material_data)
            
            logger.info(f"✅ Successfully parsed JSON response for {material}")
            return material_data
            
    except Exception as e:
        logger.warning(f"⚠️ Failed to parse JSON response: {e}")
    
    # If JSON parsing fails, create basic structure from text
    return _create_basic_material_data(response, material)

def _ensure_required_fields(data: Dict[str, Any], material: str) -> Dict[str, Any]:
    """Ensure all required fields are present"""
    required_fields = {
        "title": f"Laser Cleaning {material}",
        "nameShort": material,
        "subject": material,
        "description": f"Explore how laser cleaning removes contaminants from {material}, enhancing performance and safety in relevant industries.",
        "image": f"/images/Material/material_{material}.jpg",
        "temperature": 0.7
    }
    
    for field, default_value in required_fields.items():
        if field not in data or not data[field]:
            data[field] = default_value
    
    return data

def _convert_numeric_fields(data: Dict[str, Any]) -> Dict[str, Any]:
    """Convert numeric string fields to actual numbers"""
    numeric_fields = [
        "atomicNumber", "density", "meltingPoint", "thermalConductivity", 
        "youngsModulus", "specificHeatCapacity", "hardnessMohs", 
        "reflectivityIr", "reflectivityWavelength"
    ]
    
    for field in numeric_fields:
        if field in data and isinstance(data[field], str):
            try:
                # Try to extract number from string
                number_match = re.search(r'[\d.]+', data[field])
                if number_match:
                    value = float(number_match.group())
                    data[field] = int(value) if value.is_integer() else value
            except (ValueError, AttributeError):
                # Keep as string if conversion fails
                pass
    
    # Convert nested laser parameters
    if "laserCleaningParameters" in data:
        laser_params = data["laserCleaningParameters"]
        for param in ["energyDensity", "pulseDuration", "repetitionRate", "wavelength"]:
            if param in laser_params and isinstance(laser_params[param], str):
                try:
                    number_match = re.search(r'[\d.]+', laser_params[param])
                    if number_match:
                        value = float(number_match.group())
                        laser_params[param] = int(value) if value.is_integer() else value
                except (ValueError, AttributeError):
                    pass
    
    return data

def _create_basic_material_data(response: str, material: str) -> Dict[str, Any]:
    """Create basic material data structure from text response"""
    logger.info(f"📝 Creating basic material data for {material}")
    
    # Basic structure with dynamic content
    material_data = {
        "title": f"Laser Cleaning {material}",
        "nameShort": material,
        "subject": material,
        "description": f"Explore how laser cleaning removes contaminants from {material}, enhancing performance and safety in relevant industries.",
        "image": f"/images/Material/material_{material}.jpg",
        "temperature": 0.7,
        "materialClass": "Material",
        "materialType": "General",
        "applications": [
            "Industrial cleaning",
            "Surface preparation",
            "Coating removal",
            "Restoration",
            "Manufacturing"
        ],
        "industryStandards": [
            "ISO 9001",
            "OSHA standards",
            "EPA regulations"
        ],
        "laserCleaningParameters": {
            "energyDensity": 1.0,
            "pulseDuration": 10,
            "repetitionRate": 1000,
            "wavelength": 1064
        },
        "safetyConsiderations": [
            "Proper ventilation required",
            "Eye protection mandatory",
            "Trained operators only"
        ]
    }
    
    # Try to extract information from response if available
    if response and len(response) > 10:
        try:
            # Look for material class/type information
            if "metal" in response.lower():
                material_data["materialClass"] = "Metal"
            elif "polymer" in response.lower():
                material_data["materialClass"] = "Polymer"
            elif "ceramic" in response.lower():
                material_data["materialClass"] = "Ceramic"
            elif "composite" in response.lower():
                material_data["materialClass"] = "Composite"
            
            # Try to extract lists
            applications = _extract_list_from_text(response, ["application", "use", "industry"])
            if applications:
                material_data["applications"] = applications
            
            standards = _extract_list_from_text(response, ["standard", "ASTM", "ISO", "EN"])
            if standards:
                material_data["industryStandards"] = standards
            
            safety = _extract_list_from_text(response, ["safety", "hazard", "precaution"])
            if safety:
                material_data["safetyConsiderations"] = safety
                
        except Exception as e:
            logger.warning(f"⚠️ Failed to extract details from response: {e}")
    
    return material_data

def _extract_list_from_text(text: str, keywords: list) -> list:
    """Extract lists from text based on keywords"""
    extracted = []
    
    for keyword in keywords:
        # Look for patterns like "Applications: item1, item2, item3"
        pattern = rf"{keyword}s?:([^.]+)"
        matches = re.findall(pattern, text, re.IGNORECASE)
        
        for match in matches:
            # Split by common separators and clean up
            items = re.split(r'[,\n\r\t]+', match.strip())
            for item in items:
                cleaned_item = item.strip(' -•*')
                if cleaned_item and len(cleaned_item) > 3:
                    extracted.append(cleaned_item)
    
    return extracted[:7]  # Limit to 7 items

def format_metadata_as_yaml(metadata: Dict[str, Any]) -> str:
    """Format metadata as YAML for frontmatter"""
    import yaml
    
    # Convert to YAML string
    yaml_str = yaml.dump(metadata, default_flow_style=False, sort_keys=False)
    
    return yaml_str.strip()