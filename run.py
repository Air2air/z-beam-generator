#!/usr/bin/env python3
"""
Z-Beam Generator - Schema-Driven Article Generation
"""

# ===== EDIT THESE VALUES =====
context = {
    "article_type": "material",     # Options: material, application, region, thesaurus
    "subject": "steel",             # Subject matches article type (material name, app name, city, term)
    "author_id": 3,
    "provider": "DEEPSEEK",
}
# ===== END EDITABLE SECTION =====

import logging
from generator import generate_article
from config.constants import CONFIG
from setup_logging import setup_logging


def main():
    """Generate article with schema-driven context"""
    logger = setup_logging()

    config = CONFIG.get_full_config()
    config["provider"] = context.get("provider", "DEEPSEEK")

    logger.info("🚀 STARTING SCHEMA-DRIVEN ARTICLE GENERATION")
    logger.info(f"📄 {context['article_type'].upper()}: {context['subject']}")
    logger.info(f"🎯 Article Type: {context['article_type']} | Subject: {context['subject']}")

    try:
        output_file = generate_article(context, config)
        logger.info(f"✅ COMPLETED: {output_file}")
    except Exception as e:
        logger.error(f"❌ FAILED: {e}")
        raise


if __name__ == "__main__":
    main()


# ===== CONTEXT EXAMPLES FOR DIFFERENT ARTICLE TYPES =====
"""
# Material article - subject IS the material
context = {
    "article_type": "material",
    "subject": "steel",          # Material name
    "author_id": 3,
    "provider": "DEEPSEEK",
}

# Application article - no specific material needed
context = {
    "article_type": "application",
    "subject": "TurbineBlades",  # Application name
    "author_id": 2,
    "provider": "DEEPSEEK",
}

# Region article - needs material specification
context = {
    "article_type": "region", 
    "subject": "Fremont",        # Region name
    "material": "steel",         # Material focus for region
    "author_id": 1,
    "provider": "DEEPSEEK",
}

# Thesaurus article - no specific material needed
context = {
    "article_type": "thesaurus",
    "subject": "LaserAblation",  # Technical term
    "author_id": 4,
    "provider": "DEEPSEEK",
}
"""
