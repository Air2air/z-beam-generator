#!/usr/bin/env python3
"""
Metadata Generator - Generates structured metadata without tags
"""
import logging
import json
from datetime import datetime
from pathlib import Path
from typing import Dict

logger = logging.getLogger(__name__)

def generate_metadata(material: str, author_id: int, config: Dict, api_client) -> Dict:
    """Generate comprehensive metadata for the article"""
    logger.info(f"📊 Generating metadata for {material} by author ID {author_id}")
    
    # Load authors data
    authors_data = _load_authors_data(config)
    
    # Find author
    author = _get_author_data(author_id, authors_data)
    
    # Generate material properties
    material_properties = _generate_material_properties(material, api_client)
    
    # Create metadata with optimization method
    metadata = {
        # Article metadata
        "title": f"Laser Cleaning {material}",
        "articleType": "material",
        "nameShort": material,
        "description": f"Explore how laser cleaning removes contaminants from {material}, enhancing performance and safety in relevant industries such as Aerospace, Construction, Restoration, Manufacturing, or others.",
        "publishedAt": datetime.now().strftime("%Y-%m-%d"),
        "authorId": str(author_id),
        "authorName": author["name"],
        "authorSlug": author["slug"],
        "authorImage": author["image"],
        "authorTitle": author["title"],
        "authorCountry": author["country"],
        "lastUpdated": datetime.now().strftime("%Y-%m-%d"),
        "image": f"/images/Material/material_{material}.jpg",
        
        # Processing metadata
        "optimization_method": config.get("optimization_method", "unknown"),
        "generation_timestamp": datetime.now().isoformat(),
        "model_used": f"{config.get('provider', 'unknown')}/{config.get('model', 'unknown')}",
        "temperature": config.get("temperature", 0.3),
        
        # Material properties
        **material_properties
    }
    
    logger.info(f"✅ Metadata generated for {material}")
    logger.info(f"🔧 Using optimization method: {metadata['optimization_method']}")
    logger.info(f"🤖 Model: {metadata['model_used']}")
    
    return metadata

def _load_authors_data(config: Dict) -> list:
    """Load authors data from JSON file"""
    authors_file = Path(config.get("authors_file", "prompts/authors/authors.json"))
    
    if not authors_file.exists():
        raise FileNotFoundError(f"Authors file not found: {authors_file}")
    
    try:
        with open(authors_file, 'r', encoding='utf-8') as f:
            authors = json.load(f)
        
        if not authors:
            raise ValueError("Authors file is empty")
            
        logger.info(f"✅ Loaded {len(authors)} authors from {authors_file}")
        return authors
        
    except json.JSONDecodeError as e:
        raise RuntimeError(f"Failed to parse authors JSON: {e}")
    except Exception as e:
        raise RuntimeError(f"Failed to load authors file: {e}")

def _get_author_data(author_id: int, authors_data: list) -> Dict:
    """Get author data by ID"""
    # Find author by ID
    for author in authors_data:
        if author.get("id") == author_id:
            # Validate required author fields
            required_fields = ["name", "slug", "image", "title", "country"]
            missing_fields = [field for field in required_fields if not author.get(field)]
            
            if missing_fields:
                raise ValueError(f"Author {author_id} missing required fields: {missing_fields}")
            
            logger.info(f"✅ Found author: {author['name']} (ID: {author_id})")
            return author
    
    raise ValueError(f"Author ID {author_id} not found in authors database")

