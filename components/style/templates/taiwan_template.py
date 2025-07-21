"""Taiwan-specific writing template."""

from typing import Dict, Any

def get_style_characteristics() -> Dict[str, Any]:
    """Get Taiwan-specific style characteristics."""
    return {
        "writing_style": "precise and methodical with careful attention to technical details",
        "paragraph_structure": "builds from specific to general conclusions",
        "terminology": "formal academic terminology with occasional Chinese technical terms",
        "cultural_references": "references to Taiwanese precision manufacturing and semiconductor industry",
        "template": "taiwan"
    }

def get_country_prompt_enhancement(author_name: str, params: Dict[str, Any] = None) -> str:
    """Get Taiwan-specific prompt enhancement with parameters.
    
    Args:
        author_name: Name of the author
        params: Additional parameters including word count
        
    Returns:
        Taiwan-specific prompt enhancement
    """
    if params is None:
        params = {}
        
    # Extract schema
    schema = params.get("schema", {})
    
    # Get word count with fallback chain
    max_word_count = (
        params.get("max_word_count") or 
        schema.get("word_counts", {}).get("author_1") or
        schema.get("default_word_count") or
        400  # Last resort fallback
    )
    
    # Return Taiwan-specific enhancement with dynamic values
    return f"""
Incorporate a Taiwanese academic perspective into {author_name}'s writing with these elements:

STYLE CHARACTERISTICS:
- Write as a knowledgeable Taiwanese materials scientist with personal research experience
- Use varied sentence structures: mix short, direct statements with longer, complex analyses
- Incorporate occasional personal observations or lab experiences (e.g., "In our laboratory tests...")
- Use asymmetrical paragraph lengths (some short, some long) like human writing
- Keep the total article length under {max_word_count} words

CONTENT APPROACH:
- Begin with broad concepts, then move to specific technical details
- Reference Taiwanese manufacturing standards and compare them to international standards
- Incorporate relevant Taiwanese companies or research institutions by name (e.g., ITRI, TSMC)
- Include footnotes or parenthetical citations to actual academic papers
- Add occasional tangential but relevant observations (humans often take brief detours)

LANGUAGE ELEMENTS:
- Include 2-3 Chinese technical terms with translations in parentheses
- Use occasional passive voice constructions (natural in academic writing)
- Vary terminology rather than using the same technical term repeatedly
- Include a few uncommon but precisely accurate technical terms
- Occasionally repeat key points with slightly different wording

DISTINCTIVE FEATURES:
- Include at least one personal opinion or assessment of a technical approach
- Reference the Journal of Laser Applications or other relevant Taiwan-connected publications
- Mention how techniques relate to Taiwan's semiconductor or precision manufacturing industry
- Add one rhetorical question in the content (humans often pose these)
- Include at least one mild criticism of a common approach (humans are critical)
"""