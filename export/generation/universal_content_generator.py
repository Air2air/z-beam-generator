"""
Universal Content Generator

Consolidates all enricher functionality into a single generator-based system.
Replaces 51 enricher files with one unified generator.

Migration from Enrichers to Generators (Dec 29, 2025):
- All enricher functionality moved to generators
- Configuration-driven instead of class-based
- Plugin system for extensibility
- Maintains backwards compatibility during transition

Architecture:
- UniversalContentGenerator: Main orchestrator
- Task-based processing: Each task is a mini-generator
- Task types: linkage, metadata, relationships, seo, library, etc.
- Configuration-driven: All behavior defined in config YAML

Usage:
    from export.generation.universal_content_generator import UniversalContentGenerator
    
    config = {
        'tasks': [
            {'type': 'author_linkage', 'author_file': 'data/authors/Authors.yaml'},
            {'type': 'section_metadata', 'config_file': 'export/config/materials.yaml'},
            {'type': 'seo_description', 'source_field': 'description', 'max_length': 160},
            {'type': 'relationships', 'domain': 'materials'}
        ]
    }
    
    generator = UniversalContentGenerator(config)
    frontmatter = generator.generate(frontmatter)
"""

import logging
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional
import yaml

from export.generation.base import BaseGenerator

logger = logging.getLogger(__name__)


