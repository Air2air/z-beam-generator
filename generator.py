#!/usr/bin/env python3
"""
Generator - Schema-ready article generation
"""
import logging
from typing import Dict, Any
from pathlib import Path

logger = logging.getLogger(__name__)

def generate_article(context: Dict[str, Any], config: Dict[str, Any]) -> str:
    """Generate article with schema-ready architecture"""
    logger.info("🚀 Generating article with schema-ready approach...")
    
    try:
        # Validate context
        _validate_context(context)
        
        # Future: Schema-based validation
        # schema = SchemaFactory.get_schema(context["article_type"])
        # is_valid, errors = schema.validate_data(context)
        
        # Generate metadata and tags
        metadata_content = _generate_metadata_and_tags(context, config)
        
        # Generate article structure
        article_structure = _generate_article_structure(context, metadata_content)
        
        # Save to file
        output_file = _save_article_structure(context, article_structure)
        
        logger.info(f"✅ Article generated: {output_file}")
        return output_file
        
    except Exception as e:
        logger.error(f"❌ Generation failed: {e}")
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
    """Generate metadata and tags - ready for schema integration"""
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
    
    # Future: Schema-based metadata enhancement
    # enhanced_metadata = schema.enhance_metadata(metadata, context)
    
    # Generate tags
    tag_generator = TagGenerator(config, api_client)
    tags = tag_generator.generate_tags(material, metadata, context["article_type"])
    formatted_tags = _format_tags(tags)
    
    # Format metadata
    metadata_yaml = format_metadata_as_yaml(metadata)
    
    return {
        "metadata_yaml": metadata_yaml,
        "formatted_tags": formatted_tags,
        "material": material,
        "article_type": context["article_type"],
        "subject": context["subject"]
    }

def _get_material_from_context(context: Dict[str, Any]) -> str:
    """Get material based on article type - schema-ready"""
    article_type = context.get("article_type", "material")
    subject = context.get("subject", "steel")
    
    # Future: This logic will be moved to schemas
    if article_type == "material":
        return subject  # For material articles, subject IS the material
    elif article_type == "application":
        return "general"  # Applications don't need specific materials
    elif article_type == "region":
        return context.get("material", "steel")  # Regions need material specification
    elif article_type == "thesaurus":
        return "general"  # Technical terms don't need specific materials
    else:
        return "steel"

def _generate_article_structure(context: Dict[str, Any], metadata_content: Dict[str, Any]) -> str:
    """Generate article structure - ready for schema-based templates"""
    article_type = context["article_type"]
    subject = context["subject"]
    
    # Future: Schema-based title and section generation
    # title, sections = schema.get_article_structure(context)
    
    # Current: Simple template logic
    if article_type == "material":
        title = f"Laser Cleaning {subject}"
        sections = ["Introduction", "Material Properties", "Laser Cleaning Applications", "Process Parameters", "Quality Results"]
    elif article_type == "application":
        title = f"Laser Cleaning for {subject}"
        sections = ["Introduction", "Application Overview", "Process Benefits", "Technical Requirements", "Industry Standards"]
    elif article_type == "region":
        title = f"Laser Cleaning in {subject}"
        sections = ["Introduction", "Regional Market Overview", "Local Industries", "Manufacturing Capabilities", "Market Opportunities"]
    elif article_type == "thesaurus":
        title = f"{subject} - Laser Cleaning Technical Term"
        sections = ["Definition", "Technical Explanation", "Applications", "Related Terms", "Measurement Units"]
    else:
        title = f"Laser Cleaning {subject}"
        sections = ["Introduction", "Overview", "Applications", "Benefits", "Conclusion"]
    
    # Generate content sections
    content_sections = "\n\n".join([f"## {section}\n[Content to be added]" for section in sections])
    
    return f"""---
{metadata_content["metadata_yaml"]}
---

## Tags

{metadata_content["formatted_tags"]}

---

# {title}

<!-- CONTENT PLACEHOLDER - Ready for external text generation -->

{content_sections}

<!-- END CONTENT PLACEHOLDER -->
"""

def _save_article_structure(context: Dict[str, Any], article_structure: str) -> str:
    """Save article with schema-ready naming"""
    article_type = context["article_type"]
    subject = context["subject"]
    
    # Future: Schema-based filename generation
    # filename = schema.get_filename(context)
    
    # Current: Type-specific filename generation
    if article_type == "material":
        filename = f"{subject.lower().replace(' ', '_')}_laser_cleaning.md"
    elif article_type == "application":
        filename = f"{subject.lower().replace(' ', '_')}_application.md"
    elif article_type == "region":
        filename = f"{subject.lower().replace(' ', '_')}_region.md"
    elif article_type == "thesaurus":
        filename = f"{subject.lower().replace(' ', '_')}_definition.md"
    else:
        filename = f"{subject.lower().replace(' ', '_')}_article.md"
    
    output_dir = Path("output")
    output_dir.mkdir(exist_ok=True)
    
    output_file = output_dir / filename
    
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(article_structure)
    
    return str(output_file)

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
            logging.FileHandler(f'logs/generation_{context["material"]}.log')
        ]
    )
    
    try:
        output_file = generate_article(context, config)
        print(f"✅ Article structure generated: {output_file}")
    except Exception as e:
        logger.error(f"❌ Generation failed: {e}")
        raise