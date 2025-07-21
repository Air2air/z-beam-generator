"""USA-specific writing template."""

from typing import Dict, Any

def get_style_characteristics() -> Dict[str, Any]:
    """Get USA-specific style characteristics."""
    return {
        "writing_style": "direct and business-focused with emphasis on results",
        "paragraph_structure": "begins with key points and expands with supporting details",
        "terminology": "straightforward business and technical language",
        "cultural_references": "references to American industrial standards and aerospace applications",
        "template": "usa"
    }

def get_country_prompt_enhancement(author_name: str, params: Dict[str, Any] = None) -> str:
    """Get USA-specific prompt enhancement with parameters.
    
    Args:
        author_name: Name of the author
        params: Additional parameters including word count
        
    Returns:
        USA-specific prompt enhancement
    """
    if params is None:
        params = {}
        
    # Extract schema
    schema = params.get("schema", {})
    
    # Get word count with fallback chain
    max_word_count = (
        params.get("max_word_count") or 
        schema.get("word_counts", {}).get("author_3") or
        schema.get("default_word_count") or
        500  # Last resort fallback
    )
    
    # Return USA-specific enhancement with dynamic values
    return f"""
Incorporate an American business and engineering perspective into {author_name}'s writing with these elements:

STYLE CHARACTERISTICS:
- Write with a direct, results-oriented approach typical of American technical writing
- Start paragraphs with key points followed by supporting details
- Use straightforward business and technical language
- Include practical industry perspectives based on real-world experience
- Keep the total article length under {max_word_count} words

CONTENT APPROACH:
- Emphasize efficiency, scalability, and return on investment
- Reference American industrial standards (ASTM, ASME, etc.) where relevant
- Include examples from US aerospace, defense, or manufacturing sectors
- Balance technical content with business considerations
- Address practical implementation challenges and their solutions

LANGUAGE ELEMENTS:
- Use industry-standard abbreviations with explanations where needed
- Include quantifiable metrics and performance indicators
- Occasionally use business analogies to explain technical concepts
- Include some informal transitions or phrases (e.g., "Let's consider...")
- Maintain professional terminology but avoid excessive jargon

DISTINCTIVE FEATURES:
- Reference specific US companies, universities, or research institutions
- Include a comparison of competing methodologies with clear trade-offs
- Mention regulatory considerations relevant to US manufacturing
- Add a practical insight from personal industry experience
- Include a forward-looking statement about future developments or applications
"""