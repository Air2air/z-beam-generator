#!/usr/bin/env python3
"""
Z-Beam Generator Runner
Command-line interface to generate articles
"""

import os
import sys  # Add this import
import json
import logging
import argparse
from typing import Dict, Any
from datetime import datetime

# Import local modules
from api_client import APIClient
from generator import ZBeamGenerator
from orchestrator import ArticleOrchestrator
from utils.schema_validator import SchemaValidator

# ========================================
# ARTICLE CONTEXT CONFIGURATION - EDIT THIS SECTION
# ========================================

# Article generation parameters
ARTICLE_CONTEXT = {
    "subject": "hafnium",         # Subject to write about
    "author_id": 2,              # Author style (1-4)
    "article_type": "material"   # application, material, region, thesaurus
}

# ========================================
# END CONFIGURATION
# ========================================

# ========================================
# GENERATION OPTIONS
# ========================================
AUTO_FIX = True           # Automatically fix validation issues
VERBOSE = True            # Show verbose output during generation
FORCE_REGENERATE = False  # Force regeneration even if file exists

# ========================================
# END OPTIONS
# ========================================

# Load environment variables from .env file
load_dotenv()

# Create logs directory if it doesn't exist
os.makedirs('logs', exist_ok=True)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(f'logs/generation_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log'),
        logging.StreamHandler()
    ]
)

def load_config():
    """
    Load configuration from environment variables.
    
    Returns:
        Dict containing API configuration
        
    Raises:
        ValueError: If required environment variables are missing
    """
    config = {
        "provider": os.getenv("PROVIDER", "openai"),
        "model": os.getenv("MODEL", "gpt-4"),
        "openai_api_key": os.getenv("OPENAI_API_KEY"),
        "deepseek_api_key": os.getenv("DEEPSEEK_API_KEY"),
        "gemini_api_key": os.getenv("GEMINI_API_KEY"),
        "xai_api_key": os.getenv("XAI_API_KEY"),
        "anthropic_api_key": os.getenv("ANTHROPIC_API_KEY")
    }
    
    # Check if at least one API key is provided
    api_keys = [key for key in config.values() if key and key.startswith(("sk-", "gsk_", "xai-", "claude-"))]
    if not api_keys:
        raise ValueError("No valid API keys found in environment variables. Please check your .env file.")
    
    return config

def validate_context(context, logger):
    """
    Validate article context before generation.
    
    Args:
        context: The article context dictionary
        logger: Logger instance
        
    Returns:
        True if context is valid, False otherwise
    """
    logger.info("🔍 PRE-VALIDATION: Validating article context...")
    
    issues = []
    
    # Check required context fields
    required_fields = ["subject", "article_type"]
    for field in required_fields:
        if field not in context or not context[field]:
            issues.append(f"Missing required context field: {field}")
    
    # Validate article type
    valid_types = ["application", "material", "region", "thesaurus"]
    if "article_type" in context and context["article_type"] not in valid_types:
        issues.append(f"Invalid article type: {context['article_type']}. Valid types: {valid_types}")
    
    # Validate subject (should be non-empty string)
    if "subject" in context:
        if not isinstance(context["subject"], str) or not context["subject"].strip():
            issues.append(f"Subject must be a non-empty string")
    
    # Validate author_id (should be 1-4)
    if "author_id" in context:
        if not isinstance(context["author_id"], int) or context["author_id"] < 1 or context["author_id"] > 4:
            issues.append(f"Author ID must be an integer between 1 and 4")
    
    # Log validation results
    if issues:
        logger.error("❌ PRE-VALIDATION FAILED:")
        for issue in issues:
            logger.error(f"  - {issue}")
        return False
    
    logger.info("✅ PRE-VALIDATION: Article context is valid")
    return True

