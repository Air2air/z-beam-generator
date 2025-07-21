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

# Define the primary article context - THE ONLY SOURCE OF TRUTH
ARTICLE_CONTEXT = {
    # Core article parameters
    "subject": "magnesium",
    "article_type": "material",
    "ai_provider": "deepseek",
    
    # Components configuration with provider settings
    "components": {
        "frontmatter": {
            "enabled": True,
            "include_website": True,
            "provider": "deepseek"
        },
        "content": {
            "enabled": True,
            "min_words": 300,
            "max_words": 500,
            "paragraphs": 3,
            "provider": "deepseek"
        },
        "bullets": {
            "enabled": True,
            "count": 5,
            "style": "technical",
            "provider": "deepseek"
        },
        "table": {
            "enabled": True,
            "style": "technical",
            "include_units": True,
            "provider": "deepseek"
        },
        "tags": {
            "enabled": True,
            "max_count": 10,
            "provider": "deepseek"
        },
        "jsonld": {
            "enabled": True,
            "provider": "deepseek"
        }
    },
    
    # Output configuration
    "output_dir": "output"
}

def setup_environment() -> None:
    """Set up the application environment."""
    # Load environment variables
    load_env_variables()
    
    # Configure logging
    configure_logging()
    
    # Ensure required directories exist
    PathManager.ensure_directories()
    
    # Validate API keys for all providers in ARTICLE_CONTEXT
    check_api_keys(ARTICLE_CONTEXT)

def check_api_keys(context=None):
    """Check if required API keys are set for all providers used in ARTICLE_CONTEXT.
    
    Args:
        context: Optional context dictionary. If not provided,
                will use the global ARTICLE_CONTEXT.
    """
    # Use provided context or fall back to ARTICLE_CONTEXT
    context = context or ARTICLE_CONTEXT
    
    # Map providers to their environment variable keys
    provider_keys = {
        "deepseek": "DEEPSEEK_API_KEY",
        "openai": "OPENAI_API_KEY",
        "gemini": "GEMINI_API_KEY",
        "xai": "XAI_API_KEY"
    }
    
    # Collect all providers used in the context
    providers = set()
    
    # Add main provider
    main_provider = context.get("ai_provider")
    if main_provider:
        providers.add(main_provider)
    
    # Add component-specific providers
    components = context.get("components", {})
    for component_name, component_config in components.items():
        if isinstance(component_config, dict) and "provider" in component_config:
            providers.add(component_config["provider"])
    
    # Check each provider's API key
    for provider in providers:
        if provider in provider_keys:
            key_name = provider_keys[provider]
            key_value = os.environ.get(key_name)
            
            if not key_value:
                logging.error(f"API key missing for {provider}: {key_name}")
                raise ValueError(f"Required API key not set: {key_name}")
            elif len(key_value) < 20:
                logging.warning(f"API key for {provider} seems unusually short")

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
    try:
        # Set up environment
        setup_environment()
        
        # Validate ARTICLE_CONTEXT
        from utils.config_validator import ConfigValidator
        is_valid, errors = ConfigValidator.validate_context(ARTICLE_CONTEXT)
        if not is_valid:
            for error in errors:
                logging.error(f"Configuration error: {error}")
            raise ValueError("Invalid ARTICLE_CONTEXT configuration")
        
        # Create article assembler
        assembler = ArticleAssembler(
            subject=ARTICLE_CONTEXT["subject"],
            article_type=ARTICLE_CONTEXT["article_type"],
            config=ARTICLE_CONTEXT,
            ai_provider=ARTICLE_CONTEXT["ai_provider"]
        )
        
        # Generate article
        output_path = assembler.generate_article()
        
        if output_path:
            print(f"✅ Article generated successfully: {output_path}")
        else:
            print("❌ Failed to generate article. Check logs for details.")
            sys.exit(1)
            
    except Exception as e:
        from utils.error_handler import ErrorHandler
        ErrorHandler.handle_application_error("main", e)
        sys.exit(1)

if __name__ == '__main__':
    main()
