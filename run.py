#!/usr/bin/env python3
"""Minimal entry point with hardcoded article context."""

import os
import sys
import logging
from assembly.assembler import ArticleAssembler
from utils.env_loader import load_env_variables
from api import get_client  # Updated API import

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

# Define absolute path to output directory
OUTPUT_DIR = "/Users/todddunning/Desktop/Z-Beam/z-beam-generator/output"

# Define your article context here - edit this for each generation
ARTICLE_CONTEXT = {
    "subject": "stainless steel",  # Try a new material
    "author_id": 3,
    "article_type": "material",
    "output_dir": OUTPUT_DIR,
    "ai_provider": "deepseek",
    
    # Specify the component order
    "component_order": [
        "frontmatter",   # Material research data
        "content",       # Main content
        "bullets",       # Key points in bullet format
        "table",         # Data tables
        "tags",          # Tags 
        "jsonld"         # JSON-LD structured data
    ],
    
    # Component-specific configuration
    "component_config": {
        "frontmatter": {
            "enabled": True,
            "include_website": True
        },
        "content": {
            "enabled": True,
            "min_words": 300,
            "max_words": 500,
            "paragraphs": 3
        },
        "bullets": {
            "enabled": True,
            "count": 5,
            "style": "technical"
        },
        "table": {
            "enabled": True,
            "style": "technical",
            "include_units": True
        },
        "tags": {
            "enabled": True,
            "max_count": 10
        },
        "jsonld": {
            "enabled": True
        },
        "chart": {
            "enabled": False
        },
        "author": {
            "enabled": False
        }
    },
    "layout_template": "technical"  # Use the technical template with TOC
}

def check_api_keys():
    """Check if required API keys are set."""
    required_keys = ['DEEPSEEK_API_KEY']  # Add others as needed
    missing = [key for key in required_keys if not os.environ.get(key)]
    
    if missing:
        print("ERROR: Required API keys missing:", ", ".join(missing))
        print("Mocks are disabled - real API keys are required.")
        sys.exit(1)

def main():
    # Load environment variables from .env file
    load_env_variables()
    
    """Main entry point."""
    check_api_keys()
    
    try:
        # Create article assembler
        assembler = ArticleAssembler(ARTICLE_CONTEXT)
        
        # Assemble the article
        success, output_path = assembler.assemble_article()
        
        if success:
            print(f"Article generated successfully: {output_path}")
            sys.exit(0)
        else:
            print("Article generation failed")
            sys.exit(1)
            
    except Exception as e:
        logger.error(f"Error generating article: {e}", exc_info=True)
        print(f"Error: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()
