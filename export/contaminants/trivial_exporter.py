#!/usr/bin/env python3
"""
Trivial Contaminants Frontmatter Exporter

PURPOSE: Export Contaminants.yaml data to frontmatter YAML files.
DESIGN: Simple YAML-to-YAML copy - NO API, NO validation.

OPERATIONS:
1. Copy contaminant-specific data from Contaminants.yaml
2. Enrich with author data from registry
3. Write to frontmatter YAML file

All complex operations (AI generation, validation, quality scoring)
happen on Contaminants.yaml ONLY. This exporter just copies the complete data.

Performance: Should take SECONDS for all contamination patterns, not minutes.
"""

import logging
import yaml
from pathlib import Path
from typing import Dict, Any
from collections import OrderedDict

from shared.validation.domain_associations import DomainAssociationsValidator
from shared.validation.field_order import FrontmatterFieldOrderValidator

logger = logging.getLogger(__name__)


class TrivialContaminantsExporter:
    """
    Trivial exporter: Copy Contaminants.yaml → Frontmatter YAML files.
    
    NO API CLIENT REQUIRED.
    NO VALIDATION REQUIRED (already validated in Contaminants.yaml).
    NO COMPLETENESS CHECKS REQUIRED (already complete in Contaminants.yaml).
    NO QUALITY SCORING REQUIRED (already scored in Contaminants.yaml).
    
    Just simple field mapping and YAML writing.
    """
    
    def __init__(self):
        """Initialize with output directory."""
        self.output_dir = Path(__file__).resolve().parents[2] / "frontmatter" / "contaminants"
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.logger = logging.getLogger(__name__)
        
        # Load source data
        self.contaminants_data = self._load_contaminants()
        
        # Initialize validators for centralized systems
        self.associations_validator = DomainAssociationsValidator()
        self.associations_validator.load()
        self.field_order_validator = FrontmatterFieldOrderValidator()
        self.field_order_validator.load_schema()
        
        self.logger.info(f"✅ Loaded {len(self.contaminants_data.get('contamination_patterns', {}))} contamination patterns")
    
    def _load_contaminants(self) -> Dict[str, Any]:
        """Load Contaminants.yaml."""
        contaminants_path = Path(__file__).resolve().parents[2] / "data" / "contaminants" / "Contaminants.yaml"
        
        try:
            with open(contaminants_path, 'r', encoding='utf-8') as f:
                data = yaml.safe_load(f)
            return data or {}
        except Exception as e:
            self.logger.error(f"❌ Failed to load Contaminants.yaml: {e}")
            return {}
    
    def _create_slug(self, pattern_id: str) -> str:
        """
        Create URL-friendly slug from contamination pattern ID.
        
        MANDATORY SUFFIX: All contaminant slugs MUST end with '-contamination'
        for SEO clarity and URL structure consistency.
        
        Normalization:
        - Convert to lowercase
        - Replace underscores with hyphens
        - Remove parentheses and special characters
        - Remove consecutive hyphens
        
        Examples:
        - "industrial-oil" → "industrial-oil-contamination"
        - "rust_formation" → "rust-formation-contamination"
        
        This suffix is intentional and required for:
        - Clear URL semantics (/contaminants/industrial-oil-contamination)
        - SEO optimization (explicit contamination context)
        - Avoiding slug conflicts with materials/settings domains
        """
        # Normalize: lowercase, replace underscores with hyphens
        slug = pattern_id.lower().replace('_', '-')
        slug = slug.replace('(', '').replace(')', '')
        # Remove consecutive hyphens
        while '--' in slug:
            slug = slug.replace('--', '-')
        slug = slug.strip('-')
        
        # MANDATORY: Append -contamination suffix (if not already present)
        if not slug.endswith('-contamination'):
            slug = f"{slug}-contamination"
        
        return slug
    
    def _strip_generation_metadata(self, data: Any) -> Any:
        """
        Recursively strip generation metadata fields from data structure.
        
        Removes: _generated_at, _generation_id, _model, _temperature, etc.
        """
        if isinstance(data, dict):
            return {
                k: self._strip_generation_metadata(v)
                for k, v in data.items()
                if not k.startswith('_') or k == '_metadata'  # Keep _metadata
            }
        elif isinstance(data, list):
            return [self._strip_generation_metadata(item) for item in data]
        else:
            return data
    
    def _build_breadcrumb(self, pattern_data: Dict, slug: str) -> list:
        """
        Build breadcrumb navigation for contamination pattern.
        
        Structure: Home > Contaminants > [Category] > [Pattern Name]
        URL Format: /contaminants/{category}/{subcategory}/{slug}
        
        Per CONTAMINANT_BREADCRUMB_STRUCTURE.md (Dec 15, 2025):
        - MUST include subcategory in URL path
        - NO double "contamination" suffix in slug
        - Top level is "Contaminants" (plural) not "Contamination"
        """
        category = pattern_data.get('category', 'contamination')
        subcategory = pattern_data.get('subcategory', 'general')
        name = pattern_data.get('name', slug.replace('-', ' ').replace('_', ' ').title())
        
        # Format category display name with hyphens (e.g., "Organic-Residue")
        category_display = '-'.join(word.capitalize() for word in category.split('-'))
        
        return [
            {'label': 'Home', 'href': '/'},
            {'label': 'Contaminants', 'href': '/contaminants'},
            {'label': category_display, 'href': f'/contaminants/{category}'},
            {'label': name, 'href': f'/contaminants/{category}/{subcategory}/{slug}'}
        ]
    
    def _build_images_structure(self, pattern_data: Dict, slug: str) -> Dict:
        """
        Build images structure for contamination pattern.
        
        Phase 1: Add placeholder structure matching materials/settings format
        """
        name = pattern_data.get('name', slug.replace('-', ' ').replace('_', ' ').title())
        
        return {
            'hero': {
                'url': f'/images/contaminants/{slug}-hero.jpg',
                'alt': f'{name} contamination on surface before laser cleaning'
            },
            'micro': {
                'url': f'/images/contaminants/{slug}-micro.jpg',
                'alt': f'{name} contamination microscopic detail'
            }
        }
    
    def _build_domain_linkages(self, pattern_data: Dict, slug: str) -> Dict:
        """
        Generate domain_linkages from centralized associations.
        
        Creates bidirectional linkages:
        - produces_compounds: Compounds produced by this contaminant (forward lookup)
        - related_materials: Materials affected by this contaminant (from associations)
        
        Args:
            pattern_data: Pattern data from Contaminants.yaml
            slug: Contaminant slug (e.g., 'carbon-buildup-contamination')
        
        Returns:
            Dict with domain_linkages structure
        """
        contaminant_id = slug  # ID already has -contamination suffix
        linkages = {}
        
        # Get compounds produced by this contaminant (forward lookup)
        produces_compounds = self.associations_validator.get_compounds_for_contaminant(contaminant_id)
        if produces_compounds:
            linkages['produces_compounds'] = produces_compounds
        
        # Get materials affected by this contaminant (bidirectional)
        related_materials = self.associations_validator.get_materials_for_contaminant(contaminant_id)
        if related_materials:
            linkages['related_materials'] = related_materials
        
        return linkages
    
    def export_all(self) -> Dict[str, bool]:
        """
        Export all contamination patterns to frontmatter files.
        
        Returns:
            Dict mapping pattern names to success status
        """
        self.logger.info("🚀 Starting contaminants frontmatter export (no API, no validation)")
        
        patterns = self.contaminants_data.get('contamination_patterns', {})
        
        results = {}
        for pattern_id, pattern_data in patterns.items():
            try:
                self.export_single(pattern_id, pattern_data)
                results[pattern_id] = True
            except Exception as e:
                self.logger.error(f"❌ Export failed for {pattern_id}: {e}")
                import traceback
                traceback.print_exc()
                results[pattern_id] = False
        
        success_count = sum(1 for v in results.values() if v)
        self.logger.info(f"✅ Exported {success_count}/{len(results)} contamination patterns")
        
        return results
    
    def export_single(self, pattern_id: str, pattern_data: Dict) -> None:
        """
        Export single contamination pattern to frontmatter YAML file.
        
        Args:
            pattern_id: ID of the contamination pattern (e.g., 'adhesive-residue')
            pattern_data: Pattern data from Contaminants.yaml
        """
        # Create slug for URL (with -contamination suffix)
        slug = self._create_slug(pattern_id)
        
        # Build frontmatter in CANONICAL ORDER (matching materials/settings)
        # Order: name, slug, category, subcategory, content_type, schema_version,
        #        datePublished, dateModified, author, _metadata, title, 
        #        {domain}_description, breadcrumb, images, [domain-specific fields]
        
        frontmatter = {}
        
        # 1-3: Identification (name, slug, category)
        # Use 'name' field from source data (properly formatted with spaces)
        # Fallback to pattern_id converted to title case if name not present
        source_name = pattern_data.get('name', pattern_id.replace('-', ' ').replace('_', ' ').title())
        frontmatter['name'] = source_name
        # Note: slug already has -contamination suffix from _create_slug()
        frontmatter['slug'] = slug
        # Add id field matching filename pattern (slug is already complete with -contamination suffix)
        frontmatter['id'] = slug
        
        # FAIL-FAST: Category and subcategory are now REQUIRED (no fallbacks)
        if 'category' not in pattern_data:
            raise ValueError(f"Pattern '{pattern_id}' missing required 'category' field")
        if 'subcategory' not in pattern_data:
            raise ValueError(f"Pattern '{pattern_id}' missing required 'subcategory' field")
        
        category = pattern_data['category']
        subcategory = pattern_data['subcategory']
        
        frontmatter['category'] = category
        
        # 4: Subcategory
        frontmatter['subcategory'] = subcategory
        
        # 5-6: Content Type & Schema (Phase 1: Add metadata fields)
        frontmatter['content_type'] = 'unified_contamination'
        frontmatter['schema_version'] = '4.0.0'
        
        # 7-8: Publishing Dates (Phase 1: Add date fields)
        frontmatter['datePublished'] = pattern_data.get('datePublished', None)
        frontmatter['dateModified'] = pattern_data.get('dateModified', None)
        
        # 9: Author (Phase 1: Add FULL author block from Authors.yaml)
        author_field = pattern_data.get('author', {})
        author_id = author_field.get('id') if isinstance(author_field, dict) else author_field
        
        if author_id:
            # Get full author data from Authors.yaml
            from shared.data.author_loader import get_author
            try:
                author_data = get_author(author_id)
                # Use full author data with all 18 fields
                frontmatter['author'] = author_data.copy()
            except KeyError:
                self.logger.warning(f"⚠️  Invalid author ID {author_id} for pattern {pattern_id}")
                # Fallback to minimal author with just ID
                frontmatter['author'] = {'id': author_id}
        else:
            # No author - set to None
            frontmatter['author'] = None
        
        # 10: Metadata (voice tracking)
        if author_id and 'author' in frontmatter and frontmatter['author']:
            frontmatter['_metadata'] = {
                'voice': {
                    'author_name': frontmatter['author'].get('name', 'Unknown'),
                    'author_country': frontmatter['author'].get('country', 'Unknown'),
                    'voice_applied': True,
                    'content_type': 'contaminant'
                }
            }
        
        # 11: Title
        frontmatter['title'] = source_name + ' Contamination'
        
        # 12: Main Content (contamination_description - note naming consistency)
        if 'description' in pattern_data:
            frontmatter['contamination_description'] = self._strip_generation_metadata(pattern_data['description'])
        
        # 13: Breadcrumb (Phase 1: Add navigation structure)
        frontmatter['breadcrumb'] = self._build_breadcrumb(pattern_data, slug)
        
        # 14: Images (Phase 1: Add images structure)
        frontmatter['images'] = self._build_images_structure(pattern_data, slug)
        
        # Domain-specific fields (in logical order)
        if 'micro' in pattern_data:
            frontmatter['micro'] = self._strip_generation_metadata(pattern_data['micro'])
        
        if 'context_notes' in pattern_data:
            frontmatter['context_notes'] = pattern_data['context_notes']
        
        if 'laser_properties' in pattern_data:
            frontmatter['laser_properties'] = self._strip_generation_metadata(pattern_data['laser_properties'])
        
        if 'eeat' in pattern_data:
            frontmatter['eeat'] = self._strip_generation_metadata(pattern_data['eeat'])
        
        # Generate domain_linkages from centralized associations (replaces hardcoded copy)
        frontmatter['domain_linkages'] = self._build_domain_linkages(pattern_data, slug)
        
        # Backward compatibility: also export valid_materials if present
        if 'valid_materials' in pattern_data:
            frontmatter['valid_materials'] = pattern_data['valid_materials']
        
        if 'appearance' in pattern_data:
            frontmatter['appearance'] = self._strip_generation_metadata(pattern_data['appearance'])
        
        if 'commonality_score' in pattern_data:
            frontmatter['commonality_score'] = pattern_data['commonality_score']
        
        # Apply field order specification
        ordered_frontmatter = self.field_order_validator.reorder_fields(frontmatter, 'contaminants')
        
        # Write to file with -contamination suffix
        filename = f"{slug}.yaml"
        output_path = self.output_dir / filename
        
        with open(output_path, 'w', encoding='utf-8') as f:
            yaml.dump(
                dict(ordered_frontmatter),
                f,
                default_flow_style=False,
                allow_unicode=True,
                sort_keys=False
            )
        
        self.logger.info(f"✅ Exported {pattern_id} → {filename}")


def export_all_contaminants_frontmatter() -> Dict[str, bool]:
    """
    Convenience function to export all contaminants frontmatter files.
    
    Usage:
        from export.contaminants.trivial_exporter import export_all_contaminants_frontmatter
        results = export_all_contaminants_frontmatter()
        print(f"Exported {sum(results.values())}/{len(results)} patterns")
    
    Returns:
        Dict mapping pattern IDs to success status
    """
    exporter = TrivialContaminantsExporter()
    return exporter.export_all()


if __name__ == "__main__":
    # CLI usage: python3 -m export.contaminants.trivial_exporter
    logging.basicConfig(level=logging.INFO, format='%(message)s')
    
    print("=" * 80)
    print("TRIVIAL CONTAMINANTS FRONTMATTER EXPORTER")
    print("=" * 80)
    print()
    print("Purpose: Copy Contaminants.yaml → Frontmatter YAML files")
    print("Design: Simple export, no API calls, no validation")
    print()
    
    results = export_all_contaminants_frontmatter()
    
    print()
    print("=" * 80)
    success_count = sum(1 for v in results.values() if v)
    print(f"✅ SUCCESS: Exported {success_count}/{len(results)} contamination patterns")
    print("=" * 80)
