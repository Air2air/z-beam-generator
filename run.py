#!/usr/bin/env python3
"""
Simplified Run - Uses existing authors.json file
"""

import logging
from pathlib import Path
from datetime import datetime


def setup_logging():
    """Setup logging configuration"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler(log_dir / f"zbeam_{timestamp}.log"),
        ],
    )

    logger = logging.getLogger(__name__)
    logger.info("🚀 Starting Z-Beam article generation")
    return logger


def main():
    """Main execution function"""
    logger = setup_logging()

    # Simple context - article generation parameters
    context = {
        "article_type": "material",
        "subject": "copper",
        "author_id": 4,  # Mario Jordan from authors/authors.json
    }

    # Clean config - only API settings (authors loaded from file)
    config = {
        "api": {
            "provider": "deepseek",
            "model": "deepseek-chat",
            "temperature": 0.7,
        }
    }

    try:
        from generator import generate_article

        output_file = generate_article(context, config)
        logger.info(f"✅ Article generated: {output_file}")

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
