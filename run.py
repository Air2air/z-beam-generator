#!/usr/bin/env python3
"""
Z-Beam Generator - Simplified execution script
"""

# ===== EDIT THESE VALUES TO CONTROL GENERATION =====

# Article Context
context = {
    "material": "hafnium", 
    "author_id": 3,  # Use Todd Dunning (US) for more casual tone
    "article_type": "material"
}

# Simple Optimization Order (0=skip, 1=first, 2=second, 3=third)
optimization_config = {
    'iterative': 0,                # Skip complex iterative
    'writing_samples': 1,          # Apply author style first
    'technical_authenticity': 0    # Skip technical enhancement
}

# ===== END EDITABLE SECTION =====

import logging
from generator import generate_article
from config.constants import CONFIG
from setup_logging import setup_logging

def main():
    """Main function to generate article"""
    # Setup logging
    logger = setup_logging()
    
    # Get simple config
    config = CONFIG.get_full_config()
    config["optimization_order"] = [name for name, order in optimization_config.items() if order > 0]
    config["use_simple_ordering"] = True
    
    logger.info("🚀 STARTING ARTICLE GENERATION")
    logger.info(f"📄 Material: {context['material']} | Author: {context['author_id']}")
    logger.info(f"🎛️ Optimizations: {' → '.join(config['optimization_order'])}")
    
    try:
        # Generate article
        output_file = generate_article(context, config)
        logger.info(f"✅ COMPLETED: {output_file}")
        
    except Exception as e:
        logger.error(f"❌ FAILED: {e}")
        raise

if __name__ == "__main__":
    main()
