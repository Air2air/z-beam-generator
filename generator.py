#!/usr/bin/env python3
"""
Generator - Updated for fully dynamic components
"""
import logging
from typing import Dict, Any
from pathlib import Path

logger = logging.getLogger(__name__)

def _get_tag_generator(article_type: str, config: Dict[str, Any], api_client):
    """Get dynamic tag generator - no rules required"""
    from tags.dynamic_tag_generator import DynamicTagGenerator
    
    return DynamicTagGenerator(api_client, config)

def _get_jsonld_generator(config: Dict[str, Any], api_client):
    """Get dynamic JSON-LD generator - no rules required"""
    from jsonld.dynamic_jsonld_generator import DynamicJSONLDGenerator
    
    return DynamicJSONLDGenerator(api_client, config)

def generate_article(context: Dict[str, Any], config: Dict[str, Any]) -> str:
    """Generate article with fully dynamic components"""
    logger.info("🚀 Generating article...")
    
    # Get schema
    schema = _get_schema(context["article_type"])
    
    # Get schema fields for metadata generation
    schema_fields = _get_schema_fields(schema, context)
    
    # Generate metadata with schema context
    metadata = _generate_metadata(context, config, schema_fields)
    
    # Let schema enhance metadata with additional fields
    metadata = schema.enhance_metadata(metadata, context)
    
    # Create API client for dynamic generation
    from api_client import APIClient
    api_client = APIClient(config)
    
    # Create fully dynamic generators - no rules required
    tag_generator = _get_tag_generator(context["article_type"], config, api_client)
    jsonld_generator = _get_jsonld_generator(config, api_client)
    
    # Generate components
    tags = tag_generator.generate_tags(metadata)
    jsonld = jsonld_generator.generate_jsonld(metadata)
    
    # Create article
    article = _create_article(schema, metadata, tags, jsonld, tag_generator, jsonld_generator)
    
    # Save article
    output_file = _save_article(schema, context, article)
    
    logger.info(f"✅ Article generated: {output_file}")
    return output_file

def _get_schema_fields(schema, context: Dict[str, Any]) -> Dict[str, Any]:
    """Get schema fields for metadata generation"""
    schema_fields = {"articleType": schema.schema_type}
    
    if hasattr(schema, 'prompt_config') and schema.prompt_config:
        metadata_fields = schema.prompt_config.get("metadataFields", {})
        
        for field_name, field_config in metadata_fields.items():
            if isinstance(field_config, dict):
                if "default" in field_config:
                    schema_fields[field_name] = field_config["default"]
                elif field_config.get("useSubject", False):
                    schema_fields[field_name] = context["subject"]
                elif field_config.get("useContext"):
                    context_key = field_config["useContext"]
                    if context_key in context:
                        schema_fields[field_name] = context[context_key]
                    else:
                        raise ValueError(f"Schema field {field_name} requires context key '{context_key}' but not found")
            elif isinstance(field_config, str):
                schema_fields[field_name] = field_config
            else:
                raise ValueError(f"Invalid field configuration for {field_name}")
    
    return schema_fields

def _generate_metadata(context: Dict[str, Any], config: Dict[str, Any], schema_fields: Dict[str, Any]) -> Dict[str, Any]:
    """Generate base metadata with schema fields"""
    from api_client import APIClient
    from metadata.metadata_generator import generate_metadata
    
    subject = context["subject"]
    author_id = context.get("author_id", 1)
    
    api_client = APIClient(config)
    metadata = generate_metadata(subject, author_id, config, api_client, schema_fields)
    
    return metadata

def _get_schema(article_type: str):
    """Get schema for article type"""
    from schemas.schema_registry import get_schema
    return get_schema(article_type)

def _create_article(schema, metadata, tags, jsonld, tag_generator, jsonld_generator):
    """Create article content - no separate title parameter"""
    import yaml
    
    # Format components
    metadata_yaml = yaml.dump(metadata, default_flow_style=False, sort_keys=False)
    formatted_tags = tag_generator.format_tags(tags)
    formatted_jsonld = jsonld_generator.format_jsonld(jsonld)
    
    # Get article template
    template = schema.get_article_template()
    
    # Fill template with metadata only (title is in metadata)
    article = template.format(
        metadata_yaml=metadata_yaml,
        formatted_tags=formatted_tags,
        formatted_jsonld=formatted_jsonld,
        **metadata
    )
    
    return article

def _save_article(schema, context, article):
    """Save article to file"""
    # Get output rules
    output_rules = schema.get_output_rules()
    
    # Create output directory
    output_dir = Path(output_rules["directory"])
    if output_rules.get("create_dirs", True):
        output_dir.mkdir(parents=True, exist_ok=True)
    
    # Generate filename
    filename_template = schema.get_filename_template()
    logger.info(f"🔧 Filename template: {filename_template}")
    logger.info(f"🔧 Context keys: {list(context.keys())}")
    
    try:
        filename = filename_template.format(**context)
    except KeyError as e:
        logger.error(f"🚨 Missing key in context: {e}")
        logger.error(f"🚨 Template: {filename_template}")
        logger.error(f"🚨 Context: {context}")
        raise
    
    # Save file
    output_file = output_dir / filename
    encoding = output_rules.get("encoding", "utf-8")
    
    with open(output_file, 'w', encoding=encoding) as f:
        f.write(article)
    
    return str(output_file)

if __name__ == "__main__":
    # Remove circular import
    import sys
    if len(sys.argv) > 1:
        article_type = sys.argv[1]
        subject = sys.argv[2] if len(sys.argv) > 2 else "default"
        author_id = int(sys.argv[3]) if len(sys.argv) > 3 else 1
    else:
        article_type = "material"
        subject = "copper"
        author_id = 4
    
    context = {
        "article_type": article_type,
        "subject": subject,
        "author_id": author_id
    }
    
    config = {
        "api": {
            "provider": "deepseek",
            "model": "deepseek-chat",
            "temperature": 0.7
        }
    }
    
    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler(f'logs/generation_{article_type}_{subject}.log')
        ]
    )
    
    try:
        output_file = generate_article(context, config)
        print(f"✅ Article structure generated: {output_file}")
    except Exception as e:
        logger.error(f"❌ Generation failed: {e}")
        raise