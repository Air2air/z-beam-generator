"""Base template for country-specific styles."""

from typing import Dict, Any

def get_style_characteristics() -> Dict[str, Any]:
    """Get base style characteristics."""
    return {
        "writing_style": "clear and technical",
        "paragraph_structure": "logical progression",
        "terminology": "precise technical terminology",
        "cultural_references": "international standards",
        "template": "base"
    }

def get_country_prompt_enhancement(author_name: str) -> str:
    """Get base prompt enhancement."""
    return f"""
Write in a clear, technical style appropriate for {author_name}:
- Use precise technical terminology with proper definitions
- Structure paragraphs logically, progressing from basic to advanced concepts
- Include references to international standards where appropriate
- Maintain a formal, professional tone throughout the document
"""