def _generate_material_properties(material: str, api_client) -> Dict:
    """Generate material properties via AI prompt"""
    logger.info(f"🔬 Generating material properties for {material}")
    
    prompt = f"""Generate comprehensive material properties for {material} in JSON format. 

CRITICAL: Return valid JSON with proper data types:
- Arrays must be actual JSON arrays: ["item1", "item2"] NOT string representations
- Objects must be actual JSON objects: {{"key": "value"}} NOT string representations
- Do not wrap arrays or objects in quotes

Required fields with exact data types:

- atomicNumber: string or null
- chemicalSymbol: string or null  
- generalClassifier: string ("metal", "ceramic", "polymer", "composite")
- materialClass: string (e.g., "Transition Metal", "Thermoplastic")
- crystalStructure: string
- density: string with units
- meltingPoint: string with units
- thermalConductivity: string with units
- reflectivityIr: string percentage
- reflectivityWavelength: string (default "10.6 µm")
- hardnessMohs: string or number
- youngsModulus: string with units
- specificHeatCapacity: string with units
- materialPurity: string percentage
- materialType: "{material}"
- applications: ARRAY of 3-4 strings (NOT a string)
- safetyConsiderations: ARRAY of 3-4 strings (NOT a string)
- industryStandards: ARRAY of 2-3 strings (NOT a string)
- environmentalImpact: string description
- processingChallenges: ARRAY of 2-3 strings (NOT a string)
- relatedMaterials: ARRAY of 3-4 strings (NOT a string)
- regulatoryCompliance: ARRAY of 2-3 strings (NOT a string)
- laserCleaningParameters: OBJECT with keys: wavelength, pulseDuration, powerDensity, pulseFrequency, scanningSpeed, spotSize, fluence, pulsesPerSpot, beamProfile, ambientConditions (NOT a string)
- performanceMetrics: OBJECT with keys: contaminantRemovalEfficiency, surfaceRoughnessReduction, processingTime (NOT a string)

Example format:
{{
  "applications": ["Aerospace structures", "Medical implants", "Automotive parts"],
  "safetyConsiderations": ["Avoid dust inhalation", "Use eye protection", "Ensure ventilation"],
  "laserCleaningParameters": {{
    "wavelength": "1064 nm",
    "pulseDuration": "100 ns",
    "powerDensity": "5 kW/cm²"
  }}
}}

Output ONLY valid JSON. Use realistic, technically accurate values."""

    try:
        response = api_client.call(prompt, "material-properties")
        
        # Clean response
        if response.startswith('```json'):
            response = response[7:-3]
        elif response.startswith('```'):
            response = response[3:-3]
        
        material_data = json.loads(response)
        
        # Validate and convert string arrays/objects if needed
        material_data = _fix_data_types(material_data)
        
        # Validate required fields are present
        required_fields = [
            "atomicNumber", "chemicalSymbol", "generalClassifier", "materialClass",
            "crystalStructure", "density", "meltingPoint", "thermalConductivity",
            "reflectivityIr", "reflectivityWavelength", "hardnessMohs", "youngsModulus",
            "specificHeatCapacity", "materialPurity", "materialType", "applications",
            "safetyConsiderations", "industryStandards", "environmentalImpact",
            "processingChallenges", "relatedMaterials", "regulatoryCompliance",
            "laserCleaningParameters", "performanceMetrics"
        ]
        
        missing_fields = [field for field in required_fields if field not in material_data]
        if missing_fields:
            raise ValueError(f"Missing required fields in material data: {missing_fields}")
        
        logger.info(f"✅ Material properties generated for {material}")
        return material_data
        
    except json.JSONDecodeError as e:
        logger.error(f"❌ Failed to parse material properties JSON: {e}")
        raise RuntimeError(f"Failed to generate valid material properties JSON for {material}: {e}")
    except Exception as e:
        logger.error(f"❌ Failed to generate material properties: {e}")
        raise RuntimeError(f"Failed to generate material properties for {material}: {e}")

def _fix_data_types(material_data):
    """Fix data types if AI returned strings instead of arrays/objects"""
    import ast
    
    # Fields that should be arrays
    array_fields = ["applications", "safetyConsiderations", "industryStandards", "processingChallenges", "relatedMaterials", "regulatoryCompliance"]
    
    # Fields that should be objects
    object_fields = ["laserCleaningParameters", "performanceMetrics"]
    
    # Fix arrays
    for field in array_fields:
        if field in material_data and isinstance(material_data[field], str):
            try:
                # Try to parse string representation of array
                material_data[field] = ast.literal_eval(material_data[field])
                logger.warning(f"⚠️ Converted string to array for field: {field}")
            except (ValueError, SyntaxError):
                logger.error(f"❌ Failed to convert string to array for field: {field}")
                raise ValueError(f"Invalid array format for field: {field}")
    
    # Fix objects
    for field in object_fields:
        if field in material_data and isinstance(material_data[field], str):
            try:
                # Try to parse string representation of object
                material_data[field] = ast.literal_eval(material_data[field])
                logger.warning(f"⚠️ Converted string to object for field: {field}")
            except (ValueError, SyntaxError):
                logger.error(f"❌ Failed to convert string to object for field: {field}")
                raise ValueError(f"Invalid object format for field: {field}")
    
    return material_data