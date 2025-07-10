#!/usr/bin/env python3
"""
Z-Beam Generator - Simplified with GlobalConfigManager
"""
import argparse
import logging
from pathlib import Path
from generator import generate_article

def setup_logging(config):
    """Setup logging configuration"""
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)
    
    from datetime import datetime
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_file = log_dir / f"zbeam_{timestamp}.log"
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler()
        ]
    )
    
    logger = logging.getLogger("setup_logging")
    logger.info(f"📝 Logging initialized - File: {log_file}")
    return logger

def parse_arguments():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(description="Generate Z-Beam articles")
    parser.add_argument("--material", "-m", help="Material to generate article for")
    parser.add_argument("--author", "-a", type=int, help="Author ID (1-4)")
    parser.add_argument("--optimization", "-o", choices=["writing_samples", "iterative"], 
                       help="Optimization method")
    return parser.parse_args()

def load_config():
    """Load configuration - for now returns the hardcoded config"""
    return get_config()[0]

def get_config():
    """Get configuration and context for generator"""
    
    # User settings
    context = {
        "material": "hafnium", 
        "author_id": 2, 
        "article_type": "material"
    }

    # Initialize configuration
    config = {
        "provider": "OPENAI",  # Options: OPENAI, XAI, GEMINI, DEEPSEEK
        "model": "gpt-4-turbo",
        "temperature": 0.9,  # Lower from 0.7 to reduce AI-sounding language
        "metadata_temperature": 0.3,
        "max_tokens": 4000,
        
        # Optimization settings
        "optimization_method": "writing_samples",  # or "iterative"
        "iterative_optimizer_file": "optimizers/iterative_optimizer.py",
        "writing_samples_optimizer_file": "optimizers/writing_samples_optimizer.py",
        
        "prompts_dir": "prompts",
        "output_dir": "output",
        "authors_file": "prompts/authors/authors.json",
        "sections_file": "prompts/text/sections.json",
        
        # Section length limits
        "max_section_words": 150,
        "target_section_words": 120,
        "max_total_words": 1200,
        
        # AI Detection Settings - ADDED:
        "zerogpt_enabled": False,
        "target_ai_score": 30,
        "sapling_api_key": None,
        "winston_api_key": None,
        "contentatscale_api_key": None,
        
        # Default material for fallback
        "default_material": "titanium",
        
        # Debug settings
        "debug_prompts": True,
        "debug_responses": True,
        "debug_content_flow": True,
        
        # Similarity thresholds for delta analysis
        "high_similarity_threshold": 0.95,
        "low_similarity_threshold": 0.7,
        "final_similarity_threshold": 0.85,
        
        "providers": {
            "OPENAI": {
                "api_key_env": "OPENAI_API_KEY",
                "base_url": "https://api.openai.com/v1",
                "models": {
                    "gpt-4o": "gpt-4o",
                    "gpt-4o-mini": "gpt-4o-mini",
                    "gpt-4-turbo": "gpt-4-turbo",
                    "gpt-3.5-turbo": "gpt-3.5-turbo"
                }
            },
            "XAI": {
                "api_key_env": "XAI_API_KEY",
                "base_url": "https://api.x.ai/v1",
                "models": {
                    "grok-beta": "grok-beta",
                    "grok-vision-beta": "grok-vision-beta"
                }
            },
            "GEMINI": {
                "api_key_env": "GEMINI_API_KEY",
                "base_url": "https://generativelanguage.googleapis.com/v1beta",
                "models": {
                    "gemini-1.5-pro": "gemini-1.5-pro",
                    "gemini-1.5-flash": "gemini-1.5-flash",
                    "gemini-1.5-pro-002": "gemini-1.5-pro-002",
                    "gemini-1.5-flash-002": "gemini-1.5-flash-002"
                }
            },
            "DEEPSEEK": {
                "api_key_env": "DEEPSEEK_API_KEY",
                "base_url": "https://api.deepseek.com/v1",
                "models": {
                    "deepseek-chat": "deepseek-chat",
                    "deepseek-coder": "deepseek-coder",
                    "deepseek-reasoner": "deepseek-reasoner"
                }
            }
        },
        
        # TAG FORMATTING CONFIGURATION
        "tag_formatting": {
            "style": "hashtag",           # Options: hashtag, plain, bullet, numbered
            "separator": ", ",            # Options: ", ", " | ", " • ", "\n"
            "case_format": "title",       # Options: title, lower, upper, camel
            "remove_spaces": True,        # Remove spaces from hashtags
            "prefix": "#",                # Prefix for each tag
            "suffix": "",                 # Suffix for each tag  
            "max_tags_per_line": 6,       # Tags per line before wrapping
            "sort_tags": True,            # Sort alphabetically
            "group_by_category": False,   # Group related tags together
        },
        
        # TAG CONTENT CONFIGURATION  
        "tag_generation": {
            "max_tags": 12,               # Maximum number of tags
            "min_tags": 8,                # Minimum number of tags
            "include_material": True,     # Include material-specific tags
            "include_technical": True,    # Include technical process tags
            "include_industry": True,     # Include industry application tags
            "include_safety": True,       # Include safety-related tags
            "avoid_generic": True,        # Avoid generic tags like "Technology"
        },
    }

    return config, context

def main():
    """Main function to generate article"""
    # Initialize configuration first
    config, context = get_config()
    
    # Setup logging and get logger
    logger = setup_logging(config)
    
    try:
        # Parse command line arguments
        args = parse_arguments()
        
        # Override config with command line arguments
        if args.material:
            config["default_material"] = args.material
            context["material"] = args.material
        if args.author:
            config["default_author"] = args.author
            context["author_id"] = args.author
        if args.optimization:
            config["optimization_method"] = args.optimization
        
        logger.info("🔧 ZBeamGenerator initialized - {}/{}".format(
            config.get('provider', 'unknown'), 
            config.get('model', 'unknown')
        ))
        
        # Log start
        logger.info("🚀 STARTING ARTICLE GENERATION")
        logger.info(f"📄 Material: {context['material']} | Author: {context['author_id']} | Type: {context['article_type']}")
        logger.info(f"🔧 Optimization method: {config.get('optimization_method', 'unknown')}")
        logger.info(f"🤖 Model: {config.get('provider', 'unknown')}/{config.get('model', 'unknown')}")
        
        # Generate article
        output_file = generate_article(context, config)
        
        # Success
        logger.info(f"✅ ARTICLE GENERATION COMPLETED")
        logger.info(f"📁 Output file: {output_file}")
        
    except Exception as e:
        logger.error(f"❌ ARTICLE GENERATION FAILED: {e}")
        raise

if __name__ == "__main__":
    main()
