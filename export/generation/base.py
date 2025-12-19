"""
Base Generator Class

Abstract base class for all content generators in the export system.
Part of Export System Consolidation (Phase 2).

Generators create new content from existing frontmatter fields:
- SEO descriptions from long descriptions
- Breadcrumbs from category/subcategory
- Domain linkages from associations data
- etc.

Architecture:
- BaseGenerator: Abstract base requiring generate() method
- Specific generators: SEODescriptionGenerator, DomainLinkagesGenerator, etc.

Usage:
    class MyGenerator(BaseGenerator):
        def generate(self, frontmatter):
            # Generate content
            frontmatter['new_field'] = computed_value
            return frontmatter
"""

from abc import ABC, abstractmethod
from typing import Any, Dict


class BaseGenerator(ABC):
    """
    Abstract base class for all content generators.
    
    Generators create new fields in frontmatter based on existing fields.
    Each generator receives a config dict and implements generate().
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize generator with configuration.
        
        Args:
            config: Generator config from domain YAML
                Common keys: type, output_field, source_field, etc.
        """
        self.config = config
    
    @abstractmethod
    def generate(self, frontmatter: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate content and add to frontmatter.
        
        Args:
            frontmatter: Input frontmatter dict (modified in place)
        
        Returns:
            Frontmatter with generated content (same object, modified)
            
        Raises:
            Can raise exceptions if generation fails critically
        """
        pass
