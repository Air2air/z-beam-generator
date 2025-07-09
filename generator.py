#!/usr/bin/env python3
"""
Z-Beam Generator - Main orchestrator
Simple, focused on the core pipeline
"""
import logging
from pathlib import Path
from setup_logging import setup_logging
from run import get_config
from api_client import APIClient
from content_generator import ContentGenerator
from orchestrator import ArticleOrchestrator

# Setup logging
logger = setup_logging()

class ZBeamGenerator:
    """Main generator - orchestrates the pipeline"""
    
    def __init__(self, config, context):
        self.config = config
        self.context = context
        
        # Initialize components
        self.api_client = APIClient(config)
        self.content_generator = ContentGenerator(config, self.api_client)
        
        # Optimization method selection - NO FALLBACKS
        if config["optimization_method"] == "iterative":
            from iterative_optimizer import IterativeOptimizer
            self.optimizer = IterativeOptimizer(config, context, self.api_client)
        elif config["optimization_method"] == "writing_samples":
            from writing_samples_optimizer import WritingSamplesOptimizer
            self.optimizer = WritingSamplesOptimizer(config, context, self.api_client)
        else:
            raise ValueError(f"Invalid optimization_method: {config['optimization_method']}. Must be 'iterative' or 'writing_samples'")
        
        self.orchestrator = ArticleOrchestrator(config)
        
        logger.info(f"🔧 ZBeamGenerator initialized - {config['provider']}/{config['model']}")
        logger.info(f"🎯 Optimization method: {config['optimization_method']}")
    
    def generate_article(self):
        """Main pipeline: Generate → Optimize → Orchestrate"""
        material = self.context["material"]
        author_id = self.context["author_id"]
        article_type = self.context["article_type"]
        
        logger.info("🚀 STARTING ARTICLE GENERATION")
        logger.info(f"📄 Material: {material} | Author: {author_id} | Type: {article_type}")
        
        # GENERATE PHASE
        logger.info("🔥 GENERATION PHASE")
        text_sections = self.content_generator.generate_text_sections(material, article_type)
        metadata = self.content_generator.generate_metadata(material, author_id, article_type)
        author_data = self.content_generator.load_author_data(author_id)
        
        # OPTIMIZE PHASE
        logger.info("🔧 OPTIMIZATION PHASE")
        optimized_sections = self.optimizer.optimize_sections(text_sections, author_data)
        
        # ORCHESTRATE PHASE
        logger.info("🎼 ORCHESTRATION PHASE")
        article = self.orchestrator.orchestrate_article(optimized_sections, metadata, author_data)
        
        logger.info("🎉 ARTICLE GENERATION COMPLETED")
        return article

def main():
    """Run generator with config from run.py"""
    config, context = get_config()
    
    generator = ZBeamGenerator(config, context)
    article = generator.generate_article()
    
    # Save output
    output_dir = Path(config["output_dir"])
    output_dir.mkdir(exist_ok=True)
    
    output_file = output_dir / f"{context['material'].replace(' ', '_')}_laser_cleaning.md"
    with open(output_file, 'w') as f:
        f.write(article)
    
    logger.info(f"✅ Article saved to: {output_file}")

if __name__ == "__main__":
    main()