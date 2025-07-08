#!/usr/bin/env python3
"""
Z-Beam Generator Entry Point - No Metadata Configuration
"""

import sys
import logging
from pathlib import Path

from modules.generation.content_generator import ContentGenerator

# PRIMARY USER SETTINGS - DON'T EVER CHANGE THIS
material = "oak wood" # "copper", "oak wood", "plastic", "brick", "quartzite", "beryllium"
authorId = 2 #1,2,3,4
articleType = "material" #"region", "application", "thesaurus"  # ✅ Changed from article_type

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def main():
    """Main entry point for Z-Beam Generator"""
    
    config = {
        # Core settings
        "prompts_directory": "prompts",
        "output_directory": "output",
        
        # Generation settings
        "generation_provider": "DEEPSEEK",
        "generation_temperature": 0.7,
        "default_section_words": 150,
        "max_total_words": 700,  # ✅ Add this
        "max_tokens": 4000,
        
        # Optimization settings
        "optimization_provider": "DEEPSEEK",
        "optimization_temperature": 0.3,
        
        # Provider configurations
        "provider_models": {
            "DEEPSEEK": {
                "model": "deepseek-chat",
                "url_template": "https://api.deepseek.com/v1/chat/completions"
            },
            "XAI": {
                "model": "grok-beta",
                "url_template": "https://api.x.ai/v1/chat/completions"
            }
        },
        
        # API key mappings
        "api_key_mappings": {
            "DEEPSEEK": "DEEPSEEK_API_KEY",
            "XAI": "XAI_API_KEY"
        },
        
        # Step-specific overrides
        "step_temperatures": {
            "human_naturalness": 0.5,
            "authority_technical_enhancement": 0.2,
            "narrative_authenticity": 0.4,
            "readability_final_polish": 0.3
        },
        
        # Retry settings
        "backoff_factor": 2.0,
        "max_retries": 3,
        "timeout": 60,
        
        # Metadata module settings
        "metadata_enabled": True,
        "metadata_provider": "DEEPSEEK",
        "metadata_temperature": 0.3,
        "metadata_prompt": "prompts/metadata.md",
        
        # Pipeline control
        "pipeline_modules": {
            "metadata": {
                "enabled": True,
                "stage": "pre_generation",
                "provider": "DEEPSEEK"
            }
        },
        
        # Health check settings
        "health_check_prompt": "Respond with 'OK' if you can process this request.",
        "health_check_temperature": 0.1,
        "health_check_max_tokens": 10,
    }
    
    try:
        logger.info("🚀 Starting Z-Beam Generator - With Metadata")
        logger.info("✅ Configuration initialized")
        
        # Create content generator
        generator = ContentGenerator(config)
        
        # Pass PRIMARY USER SETTINGS to generator
        context = {
            "materialType": material,
            "authorId": authorId,
            "articleType": articleType  # ✅ Changed from article_type
        }
        
        # Generate article with metadata
        article = generator.generate_article(context)
        
        # Save output
        output_dir = Path(config["output_directory"])
        output_dir.mkdir(exist_ok=True)
        
        output_file = output_dir / f"{material.lower()}_laser_cleaning.mdx"
        
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(article)
        
        logger.info(f"✅ Article saved to: {output_file}")
        logger.info(f"📊 Final article: {len(article.split())} words")
        
    except Exception as e:
        logger.error(f"❌ Generation failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()