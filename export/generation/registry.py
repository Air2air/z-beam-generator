"""
Generator Registry and Base Classes

Plugin system for generating derived content in frontmatter.
Part of Export System Consolidation (Phase 1).

Generators create new content from existing frontmatter fields:
- SEO descriptions from long descriptions
- Breadcrumbs from category/subcategory
- Excerpts from full content
- etc.

Example:
    SEODescriptionGenerator reads 'contamination_description' field,
    truncates intelligently, and writes to 'seo_description' field.

Architecture:
- GENERATOR_REGISTRY: Maps generator type string → class
- BaseGenerator: Abstract base for all generators
- Specific generators: SEODescriptionGenerator, BreadcrumbGenerator, etc.

Usage:
    from export.generation.registry import create_generators
    
    configs = [
        {
            'type': 'seo_description',
            'source_field': 'contamination_description',
            'output_field': 'seo_description',
            'max_length': 160
        }
    ]
    
    generators = create_generators(configs)
    for generator in generators:
        frontmatter = generator.generate(frontmatter)
"""

from typing import Dict, Any, List
import logging
import re

# Import base generator class
from export.generation.base import BaseGenerator

# Import domain linkages generator
from export.generation.relationships_generator import DomainLinkagesGenerator

# Import contaminant materials grouping generator
from export.generation.contaminant_materials_grouping_generator import ContaminantMaterialsGroupingGenerator

# Import field cleanup generator
from export.generation.field_cleanup_generator import FieldCleanupGenerator

logger = logging.getLogger(__name__)


