#!/usr/bin/env python3
"""
Z-Beam Generator - Main entry point
"""

import logging
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from generator import generate_article
from schemas.schema_registry import list_available_schemas, get_available_types
from config import load_config


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


def main():
    """Main entry point"""
    logger.info("🚀 Starting Z-Beam article generation")

    # Load configuration
    config = load_config()

    # Show available schemas
    available_schemas = list_available_schemas()
    logger.info(f"📋 Available article types: {get_available_types()}")

    # Test context
    context = {
        "article_type": "thesaurus",
        "subject": "copper",
        "author_id": 4,
    }

    try:
        # Generate article
        output_file = generate_article(context, config)

        logger.info(f"✅ Article generated successfully: {output_file}")

        # Show file contents
        with open(output_file, "r", encoding="utf-8") as f:
            content = f.read()
            logger.info(f"📄 Generated content:\n{content[:500]}...")

    except Exception as e:
        logger.error(f"❌ Generation failed: {e}")
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
