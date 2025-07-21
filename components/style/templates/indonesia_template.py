"""Indonesia-specific writing template."""

from typing import Dict, Any

def get_style_characteristics() -> Dict[str, Any]:
    """Get Indonesia-specific style characteristics."""
    return {
        "writing_style": "respectful and thorough with collective emphasis",
        "paragraph_structure": "provides context before introducing technical concepts",
        "terminology": "clear technical explanations with some Indonesian industry terms",
        "cultural_references": "references to Indonesian manufacturing growth and regional applications",
        "template": "indonesia"
    }

def get_country_prompt_enhancement(author_name: str, params: Dict[str, Any] = None) -> str:
    """Get Indonesia-specific prompt enhancement with parameters.
    
    Args:
        author_name: Name of the author
        params: Additional parameters including word count
        
    Returns:
        Indonesia-specific prompt enhancement
    """
    if params is None:
        params = {}
        
    # Extract schema
    schema = params.get("schema", {})
    
    # Get word count with fallback chain
    max_word_count = (
        params.get("max_word_count") or 
        schema.get("word_counts", {}).get("author_4") or
        schema.get("default_word_count") or
        600  # Last resort fallback
    )
    
    # Return Indonesia-specific enhancement with dynamic values
    return f"""
Incorporate an Indonesian perspective into {author_name}'s writing with these elements:

STYLE CHARACTERISTICS:
- Write with a respectful and thorough approach that emphasizes collective knowledge
- Provide contextual information before introducing technical concepts
- Use a blend of formal and accessible language to reach diverse audiences
- Occasionally use the collective "we" to emphasize shared understanding
- Keep the total article length under {max_word_count} words

CONTENT APPROACH:
- Reference Indonesia's growing manufacturing sector and regional applications
- Include examples relevant to Southeast Asian industrial development
- Balance technical explanations with practical implementation considerations
- Connect global technologies to local contexts and applications
- Consider sustainability and resource efficiency aspects

LANGUAGE ELEMENTS:
- Include 2-3 Indonesian terms for technical concepts (with translations)
- Use respectful but confident tone throughout the document
- Incorporate figurative language to explain complex concepts
- Include contextual transitions between sections
- Occasionally address the reader directly with considerations or recommendations

DISTINCTIVE FEATURES:
- Reference specific Indonesian industries or regional manufacturing centers
- Include a consideration of how technologies apply in tropical environments
- Mention adaptations required for local implementation
- Add a perspective on capacity building or knowledge transfer
- Reference how the technology connects to Indonesia's industrial development goals
"""