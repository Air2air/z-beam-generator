"""Content Generator

Consolidates all enricher functionality into a single generator-based system.
Replaces 51 enricher files with one unified generator.

Migration from Enrichers to Generators (Dec 29, 2025):
- All enricher functionality moved to generators
- Configuration-driven instead of class-based
- Plugin system for extensibility
- Maintains backwards compatibility during transition

Architecture:
- ContentGenerator: Main orchestrator
- Task-based processing: Each task is a mini-generator
- Task types: linkage, metadata, relationships, seo, library, etc.
- Configuration-driven: All behavior defined in config YAML

Usage:
    from export.generation.universal_content_generator import ContentGenerator
    
    config = {
        'tasks': [
            {'type': 'author_linkage', 'author_file': 'data/authors/Authors.yaml'},
            {'type': 'section_metadata', 'config_file': 'export/config/materials.yaml'},
            {'type': 'seo_description', 'source_field': 'description', 'max_length': 160},
            {'type': 'relationships', 'domain': 'materials'}
        ]
    }
    
    generator = ContentGenerator(config)
    frontmatter = generator.generate(frontmatter)
"""

import logging
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional
import yaml

from export.generation.base import BaseGenerator

logger = logging.getLogger(__name__)


class ContentGenerator(BaseGenerator):
    """
    Content generator that replaces all enrichers.
    
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
        
        logger.info(f"Initialized ContentGenerator with {len(self.tasks)} tasks")
    
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
            'field_mapping': self._task_field_mapping,
            'camelcase_normalization': self._task_camelcase_normalization,
            'field_cleanup': self._task_field_cleanup,
            'field_ordering': self._task_field_ordering,
            'library_enrichment': self._task_library_enrichment,
            'image_paths': self._task_image_paths,
            'category_grouping': self._task_category_grouping,
            'relationship_grouping': self._task_relationship_grouping,
            'normalize_applications': self._task_normalize_applications,
            'normalize_prevention': self._task_normalize_prevention,
            'normalize_expert_answers': self._task_normalize_expert_answers,
            'normalize_compounds': self._task_normalize_compounds,
            'remove_duplicate_safety_fields': self._task_remove_duplicate_safety_fields,
            'remove_storage_requirements': self._task_remove_storage_requirements,
            'enrich_material_relationships': self._task_enrich_material_relationships,
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
                if task_type == 'normalize_applications':
                    print(f"🔧 normalize_applications task completed")
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
        Add complete author metadata from author registry.
        Replaces: AuthorEnricher
        Populates: ALL fields from registry including image, imageAlt, url, sameAs, etc.
        """
        # Get author from frontmatter (already present from source data)
        author_info = frontmatter.get('author', {})
        if not author_info:
            logger.debug("No author in frontmatter")
            return frontmatter
        
        # Get author ID
        if isinstance(author_info, dict):
            author_id = author_info.get('id')
        else:
            author_id = author_info
        
        if not author_id:
            logger.debug("No author ID in frontmatter")
            return frontmatter
        
        # Load complete author data from registry
        try:
            from data.authors.registry import get_author
            registry_author = get_author(author_id)
            
            # Use registry as source of truth, preserve source data as fallback
            complete_author = {
                'id': author_id,
                'name': registry_author.get('name'),
                'country': registry_author.get('country'),
                'countryDisplay': registry_author.get('country_display') or registry_author.get('countryDisplay'),  # Normalize to camelCase
                'title': registry_author.get('title'),
                'sex': registry_author.get('sex'),
                'jobTitle': registry_author.get('jobTitle'),
                'expertise': registry_author.get('expertise', []),
                'affiliation': registry_author.get('affiliation', {}),
                'credentials': registry_author.get('credentials', []),
                'email': registry_author.get('email'),
                'image': registry_author.get('image'),
                'imageAlt': registry_author.get('imageAlt'),
                'url': registry_author.get('url'),
                'sameAs': registry_author.get('sameAs', []),
            }
            
            # Add optional fields if present
            if registry_author.get('alumniOf'):
                complete_author['alumniOf'] = registry_author['alumniOf']
            if registry_author.get('languages'):
                complete_author['languages'] = registry_author['languages']
            
            # Generate bio if not in registry
            if not complete_author.get('bio'):
                bio_parts = []
                if complete_author.get('name'):
                    bio_parts.append(f"{complete_author['name']}")
                if complete_author.get('title'):
                    bio_parts.append(f"holds a {complete_author['title']} degree")
                if complete_author.get('expertise'):
                    expertise = complete_author['expertise']
                    if isinstance(expertise, list):
                        bio_parts.append(f"with expertise in {', '.join(expertise)}")
                if complete_author.get('country'):
                    bio_parts.append(f"based in {complete_author['country']}")
                
                complete_author['bio'] = '. '.join(bio_parts) + '.' if bio_parts else None
            
            # Add slug
            complete_author['slug'] = registry_author.get('url', '').split('/')[-1] if registry_author.get('url') else str(author_id)
            
            frontmatter['author'] = complete_author
            
        except (ImportError, KeyError) as e:
            logger.warning(f"Failed to load author {author_id} from registry: {e}")
            # Fallback: preserve existing author data
            if isinstance(author_info, dict):
                frontmatter['author'] = author_info
        
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
        Add _section metadata to ALL relationship sections.
        Replaces: SectionMetadataEnricher
        Priority: Adds _section from config OR generates default metadata
        """
        config_file = config.get('config_file')
        
        if not config_file or not Path(config_file).exists():
            return frontmatter
        
        with open(config_file, 'r') as f:
            domain_config = yaml.safe_load(f)
        
        # Get explicit section metadata from config
        configured_metadata = domain_config.get('section_metadata', {})
        
        if 'relationships' not in frontmatter:
            return frontmatter
        
        # Default metadata by section key (fallback if not in config)
        default_metadata = {
            'regulatory_standards': {
                'section_title': 'Safety Standards & Compliance',
                'section_description': 'OSHA, ANSI, ISO requirements and compliance standards',
                'icon': 'shield-check',
                'order': 10,
                'variant': 'default'
            },
            'removes_contaminants': {
                'section_title': 'Effective Contaminants',
                'section_description': 'Contamination types successfully removed',
                'icon': 'droplet',
                'order': 20,
                'variant': 'default'
            },
            'works_on_materials': {
                'section_title': 'Compatible Materials',
                'section_description': 'Materials optimized for these settings',
                'icon': 'box',
                'order': 30,
                'variant': 'default'
            }
        }
        
        # Add/update _section metadata for each relationship section
        for category, sections in frontmatter['relationships'].items():
            if not isinstance(sections, dict):
                continue
            
            for section_key, section_data in sections.items():
                if not isinstance(section_data, dict):
                    continue
                
                # Try to get from config first (use category.section_key format)
                metadata_key = f"{category}.{section_key}"
                metadata = configured_metadata.get(metadata_key) or configured_metadata.get(section_key)
                
                # Fall back to default if not in config
                if not metadata:
                    metadata = default_metadata.get(section_key)
                
                # If we have metadata, create or update _section
                if metadata:
                    # Get existing _section or create new one
                    if '_section' not in section_data:
                        section_data['_section'] = {}
                    
                    # Update with complete metadata (overwrites partial metadata)
                    section_data['_section'].update({
                        'title': metadata.get('section_title', section_key.replace('_', ' ').title()),
                        'description': metadata.get('section_description', ''),
                        'icon': metadata.get('icon', 'circle-info'),
                        'order': metadata.get('order', 100),
                        'variant': metadata.get('variant', 'default')
                    })
        
        return frontmatter
    
    def _task_seo_description(self, frontmatter: Dict[str, Any], config: Dict) -> Dict[str, Any]:
        """
        Generate SEO description from source field.
        Replaces: SEODescriptionGenerator
        """
        source_field = config.get('source_field', 'description')
        output_field = config.get('output_field', 'meta_description')
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
        Generate breadcrumb navigation array.
        Replaces: BreadcrumbGenerator
        
        Creates 'breadcrumbs' (plural) array for frontend navigation.
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
        
        # Use plural 'breadcrumbs' for consistency with frontend
        frontmatter['breadcrumbs'] = breadcrumbs
        return frontmatter
    
    def _task_field_mapping(self, frontmatter: Dict[str, Any], config: Dict) -> Dict[str, Any]:
        """
        Create aliased fields for consistency and rename fields.
        Maps common fields to standardized names for frontend.
        
        Example mappings:
        - 'title' from 'name' or 'page_title'
        - 'description' from appropriate source field
        - 'displayName' from 'display_name' (field rename)
        
        If the target field starts with an uppercase letter or contains uppercase,
        it's considered a rename operation (not an alias), and the source field is removed.
        """
        mappings = config.get('mappings', {})
        
        for target_field, source_config in mappings.items():
            # Get source field(s) - can be string or list
            sources = source_config if isinstance(source_config, list) else [source_config]
            
            # Check if this is a rename operation (target has different casing than source)
            is_rename = False
            for source_field in sources:
                if isinstance(source_field, str):
                    # If target != source and source exists, it's a rename
                    if target_field != source_field and source_field in frontmatter:
                        is_rename = True
                        break
            
            # Skip if target already exists (for aliases only)
            if not is_rename and target_field in frontmatter and frontmatter[target_field]:
                continue
            
            # Try each source in order
            for source_field in sources:
                if source_field in frontmatter and frontmatter[source_field]:
                    frontmatter[target_field] = frontmatter[source_field]
                    logger.debug(f"Mapped '{target_field}' from '{source_field}'")
                    
                    # Remove source field if this is a rename operation
                    if is_rename and source_field != target_field:
                        del frontmatter[source_field]
                        logger.debug(f"Renamed '{source_field}' to '{target_field}'")
                    break
        
        return frontmatter
    
    def _to_camel_case(self, snake_str: str) -> str:
        """Convert snake_case string to camelCase"""
        components = snake_str.split('_')
        # Keep first component as-is, capitalize the rest
        return components[0] + ''.join(x.title() for x in components[1:])
    
    def _task_camelcase_normalization(self, frontmatter: Dict[str, Any], config: Dict) -> Dict[str, Any]:
        """
        Recursively convert all snake_case field names to camelCase.
        Applies globally to normalize YAML output.
        
        Excludes:
        - Fields starting with underscore (_section, _collapsible, _open)
        - Breadcrumb href paths (e.g., /settings/plastic/...)
        - URLs and file paths
        """
        logger.info("🔄 Running camelCase normalization...")
        
        def normalize_dict(d):
            if not isinstance(d, dict):
                return d
            
            normalized = {}
            for key, value in d.items():
                # Skip fields starting with underscore
                if key.startswith('_'):
                    normalized[key] = normalize_value(value)
                    continue
                
                # Convert snake_case to camelCase if key contains underscore
                if '_' in key:
                    new_key = self._to_camel_case(key)
                    logger.debug(f"   {key} → {new_key}")
                    normalized[new_key] = normalize_value(value)
                else:
                    normalized[key] = normalize_value(value)
            
            return normalized
        
        def normalize_value(value):
            if isinstance(value, dict):
                return normalize_dict(value)
            elif isinstance(value, list):
                return [normalize_value(item) for item in value]
            else:
                return value
        
        result = normalize_dict(frontmatter)
        logger.info("✅ camelCase normalization complete")
        return result
    
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
        Also removes legacy common_challenges section (replaced by prevention).
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
            
            # Remove legacy common_challenges from operational (replaced by prevention)
            if 'operational' in relationships and isinstance(relationships['operational'], dict):
                if 'common_challenges' in relationships['operational']:
                    logger.info("🗑️  Removing legacy common_challenges (replaced by prevention collapsible)")
                    del relationships['operational']['common_challenges']
            
            return frontmatter
        
        # Legacy structure detected - could migrate here
        logger.debug("Legacy relationship structure - consider migration")
        
        return frontmatter
    
    def _task_normalize_applications(self, frontmatter: Dict[str, Any], config: Dict) -> Dict[str, Any]:
        """
        Normalize industry_applications to COLLAPSIBLE_NORMALIZATION_SCHEMA.md format.
        
        Converts flat arrays or simple items to collapsible structure:
        {
            presentation: "collapsible",
            sectionMetadata: {
                section_title: "...",
                section_description: "...",
                icon: "...",
                order: ...
            },
            items: [{applications: [{id, name, description}, ...]}]
        }
        
        UPDATED (Jan 3, 2026): Now handles top-level 'applications' field from Materials.yaml
        """
        # Initialize relationships if it doesn't exist
        if 'relationships' not in frontmatter:
            frontmatter['relationships'] = {}
        
        relationships = frontmatter['relationships']
        
        # Initialize operational category if needed
        if 'operational' not in relationships:
            relationships['operational'] = {}
        
        # STEP 1: Move top-level 'applications' to relationships.operational.industry_applications
        if 'applications' in frontmatter and isinstance(frontmatter['applications'], list):
            logger.info(f"📦 Moving top-level 'applications' ({len(frontmatter['applications'])} items) to relationships.operational.industry_applications")
            relationships['operational']['industry_applications'] = frontmatter['applications']
            # Remove from top level
            del frontmatter['applications']
        
        # Check for industry_applications in operational group
        if 'operational' in relationships and isinstance(relationships['operational'], dict):
            if 'industry_applications' in relationships['operational']:
                apps = relationships['operational']['industry_applications']
                print(f"🔍 Found industry_applications, type: {type(apps)}, has items: {'items' in apps if isinstance(apps, dict) else 'N/A'}")
                
                # If already has collapsible structure, check items
                if isinstance(apps, dict) and 'items' in apps:
                    # Check if items are already properly structured
                    items = apps['items']
                    if items and isinstance(items, list) and len(items) > 0:
                        first_item = items[0]
                        # Check if it's the collapsible format (has 'applications' key)
                        if isinstance(first_item, dict) and 'applications' in first_item:
                            logger.debug("industry_applications already in collapsible format")
                            return frontmatter
                        # Old format - has items as dicts with id/name/description directly
                        elif isinstance(first_item, dict) and 'id' in first_item:
                            logger.info(f"🔧 Converting old normalized format to collapsible format")
                            # Wrap in collapsible structure
                            pass  # Fall through to conversion
                        # Has string items - needs normalization
                        elif isinstance(first_item, str):
                            logger.info(f"🔧 industry_applications has wrapper but items are still strings, normalizing {len(items)} items")
                            pass  # Fall through to conversion
                    else:
                        # Empty items
                        logger.debug("industry_applications items empty")
                        return frontmatter
                
                # Extract list of app names (either from dict wrapper or direct list)
                if isinstance(apps, dict) and 'items' in apps:
                    existing_items = apps['items']
                    # Check if items are old structured format (dicts with id/name/description)
                    if existing_items and isinstance(existing_items[0], dict) and 'id' in existing_items[0]:
                        app_objects = existing_items  # Already structured, just wrap
                    else:
                        app_names = existing_items  # String array
                        app_objects = None
                    existing_wrapper = apps  # Preserve presentation and _section
                elif isinstance(apps, list):
                    app_names = apps  # Flat list, needs full wrapper
                    app_objects = None
                    existing_wrapper = None
                else:
                    logger.debug(f"industry_applications unexpected type: {type(apps)}")
                    return frontmatter
                
                # Build industry descriptions
                industry_descriptions = {
                    'Aerospace': 'Aircraft components and aerospace systems',
                    'Automotive': 'Vehicle manufacturing and automotive parts',
                    'Medical Devices': 'Medical equipment and surgical instruments',
                    'Electronics Manufacturing': 'Circuit boards and electronic components',
                    'Construction': 'Building materials and construction equipment',
                    'Food and Beverage Processing': 'Food processing equipment and beverage containers',
                    'Marine': 'Marine vessels and offshore equipment',
                    'Packaging': 'Packaging materials and containers',
                    'Rail Transport': 'Railway vehicles and rail infrastructure',
                    'Renewable Energy': 'Solar panels and wind turbine components',
                    'Oil and Gas': 'Drilling equipment and refinery systems',
                    'Pharmaceuticals': 'Pharmaceutical manufacturing equipment',
                    'Telecommunications': 'Telecommunications infrastructure and equipment',
                    'Defense': 'Military equipment and defense systems',
                    'Semiconductor': 'Semiconductor manufacturing and wafer processing',
                    'Power Generation': 'Power plant equipment and turbines',
                    'Chemical Processing': 'Chemical reactors and processing equipment',
                    'Mining': 'Mining equipment and mineral processing',
                    'Textiles': 'Textile manufacturing machinery',
                    'Aerospace & Defense': 'Combined aerospace and defense applications',
                    'Research & Development': 'Laboratory equipment and research facilities'
                }
                
                # Build application objects if we have strings
                if app_objects is None and app_names:
                    app_objects = []
                    for app_name in app_names:
                        if isinstance(app_name, str):
                            # Generate kebab-case ID
                            app_id = app_name.lower().replace(' ', '-').replace('&', 'and')
                            
                            # Get description or generate default
                            description = industry_descriptions.get(
                                app_name,
                                f"{app_name} industry applications and manufacturing"
                            )
                            
                            app_objects.append({
                                'id': app_id,
                                'name': app_name,
                                'description': description
                            })
                
                # Handle empty list
                if not app_objects:
                    app_objects = []
                
                # Get sectionMetadata from existing _section or create default
                if existing_wrapper and '_section' in existing_wrapper:
                    section_metadata = {
                        'section_title': existing_wrapper['_section'].get('title', 'Industry Applications'),
                        'section_description': existing_wrapper['_section'].get('description', 'Common uses across industries'),
                        'icon': existing_wrapper['_section'].get('icon', 'layers'),
                        'order': existing_wrapper['_section'].get('order', 50)
                    }
                else:
                    section_metadata = {
                        'section_title': 'Industry Applications',
                        'section_description': 'Common uses across industries',
                        'icon': 'layers',
                        'order': 50
                    }
                
                # Create collapsible structure per COLLAPSIBLE_NORMALIZATION_SCHEMA.md
                collapsible_structure = {
                    'presentation': 'collapsible',
                    'sectionMetadata': section_metadata,
                    'items': [
                        {
                            'applications': app_objects
                        }
                    ] if app_objects else []
                }
                
                # Replace with collapsible structure
                relationships['operational']['industry_applications'] = collapsible_structure
                print(f"✅ Converted to collapsible format with {len(app_objects)} applications")
                logger.info(f"✅ Normalized to collapsible format: {len(app_objects)} industry applications")
        
        return frontmatter
    
    def _task_normalize_prevention(self, frontmatter: Dict[str, Any], task_config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Transform challenges data to prevention collapsible structure.
        
        Reads challenge IDs from operational.common_challenges,
        loads full challenge data from ChallengePatterns.yaml,
        and creates a collapsible prevention section.
        
        Task config:
            - challenge_file: Path to ChallengePatterns.yaml (default: data/challenges/ChallengePatterns.yaml)
            - target_field: Where to put prevention section (default: operational.prevention)
        
        Expected structure per COLLAPSIBLE_NORMALIZATION_SCHEMA-2.md:
        {
            'presentation': 'collapsible',
            'sectionMetadata': {...},
            'items': [
                {
                    'id': 'rust-oxide-removal',
                    'category': 'Contamination',
                    'challenge': 'Rust and oxide layer removal',
                    'description': 'Requires multiple passes...',
                    'severity': 'medium',
                    'solutions': ['First pass at higher power...', ...]
                }
            ],
            'options': {'autoOpenFirst': True, 'sortBy': 'severity'}
        }
        """
        # Get challenge file path
        challenge_file = task_config.get('challenge_file', 'data/challenges/ChallengePatterns.yaml')
        target_field = task_config.get('target_field', 'operational.prevention')
        
        # Load challenge patterns
        try:
            with open(challenge_file, 'r') as f:
                challenge_data = yaml.safe_load(f)
                challenge_patterns = challenge_data.get('challenge_patterns', {})
        except Exception as e:
            logger.error(f"Failed to load challenge patterns from {challenge_file}: {e}")
            return frontmatter
        
        # Get challenge IDs from operational.common_challenges
        if 'relationships' not in frontmatter:
            return frontmatter
        
        relationships = frontmatter['relationships']
        if 'operational' not in relationships:
            return frontmatter
        
        operational = relationships['operational']
        if 'common_challenges' not in operational:
            return frontmatter
        
        common_challenges = operational['common_challenges']
        challenge_items = common_challenges.get('items', [])
        
        if not challenge_items:
            return frontmatter
        
        # Extract challenges - handle both full objects and ID references
        challenge_ids = []
        full_challenges = []
        
        for item in challenge_items:
            if isinstance(item, dict):
                # Handle nested structure: [{'thermal_management': [...], 'contamination_challenges': [...]}]
                for category_key, category_items in item.items():
                    if isinstance(category_items, list):
                        for challenge_ref in category_items:
                            if isinstance(challenge_ref, dict):
                                if 'id' in challenge_ref and 'type' in challenge_ref:
                                    # ID reference like: {'id': 'rust-oxide-removal', 'type': 'challenge'}
                                    challenge_ids.append(challenge_ref['id'])
                                elif 'challenge' in challenge_ref:
                                    # Full challenge object with challenge, severity, impact, solutions
                                    full_challenges.append({
                                        **challenge_ref,
                                        'category': self._format_category_name(category_key)
                                    })
            elif isinstance(item, list):
                # Handle flat list structure
                for challenge_ref in item:
                    if isinstance(challenge_ref, dict):
                        if 'id' in challenge_ref and 'type' in challenge_ref:
                            challenge_ids.append(challenge_ref['id'])
                        elif 'challenge' in challenge_ref:
                            full_challenges.append(challenge_ref)
        
        if not challenge_ids and not full_challenges:
            logger.info("No challenges found in common_challenges")
            return frontmatter
        
        # Load challenge patterns for ID references
        prevention_items = []
        
        # First, add challenges from ID references (from ChallengePatterns.yaml)
        for challenge_id in challenge_ids:
            if challenge_id in challenge_patterns:
                pattern = challenge_patterns[challenge_id]
                
                # Transform to prevention format
                prevention_item = {
                    'id': pattern.get('id', challenge_id),
                    'category': self._format_category_name(pattern.get('category', 'General')),
                    'challenge': pattern.get('challenge', ''),
                    'description': pattern.get('impact', ''),
                    'severity': pattern.get('severity', 'medium'),
                    'solutions': pattern.get('solutions', [])
                }
                
                # Add optional fields if present
                if 'property_value' in pattern:
                    prevention_item['threshold'] = pattern['property_value']
                
                prevention_items.append(prevention_item)
        
        # Second, add full challenge objects (already in Settings.yaml)
        for challenge_obj in full_challenges:
            prevention_item = {
                'category': challenge_obj.get('category', 'General'),
                'challenge': challenge_obj.get('challenge', ''),
                'description': challenge_obj.get('impact', ''),
                'severity': challenge_obj.get('severity', 'medium'),
                'solutions': challenge_obj.get('solutions', [])
            }
            
            # Add optional fields
            if 'threshold_temperature' in challenge_obj:
                prevention_item['threshold'] = challenge_obj['threshold_temperature']
            
            prevention_items.append(prevention_item)
        
        if not prevention_items:
            logger.info(f"No challenges processed (IDs: {len(challenge_ids)}, Full: {len(full_challenges)})")
            return frontmatter
        
        # Create collapsible structure per COLLAPSIBLE_NORMALIZATION_SCHEMA-2.md
        prevention_section = {
            'presentation': 'collapsible',
            'sectionMetadata': {
                'section_title': 'Challenges & Prevention',
                'section_description': 'Common issues and how to prevent them',
                'icon': 'shield-halved',
                'order': 5
            },
            'items': prevention_items,
            'options': {
                'autoOpenFirst': True,
                'sortBy': 'severity'
            }
        }
        
        # Place in target field
        if target_field == 'operational.prevention':
            # Add prevention to operational section
            operational['prevention'] = prevention_section
        else:
            # Handle nested field paths
            parts = target_field.split('.')
            current = relationships
            for part in parts[:-1]:
                if part not in current:
                    current[part] = {}
                current = current[part]
            current[parts[-1]] = prevention_section
        
        print(f"✅ Created prevention section with {len(prevention_items)} challenges")
        logger.info(f"✅ Normalized {len(prevention_items)} challenges to prevention collapsible format")
        
        return frontmatter
    
    def _format_category_name(self, category_key: str) -> str:
        """Convert snake_case or lowercase to Title Case."""
        return ' '.join(word.capitalize() for word in category_key.replace('_', ' ').split())
    
    def _task_normalize_expert_answers(self, frontmatter: Dict[str, Any], task_config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Transform FAQ data to expert_answers collapsible structure per COLLAPSIBLE_NORMALIZATION_SCHEMA-2.md.
        
        Reads 'faq' field from frontmatter, enriches with author expertise,
        and creates a collapsible expert_answers section.
        
        Task config:
            - target_field: Where to put expert_answers section (default: operational.expert_answers)
        
        Expected structure:
        {
            'presentation': 'collapsible',
            'sectionMetadata': {
                'section_title': 'Expert Q&A',
                'section_description': 'Frequently asked questions answered by laser cleaning experts',
                'icon': 'user-tie',
                'order': 40
            },
            'items': [
                {
                    'id': 'safely-remove-dirt',
                    'question': '...',
                    'answer': '...',
                    'topic': 'safely remove dirt',
                    'expertInfo': {
                        'name': 'Todd Dunning',
                        'title': 'Ph.D.',
                        'expertise': ['Laser Physics', ...]
                    },
                    'severity': 'medium',  # Inferred from topic keywords
                    'acceptedAnswer': True
                }
            ],
            'options': {'autoOpenFirst': True, 'sortBy': 'severity'}
        }
        """
        target_field = task_config.get('target_field', 'operational.expert_answers')
        
        # Get FAQ data from frontmatter
        faq_items = frontmatter.get('faq', [])
        if not faq_items:
            logger.debug("No FAQ items to normalize")
            return frontmatter
        
        # Get author info for expert details
        author_info = frontmatter.get('author', {})
        expert_info = None
        if author_info and isinstance(author_info, dict):
            expert_info = {
                'name': author_info.get('name', ''),
                'title': author_info.get('title', ''),
                'expertise': author_info.get('expertise', [])
            }
        
        # Severity keywords for classification
        severity_keywords = {
            'critical': ['damage', 'safety', 'hazard', 'prevent', 'fragile', 'sensitive'],
            'high': ['suitable', 'ideal', 'restore', 'optimize', 'proper'],
            'medium': ['effective', 'clean', 'remove', 'work', 'use'],
            'low': ['maintain', 'typical', 'common', 'regular']
        }
        
        # Convert FAQ items to expert_answers format
        expert_items = []
        for faq in faq_items:
            if not isinstance(faq, dict):
                continue
            
            question = faq.get('question', '')
            answer = faq.get('answer', '')
            topic_keyword = faq.get('topic_keyword', '')
            
            if not question or not answer:
                continue
            
            # Generate ID from topic_keyword or question
            id_source = topic_keyword if topic_keyword else question
            item_id = id_source.lower().replace(' ', '-').replace('?', '').replace(',', '').replace("'", '')
            item_id = item_id[:50]  # Limit length
            
            # Infer severity from question/answer content
            severity = 'medium'  # Default
            question_lower = question.lower()
            for sev, keywords in severity_keywords.items():
                if any(keyword in question_lower for keyword in keywords):
                    severity = sev
                    break
            
            expert_item = {
                'id': item_id,
                'question': question,
                'answer': answer,
                'topic': topic_keyword if topic_keyword else question[:50],
                'severity': severity,
                'acceptedAnswer': True
            }
            
            # Add expert info if available
            if expert_info:
                expert_item['expertInfo'] = expert_info
            
            expert_items.append(expert_item)
        
        # Create collapsible structure
        collapsible_structure = {
            'presentation': 'collapsible',
            'sectionMetadata': {
                'section_title': 'Expert Q&A',
                'section_description': 'Frequently asked questions answered by laser cleaning experts',
                'icon': 'user-tie',
                'order': 40
            },
            'items': expert_items,
            'options': {
                'autoOpenFirst': True,
                'sortBy': 'severity'
            }
        }
        
        # Place in target field (e.g., relationships.operational.expert_answers)
        if 'relationships' not in frontmatter:
            frontmatter['relationships'] = {}
        
        relationships = frontmatter['relationships']
        
        # Parse target field (e.g., "operational.expert_answers")
        field_parts = target_field.split('.')
        if len(field_parts) == 2:
            category, section = field_parts
            if category not in relationships:
                relationships[category] = {}
            relationships[category][section] = collapsible_structure
        elif len(field_parts) == 1:
            # Direct placement in relationships
            relationships[target_field] = collapsible_structure
        
        logger.info(f"✅ Normalized {len(expert_items)} FAQ items to expert_answers collapsible format")
        print(f"✅ Converted {len(expert_items)} FAQ items to expert_answers collapsible format")
        
        return frontmatter
    
    def _task_normalize_compounds(self, frontmatter: Dict[str, Any], task_config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Restructure compound scattered content into relationships per FRONTMATTER_FRONTEND_GUIDE.
        
        Moves top-level text fields into organized relationship sections:
        - health_effects → safety.health_impacts (descriptive)
        - exposure_guidelines → safety.exposure_guidance (descriptive)
        - ppe_requirements → safety.personal_protection (descriptive)
        - first_aid → safety.emergency_procedures (descriptive)
        - detection_methods → detection.methods (descriptive)
        - faq → operational.expert_answers (collapsible)
        
        Subject areas created:
        - formation: Sources and production mechanisms
        - safety: Health, exposure, PPE, first aid
        - detection: Detection and monitoring methods
        - operational: Expert Q&A and handling guidance
        
        Follows Contaminants model (A+ gold standard).
        """
        # Get scattered top-level fields
        health_effects = frontmatter.get('health_effects', '')
        exposure_guidelines = frontmatter.get('exposure_guidelines', '')
        ppe_requirements = frontmatter.get('ppe_requirements', '')
        first_aid = frontmatter.get('first_aid', '')
        detection_methods = frontmatter.get('detection_methods', '')
        faq_items = frontmatter.get('faq', [])
        
        # Ensure relationships exists
        if 'relationships' not in frontmatter:
            frontmatter['relationships'] = {}
        
        relationships = frontmatter['relationships']
        
        # Create/update subject areas
        
        # SAFETY subject area
        if 'safety' not in relationships:
            relationships['safety'] = {}
        
        safety = relationships['safety']
        
        # Move health_effects to safety.health_impacts
        if health_effects and isinstance(health_effects, str):
            safety['health_impacts'] = {
                'presentation': 'descriptive',
                '_section': {
                    'title': 'Health Impacts',
                    'description': 'Health effects and risks from exposure to this compound',
                    'icon': 'heart-pulse',
                    'order': 1,
                    'variant': 'warning'
                },
                'items': [{'content': health_effects}]
            }
            print(f"   ✅ Moved health_effects → safety.health_impacts")
        
        # Move exposure_guidelines to safety.exposure_guidance
        if exposure_guidelines and isinstance(exposure_guidelines, str):
            safety['exposure_guidance'] = {
                'presentation': 'descriptive',
                '_section': {
                    'title': 'Exposure Guidelines',
                    'description': 'Safe exposure limits and handling precautions',
                    'icon': 'shield-exclamation',
                    'order': 2,
                    'variant': 'warning'
                },
                'items': [{'content': exposure_guidelines}]
            }
            print(f"   ✅ Moved exposure_guidelines → safety.exposure_guidance")
        
        # Move ppe_requirements to safety.personal_protection
        if ppe_requirements and isinstance(ppe_requirements, str):
            safety['personal_protection'] = {
                'presentation': 'descriptive',
                '_section': {
                    'title': 'Personal Protection',
                    'description': 'Required protective equipment for handling this compound',
                    'icon': 'shield-check',
                    'order': 3,
                    'variant': 'warning'
                },
                'items': [{'content': ppe_requirements}]
            }
            print(f"   ✅ Moved ppe_requirements → safety.personal_protection")
        
        # Move first_aid to safety.emergency_procedures
        if first_aid and isinstance(first_aid, str):
            safety['emergency_procedures'] = {
                'presentation': 'descriptive',
                '_section': {
                    'title': 'Emergency Procedures',
                    'description': 'First aid and emergency response for exposure incidents',
                    'icon': 'first-aid',
                    'order': 4,
                    'variant': 'danger'
                },
                'items': [{'content': first_aid}]
            }
            print(f"   ✅ Moved first_aid → safety.emergency_procedures")
        
        # DETECTION subject area
        if detection_methods and isinstance(detection_methods, str):
            if 'detection' not in relationships:
                relationships['detection'] = {}
            
            relationships['detection']['methods'] = {
                'presentation': 'descriptive',
                '_section': {
                    'title': 'Detection Methods',
                    'description': 'Techniques and equipment for detecting this compound',
                    'icon': 'microscope',
                    'order': 1,
                    'variant': 'default'
                },
                'items': [{'content': detection_methods}]
            }
            print(f"   ✅ Moved detection_methods → detection.methods")
        
        # OPERATIONAL subject area - FAQ to expert_answers
        if faq_items and isinstance(faq_items, list) and len(faq_items) > 0:
            if 'operational' not in relationships:
                relationships['operational'] = {}
            
            # Get author info for expert details
            author_info = frontmatter.get('author', {})
            expert_info = None
            if author_info and isinstance(author_info, dict):
                expert_info = {
                    'name': author_info.get('name', ''),
                    'title': author_info.get('title', ''),
                    'expertise': author_info.get('expertise', [])
                }
            
            # Convert FAQ items to expert_answers format
            expert_items = []
            for faq in faq_items:
                if not isinstance(faq, dict):
                    continue
                
                question = faq.get('question', '')
                answer = faq.get('answer', '')
                topic_keyword = faq.get('topic_keyword', '')
                
                if not question or not answer:
                    continue
                
                # Generate ID from topic or question
                id_source = topic_keyword if topic_keyword else question
                item_id = id_source.lower().replace(' ', '-').replace('?', '').replace(',', '').replace("'", '')
                item_id = item_id[:50]
                
                expert_item = {
                    'id': item_id,
                    'question': question,
                    'answer': answer,
                    'topic': topic_keyword if topic_keyword else question[:50],
                    'acceptedAnswer': True
                }
                
                if expert_info:
                    expert_item['expertInfo'] = expert_info
                
                expert_items.append(expert_item)
            
            if expert_items:
                relationships['operational']['expert_answers'] = {
                    'presentation': 'collapsible',
                    '_section': {
                        'title': 'Expert Q&A',
                        'description': 'Common questions about this compound answered by experts',
                        'icon': 'user-tie',
                        'order': 1,
                        'variant': 'default'
                    },
                    'items': expert_items,
                    'options': {
                        'autoOpenFirst': True,
                        'sortBy': 'topic'
                    }
                }
                print(f"   ✅ Moved {len(expert_items)} FAQ items → operational.expert_answers")
        
        # Clean up old top-level fields
        fields_to_remove = []
        if health_effects:
            frontmatter.pop('health_effects', None)
            fields_to_remove.append('health_effects')
        if exposure_guidelines:
            frontmatter.pop('exposure_guidelines', None)
            fields_to_remove.append('exposure_guidelines')
        if ppe_requirements:
            frontmatter.pop('ppe_requirements', None)
            fields_to_remove.append('ppe_requirements')
        if first_aid:
            frontmatter.pop('first_aid', None)
            fields_to_remove.append('first_aid')
        if detection_methods:
            frontmatter.pop('detection_methods', None)
            fields_to_remove.append('detection_methods')
        if faq_items:
            frontmatter.pop('faq', None)
            fields_to_remove.append('faq')
        
        if fields_to_remove:
            print(f"🗑️  Removed {len(fields_to_remove)} top-level fields: {', '.join(fields_to_remove)}")
            logger.info(f"✅ Restructured compound: moved and removed {len(fields_to_remove)} scattered fields")
        
        return frontmatter
    
    def _task_remove_duplicate_safety_fields(self, frontmatter: Dict[str, Any], task_config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Remove legacy duplicate safety fields from compounds.
        
        Compounds domain has both old and new field names for the same data:
        - health_effects (old) vs health_impacts (new)
        - ppe_requirements (old) vs personal_protection (new)
        - emergency_response (old) vs emergency_procedures (new)
        - exposure_limits (old) vs exposure_guidance (new)
        
        This task removes the OLD fields, keeping only the NEW standardized names.
        
        Added: January 4, 2026 - Section categorization cleanup
        """
        if 'relationships' not in frontmatter:
            return frontmatter
        
        relationships = frontmatter['relationships']
        
        if 'safety' not in relationships or not isinstance(relationships['safety'], dict):
            return frontmatter
        
        safety = relationships['safety']
        
        # Define old → new mappings
        duplicates_to_remove = [
            'health_effects',        # Keep: health_impacts
            'ppe_requirements',      # Keep: personal_protection
            'emergency_response',    # Keep: emergency_procedures
            'exposure_limits'        # Keep: exposure_guidance
        ]
        
        removed_count = 0
        for old_field in duplicates_to_remove:
            if old_field in safety:
                del safety[old_field]
                removed_count += 1
        
        if removed_count > 0:
            logger.info(f"🗑️  Removed {removed_count} duplicate safety fields")
        
        return frontmatter
    
    def _task_remove_storage_requirements(self, frontmatter: Dict[str, Any], task_config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Remove storage_requirements section from compounds.
        
        Storage requirements are too generic and not specific to laser cleaning operations.
        This section adds no value to the user experience.
        
        Added: January 4, 2026 - Section cleanup
        """
        if 'relationships' not in frontmatter:
            return frontmatter
        
        relationships = frontmatter['relationships']
        
        if 'safety' not in relationships or not isinstance(relationships['safety'], dict):
            return frontmatter
        
        safety = relationships['safety']
        
        if 'storage_requirements' in safety:
            del safety['storage_requirements']
            logger.info(f"🗑️  Removed storage_requirements section")
        
        return frontmatter
    
    def _task_enrich_material_relationships(self, frontmatter: Dict[str, Any], task_config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Enrich material relationship items with frequency/severity metadata.
        
        Adds contextual metadata to relationship items like contaminated_by:
        - frequency: very_common, common, occasional, rare
        - severity: critical, high, moderate, low
        - conditions: Environmental or operational conditions that promote this
        
        Example transformation:
            Before: {id: "aluminum-oxidation-contamination"}
            After:  {id: "aluminum-oxidation-contamination", frequency: "very_common", severity: "moderate"}
        
        Task config:
            - target_sections: List of relationship sections to enrich (default: ['contaminated_by'])
            - default_frequency: Default if not determinable (default: 'common')
            - default_severity: Default if not determinable (default: 'moderate')
        """
        target_sections = task_config.get('target_sections', ['contaminated_by'])
        default_frequency = task_config.get('default_frequency', 'common')
        default_severity = task_config.get('default_severity', 'moderate')
        
        # Check if relationships exist
        if 'relationships' not in frontmatter:
            return frontmatter
        
        relationships = frontmatter['relationships']
        enriched_count = 0
        
        # Common frequency keywords for heuristics
        frequency_keywords = {
            'very_common': ['always', 'constantly', 'very common', 'ubiquitous', 'everywhere'],
            'common': ['common', 'frequent', 'typical', 'often', 'regularly'],
            'occasional': ['occasional', 'sometimes', 'periodic', 'intermittent'],
            'rare': ['rare', 'seldom', 'infrequent', 'uncommon', 'unusual']
        }
        
        # Severity keywords for heuristics
        severity_keywords = {
            'critical': ['critical', 'severe', 'extreme', 'dangerous', 'fatal'],
            'high': ['high', 'significant', 'major', 'serious', 'substantial'],
            'moderate': ['moderate', 'medium', 'considerable', 'noticeable'],
            'low': ['low', 'mild', 'minor', 'slight', 'minimal']
        }
        
        # Iterate through relationship groups
        for group_key, group_data in relationships.items():
            if not isinstance(group_data, dict):
                continue
            
            for section_key, section_data in group_data.items():
                # Check if this is a target section
                if section_key not in target_sections:
                    continue
                
                if not isinstance(section_data, dict):
                    continue
                
                items = section_data.get('items', [])
                if not isinstance(items, list):
                    continue
                
                # Enrich each item
                for item in items:
                    if not isinstance(item, dict):
                        continue
                    
                    # Skip if already enriched
                    if 'frequency' in item and 'severity' in item:
                        continue
                    
                    # Add frequency (use default for now, could be smarter with contaminant data)
                    if 'frequency' not in item:
                        item['frequency'] = default_frequency
                    
                    # Add severity (use default for now, could be smarter with contaminant data)
                    if 'severity' not in item:
                        item['severity'] = default_severity
                    
                    enriched_count += 1
        
        if enriched_count > 0:
            print(f"✅ Enriched {enriched_count} relationship items with frequency/severity metadata")
            logger.info(f"✅ Enriched {enriched_count} relationship items in {len(target_sections)} sections")
        
        return frontmatter


def create_universal_generator(config: Dict[str, Any]) -> ContentGenerator:
    """
    Factory function to create ContentGenerator.
    
    Args:
        config: Configuration dict with tasks
    
    Returns:
        Configured ContentGenerator instance
    
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
    return ContentGenerator(config)
