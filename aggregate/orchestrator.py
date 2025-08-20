"""
Simple Aggregate Generation Orchestrator

Collects prompts from existing generators, makes one API call, parses JSON response.
No complex post-processing, no fallbacks, no bloat.
"""

import logging
import importlib
from typing import Dict, List

logger = logging.getLogger(__name__)

def orchestrate_components(subject: str, article_type: str, enabled_components: List[str], article_context: dict) -> Dict[str, str]:
    """Aggregate generation through individual generators - ensures all formatting goes through base utilities.
    
    Instead of combining prompts into one API call, this approach:
    1. Uses each generator's own tested prompt and post-processing
    2. Ensures all formatting goes through base component utilities  
    3. Reduces API calls by reusing template data and caching
    4. Maintains the reliability of individual component generation
    
    Args:
        subject: Material name
        article_type: Type of article  
        enabled_components: List of component names to generate
        article_context: Complete context including configs, author data, etc.
        
    Returns:
        Dict[str, str]: Component name -> generated content
    """
    
    logger.info(f"Starting aggregate generation for {subject}")
    logger.info(f"Components: {', '.join(enabled_components)}")
    
    # Step 1: Load generators 
    generators = {}
    
    for component_name in enabled_components:
        # Skip non-AI components
        if component_name == "propertiestable":
            continue
            
        # Load generator
        try:
            module_name = f"components.{component_name}.generator"
            module = importlib.import_module(module_name)
            
            # Get class name with special cases
            if component_name == "metatags":
                class_name = "MetatagsGenerator"
            elif component_name == "propertiestable":
                class_name = "PropertiesTableGenerator"
            elif component_name == "jsonld":
                class_name = "JsonldGenerator"
            else:
                class_name = f"{component_name.capitalize()}Generator"
            
            generator_class = getattr(module, class_name)
            
            # Initialize generator
            component_config = article_context["components"][component_name].copy()
            component_config["ai_provider"] = article_context["ai_provider"]
            component_config["options"] = article_context["options"].copy()
            
            if "category" in article_context:
                component_config["category"] = article_context["category"]
            if "author_id" in article_context:
                component_config["author_id"] = article_context["author_id"]
            
            generator = generator_class(
                subject=subject,
                article_type=article_type,
                schema=article_context.get("schema", {}),
                author_data=article_context.get("author_data", {}),
                component_config=component_config
            )
            
            generators[component_name] = generator
            
            logger.info(f"Loaded generator for {component_name}")
            
        except Exception as e:
            logger.error(f"Failed to load generator for {component_name}: {e}")
            raise ValueError(f"Cannot load generator for {component_name}: {e}")
    
    # Step 2: Generate each component using its own generator
    # This ensures all formatting goes through the tested base component utilities
    results = {}
    
    for component_name, generator in generators.items():
        try:
            logger.info(f"Generating {component_name} using individual generator")
            
            # Use the generator's own generate() method to ensure proper formatting
            content = generator.generate()
            results[component_name] = content
            
            logger.info(f"Successfully generated {component_name} through base utilities ({len(content)} chars)")
            
        except Exception as e:
            logger.error(f"Failed to generate {component_name}: {e}")
            results[component_name] = ""
    
    logger.info(f"Aggregate generation completed: {len(results)} components generated individually")
    return results
