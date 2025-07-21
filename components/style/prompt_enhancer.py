"""Enhance prompts with style-specific instructions."""

import importlib
import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)

def enhance_prompt(base_prompt: str, country: str, author: Dict[str, Any], params: Dict[str, Any]) -> str:
    """Enhance a prompt with country-specific style instructions."""
    # Add humanization techniques
    from components.style.humanization.humanizer import get_humanization_instructions
    humanization = get_humanization_instructions(params)
    
    # Add anti-detection techniques
    from components.style.anti_detection.techniques import get_anti_detection_techniques
    anti_detection = get_anti_detection_techniques()
    
    # Get schema from params if available
    schema = params.get("schema", {})
    
    # Word count parameters with clear fallback chain
    max_word_count = (
        params.get("max_word_count") or 
        schema.get("max_word_count") or 
        schema.get("word_counts", {}).get(f"author_{author.get('id', 1)}") or
        schema.get("default_word_count") or
        400  # Last resort fallback
    )
    
    # Other parameters with similar fallback chain
    target_percent = (
        params.get("target_percent") or 
        schema.get("target_percent") or 
        0.85
    )
    
    # Calculate derived values
    target_word_count = int(max_word_count * target_percent)
    paragraphs = params.get("paragraphs", 3)
    words_per_paragraph = params.get("words_per_paragraph", 150)
    
    # Try to get country-specific template
    try:
        # Import template dynamically
        module_name = f"components.style.templates.{country}_template"
        template_module = importlib.import_module(module_name)
        
        # Get country-specific prompt enhancement - pass ALL parameters
        author_name = author.get("name", "")
        country_prompt = template_module.get_country_prompt_enhancement(author_name, params)
        
        # Add word count limit guidance - all from parameters
        word_count_instruction = f"""
WORD COUNT LIMIT:
- MAXIMUM: {max_word_count} words (strict limit, do not exceed)
- TARGET: Aim for {target_word_count} words to stay safely under the maximum
- Structure: This typically means {paragraphs} paragraphs with varied lengths
"""
        
        # Combine all elements
        enhanced_prompt = f"{base_prompt}\n\n# STYLE INSTRUCTIONS\n{country_prompt}\n\n# WORD COUNT\n{word_count_instruction}\n\n# HUMANIZATION\n{humanization}\n\n# AUTHENTICITY\n{anti_detection}"
        
        return enhanced_prompt
        
    except (ImportError, AttributeError) as e:
        logger.warning(f"Failed to load template for {country}: {str(e)}")
        # Return base prompt with generic humanization and word count if template fails
        word_count_instruction = f"\n\nIMPORTANT: Do not exceed {max_word_count} words maximum. Aim for about {target_word_count} words."
        return f"{base_prompt}{word_count_instruction}\n\n# HUMANIZATION\n{humanization}"