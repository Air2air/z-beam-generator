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
            'normalize_expert_answers': self._task_normalize_expert_answers,  # GRANDFATHER CLAUSE: Pre-Jan 5 2026 data
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
        Convert software metadata fields from snake_case to camelCase.
        
        Software Metadata (camelCase): contentType, schemaVersion, fullPath, pageTitle, metaDescription, displayName
        Domain Data (snake_case): machine_settings, chemical_formula, cas_number, exposure_limits, etc.
        
        Excludes:
        - Fields starting with underscore (_section, _collapsible, _open)
        - Domain-specific data fields (scientific, technical, regulatory)
        - Nested fields within domain data structures
        """
        logger.info("🔄 Running camelCase normalization (software metadata only)...")
        
        # Software metadata fields that should be camelCase
        SOFTWARE_FIELDS = {
            'content_type': 'contentType',
            'schema_version': 'schemaVersion',
            'full_path': 'fullPath',
            'page_title': 'pageTitle',
            'meta_description': 'metaDescription',
            'page_description': 'pageDescription',
            'date_published': 'datePublished',
            'date_modified': 'dateModified',
            'display_name': 'displayName',
            'image_url': 'imageUrl',
            'image_alt': 'imageAlt',
            'image_width': 'imageWidth',
            'image_height': 'imageHeight',
        }
        
        # Domain data structures that should remain snake_case
        DOMAIN_DATA_FIELDS = {
            'machine_settings',
            'chemical_formula',
            'cas_number',
            'molecular_weight',
            'exposure_limits',
            'hazard_class',
            'detection_methods',
            'first_aid',
            'exposure_guidelines',
            'health_effects',
            'health_effects_keywords',
            'environmental_effects',
            'prohibited_materials',
            'regulatory_standards',
            'monitoring_required',
            'typical_concentration_range',
            'sources_in_laser_cleaning',
            'ppe_requirements',
            'osha_pel_ppm',
            'osha_pel_mg_m3',
            'niosh_rel_ppm',
            'niosh_rel_mg_m3',
            'acgih_tlv_ppm',
            'acgih_tlv_mg_m3',
            'nfpa_health',
            'nfpa_flammability',
            'nfpa_instability',
            'nfpa_special',
        }
        
        def normalize_dict(d, is_domain_data=False):
            if not isinstance(d, dict):
                return d
            
            normalized = {}
            for key, value in d.items():
                # Skip fields starting with underscore
                if key.startswith('_'):
                    normalized[key] = normalize_value(value, is_domain_data)
                    continue
                
                # If we're inside domain data structure, preserve snake_case
                if is_domain_data:
                    normalized[key] = normalize_value(value, is_domain_data=True)
                    continue
                
                # Check if this is a domain data field that should remain snake_case
                if key in DOMAIN_DATA_FIELDS:
                    normalized[key] = normalize_value(value, is_domain_data=True)
                    continue
                
                # Convert software metadata fields to camelCase
                if key in SOFTWARE_FIELDS:
                    new_key = SOFTWARE_FIELDS[key]
                    logger.debug(f"   {key} → {new_key}")
                    normalized[new_key] = normalize_value(value, is_domain_data)
                else:
                    # Keep field as-is if not in software fields list
                    normalized[key] = normalize_value(value, is_domain_data)
            
            return normalized
        
        def normalize_value(value, is_domain_data=False):
            if isinstance(value, dict):
                return normalize_dict(value, is_domain_data)
            elif isinstance(value, list):
                return [normalize_value(item, is_domain_data) for item in value]
            else:
                return value
        
        result = normalize_dict(frontmatter)
        logger.info("✅ camelCase normalization complete (software metadata converted, domain data preserved)")
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
    
    def _task_normalize_expert_answers(self, frontmatter: Dict[str, Any], task_config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Transform FAQ data to unified collapsible structure.
        
        Reads 'faq' field from frontmatter, enriches with author expertise,
        and creates a collapsible expert_answers section following the unified pattern:
        - title: Question text (what you see when collapsed)
        - content: Answer text (what you see when expanded)
        - metadata: Domain-specific fields (expertInfo, severity, etc.)
        
        Task config:
            - target_field: Where to put expert_answers section (default: operational.expert_answers)
        
        Unified structure:
        {
            'presentation': 'collapsible',
            'sectionMetadata': {...},
            'items': [
                {
                    'id': 'safely-remove-dirt',
                    'title': 'How does laser cleaning safely remove dirt?',  # Question
                    'content': 'Laser cleaning employs precise...',          # Answer
                    'metadata': {
                        'topic': 'safely remove dirt',
                        'severity': 'medium',
                        'acceptedAnswer': True,
                        'expertInfo': {...}
                    },
                    '_display': {'_open': False, 'order': 1}
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
        
        # Convert FAQ items to unified collapsible format
        expert_items = []
        for idx, faq in enumerate(faq_items, 1):
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
            
            # Build metadata object for domain-specific fields
            metadata = {
                'topic': topic_keyword if topic_keyword else question[:50],
                'severity': severity,
                'acceptedAnswer': True
            }
            
            # Add expert info if available
            if expert_info:
                metadata['expertInfo'] = expert_info
            
            # Unified collapsible item: title/content/metadata/_display
            expert_item = {
                'id': item_id,
                'title': question,      # Question is the title (collapsed state)
                'content': answer,      # Answer is the content (expanded state)
                'metadata': metadata,   # Domain-specific fields
                '_display': {
                    '_open': idx == 1,  # Auto-open first item
                    'order': idx
                }
            }
            
            expert_items.append(expert_item)
        
        # Create unified collapsible structure
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
