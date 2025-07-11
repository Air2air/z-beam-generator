#!/usr/bin/env python3
"""
Metadata Generator - Simple, clean metadata generation
"""
import logging
import json
from datetime import datetime
from typing import Dict, Any

logger = logging.getLogger(__name__)

def generate_metadata(material: str, author_id: int, config: Dict, api_client) -> Dict:
    """Generate comprehensive metadata for the article"""
    logger.info(f"📊 Generating metadata for {material} by author ID {author_id}")
    
    # Get author from config (already loaded)
    author = _get_author_from_config(author_id, config)
    
    # Generate material properties
    material_properties = _generate_material_properties(material, api_client)
    
    # Create complete metadata
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
        "generation_timestamp": datetime.now().isoformat(),
        "model_used": f"{config.get('provider', 'unknown')}/{_get_model_from_config(config)}",
        "temperature": config.get("temperature", 0.7),
        
        # Material properties
        **material_properties
    }
    
    logger.info(f"✅ Metadata generated for {material}")
    return metadata

def _get_author_from_config(author_id: int, config: Dict) -> Dict:
    """Get author from already-loaded config"""
    authors = config.get("authors", [])
    
    for author in authors:
        if author.get("id") == author_id:
            logger.info(f"✅ Found author: {author['name']} (ID: {author_id})")
            return author
    
    raise ValueError(f"Author ID {author_id} not found in config")

def _get_model_from_config(config: Dict) -> str:
    """Get model name from config"""
    provider = config.get("provider", "unknown")
    providers = config.get("providers", {})
    
    if provider in providers:
        return providers[provider].get("model", "unknown")
    
    return config.get("model", "unknown")

def _generate_material_properties(material: str, api_client) -> Dict:
    """Generate material properties - simplified"""
    
    prompt = f"""Generate comprehensive material properties for {material}.

Return ONLY a JSON object with these fields:
- atomicNumber, chemicalSymbol, generalClassifier, materialClass
- crystalStructure, density, meltingPoint, thermalConductivity
- reflectivityIr, reflectivityWavelength, hardnessMohs, youngsModulus
- specificHeatCapacity, materialPurity, materialType
- applications (array), safetyConsiderations (array), industryStandards (array)
- environmentalImpact, processingChallenges (array), relatedMaterials (array)
- regulatoryCompliance (array)
- laserCleaningParameters (object), performanceMetrics (object)

Return ONLY valid JSON. No markdown, no explanations."""
    
    result = api_client.call(prompt, "material-properties")
    
    # Simple JSON parsing with basic cleanup
    cleaned = result.strip()
    if cleaned.startswith('```'):
        # Remove any markdown wrapping
        lines = cleaned.split('\n')
        cleaned = '\n'.join(line for line in lines if not line.startswith('```'))
    
    try:
        return json.loads(cleaned)
    except json.JSONDecodeError as e:
        logger.error(f"❌ Invalid JSON response for {material}: {e}")
        logger.error(f"❌ Response: {result}")
        raise RuntimeError(f"Material properties generation failed for {material}")

def format_metadata_as_yaml(metadata: Dict) -> str:
    """Simple YAML formatting"""
    import yaml
    
    try:
        return yaml.dump(metadata, default_flow_style=False, allow_unicode=True)
    except Exception as e:
        logger.error(f"❌ YAML formatting failed: {e}")
        raise RuntimeError(f"YAML formatting failed: {e}")