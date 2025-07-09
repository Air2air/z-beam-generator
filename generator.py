#!/usr/bin/env python3
"""
Z-Beam Generator - Main orchestrator with discrete tag module
"""
import logging
from pathlib import Path

from api_client import APIClient
from content_generator import ContentGenerator
from metadata.metadata_generator import MetadataGenerator
from tags.tag_generator import TagGenerator  # Import from tags module
from orchestrator import ArticleOrchestrator
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

def generate_article(context, config):
    """Generate a complete laser cleaning article using four-phase pipeline"""
    material = context["material"]
    author_id = context["author_id"]
    article_type = context["article_type"]
    
    logger.info(f"🚀 Starting article generation for {material}")
    logger.info(f"📋 Context: {context}")
    logger.info(f"⚙️ Config: {config}")
    
    # Initialize components
    api_client = APIClient(config)
    content_generator = ContentGenerator(config, api_client)
    metadata_generator = MetadataGenerator(config, api_client)
    tag_generator = TagGenerator(config, api_client)  # Discrete tag module
    optimizer = get_optimizer(config, api_client)
    orchestrator = ArticleOrchestrator(config)
    
    # PHASE 1: GENERATION
    logger.info("🔄 PHASE 1: GENERATION")
    
    # Generate content sections - FIXED WITH BOTH PARAMETERS
    sections = content_generator.generate_text_sections(material, article_type)
    logger.info(f"✅ Generated {len(sections)} content sections")
    
    # Generate metadata and get material data
    metadata, material_data = metadata_generator.generate_metadata(material, author_id, article_type)
    logger.info(f"✅ Generated metadata with {len(metadata)} fields")
    
    # Generate tags using discrete module
    tags = tag_generator.generate_tags(material, material_data)
    logger.info(f"✅ Generated {len(tags)} optimized tags")
    
    # PHASE 2: OPTIMIZATION
    logger.info("🔄 PHASE 2: OPTIMIZATION")
    optimized_sections = optimizer.optimize_sections(sections, material, metadata)
    logger.info(f"✅ Optimized {len(optimized_sections)} sections")
    
    # PHASE 3: ORCHESTRATION
    logger.info("🔄 PHASE 3: ORCHESTRATION")
    final_article = orchestrator.orchestrate_article(optimized_sections, metadata, tags)
    logger.info("✅ Article orchestration completed")
    
    # Save output
    output_file = Path("output") / f"{material}_laser_cleaning.md"
    output_file.parent.mkdir(exist_ok=True)
    
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(final_article)
    
    logger.info(f"🎉 Article generated successfully: {output_file}")
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