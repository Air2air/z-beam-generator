"""Country-specific writing style configurations."""

from typing import Dict, Any

# Country style guides
COUNTRY_STYLES = {
    "taiwan": {
        "writing_style": "precise and methodical with careful attention to technical details",
        "paragraph_structure": "builds from specific to general conclusions",
        "terminology": "formal academic terminology with occasional Chinese technical terms",
        "cultural_references": "references to Taiwanese precision manufacturing and semiconductor industry",
        "template": "taiwan"
    },
    
    "italy": {
        "writing_style": "expressive and practical with emphasis on craftsmanship",
        "paragraph_structure": "alternates between practical examples and technical explanations",
        "terminology": "accessible technical language with occasional Italian industrial terms",
        "cultural_references": "references to Italian design principles and manufacturing heritage",
        "template": "italy"
    },
    
    "usa": {
        "writing_style": "direct and business-focused with emphasis on results",
        "paragraph_structure": "begins with key points and expands with supporting details",
        "terminology": "straightforward business and technical language",
        "cultural_references": "references to American industrial standards and aerospace applications",
        "template": "usa"
    },
    
    "indonesia": {
        "writing_style": "respectful and thorough with collective emphasis",
        "paragraph_structure": "provides context before introducing technical concepts",
        "terminology": "clear technical explanations with some Indonesian industry terms",
        "cultural_references": "references to Indonesian manufacturing growth and regional applications",
        "template": "indonesia"
    }
}

def get_country_style(country: str) -> Dict[str, Any]:
    """Get style guide for a specific country."""
    # Normalize country name to lowercase
    country_lower = country.lower()
    
    if country_lower in COUNTRY_STYLES:
        return COUNTRY_STYLES[country_lower]
    
    # Return US style as default if country not found
    return COUNTRY_STYLES["usa"]