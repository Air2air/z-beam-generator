#!/usr/bin/env python3
"""
Z-Beam Generator - Simplified execution script
"""

# ===== EDIT THESE VALUES TO CONTROL GENERATION =====

# Article Context
context = {
    "material": "hafnium", 
    "author_id": 3,
    "article_type": "material"
}

# Optimization Order (0=skip, 1=first, 2=second)
optimization_config = {
    'writing_samples': 1,          # Author style
    'iterative': 0,                # Humanization
    'technical_authenticity': 2    # Technical depth
}

# Simple Controls
simple_config = {
    "word_limit": 1200,           # Total words
    "style_intensity": "moderate", # light, moderate, heavy
    "technical_depth": "moderate", # light, moderate, deep
    "temperature": 0.7            # AI creativity (0.3-0.9)
}

# ===== END EDITABLE SECTION =====

import logging
from generator import generate_article
from config.constants import CONFIG
from setup_logging import setup_logging

def main():
    """Main function to generate article"""
    logger = setup_logging()
    
    # Get simple config
    config = CONFIG.get_full_config()
    config.update({
        "optimization_order": [name for name, order in optimization_config.items() if order > 0],
        "simple_config": simple_config
    })
    
    logger.info("🚀 STARTING ARTICLE GENERATION")
    logger.info(f"📄 {context['material']} | Author: {context['author_id']}")
    logger.info(f"🎛️ {' → '.join(config['optimization_order'])}")
    
    try:
        output_file = generate_article(context, config)
        logger.info(f"✅ COMPLETED: {output_file}")
        
    except Exception as e:
        logger.error(f"❌ FAILED: {e}")
        raise

if __name__ == "__main__":
    main()
