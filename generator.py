#!/usr/bin/env python3
"""
Z-Beam Generator - Main orchestrator (simplified)
"""
import logging
import json
from pathlib import Path
from typing import Dict, List

from api_client import APIClient
from optimizers.iterative_optimizer import IterativeOptimizer
from optimizers.writing_samples_optimizer import WritingSamplesOptimizer

logger = logging.getLogger(__name__)

def get_optimizer(config, api_client):
    """Return appropriate optimizer based on configuration"""
    optimization_method = config.get("optimization_method", "writing_samples")
    
    if optimization_method == "iterative":
        return IterativeOptimizer(config, api_client)
    elif optimization_method == "writing_samples":
        return WritingSamplesOptimizer(config, api_client)
    else:
        raise ValueError(f"Unknown optimization method: {optimization_method}")

def generate_content_sections(material: str, config: Dict, api_client) -> List[Dict]:
    """Generate content sections using sections.json configuration"""
    logger.info(f"📝 Generating content sections for {material}")
    
    # Load sections configuration
    sections_file = Path(config.get("sections_file", "prompts/text/sections.json"))
    
    if not sections_file.exists():
        logger.error(f"❌ Sections file not found: {sections_file}")
        raise FileNotFoundError(f"Sections file not found: {sections_file}")
    
    try:
        with open(sections_file, 'r') as f:
            sections_data = json.load(f)
        
        # Extract sections array from the nested structure
        if "sections" in sections_data:
            sections_config = sections_data["sections"]
        else:
            # Fallback for direct array format
            sections_config = sections_data
        
        logger.info(f"📚 Loaded {len(sections_config)} section configurations")
        
    except json.JSONDecodeError as e:
        logger.error(f"❌ Invalid JSON in sections file: {e}")
        raise
    except Exception as e:
        logger.error(f"❌ Failed to load sections file: {e}")
        raise
    
    # Filter and sort sections
    applicable_sections = []
    for section in sections_config:
        # Check if section applies to this material
        section_materials = section.get("materials", [])
        
        # If no materials specified, or material is in the list, or material is close match
        if (not section_materials or 
            material.title() in section_materials or 
            material.lower() in [m.lower() for m in section_materials] or
            any(material.lower() in m.lower() for m in section_materials)):
            
            applicable_sections.append(section)
            logger.info(f"✅ Section '{section.get('title')}' applies to {material}")
        else:
            logger.info(f"⏭️ Section '{section.get('title')}' skipped (materials: {section_materials})")
    
    # Sort by order if specified
    applicable_sections.sort(key=lambda x: x.get("order", 999))
    
    if not applicable_sections:
        logger.warning(f"⚠️ No applicable sections found for {material}, using all sections")
        applicable_sections = sections_config
    
    # Generate sections
    sections = []
    for section_config in applicable_sections:
        section_name = section_config.get("name", "unknown")
        section_title = section_config.get("title", "Unknown Section")
        section_type = section_config.get("section_type", "TEXT")
        
        logger.info(f"📄 Generating section: {section_title} (type: {section_type})")
        
        # Get custom prompt or create default
        if "prompt" in section_config:
            # Use custom prompt and substitute material
            base_prompt = section_config["prompt"]
            custom_prompt = base_prompt.format(material=material)
            
            # Enhance with additional requirements
            prompt = f"""{custom_prompt}

Requirements:
- Write approximately 75 words
- Focus on technical accuracy and specific details about {material}
- Use professional, technical language suitable for industrial applications
- Include relevant technical parameters where applicable
- Do not include section headers or titles in the content
- Ensure content is specific to {material} properties and characteristics

Generate only the content for this section:"""
            
        else:
            # Create default prompt
            prompt = f"""Generate a detailed section about laser cleaning of {material}.

Section Title: {section_title}
Section Type: {section_type}

Requirements:
- Write approximately 75 words
- Focus on technical accuracy
- Include specific details about {material}
- Use professional, technical language
- Do not include section headers or titles

Generate only the content for this section:"""
        
        # Generate section content
        try:
            content = api_client.call(prompt, f"section-{section_name}")
            
            sections.append({
                "name": section_name,
                "title": section_title,
                "content": content.strip(),
                "type": section_type,
                "order": section_config.get("order", 999)
            })
            
            logger.info(f"✅ Generated section '{section_title}': {len(content)} chars")
            
        except Exception as e:
            logger.error(f"❌ Failed to generate section '{section_title}': {e}")
            # Add placeholder content to maintain structure
            sections.append({
                "name": section_name,
                "title": section_title,
                "content": f"Content for {section_title} section about {material} laser cleaning.",
                "type": section_type,
                "order": section_config.get("order", 999)
            })
    
    logger.info(f"✅ Generated {len(sections)} sections for {material}")
    
    # Log section summary
    for section in sections:
        words = len(section['content'].split())
        logger.info(f"📊 Section '{section['title']}': {words} words, order {section.get('order', 'N/A')}")
    
    return sections

