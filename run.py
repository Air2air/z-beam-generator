#!/usr/bin/env python3
"""
Z-Beam content generation system entry point.

MODULE DIRECTIVES FOR AI ASSISTANTS:
1. CONFIGURATION PRECEDENCE: ARTICLE_CONTEXT is the primary configuration source
2. NO CACHING: No caching of resources, data, or objects anywhere in the system
3. FRESH LOADING: Always load fresh data on each access
4. ARTICLE_CONTEXT DRIVEN: All configuration derives from ARTICLE_CONTEXT
5. DYNAMIC COMPONENTS: Use registry to discover and load components
6. ERROR HANDLING: Provide clear error messages with proper logging
7. ENVIRONMENT VARIABLES: Load environment variables from .env file
8. API KEY MANAGEMENT: Check for required API keys and warn if missing
9. SIMPLIFIED INTERFACE: Edit ARTICLE_CONTEXT directly for all configuration
"""

import sys
import os
import logging
from typing import Dict, Any, List, Optional

from assembly.assembler import ArticleAssembler
from utils.registry_factory import RegistryFactory
from utils.config_manager import ConfigManager
from utils.path_manager import PathManager
from utils.log_config import configure_logging
from utils.env_loader import load_env_variables

# Define the primary article context - edit this for all configuration
ARTICLE_CONTEXT = {
    # Core article parameters
    "subject": "magnesium",
    "article_type": "material",
    "ai_provider": "deepseek",
    
    # Control flags
    "list_schemas": False,     # Set to True to list available schemas and exit
    "list_components": False,  # Set to True to list available components and exit
    "use_cli_args": True,      # Set to False to ignore command line arguments
    
    # Output configuration
    "output_dir": "output",    # Directory to save generated articles
    
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

def setup_environment() -> None:
    """Set up the application environment."""
    # Load environment variables
    load_env_variables()
    
    # Configure logging
    configure_logging()
    
    # Ensure required directories exist
    PathManager.ensure_directories()
    
    # Check API keys
    check_api_keys()

def check_api_keys() -> None:
    """Check if required API keys are set."""
    required_keys = ['DEEPSEEK_API_KEY']  # Add others as needed
    missing = [key for key in required_keys if not os.environ.get(key)]
    
    if missing:
        logging.warning("Required API keys missing: %s", ", ".join(missing))
        logging.warning("API operations will fail unless keys are provided")

def list_available_schemas() -> List[str]:
    """List all available schema types."""
    schema_registry = RegistryFactory.schema_registry()
    return schema_registry.list_schemas()

def list_available_components() -> List[str]:
    """List all available components."""
    component_registry = RegistryFactory.component_registry()
    return component_registry.list_components()

def generate_article_from_context(context: Dict[str, Any]) -> Optional[str]:
    """Generate an article from a context dictionary.
    
    Args:
        context: Article context with subject, article_type, etc.
        
    Returns:
        Path to generated article or None if failed
    """
    try:
        # Load base configuration
        config = ConfigManager.load_config()
        
        # Extract key parameters
        subject = context.get("subject", "")
        article_type = context.get("article_type", "material")
        ai_provider = context.get("ai_provider", "deepseek")
        
        # Update assembly configuration with component order from context
        if "component_order" in context:
            if "assembly" not in config:
                config["assembly"] = {}
            config["assembly"]["component_order"] = context["component_order"]
        
        # Update components configuration from context
        if "component_config" in context:
            if "components" not in config:
                config["components"] = {}
                
            for component_name, component_config in context["component_config"].items():
                config["components"][component_name] = component_config
        
        # Update output directory if specified
        output_dir = context.get("output_dir")
        if output_dir:
            if "output" not in config:
                config["output"] = {}
            config["output"]["directory"] = output_dir
        
        # Create article assembler
        assembler = ArticleAssembler(
            subject=subject,
            article_type=article_type,
            config=config,
            ai_provider=ai_provider
        )
        
        # Generate article
        return assembler.generate_article()
        
    except Exception as e:
        logging.error("Error generating article: %s", e, exc_info=True)
        return None

def parse_command_line() -> Dict[str, Any]:
    """Parse command line arguments and return as context overrides.
    
    Returns:
        Dictionary with command line arguments as context overrides
    """
    import argparse
    
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='Z-Beam content generator')
    parser.add_argument('subject', nargs='?', help='Subject of the article')
    parser.add_argument('--type', dest='article_type', help='Article type (e.g., material, region)')
    parser.add_argument('--ai', dest='ai_provider', help='AI provider to use')
    
    args = parser.parse_args()
    
    # Convert to context overrides
    overrides = {}
    if args.subject:
        overrides["subject"] = args.subject
    if args.article_type:
        overrides["article_type"] = args.article_type
    if args.ai_provider:
        overrides["ai_provider"] = args.ai_provider
    
    return overrides

def main() -> None:
    """Main entry point for Z-Beam generator."""
    # Set up environment
    setup_environment()
    
    # Start with the global ARTICLE_CONTEXT
    context = ARTICLE_CONTEXT.copy()
    
    # Apply command line overrides if enabled
    if context.get("use_cli_args", True):
        cli_overrides = parse_command_line()
        context.update(cli_overrides)
    
    # Handle list commands
    if context.get("list_schemas", False):
        schemas = list_available_schemas()
        print("Available schemas:")
        for schema in schemas:
            print(f"  - {schema}")
        return
    
    if context.get("list_components", False):
        components = list_available_components()
        print("Available components:")
        for component in components:
            print(f"  - {component}")
        return
    
    # Generate article
    output_path = generate_article_from_context(context)
    
    if output_path:
        print(f"Article generated successfully: {output_path}")
    else:
        print("Failed to generate article. Check logs for details.")
        sys.exit(1)

if __name__ == '__main__':
    main()
