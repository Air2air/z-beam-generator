"""Italy-specific writing template."""

from typing import Dict, Any

def get_style_characteristics() -> Dict[str, Any]:
    """Get Italy-specific style characteristics."""
    return {
        "writing_style": "expressive and practical with emphasis on craftsmanship",
        "paragraph_structure": "alternates between practical examples and technical explanations",
        "terminology": "accessible technical language with occasional Italian industrial terms",
        "cultural_references": "references to Italian design principles and manufacturing heritage",
        "template": "italy"
    }

def get_country_prompt_enhancement(author_name: str, params: Dict[str, Any] = None) -> str:
    """Get Italy-specific prompt enhancement with parameters.
    
    Args:
        author_name: Name of the author
        params: Additional parameters including word count
        
    Returns:
        Italy-specific prompt enhancement
    """
    if params is None:
        params = {}
        
    # Extract schema
    schema = params.get("schema", {})
    
    # Get word count with fallback chain
    max_word_count = (
        params.get("max_word_count") or 
        schema.get("word_counts", {}).get("author_2") or
        schema.get("default_word_count") or
        250  # Last resort fallback
    )
    
    # Return Italy-specific enhancement with dynamic values
    return f"""
Incorporate an Italian design and engineering perspective into {author_name}'s writing with these elements:

STYLE CHARACTERISTICS:
- Write as an experienced Italian engineer with practical industry knowledge
- Balance technical precision with expressiveness and emphasis on craftsmanship
- Use varied sentence structures that flow naturally between ideas
- Include occasional passionate opinions about quality and design considerations
- Keep the total article length under {max_word_count} words

CONTENT APPROACH:
- Alternate between practical examples and technical explanations
- Reference Italian design principles of form and function working together
- Include examples relevant to Italian manufacturing expertise
- Connect technical concepts to real-world applications and craftsmanship
- Emphasize the balance between traditional techniques and modern innovation

LANGUAGE ELEMENTS:
- Include 2-3 Italian industrial or technical terms with translations
- Express enthusiasm for elegant engineering solutions
- Use sensory language when describing material properties or processes
- Include rhetorical questions that explore design implications
- Occasionally use first-person plural ("we") to describe industry practices

DISTINCTIVE FEATURES:
- Reference specific Italian industrial standards or manufacturing regions
- Include at least one critique of approaches that prioritize theory over practice
- Mention historical context for techniques when relevant
- Draw connections between aesthetic considerations and technical performance
- Add a brief personal reflection based on hands-on experience
"""