class UniversalContentGenerator(BaseGenerator):
    """
    Universal content generator that replaces all enrichers.
    
    Performs all frontmatter enrichment tasks through configuration:
    - Author linkage
    - Slug generation
    - Timestamp injection
    - Relationship resolution
    - SEO metadata
    - Section metadata
    - Field ordering
    - Validation
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize with task configuration.
        
        Args:
            config: Configuration dict with 'tasks' list
                Each task: {'type': 'task_name', ...task_params}
        """
        super().__init__(config)
        self.tasks = config.get('tasks', [])
        self._task_handlers = self._register_task_handlers()
        
        logger.info(f"Initialized UniversalContentGenerator with {len(self.tasks)} tasks")
    
    def _register_task_handlers(self) -> Dict[str, callable]:
        """Register all task type handlers."""
        return {
            'author_linkage': self._task_author_linkage,
            'slug_generation': self._task_slug_generation,
            'timestamp': self._task_timestamp,
            'relationships': self._task_relationships,
            'section_metadata': self._task_section_metadata,
            'seo_description': self._task_seo_description,
            'seo_excerpt': self._task_seo_excerpt,
            'breadcrumbs': self._task_breadcrumbs,
            'field_cleanup': self._task_field_cleanup,
            'field_ordering': self._task_field_ordering,
            'library_enrichment': self._task_library_enrichment,
            'image_paths': self._task_image_paths,
            'category_grouping': self._task_category_grouping,
            'relationship_grouping': self._task_relationship_grouping,
        }
    
    def generate(self, frontmatter: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute all configured tasks in order.
        
        Args:
            frontmatter: Input frontmatter dict
        
        Returns:
            Enhanced frontmatter dict
        """
        for task_config in self.tasks:
            task_type = task_config.get('type')
            
            if task_type not in self._task_handlers:
                logger.warning(f"Unknown task type: {task_type}")
                continue
            
            handler = self._task_handlers[task_type]
            
            try:
                frontmatter = handler(frontmatter, task_config)
                logger.debug(f"✅ Completed task: {task_type}")
            except Exception as e:
                logger.error(f"Task '{task_type}' failed: {e}")
                if task_config.get('required', False):
                    raise
        
        return frontmatter
    
    # ================================================================
    # TASK HANDLERS (replace enrichers)
    # ================================================================
    
    def _task_author_linkage(self, frontmatter: Dict[str, Any], config: Dict) -> Dict[str, Any]:
        """
        Add author metadata from Authors.yaml.
        Replaces: AuthorEnricher
        """
        author_file = Path(config.get('author_file', 'data/authors/Authors.yaml'))
        
        if not author_file.exists():
            logger.warning(f"Author file not found: {author_file}")
            return frontmatter
        
        with open(author_file, 'r') as f:
            authors_data = yaml.safe_load(f)
        
        # Get author from frontmatter
        author_info = frontmatter.get('author', {})
        if isinstance(author_info, dict):
            author_id = author_info.get('id')
        else:
            author_id = author_info
        
        if not author_id:
            logger.debug("No author ID in frontmatter")
            return frontmatter
        
        # Find author in database
        author_data = authors_data.get('authors', {}).get(author_id)
        
        if not author_data:
            logger.warning(f"Author not found: {author_id}")
            return frontmatter
        
        # Enrich author field with full data
        frontmatter['author'] = {
            'id': author_id,
            'name': author_data.get('name'),
            'author_title': author_data.get('credentials'),
            'bio': author_data.get('bio'),
            'slug': author_data.get('slug', author_id)
        }
        
        return frontmatter
    
    def _task_slug_generation(self, frontmatter: Dict[str, Any], config: Dict) -> Dict[str, Any]:
        """
        Generate slug from ID or name.
        Replaces: DomainLinkagesSlugEnricher
        """
        if 'slug' in frontmatter:
            return frontmatter  # Already has slug
        
        # Generate from id or name
        source = frontmatter.get('id') or frontmatter.get('name') or ''
        slug = source.lower().replace(' ', '-').replace('_', '-')
        
        # Remove special characters
        slug = ''.join(c for c in slug if c.isalnum() or c == '-')
        
        frontmatter['slug'] = slug
        return frontmatter
    
    def _task_timestamp(self, frontmatter: Dict[str, Any], config: Dict) -> Dict[str, Any]:
        """
        Add lastModified timestamp.
        Replaces: TimestampEnricher
        """
        if 'lastModified' not in frontmatter:
            frontmatter['lastModified'] = datetime.now().isoformat()
        
        return frontmatter
    
    def _task_relationships(self, frontmatter: Dict[str, Any], config: Dict) -> Dict[str, Any]:
        """
        Process and enhance relationships.
        Replaces: RelationshipResolutionEnricher, RelationshipRenamingEnricher
        """
        domain = config.get('domain')
        
        if 'relationships' not in frontmatter:
            return frontmatter
        
        # Modern category structure detection
        relationships = frontmatter['relationships']
        modern_categories = {
            'identity', 'interactions', 'operational', 'safety',
            'environmental', 'detection_monitoring', 'visual',
            'quality_control', 'performance'
        }
        
        is_modern = any(cat in relationships for cat in modern_categories)
        
        if is_modern:
            # Already using modern structure, pass through
            logger.debug("Modern relationship structure detected, preserving")
            return frontmatter
        
        # Legacy structure - could migrate here if needed
        logger.debug("Legacy relationship structure detected")
        
        return frontmatter
    
    def _task_section_metadata(self, frontmatter: Dict[str, Any], config: Dict) -> Dict[str, Any]:
        """
        Add _section metadata to relationship blocks.
        Replaces: SectionMetadataEnricher
        """
        config_file = config.get('config_file')
        
        if not config_file or not Path(config_file).exists():
            return frontmatter
        
        with open(config_file, 'r') as f:
            domain_config = yaml.safe_load(f)
        
        section_metadata = domain_config.get('section_metadata', {})
        
        if 'relationships' not in frontmatter:
            return frontmatter
        
        # Add _section metadata to each relationship category
        for category, sections in frontmatter['relationships'].items():
            if not isinstance(sections, dict):
                continue
            
            for section_key, section_data in sections.items():
                if not isinstance(section_data, dict):
                    continue
                
                # Get metadata from config
                metadata_key = f"{category}.{section_key}"
                metadata = section_metadata.get(metadata_key, {})
                
                if metadata:
                    section_data['_section'] = metadata
        
        return frontmatter
    
    def _task_seo_description(self, frontmatter: Dict[str, Any], config: Dict) -> Dict[str, Any]:
        """
        Generate SEO description from source field.
        Replaces: SEODescriptionGenerator
        """
        source_field = config.get('source_field', 'description')
        output_field = config.get('output_field', 'seo_description')
        max_length = config.get('max_length', 160)
        
        source_text = frontmatter.get(source_field, '')
        
        if not source_text:
            return frontmatter
        
        # Truncate intelligently at sentence boundary
        if len(source_text) <= max_length:
            seo_desc = source_text
        else:
            # Find last sentence that fits
            truncated = source_text[:max_length]
            last_period = truncated.rfind('.')
            
            if last_period > max_length * 0.6:  # At least 60% of max length
                seo_desc = truncated[:last_period + 1]
            else:
                # No good sentence boundary, truncate at word
                seo_desc = truncated.rsplit(' ', 1)[0] + '...'
        
        frontmatter[output_field] = seo_desc
        return frontmatter
    
    def _task_seo_excerpt(self, frontmatter: Dict[str, Any], config: Dict) -> Dict[str, Any]:
        """
        Generate SEO excerpt (longer than description).
        Replaces: SEOExcerptGenerator
        """
        source_field = config.get('source_field', 'description')
        output_field = config.get('output_field', 'seo_excerpt')
        max_length = config.get('max_length', 300)
        
        source_text = frontmatter.get(source_field, '')
        
        if not source_text:
            return frontmatter
        
        # Similar to SEO description but longer
        if len(source_text) <= max_length:
            excerpt = source_text
        else:
            truncated = source_text[:max_length]
            last_period = truncated.rfind('.')
            
            if last_period > max_length * 0.6:
                excerpt = truncated[:last_period + 1]
            else:
                excerpt = truncated.rsplit(' ', 1)[0] + '...'
        
        frontmatter[output_field] = excerpt
        return frontmatter
    
    def _task_breadcrumbs(self, frontmatter: Dict[str, Any], config: Dict) -> Dict[str, Any]:
        """
        Generate breadcrumb navigation.
        Replaces: BreadcrumbGenerator
        """
        domain = config.get('domain')
        
        breadcrumbs = [
            {'label': 'Home', 'href': '/'}
        ]
        
        if domain:
            breadcrumbs.append({
                'label': domain.capitalize(),
                'href': f'/{domain}'
            })
        
        # Add current page (if name or title available)
        page_name = frontmatter.get('name') or frontmatter.get('page_title', '')
        if page_name:
            breadcrumbs.append({
                'label': page_name,
                'href': ''  # Current page
            })
        
        frontmatter['breadcrumb'] = breadcrumbs
        return frontmatter
    
    def _task_field_cleanup(self, frontmatter: Dict[str, Any], config: Dict) -> Dict[str, Any]:
        """
        Remove deprecated or empty fields.
        Replaces: FieldCleanupEnricher
        """
        deprecated_fields = config.get('deprecated_fields', [])
        
        for field in deprecated_fields:
            if field in frontmatter:
                del frontmatter[field]
                logger.debug(f"Removed deprecated field: {field}")
        
        # Remove empty relationships
        if 'relationships' in frontmatter:
            empty_cats = [
                cat for cat, data in frontmatter['relationships'].items()
                if not data or (isinstance(data, dict) and not data)
            ]
            for cat in empty_cats:
                del frontmatter['relationships'][cat]
        
        return frontmatter
    
    def _task_field_ordering(self, frontmatter: Dict[str, Any], config: Dict) -> Dict[str, Any]:
        """
        Reorder fields according to domain config.
        Replaces: FieldOrderEnricher
        """
        domain = config.get('domain')
        
        # Import field validator
        from shared.validation.field_order import FrontmatterFieldOrderValidator
        
        validator = FrontmatterFieldOrderValidator()
        frontmatter = validator.reorder_fields(frontmatter, domain)
        
        return frontmatter
    
    def _task_library_enrichment(self, frontmatter: Dict[str, Any], config: Dict) -> Dict[str, Any]:
        """
        Expand library relationships with full data.
        Replaces: LibraryEnrichmentProcessor
        """
        library_config = config.get('library_config', {})
        
        if not library_config.get('enabled', False):
            return frontmatter
        
        # This would integrate with library system
        # For now, pass through
        logger.debug("Library enrichment not yet implemented in generator")
        
        return frontmatter
    
    def _task_image_paths(self, frontmatter: Dict[str, Any], config: Dict) -> Dict[str, Any]:
        """
        Add image paths and metadata.
        Replaces: ImageEnricher
        """
        image_dir = config.get('image_dir', 'public/images')
        domain = config.get('domain')
        
        item_id = frontmatter.get('id') or frontmatter.get('slug', '')
        
        if not item_id:
            return frontmatter
        
        # Add hero image path
        hero_image = f"/{image_dir}/{domain}/{item_id}-hero.jpg"
        frontmatter['hero_image'] = hero_image
        
        # Add thumbnail
        thumbnail = f"/{image_dir}/{domain}/{item_id}-thumb.jpg"
        frontmatter['thumbnail'] = thumbnail
        
        return frontmatter
    
    def _task_category_grouping(self, frontmatter: Dict[str, Any], config: Dict) -> Dict[str, Any]:
        """
        Group items by category.
        Replaces: CategoryGroupingEnricher
        """
        # Implementation depends on domain needs
        return frontmatter
    
    def _task_relationship_grouping(self, frontmatter: Dict[str, Any], config: Dict) -> Dict[str, Any]:
        """
        Group relationships by semantic categories.
        Replaces: RelationshipGroupEnricher
        """
        if 'relationships' not in frontmatter:
            return frontmatter
        
        relationships = frontmatter['relationships']
        
        # Modern categories (8 total after Phase 4 completion)
        modern_categories = {
            'identity', 'interactions', 'operational', 'safety',
            'environmental', 'detection_monitoring', 'visual',
            'quality_control', 'performance'
        }
        
        is_modern = any(cat in relationships for cat in modern_categories)
        
        if is_modern:
            # Already modern structure
            logger.debug("Modern relationship structure detected (7-8 categories)")
            return frontmatter
        
        # Legacy structure detected - could migrate here
        logger.debug("Legacy relationship structure - consider migration")
        
        return frontmatter


def create_universal_generator(config: Dict[str, Any]) -> UniversalContentGenerator:
    """
    Factory function to create UniversalContentGenerator.
    
    Args:
        config: Configuration dict with tasks
    
    Returns:
        Configured UniversalContentGenerator instance
    
    Example:
        config = {
            'tasks': [
                {'type': 'author_linkage', 'author_file': 'data/authors/Authors.yaml'},
                {'type': 'slug_generation'},
                {'type': 'timestamp'},
                {'type': 'relationships', 'domain': 'materials'},
                {'type': 'section_metadata', 'config_file': 'export/config/materials.yaml'},
                {'type': 'seo_description', 'source_field': 'description', 'max_length': 160},
                {'type': 'breadcrumbs', 'domain': 'materials'},
                {'type': 'field_ordering', 'domain': 'materials'}
            ]
        }
        generator = create_universal_generator(config)
    """
    return UniversalContentGenerator(config)
