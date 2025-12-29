"""
Field Order Enricher - Normalize frontmatter field order

Ensures all page metadata appears at the top in a consistent order across all domains.
This improves maintainability and makes frontmatter files easier to read/edit.

STANDARD FRONTMATTER SCHEMA:
═══════════════════════════════════════════════════════════════════════════════

📋 PAGE METADATA (Top Priority - Always First)
───────────────────────────────────────────────────────────────────────────────
  id                    Unique identifier (slug-based)
  name                  Display name
  title                 Full page title
  content_type          Type (materials, contaminants, compounds, settings)
  schema_version        Schema version (5.0.0)
  page_title            SEO optimized page title
  meta_description      SEO meta description (160 chars)
  seo_description       Short SEO description
  full_path             URL path (/materials/metal/aluminum-laser-cleaning)
  breadcrumb            Navigation breadcrumb array
  category              Primary category
  subcategory           Sub-category
  datePublished         ISO 8601 timestamp
  dateModified          ISO 8601 timestamp

📝 CONTENT FIELDS (High Priority)
───────────────────────────────────────────────────────────────────────────────
  description           Main content description
  micro                 Short caption/excerpt (25-50 words)
  faq                   FAQ array with questions/answers

🖼️  MEDIA & DISPLAY (Medium Priority)
───────────────────────────────────────────────────────────────────────────────
  images                Image assets (hero, micro, etc.)
  card                  Card display metadata (how page appears in UI cards)
  author                Full author profile with credentials

🏷️  DOMAIN-SPECIFIC FIELDS (Low Priority)
───────────────────────────────────────────────────────────────────────────────
  properties, characteristics, applications, laser_parameters, etc.
  (order varies by domain, appears after standard fields)

🔗 RELATIONSHIPS (Always Last)
───────────────────────────────────────────────────────────────────────────────
  relationships         All relationship arrays (contaminated_by, used_in, etc.)

═══════════════════════════════════════════════════════════════════════════════
"""

import logging
from typing import Any, Dict, List

from export.enrichers.base import BaseEnricher

logger = logging.getLogger(__name__)


class FieldOrderEnricher(BaseEnricher):
    """
    Reorder frontmatter fields per standard schema.
    
    Enforces consistent field order:
    - Page metadata at top (id, title, SEO, navigation, timestamps)
    - Content fields (description, micro, faq)
    - Media & author
    - Domain-specific fields
    - Relationships always last
    """
    
    # Standard field ordering (fields not in list appear after these, before relationships)
    FIELD_ORDER = [
        # ═══════════════════════════════════════════════════════════════════
        # PAGE METADATA - Top Priority (Always First)
        # ═══════════════════════════════════════════════════════════════════
        
        # Core Identity
        'id',
        'name',
        'title',
        
        # Schema & Type
        'content_type',
        'schema_version',
        
        # SEO Metadata (page-level)
        'page_title',
        'page_description',
        'meta_description',
        'seo_description',
        
        # Navigation
        'full_path',
        'breadcrumb',
        
        # Categorization
        'category',
        'subcategory',
        'material_type',
        'contaminant_category',
        'compound_category',
        'setting_type',
        
        # Timestamps
        'datePublished',
        'dateModified',
        
        # ═══════════════════════════════════════════════════════════════════
        # CONTENT FIELDS - High Priority
        # ═══════════════════════════════════════════════════════════════════
        'description',
        'micro',
        'caption',
        'excerpt',
        'summary',
        'faq',
        
        # ═══════════════════════════════════════════════════════════════════
        # MEDIA & AUTHOR - Medium Priority
        # ═══════════════════════════════════════════════════════════════════
        'images',
        'card',
        'author',
        
        # Navigation
        'full_path',
        'breadcrumb',
        
        # Author & Timestamps
        'author',
        'datePublished',
        'dateModified',
        
        # Images & Media
        'images',
        
        # Metrics
        'word_count',
        'readability_score',
        
        # Common domain fields (mid-priority)
        'synonyms',
        'cas_number',
        'chemical_formula',
        'molecular_weight',
        'hazard_class',
        'exposure_limits',
        'physical_properties',
        'thermal_properties',
        'optical_properties',
        'mechanical_properties',
        'laser_parameters',
        'power_settings',
        'scan_settings',
        'pulse_settings',
        
        # Relationships always last
        'relationships'
    ]
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize field order enricher.
        
        Args:
            config: Configuration dict (no specific keys required)
        """
        super().__init__(config)
    
    def enrich(self, frontmatter: Dict[str, Any]) -> Dict[str, Any]:
        """
        Reorder frontmatter fields according to standard order.
        
        Args:
            frontmatter: Input frontmatter dict
        
        Returns:
            Frontmatter with fields in standard order
        """
        ordered = {}
        
        # First pass: Add fields in FIELD_ORDER that exist in frontmatter
        # EXCEPT relationships (which goes last)
        for field in self.FIELD_ORDER:
            if field in frontmatter and field != 'relationships':
                ordered[field] = frontmatter[field]
        
        # Second pass: Add any remaining fields (not in FIELD_ORDER)
        # These go after standard fields but before relationships
        for field, value in frontmatter.items():
            if field not in ordered and field != 'relationships':
                ordered[field] = value
        
        # Third pass: Add relationships last (if it exists)
        if 'relationships' in frontmatter:
            ordered['relationships'] = frontmatter['relationships']
        
        logger.debug(f"Reordered {len(frontmatter)} fields into standard order")
        
        return ordered
    
    def generate(self, frontmatter: Dict[str, Any]) -> Dict[str, Any]:
        """
        Alias for enrich() to support generator interface.
        
        Generators use generate() method, enrichers use enrich() method.
        This class works in both contexts.
        
        Args:
            frontmatter: Input frontmatter dict
        
        Returns:
            Frontmatter with fields in standard order
        """
        return self.enrich(frontmatter)
