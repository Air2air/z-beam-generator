"""
Base class for all JSON-LD generators."""

import logging
import re
from datetime import datetime
from typing import Dict, Any, List

logger = logging.getLogger(__name__)

class BaseTypeGenerator:
    """Base generator for JSON-LD data."""
    
    def __init__(self, subject: str, frontmatter: Dict[str, Any] = None):
        """Initialize the generator."""
        self.subject = subject
        self.frontmatter = frontmatter or {}
    
    def generate_jsonld(self, frontmatter: Dict[str, Any] = None) -> Dict[str, Any]:
        """Generate JSON-LD for this article."""
        # This should be implemented by subclasses
        raise NotImplementedError("Subclasses must implement generate_jsonld()")
    
    def _normalize_text(self, text: str) -> str:
        """Normalize text to handle special Unicode characters and formatting.
        
        Args:
            text: Text to normalize
            
        Returns:
            Normalized text with proper Unicode characters
        """
        if not isinstance(text, str):
            text = str(text)
            
        # Replace Unicode escape sequences with actual Unicode characters
        # Common characters in scientific and technical specifications
        replacements = {
            r'\\u00b0': '°',  # degree symbol
            r'\\u00b5': 'μ',  # micro symbol
            r'\\u00b1': '±',  # plus-minus symbol
            r'\\u2013': '–',  # en dash
            r'\\u2014': '—',  # em dash
            r'\\u00d7': '×',  # multiplication symbol
            r'\\u03bc': 'μ',  # Greek mu (alternative)
            r'\\u2082': '₂',  # subscript 2 (for CO₂)
            r'\u00b0': '°',   # degree symbol (without extra escape)
            r'\u00b5': 'μ',   # micro symbol (without extra escape)
            r'\u00b1': '±',   # plus-minus symbol (without extra escape)
            r'\u2013': '–',   # en dash (without extra escape)
            r'\u2014': '—',   # em dash (without extra escape)
            r'\u00d7': '×',   # multiplication symbol (without extra escape)
            r'\u03bc': 'μ',   # Greek mu (alternative without extra escape)
            r'\u2082': '₂',   # subscript 2 (for CO₂, without extra escape)
            r'CO2': 'CO₂',    # Common chemical formula
            r'um': 'μm',      # Common incorrect micro unit
        }
        
        # Replace Unicode escape sequences
        for pattern, replacement in replacements.items():
            text = text.replace(pattern, replacement)
        
        # Fix spacing issues in measurements
        text = text.replace(" °C", "°C").replace(" µm", "µm")
        
        # Fix double periods that might appear when joining sentences
        text = text.replace("..", ".").replace(" .", ".")
        
        return text
        
    def _get_frontmatter_value(self, frontmatter: Dict[str, Any], key: str, default: Any = None) -> Any:
        """Get value from frontmatter safely."""
        return frontmatter.get(key, default)
    
    def _get_nested_value(self, data: Dict[str, Any], key: str, default: Any = None) -> Any:
        """Get nested value from dictionary."""
        if not isinstance(data, dict):
            return default
        return data.get(key, default)
    
    def _get_current_date(self) -> str:
        """Get current date in YYYY-MM-DD format."""
        return datetime.now().strftime("%Y-%m-%d")
    
    def _get_slug(self, frontmatter: Dict[str, Any]) -> str:
        """Get URL slug from frontmatter or generate one."""
        if "slug" in frontmatter:
            return frontmatter["slug"]
        name = frontmatter.get("name", self.subject)
        return name.lower().replace(" ", "-")
    
    def _format_keywords(self, keywords: Any, article_type: str = None, subject: str = None) -> str:
        """Format keywords as comma-separated string with type-specific defaults."""
        subject = subject or self.subject
        
        if isinstance(keywords, str):
            return keywords
        
        if isinstance(keywords, list) and keywords:
            return ", ".join(keywords)
        
        # Type-specific default keywords
        if article_type == "material":
            return f"{subject} laser cleaning, {subject} surface preparation, laser ablation, contaminant removal"
        elif article_type == "application":
            return f"{subject} applications, laser cleaning technology, surface treatment, industrial cleaning"
        elif article_type == "thesaurus":
            return f"{subject}, laser cleaning glossary, technical terminology, industrial laser definition"
        
        return f"{subject} laser cleaning"
    
    def _format_property_name(self, key: str) -> str:
        """Convert camelCase property name to Title Case."""
        result = ""
        for i, char in enumerate(key):
            if char.isupper() and i > 0:
                result += " " + char
            else:
                result += char
        return result.strip().capitalize()
    
    def _build_url(self, slug: str, article_type: str) -> str:
        """Build URL for article with consistent patterns."""
        base_url = "https://www.z-beam.com"
        
        if article_type == "material":
            return f"{base_url}/{slug}-laser-cleaning"
        elif article_type == "application":
            return f"{base_url}/{slug}-laser-cleaning"
        elif article_type == "thesaurus":
            return f"{base_url}/{slug}"
        else:
            # Default with article type as a path component
            return f"{base_url}/{slug}-laser-cleaning"