def validate_output_file(filepath, logger):
    """
    Validate that the output file exists and is properly formatted.
    
    Args:
        filepath: Path to the output file
        logger: Logger instance
        
    Returns:
        True if the file is valid, False otherwise
    """
    logger.info("🔍 POST-VALIDATION: Validating output file...")
    
    issues = []
    
    # Check file exists
    if not os.path.exists(filepath):
        issues.append(f"Output file does not exist: {filepath}")
        logger.error("❌ POST-VALIDATION FAILED: Output file not found")
        return False
    
    # Check file is not empty
    if os.path.getsize(filepath) == 0:
        issues.append("Output file is empty")
    
    # Check file contains YAML frontmatter
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
            
        if not content.startswith('---'):
            issues.append("Output file does not start with YAML frontmatter (---)")
        
        # Extract and parse frontmatter
        frontmatter_end = content.find('---', 3)
        if frontmatter_end == -1:
            issues.append("YAML frontmatter is not properly closed (missing second ---)")
        else:
            frontmatter_content = content[3:frontmatter_end].strip()
            try:
                frontmatter = yaml.safe_load(frontmatter_content)
                if not isinstance(frontmatter, dict):
                    issues.append("YAML frontmatter is not a valid dictionary")
            except Exception as e:
                issues.append(f"Failed to parse YAML frontmatter: {str(e)}")
        
        # Check for JSON-LD
        if '<script type="application/ld+json">' not in content:
            issues.append("Output file does not contain JSON-LD script tag")
        
        # Basic structure checks
        if '# ' not in content:
            issues.append("Output file does not contain any headings")
        
        if '## Tags' not in content:
            issues.append("Output file does not contain Tags section")
        
        if '## Overview' not in content:
            issues.append("Output file does not contain Overview section")
        
        # Check for Validation Results section - this should be added by the orchestrator
        if '## Validation Results' not in content:
            issues.append("Output file does not contain Validation Results section")
            
    except Exception as e:
        issues.append(f"Failed to read or parse output file: {str(e)}")
    
    # Log validation results
    if issues:
        logger.error("❌ POST-VALIDATION FAILED:")
        for issue in issues:
            logger.error(f"  - {issue}")
        return False
    
    logger.info("✅ POST-VALIDATION: Output file is valid")
    return True

def main():
    """Main function to run the generator"""
    
    # Use the article context from the top of the file
    context = ARTICLE_CONTEXT

    logger = logging.getLogger(__name__)
    logger.info("Starting Z-Beam Generator (Simplified)")

    try:
        # Load configuration from environment variables
        logger.info("Loading configuration from .env file")
        config = load_config()
        
        # Initialize components
        api_client = APIClient(config)
        generator = ZBeamGenerator(api_client, logger)
        orchestrator = ArticleOrchestrator(logger)

        # PRE-VALIDATION: Validate context before proceeding
        if not validate_context(context, logger):
            raise ValueError("Article context validation failed. Please fix the issues and try again.")

        # Generate article
        logger.info(f"Generating {context['article_type']} article for: {context['subject']}")
        result = generator.generate_article(context)

        # Assemble final article with embedded validation
        logger.info("Assembling final article with validation")
        final_article = orchestrator.assemble_article(result)

        # Save output
        output_dir = f"output/{context['article_type']}"
        os.makedirs(output_dir, exist_ok=True)

        filename = f"{context['article_type']}_{context['subject'].lower().replace(' ', '_')}.md"
        filepath = os.path.join(output_dir, filename)

        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(final_article)

        logger.info(f"Article generated successfully: {filepath}")
        logger.info(f"Word count: {len(final_article.split())} words")

        # POST-VALIDATION: Validate the output file
        file_validation = validate_output_file(filepath, logger)

        # Check orchestrator validation status
        orchestrator_validation, validation_issues = orchestrator.get_validation_status()

        # Combined validation status - both must pass
        validation_passed = file_validation and orchestrator_validation

        if not validation_passed:
            logger.warning("=" * 80)
            logger.warning(f"⚠️  VALIDATION FAILED: Issues found in {context['subject']}")
            logger.warning("-" * 80)
            logger.warning(f"📋 See complete validation report in the generated file:")
            logger.warning(f"   {filepath}")
            logger.warning("=" * 80)
            sys.exit(1)  # Exit with error code
        else:
            logger.info("=" * 80)
            logger.info(f"✅ VALIDATION PASSED: {context['subject']} meets all schema requirements")
            logger.info("=" * 80)
            
        # Return validation status code (useful for CI/CD pipelines)
        return 0 if validation_passed else 1

    except ValueError as e:
        logger.error(f"Configuration error: {e}")
        logger.error("Please ensure your .env file contains valid API keys")
        raise
    except Exception as e:
        logger.error(f"Generation failed: {e}")
        raise
        return 2  # Error exit code


if __name__ == "__main__":
    exit_code = main()
    # Uncomment to make the script return validation status to the shell
    # import sys
    # sys.exit(exit_code)