class SEODescriptionGenerator(BaseGenerator):
    """
    Generate SEO meta descriptions from content fields.
    
    Takes a long description field (e.g., 'contamination_description'),
    truncates intelligently at word boundaries, and creates a concise
    SEO-friendly description (~160 characters).
    
    Features:
    - Truncates at word boundary (not mid-word)
    - Adds ellipsis if truncated
    - Strips HTML tags (if present)
    - Preserves first sentence if possible
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize SEO description generator.
        
        Args:
            config: Config with keys:
                - source_field: Field to read from (e.g., 'description')
                - output_field: Field to write to (e.g., 'seo_description')
                - max_length: Maximum characters (default: 160)
        
        Raises:
            ValueError: If required config keys missing
        """
        super().__init__(config)
        
        if 'source_field' not in config or 'output_field' not in config:
            raise ValueError(
                "SEODescriptionGenerator requires 'source_field' and 'output_field'"
            )
        
        self.source_field = config['source_field']
        self.output_field = config['output_field']
        self.max_length = config.get('max_length', 160)
    
    def generate(self, frontmatter: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate SEO description from source field.
        
        Args:
            frontmatter: Input frontmatter dict
        
        Returns:
            Frontmatter with SEO description added
        """
        # Check if source field exists
        if self.source_field not in frontmatter:
            logger.debug(
                f"Source field '{self.source_field}' not found, "
                f"skipping SEO generation"
            )
            return frontmatter
        
        source_text = frontmatter[self.source_field]
        if not source_text:
            return frontmatter
        
        # Generate SEO description
        seo_description = self._create_seo_description(source_text)
        frontmatter[self.output_field] = seo_description
        
        logger.debug(
            f"Generated SEO description ({len(seo_description)} chars) "
            f"from '{self.source_field}'"
        )
        
        return frontmatter
    
    def _create_seo_description(self, text: str) -> str:
        """
        Create SEO-optimized description from text.
        
        Args:
            text: Source text (long description)
        
        Returns:
            SEO description (~160 chars, word-boundary truncated)
        """
        # Strip HTML tags if present
        text = re.sub(r'<[^>]+>', '', text)
        
        # Remove excess whitespace
        text = ' '.join(text.split())
        
        # If already short enough, return as-is
        if len(text) <= self.max_length:
            return text
        
        # Try to use first sentence if short enough
        first_sentence = text.split('.')[0] + '.'
        if len(first_sentence) <= self.max_length:
            return first_sentence
        
        # Truncate at word boundary
        truncated = text[:self.max_length].rsplit(' ', 1)[0]
        return truncated.rstrip(',.;:') + '...'


class ExcerptGenerator(BaseGenerator):
    """
    Generate short excerpts from long content.
    
    Similar to SEO description but for general-purpose excerpts
    (first paragraph, first N sentences, etc.).
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize excerpt generator.
        
        Args:
            config: Config with keys:
                - source_field: Field to read from
                - output_field: Field to write to
                - mode: 'sentences' or 'words' or 'characters'
                - length: Number of sentences/words/characters
        """
        super().__init__(config)
        
        if 'source_field' not in config or 'output_field' not in config:
            raise ValueError(
                "ExcerptGenerator requires 'source_field' and 'output_field'"
            )
        
        self.source_field = config['source_field']
        self.output_field = config['output_field']
        self.mode = config.get('mode', 'sentences')
        self.length = config.get('length', 2)
    
    def generate(self, frontmatter: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate excerpt from source field.
        
        Args:
            frontmatter: Input frontmatter dict
        
        Returns:
            Frontmatter with excerpt added
        """
        if self.source_field not in frontmatter:
            return frontmatter
        
        source_text = frontmatter[self.source_field]
        if not source_text:
            return frontmatter
        
        # Generate excerpt based on mode
        if self.mode == 'sentences':
            excerpt = self._extract_sentences(source_text, self.length)
        elif self.mode == 'words':
            excerpt = self._extract_words(source_text, self.length)
        elif self.mode == 'characters':
            excerpt = self._extract_characters(source_text, self.length)
        else:
            logger.warning(f"Unknown excerpt mode: {self.mode}")
            return frontmatter
        
        frontmatter[self.output_field] = excerpt
        logger.debug(f"Generated excerpt ({len(excerpt)} chars)")
        
        return frontmatter
    
    def _extract_sentences(self, text: str, num_sentences: int) -> str:
        """Extract first N sentences."""
        sentences = re.split(r'[.!?]+', text)
        sentences = [s.strip() for s in sentences if s.strip()]
        excerpt = '. '.join(sentences[:num_sentences]) + '.'
        return excerpt
    
    def _extract_words(self, text: str, num_words: int) -> str:
        """Extract first N words."""
        words = text.split()
        excerpt = ' '.join(words[:num_words])
        if len(words) > num_words:
            excerpt += '...'
        return excerpt
    
    def _extract_characters(self, text: str, num_chars: int) -> str:
        """Extract first N characters at word boundary."""
        if len(text) <= num_chars:
            return text
        truncated = text[:num_chars].rsplit(' ', 1)[0]
        return truncated + '...'


# Registry mapping generator type → class
GENERATOR_REGISTRY = {
    'seo_description': SEODescriptionGenerator,
    'excerpt': ExcerptGenerator,
    'relationships': DomainLinkagesGenerator,
    'contaminant_materials_grouping': ContaminantMaterialsGroupingGenerator,  # Change 4: Dec 19, 2025
    'field_cleanup': FieldCleanupGenerator,  # Changes 2 & 5: Dec 19, 2025
}


def create_generators(configs: List[Dict[str, Any]]) -> List[BaseGenerator]:
    """
    Create generator instances from config list.
    
    Args:
        configs: List of generator configs from domain YAML
            Each config needs 'type' key matching GENERATOR_REGISTRY
    
    Returns:
        List of initialized generator instances (in config order)
    
    Raises:
        ValueError: If generator type not found in registry
    
    Example:
        configs = [
            {
                'type': 'seo_description',
                'source_field': 'description',
                'output_field': 'seo_description'
            },
            {
                'type': 'breadcrumb',
                'template': 'Home / Materials / {category}'
            }
        ]
        generators = create_generators(configs)
    """
    generators = []
    
    for config in configs:
        generator_type = config.get('type')
        
        if not generator_type:
            logger.warning(f"Generator config missing 'type': {config}")
            continue
        
        if generator_type not in GENERATOR_REGISTRY:
            raise ValueError(
                f"Unknown generator type: {generator_type}\n"
                f"Available types: {', '.join(GENERATOR_REGISTRY.keys())}"
            )
        
        generator_class = GENERATOR_REGISTRY[generator_type]
        generator = generator_class(config)
        generators.append(generator)
        
        logger.debug(f"Created generator: {generator_class.__name__}")
    
    return generators
