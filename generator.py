#!/usr/bin/env python3
"""
Generator - Schema-ready article generation
"""
import logging
from typing import Dict, Any
from pathlib import Path

logger = logging.getLogger(__name__)

def generate_article(context: Dict[str, Any], config: Dict[str, Any]) -> str:
    """Generate article with full orchestration including JSON-LD"""
    logger.info("🚀 Generating article with complete orchestration...")
    
    try:
        # Validate context
        _validate_context(context)
        
        logger.info("📊 Generating metadata...")
        logger.info("🏷️ Generating tags...")
        logger.info("🔗 Generating JSON-LD structured data...")
        
        # Generate metadata, tags, and JSON-LD
        metadata_content = _generate_metadata_and_tags(context, config)
        
        logger.info("📝 Building article structure...")
        
        # Generate article structure
        article_structure = _generate_article_structure(context, metadata_content)
        
        logger.info("💾 Saving article...")
        
        # Save to file
        output_file = _save_article_structure(context, article_structure)
        
        logger.info(f"✅ Article generated with complete orchestration: {output_file}")
        logger.info(f"🎯 Generated: Metadata ✓ | Tags ✓ | JSON-LD ✓ | Article Structure ✓")
        
        return output_file
        
    except Exception as e:
        logger.error(f"❌ Article generation failed: {e}")
        raise

def _validate_context(context: Dict[str, Any]):
    """Basic context validation - will be enhanced with schemas"""
    required_fields = ["article_type", "subject", "author_id"]
    
    for field in required_fields:
        if not context.get(field):
            raise ValueError(f"Missing required field: {field}")
    
    # Validate article type
    supported_types = ["material", "application", "region", "thesaurus"]
    if context["article_type"] not in supported_types:
        raise ValueError(f"Unknown article type: {context['article_type']}. Available: {supported_types}")

def _generate_metadata_and_tags(context: Dict[str, Any], config: Dict[str, Any]) -> Dict[str, Any]:
    """Generate metadata, tags, and JSON-LD from schemas"""
    from api_client import APIClient
    from tags.tag_generator import TagGenerator
    from metadata.metadata_generator import generate_metadata, format_metadata_as_yaml
    
    # Determine material from context
    material = _get_material_from_context(context)
    
    # Generate metadata
    api_client = APIClient(config)
    metadata = generate_metadata(material, context.get("author_id", 1), config, api_client)
    
    # Add article type and subject to metadata
    metadata["articleType"] = context["article_type"]
    metadata["subject"] = context["subject"]
    
    # Generate tags
    tag_generator = TagGenerator(config, api_client)
    tags = tag_generator.generate_tags(material, metadata, context["article_type"])
    formatted_tags = _format_tags(tags)
    
    # Generate JSON-LD from schema
    formatted_jsonld = _generate_schema_jsonld(context, metadata)
    
    # Format metadata
    metadata_yaml = format_metadata_as_yaml(metadata)
    
    return {
        "metadata_yaml": metadata_yaml,
        "formatted_tags": formatted_tags,
        "formatted_jsonld": formatted_jsonld,
        "material": material,
        "article_type": context["article_type"],
        "subject": context["subject"]
    }

def _get_material_from_context(context: Dict[str, Any]) -> str:
    """Get material based on article type - schema-ready"""
    article_type = context.get("article_type", "material")
    subject = context.get("subject", "steel")
    
    # Only material articles need specific materials
    if article_type == "material":
        return subject  # For material articles, subject IS the material
    else:
        return "general"  # All other article types are material-agnostic

def _generate_schema_jsonld(context: Dict[str, Any], metadata: Dict[str, Any]) -> str:
    """Generate JSON-LD dynamically from schema properties - NO FALLBACKS"""
    # Get schema for article type - MUST EXIST
    schema = _get_schema_for_type(context["article_type"])
    
    # Generate JSON-LD structure dynamically from schema
    jsonld_data = _build_dynamic_jsonld(schema, context, metadata)
    
    # Format as markdown code block
    import json
    json_str = json.dumps(jsonld_data, indent=2)
    return f"```json\n{json_str}\n```"

def _get_schema_for_type(article_type: str):
    """Get schema for article type - NO FALLBACKS"""
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
        raise ValueError(f"Unknown article type: {article_type}")

def _build_dynamic_jsonld(schema, context: Dict[str, Any], metadata: Dict[str, Any]) -> Dict[str, Any]:
    """Build JSON-LD structure dynamically from schema metadata properties"""
    # Get JSON-LD template from schema
    jsonld_template = schema.get_jsonld_schema()
    
    # Get template context from schema
    template_context = schema.get_template_context(metadata)
    
    # Populate template with metadata
    populated_jsonld = _populate_jsonld_template(jsonld_template, template_context, metadata)
    
    return populated_jsonld

