#!/usr/bin/env python3
"""
Z-Beam Article Generator
"""
import logging
from typing import Dict, Any
from pathlib import Path
from datetime import datetime

logger = logging.getLogger(__name__)

def generate_article(context: Dict[str, Any], config: Dict[str, Any]) -> str:
    """Generate article with optimizations"""
    logger.info("🚀 Generating base content...")
    
    # Generate base content
    current_content = _generate_base_content(context, config)
    logger.info(f"📝 Base content generated: {len(current_content.split())} words")
    
    # Apply optimizations in order
    optimization_order = config.get("optimization_order", [])
    logger.info(f"🎛️ Optimization order: {optimization_order}")
    
    if not optimization_order:
        logger.warning("⚠️ No optimizations configured!")
    
    for i, optimizer_name in enumerate(optimization_order, 1):
        logger.info(f"🔧 Step {i}: Applying {optimizer_name}...")
        
        # Store previous content length for comparison
        prev_length = len(current_content.split())
        
        # Apply optimizer
        current_content = _apply_optimizer(optimizer_name, current_content, context, config)
        
        # Log changes
        new_length = len(current_content.split())
        logger.info(f"✅ {optimizer_name} applied: {prev_length} → {new_length} words")
    
    # Finalize with metadata
    logger.info("📝 Adding comprehensive metadata...")
    final_article = _finalize_article(current_content, context, config)
    
    # Save article
    output_path = _save_article(final_article, context)
    
    return output_path

def _generate_base_content(context: Dict[str, Any], config: Dict[str, Any]) -> str:
    """Generate base article content"""
    from api_client import APIClient
    
    api_client = APIClient(config)
    material = context.get("material", "unknown")
    
    # Get word limit from simple config
    simple_config = config.get("simple_config", {})
    word_limit = simple_config.get("word_limit", 1200)
    
    # Calculate section word distribution
    section_words = word_limit // 4  # 300 words per section for 4 sections
    
    # Enhanced base generation with better word distribution
    base_prompt = f"""Write a technical article about {material} laser cleaning.

STRUCTURE WITH WORD LIMITS:
## Introduction ({section_words} words)
- Brief overview of {material} laser cleaning
- Key benefits and applications

## Comparison with Traditional Methods ({section_words} words)  
- Compare laser vs mechanical/chemical cleaning
- Advantages and limitations
- Efficiency comparisons

## Contaminants Removed ({section_words} words)
- Types of contaminants on {material}
- How laser cleaning removes them
- Process parameters

## Substrate Applications ({section_words} words)
- Industries using {material}
- Specific applications
- Success stories

REQUIREMENTS:
- TOTAL: {word_limit} words (approximately {section_words} words per section)
- Technical but readable
- Include specific measurements where relevant
- Use casual, conversational tone
- Focus on practical benefits
- Each section should be roughly equal in length

CRITICAL: Ensure each section is approximately {section_words} words. Do not exceed {word_limit} total words.

Write the complete article:"""
    
    logger.info(f"📝 Generating base content: {word_limit} words ({section_words} per section)")
    return api_client.call(base_prompt, "base-generation")

def _apply_optimizer(optimizer_name: str, content: str, context: Dict[str, Any], config: Dict[str, Any]) -> str:
    """Apply single optimizer using simplified functions"""
    from api_client import APIClient
    from optimizers.simple_optimizers import apply_writing_style, add_technical_depth, humanize_content
    
    api_client = APIClient(config)
    
    if optimizer_name == "writing_samples":
        return apply_writing_style(content, context, api_client, config)
    
    elif optimizer_name == "technical_authenticity":
        return add_technical_depth(content, context, api_client, config)
    
    elif optimizer_name == "iterative":
        return humanize_content(content, context, api_client, config)
    
    logger.warning(f"⚠️ Unknown optimizer: {optimizer_name}")
    return content

def _finalize_article(content: str, context: Dict[str, Any], config: Dict[str, Any]) -> str:
    """Add metadata and finalize article"""
    from api_client import APIClient
    from tags.tag_generator import TagGenerator
    from metadata.metadata_generator import generate_metadata
    
    api_client = APIClient(config)
    
    # Generate tags
    tag_generator = TagGenerator(config, api_client)
    material = context.get("material", "unknown")
    
    # Simple material metadata for tags
    material_data = {
        "material": material,
        "density": "Unknown",
        "melting_point": "Unknown",
        "applications": ["Industrial cleaning", "Surface preparation"]
    }
    
    tags = tag_generator.generate_tags(material, material_data)
    formatted_tags = _format_tags(tags)
    
    # Get optimization info
    optimization_order = config.get("optimization_order", [])
    optimization_summary = " → ".join(optimization_order) if optimization_order else "None"
    
    # Add optimization method to config for metadata generator
    config["optimization_method"] = optimization_summary
    
    # ✅ GENERATE COMPREHENSIVE METADATA using metadata_generator
    logger.info("📊 Generating comprehensive metadata...")
    metadata = generate_metadata(material, context.get("author_id", 1), config, api_client)
    
    # Format metadata as YAML (assuming you have this function)
    try:
        from metadata.metadata_generator import _format_metadata_as_yaml
        metadata_yaml = _format_metadata_as_yaml(metadata)
    except ImportError:
        # Fallback to simple formatting
        metadata_yaml = _format_metadata_simple(metadata)
    
    # Create final article with researched metadata
    final_article = f"""---
{metadata_yaml}
---

## Tags

{formatted_tags}

---

# Laser Cleaning {material}

{content}
"""
    
    return final_article

def _format_metadata_simple(metadata: dict) -> str:
    """Simple metadata formatting if YAML formatter not available"""
    lines = []
    for key, value in metadata.items():
        if isinstance(value, list):
            lines.append(f"{key}:")
            for item in value:
                lines.append(f"  - \"{item}\"")
        elif isinstance(value, dict):
            lines.append(f"{key}:")
            for k, v in value.items():
                lines.append(f"  {k}: \"{v}\"")
        else:
            lines.append(f"{key}: \"{value}\"")
    return "\n".join(lines)

def _format_tags(tags: list) -> str:
    """Format tags for display"""
    if not tags:
        return "#LaserCleaning, #SurfacePreparation, #IndustrialCleaning"
    
    # Format as hashtags
    hashtags = [f"#{tag}" for tag in tags]
    
    # Split into two lines for better formatting
    mid_point = len(hashtags) // 2
    line1 = ", ".join(hashtags[:mid_point])
    line2 = ", ".join(hashtags[mid_point:])
    
    return f"{line1}\n{line2}" if line2 else line1

def _save_article(article: str, context: Dict[str, Any]) -> str:
    """Save article to file"""
    material = context.get("material", "unknown")
    output_dir = Path("output")
    output_dir.mkdir(exist_ok=True)
    
    output_file = output_dir / f"{material}_laser_cleaning.md"
    
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
            logging.FileHandler(f'logs/generation_{context["material"]}.log')
        ]
    )
    
    try:
        output_file = generate_article(context, config)
        print(f"✅ Article generated: {output_file}")
    except Exception as e:
        logger.error(f"❌ Generation failed: {e}")
        raise