def generate_tags(material: str, metadata: Dict, config: Dict, api_client) -> List[str]:
    """Generate optimized tags for the material"""
    logger.info(f"🏷️ Generating tags for {material}")
    
    # Create prompt for tag generation
    prompt = f"""Generate 10-12 relevant tags for a laser cleaning article about {material}.

Material: {material}
Material Properties: {metadata.get('materialClass', 'Unknown')}
Density: {metadata.get('density', 'Unknown')}
Melting Point: {metadata.get('meltingPoint', 'Unknown')}

Focus on:
- Material properties (density, temperature, structure)
- Processing characteristics
- Safety considerations
- Applications
- Industry relevance

Return only a JSON array of strings, no other text:
["tag1", "tag2", "tag3", ...]"""
    
    # Generate tags
    tags_response = api_client.call(prompt, "tag-generation")
    
    try:
        # Parse JSON response
        tags = json.loads(tags_response)
        if not isinstance(tags, list):
            raise ValueError("Tags response is not a list")
        
        # Clean and validate tags
        clean_tags = []
        for tag in tags:
            if isinstance(tag, str) and tag.strip():
                clean_tags.append(tag.strip())
        
        logger.info(f"✅ Generated {len(clean_tags)} tags for {material}")
        return clean_tags
        
    except (json.JSONDecodeError, ValueError) as e:
        logger.error(f"❌ Failed to parse tags response: {e}")
        # Return fallback tags
        fallback_tags = [
            "High Temperature", "Metal Processing", "Laser Cleaning",
            "Surface Treatment", "Industrial Applications", "Precision Cleaning"
        ]
        logger.info(f"🔄 Using fallback tags: {len(fallback_tags)} tags")
        return fallback_tags

def assemble_final_article(material: str, metadata: Dict, tags: List[str], sections: List[Dict], config: Dict) -> str:
    """Assemble final markdown article"""
    logger.info(f"🔧 Assembling final article for {material}")
    
    # Create output directory
    output_dir = Path(config.get("output_dir", "output"))
    output_dir.mkdir(exist_ok=True)
    
    # Create output filename
    output_file = output_dir / f"{material}_laser_cleaning.md"
    
    # Build markdown content
    content_lines = []
    
    # Add YAML frontmatter
    content_lines.append("---")
    for key, value in metadata.items():
        if isinstance(value, str):
            content_lines.append(f'{key}: "{value}"')
        elif isinstance(value, list):
            content_lines.append(f"{key}:")
            for item in value:
                content_lines.append(f'  - "{item}"')
        else:
            content_lines.append(f"{key}: {value}")
    
    # Add tags
    content_lines.append("tags:")
    for tag in tags:
        content_lines.append(f'  - "{tag}"')
    
    content_lines.append("---")
    content_lines.append("")
    
    # Add title
    content_lines.append(f"# {metadata.get('title', f'Laser Cleaning {material}')}")
    content_lines.append("")
    
    # Add sections
    for section in sections:
        content_lines.append(f"## {section['title']}")
        content_lines.append(section['content'])
        content_lines.append("")
    
    # Write to file
    final_content = "\n".join(content_lines)
    
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(final_content)
    
    logger.info(f"✅ Article assembled: {output_file}")
    return str(output_file)

def generate_article(context: Dict, config: Dict) -> str:
    """Generate complete article with metadata, tags, and content"""
    material = context["material"]
    author_id = context["author_id"]
    article_type = context["article_type"]
    
    logger.info(f"🚀 Starting article generation for {material}")
    logger.info(f"📋 Context: {context}")
    logger.info(f"⚙️ Config: {config}")
    
    # Initialize API client
    api_client = APIClient(config)
    
    # Phase 1: Generate content
    logger.info("🔄 PHASE 1: GENERATION")
    sections = generate_content_sections(material, config, api_client)
    logger.info(f"✅ Generated {len(sections)} content sections")
    
    # Generate metadata using function-based approach
    from metadata.metadata_generator import generate_metadata
    metadata = generate_metadata(material, author_id, config, api_client)
    logger.info(f"✅ Generated metadata with {len(metadata)} fields")
    
    # Generate tags
    tags = generate_tags(material, metadata, config, api_client)
    logger.info(f"✅ Generated {len(tags)} optimized tags")
    
    # Phase 2: Optimize content
    logger.info("🔄 PHASE 2: OPTIMIZATION")
    optimizer = get_optimizer(config, api_client)
    optimized_sections = optimizer.optimize_sections(sections, material, metadata)
    logger.info(f"✅ Optimized {len(optimized_sections)} sections")
    
    # Phase 3: Assemble final article
    logger.info("🔄 PHASE 3: ASSEMBLY")
    output_file = assemble_final_article(material, metadata, tags, optimized_sections, config)
    logger.info(f"✅ Article assembled: {output_file}")
    
    return output_file

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
        print(f"✅ Article generated: {output_file}")
    except Exception as e:
        logger.error(f"❌ Generation failed: {e}")
        raise