#!/usr/bin/env python3
"""
Simplified Z-Beam Generator
"""
import logging
from typing import Dict, Any
from pathlib import Path
from datetime import datetime

logger = logging.getLogger(__name__)

def generate_article(context: Dict[str, Any], config: Dict[str, Any]) -> str:
    """Generate article with simplified orchestration"""
    
    # 1. Generate base content
    logger.info("🚀 Generating base content...")
    base_content = _generate_base_content(context, config)
    
    # 2. Apply optimizations (simplified)
    current_content = base_content
    optimization_order = config.get("optimization_order", [])
    
    for optimizer_name in optimization_order:
        logger.info(f"🔧 Applying {optimizer_name}...")
        current_content = _apply_optimizer(optimizer_name, current_content, context, config)
    
    # 3. Generate metadata and save
    logger.info("📝 Generating metadata...")
    final_article = _finalize_article(current_content, context, config)
    
    # 4. Save to file
    output_path = _save_article(final_article, context)
    
    return output_path

def _generate_base_content(context: Dict[str, Any], config: Dict[str, Any]) -> str:
    """Generate base article content"""
    from api_client import APIClient
    
    api_client = APIClient(config)
    material = context.get("material", "unknown")
    
    # Single, comprehensive base generation prompt
    base_prompt = f"""Write a technical article about {material} laser cleaning.

STRUCTURE:
## Introduction
- What is {material} and why laser cleaning matters
- Key benefits over traditional methods
- Brief technical overview

## Comparison with Traditional Methods  
- Laser vs mechanical/chemical cleaning
- Advantages and limitations
- Efficiency comparisons

## Contaminants Removed
- Types of contaminants on {material}
- How laser cleaning removes them
- Process parameters

## Substrate Applications
- Industries using {material}
- Specific applications
- Success stories

REQUIREMENTS:
- Technical but readable
- 1200 words total (~300 per section)
- Include specific measurements where relevant
- Use casual, professional tone
- Focus on practical benefits

Write the complete article:"""
    
    return api_client.call(base_prompt, "base-generation")

def _apply_optimizer(optimizer_name: str, content: str, context: Dict[str, Any], config: Dict[str, Any]) -> str:
    """Apply single optimizer using simplified functions"""
    from api_client import APIClient
    from optimizers.simple_optimizers import apply_writing_style, add_technical_depth, humanize_content
    
    api_client = APIClient(config)
    
    if optimizer_name == "writing_samples":
        return apply_writing_style(content, context, api_client)
    
    elif optimizer_name == "technical_authenticity":
        return add_technical_depth(content, context, api_client)
    
    elif optimizer_name == "iterative":
        return humanize_content(content, context, api_client)
    
    logger.warning(f"⚠️ Unknown optimizer: {optimizer_name}")
    return content

def _finalize_article(content: str, context: Dict[str, Any], config: Dict[str, Any]) -> str:
    """Add metadata and finalize article"""
    from api_client import APIClient
    from tags.tag_generator import TagGenerator
    
    api_client = APIClient(config)
    
    # Generate tags
    tag_generator = TagGenerator(config, api_client)
    material = context.get("material", "unknown")
    
    # Simple material metadata (you can expand this)
    material_data = {
        "material": material,
        "density": "Unknown",
        "melting_point": "Unknown",
        "applications": ["Industrial cleaning", "Surface preparation"]
    }
    
    tags = tag_generator.generate_tags(material, material_data)
    
    # Format tags
    formatted_tags = _format_tags(tags)
    
    # Create final article with metadata
    final_article = f"""---
title: "Laser Cleaning {material}"
articleType: "material"
nameShort: "{material}"
description: "Explore how laser cleaning removes contaminants from {material}, enhancing performance and safety."
publishedAt: "{datetime.now().strftime('%Y-%m-%d')}"
authorId: "{context.get('author_id', 1)}"
generation_timestamp: "{datetime.now().isoformat()}"
model_used: "{config.get('provider', 'unknown')}/{config.get('model', 'unknown')}"
---

## Tags

{formatted_tags}

---

# Laser Cleaning {material}

{content}
"""
    
    return final_article

def _format_tags(tags: list) -> str:
    """Format tags for output"""
    if not tags:
        return ""
    
    # Format as two lines of hashtags
    hashtags = [f"#{tag}" for tag in tags]
    mid_point = len(hashtags) // 2
    line1 = ", ".join(hashtags[:mid_point])
    line2 = ", ".join(hashtags[mid_point:])
    return f"{line1}\n{line2}"

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