def _populate_jsonld_template(template: Dict[str, Any], context: Dict[str, Any], metadata: Dict[str, Any]) -> Dict[str, Any]:
    """Populate JSON-LD template with metadata"""
    import json
    from datetime import datetime
    
    # Convert template to string for replacement
    template_str = json.dumps(template, indent=2)
    
    # Combine context and metadata for replacement
    all_data = {**context, **metadata}
    
    # Handle nested objects (like laserCleaningParameters)
    flattened_data = _flatten_nested_data(all_data)
    
    # Replace placeholders
    for key, value in flattened_data.items():
        if value is not None:
            placeholder = f"{{{key}}}"
            template_str = template_str.replace(placeholder, str(value))
    
    # Add current timestamp if not present
    if "{datePublished}" in template_str:
        template_str = template_str.replace("{datePublished}", datetime.now().isoformat())
    
    # Clean up unreplaced placeholders - REMOVE EMPTY FIELDS
    import re
    # Remove fields with unreplaced placeholders
    lines = template_str.split('\n')
    cleaned_lines = []
    for line in lines:
        if not re.search(r':\s*"\{[^}]+\}"', line):  # Skip lines with unreplaced placeholders
            cleaned_lines.append(line)
    
    template_str = '\n'.join(cleaned_lines)
    
    return json.loads(template_str)

def _flatten_nested_data(data: Dict[str, Any], parent_key: str = '', sep: str = '.') -> Dict[str, Any]:
    """Flatten nested dictionary for template replacement"""
    items = []
    for k, v in data.items():
        new_key = f"{parent_key}{sep}{k}" if parent_key else k
        if isinstance(v, dict):
            items.extend(_flatten_nested_data(v, new_key, sep=sep).items())
        elif isinstance(v, list):
            # Convert lists to comma-separated strings
            items.append((new_key, ', '.join(str(item) for item in v)))
        else:
            items.append((new_key, v))
    return dict(items)

def _generate_article_structure(context: Dict[str, Any], metadata_content: Dict[str, Any]) -> str:
    """Generate article structure with flexible content area"""
    article_type = context["article_type"]
    subject = context["subject"]
    
    # Generate title based on article type
    title = _generate_title(article_type, subject)
    
    # Simple article structure with content placeholder
    return f"""---
{metadata_content["metadata_yaml"]}
---

## Tags

{metadata_content["formatted_tags"]}

## JSON-LD Structured Data

{metadata_content["formatted_jsonld"]}

---

# {title}

<!-- CONTENT PLACEHOLDER -->
<!-- Article Type: {article_type} | Subject: {subject} -->
<!-- This content area will be populated by external text generation -->

[Article content will be generated here]

<!-- END CONTENT PLACEHOLDER -->
"""

def _generate_title(article_type: str, subject: str) -> str:
    """Generate title based on article type and subject"""
    if article_type == "material":
        return f"Laser Cleaning {subject}"
    elif article_type == "application":
        return f"Laser Cleaning for {subject}"
    elif article_type == "region":
        return f"Laser Cleaning in {subject}"
    elif article_type == "thesaurus":
        return f"{subject} - Laser Cleaning Technical Term"
    else:
        return f"Laser Cleaning {subject}"

def _save_article_structure(context: Dict[str, Any], article_structure: str) -> str:
    """Save article with schema-ready naming"""
    article_type = context["article_type"]
    subject = context["subject"]
    
    # Generate filename based on article type
    filename = _generate_filename(article_type, subject)
    
    output_dir = Path("output")
    output_dir.mkdir(exist_ok=True)
    
    output_file = output_dir / filename
    
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(article_structure)
    
    return str(output_file)

def _generate_filename(article_type: str, subject: str) -> str:
    """Generate filename based on article type and subject"""
    safe_subject = subject.lower().replace(' ', '_').replace('-', '_')
    
    if article_type == "material":
        return f"{safe_subject}_laser_cleaning.md"
    elif article_type == "application":
        return f"{safe_subject}_application.md"
    elif article_type == "region":
        return f"{safe_subject}_region.md"
    elif article_type == "thesaurus":
        return f"{safe_subject}_definition.md"
    else:
        return f"{safe_subject}_article.md"

def _format_tags(tags: list) -> str:
    """Format tags for output"""
    if not tags:
        return "#LaserCleaning"
    
    formatted = []
    for tag in tags:
        if not tag.startswith('#'):
            formatted.append(f"#{tag}")
        else:
            formatted.append(tag)
    
    return ", ".join(formatted)

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