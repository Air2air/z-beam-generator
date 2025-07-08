# run.py
"""
Z-Beam Generator Entry Point - Simplified Configuration
"""

import sys
import logging
from pathlib import Path

# UPDATED IMPORT:
from modules.generation.content_generator import ContentGenerator

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler("z_beam_generator.log"),
    ],
)

logger = logging.getLogger(__name__)

# ---- PROVIDER CONFIGURATION ----
PROVIDER_MODELS = {
    "GEMINI": {
        "model": "gemini-1.5-flash",
        "url_template": "https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent",
    },
    "XAI": {
        "model": "grok-2-1212",
        "url_template": "https://api.x.ai/v1/chat/completions",
    },
    "DEEPSEEK": {
        "model": "deepseek-chat",
        "url_template": "https://api.deepseek.com/v1/chat/completions",
    },
}


# ---- SYSTEM CONFIGURATION ----
def create_config():
    """
    Create complete system configuration - no GlobalConfigManager needed
    """
    return {
        # GENERATION SETTINGS
        "material": "Aluminum",
        "category": "Material",
        "file_name": "aluminum_laser_cleaning.mdx",
        "generation_provider": "XAI",  # Renamed from generator_provider
        "optimization_provider": "XAI",
        "author": "todd_dunning.mdx",
        "force_regenerate": True,
        # PROVIDER CONFIGURATION
        "provider_models": PROVIDER_MODELS,
        # API SETTINGS
        "max_article_words": 800,
        "api_timeout": 60,
        "max_tokens": 4096,
        "overall_timeout": 300,
        "default_section_words": 150,
        "backoff_factor": 2.0,
        # TEMPERATURE SETTINGS (previously hardcoded)
        "generation_temperature": 0.7,  # Was hardcoded in content_generator.py
        "optimization_temperature": 0.3,  # Was hardcoded in optimization_orchestrator.py
        "health_check_temperature": 0.1,  # Was hardcoded in health checks
        "health_check_max_tokens": 10,  # Was hardcoded in health checks
        "health_check_prompt": "Respond with 'OK' if you can process this request.",
        # STEP-SPECIFIC OVERRIDES
        "step_temperatures": {
            "human_naturalness": 0.5,
            "authority_technical_enhancement": 0.2,
            "narrative_authenticity": 0.4,
            "readability_final_polish": 0.3,
        },
        # DIRECTORY PATHS
        "prompts_directory": "prompts",  # Was hardcoded as Path("prompts")
        "sections_directory": "prompts",
        "output_directory": "output",
        # SYSTEM INFO
        "generator_version": "2.0.0-single-pass",
        "supported_categories": [
            "application",
            "author",
            "material",
            "region",
            "thesaurus",
        ],
        # API KEY MAPPINGS
        "api_key_mappings": {
            "GEMINI": "GEMINI_API_KEY",
            "XAI": "XAI_API_KEY",
            "DEEPSEEK": "DEEPSEEK_API_KEY",
        },
    }


class SimpleConfig:
    """
    Simple configuration wrapper - replaces GlobalConfigManager
    """

    def __init__(self, config_dict):
        self.config = config_dict

    def get(self, key, default=None):
        """Get configuration value"""
        return self.config.get(key, default)

    def __getitem__(self, key):
        """Allow dict-style access"""
        return self.config[key]

    def __contains__(self, key):
        """Allow 'in' operator"""
        return key in self.config


def main():
    """
    Main execution function - no GlobalConfigManager dependency
    """
    try:
        logger.info("🚀 Starting Z-Beam Generator with simplified configuration")

        # CREATE SIMPLE CONFIG (no GlobalConfigManager)
        config_data = create_config()
        config = SimpleConfig(config_data)

        logger.info("✅ Configuration initialized")

        # Initialize content generator
        generator = ContentGenerator(config)

        # Generate article
        material = config.get("material")
        logger.info(f"🔧 Generating article for material: {material}")

        article = generator.generate_article(material)

        # Create output directory if it doesn't exist
        output_dir = Path(config.get("output_directory", "output"))
        output_dir.mkdir(exist_ok=True)

        # Save article to file
        output_file = output_dir / config.get(
            "file_name", f"{material.lower()}_laser_cleaning.md"
        )
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(article)

        logger.info(f"✅ Article saved to: {output_file}")
        logger.info(f"📊 Article length: {len(article.split())} words")

        return True

    except Exception as e:
        logger.error(f"❌ FATAL ERROR: {e}")
        logger.error("NO FALLBACKS - system must fail fast.")
        return False


if __name__ == "__main__":
    success = main()
    if not success:
        sys.exit(1)