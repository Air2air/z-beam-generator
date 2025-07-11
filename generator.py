#!/usr/bin/env python3
"""
Pure Schema-Driven Generator - Zero fallbacks, zero hardcoded values
"""
import logging
import json
from typing import Dict, Any
from pathlib import Path

logger = logging.getLogger(__name__)

def generate_article(context: Dict[str, Any], config: Dict[str, Any]) -> str:
    """Generate article - pure schema-driven, no fallbacks"""
    logger.info("🚀 Generating schema-driven article...")
    
    # Get schema for article type
    schema = _get_schema(context["article_type"])
    
    # Generate metadata using schema
    metadata = _generate_metadata(context, config, schema)
    
    # Generate tags using schema
    tags = _generate_tags_from_schema(schema, metadata)
    
    # Generate JSON-LD using schema
    jsonld = _generate_jsonld_from_schema(schema, metadata)
    
    # Create article using schema
    article = _create_article_from_schema(schema, metadata, tags, jsonld)
    
    # Save article
    output_file = _save_article(context, article)
    
    logger.info(f"✅ Schema-driven article generated: {output_file}")
    return output_file

def _get_schema(article_type: str):
    """Get schema - no fallbacks"""
    if article_type == "material":
        from schemas.material_schema import MaterialSchema
        return MaterialSchema()
    elif article_type == "application":
        from schemas.application_schema import ApplicationSchema
        return ApplicationSchema()
    elif article_type == "region":
        from schemas.region_schema import RegionSchema
        return RegionSchema()
    elif article_type == "thesaurus":
        from schemas.thesaurus_schema import ThesaurusSchema
        return ThesaurusSchema()
    else:
        raise ValueError(f"Unsupported article type: {article_type}")

def _generate_metadata(context: Dict[str, Any], config: Dict[str, Any], schema) -> Dict[str, Any]:
    """Generate metadata - enhanced by schema"""
    from api_client import APIClient
    from metadata.metadata_generator import generate_metadata
    
    # Get material requirement from schema
    material = schema.get_material_requirement(context)
    
    # Generate base metadata
    api_client = APIClient(config)
    metadata = generate_metadata(material, context.get("author_id", 1), config, api_client)
    
    # Enhance metadata with schema context
    metadata = schema.enhance_metadata(metadata, context)
    
    return metadata

def _generate_tags_from_schema(schema, metadata: Dict[str, Any]) -> list:
    """Generate tags purely from schema - no hardcoded values"""
    return schema.generate_tags(metadata)

def _generate_jsonld_from_schema(schema, metadata: Dict[str, Any]) -> Dict[str, Any]:
    """Generate JSON-LD purely from schema - no hardcoded values"""
    return schema.generate_jsonld(metadata)

def _create_article_from_schema(schema, metadata: Dict[str, Any], tags: list, jsonld: Dict[str, Any]) -> str:
    """Create article structure from schema"""
    from metadata.metadata_generator import format_metadata_as_yaml
    
    # Get article template from schema
    template = schema.get_article_template()
    
    # Format components
    metadata_yaml = format_metadata_as_yaml(metadata)
    formatted_tags = schema.format_tags(tags)
    formatted_jsonld = f"```json\n{json.dumps(jsonld, indent=2)}\n```"
    
    # Get title from schema
    title = schema.generate_title(metadata)
    
    # Populate template
    return template.format(
        metadata_yaml=metadata_yaml,
        formatted_tags=formatted_tags,
        formatted_jsonld=formatted_jsonld,
        title=title,
        article_type=metadata.get("articleType", ""),
        subject=metadata.get("subject", "")
    )

def _save_article(context: Dict[str, Any], article: str) -> str:
    """Save article - filename from schema"""
    schema = _get_schema(context["article_type"])
    filename = schema.generate_filename(context)
    
    output_dir = Path("output")
    output_dir.mkdir(exist_ok=True)
    
    output_file = output_dir / filename
    
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(article)
    
    return str(output_file)

if __name__ == "__main__":
    from run import context, config
    
    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler(f'logs/generation_{context["article_type"]}_{context["subject"]}.log')
        ]
    )
    
    try:
        output_file = generate_article(context, config)
        print(f"✅ Article structure generated: {output_file}")
    except Exception as e:
        logger.error(f"❌ Generation failed: {e}")
        raise