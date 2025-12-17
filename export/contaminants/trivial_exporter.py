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

from export.core.base_trivial_exporter import BaseTrivialExporter
from shared.data.author_loader import get_author
from export.contaminants.compound_lookup import enrich_produces_compounds

logger = logging.getLogger(__name__)


class TrivialContaminantsExporter(BaseTrivialExporter):
    """
    Trivial exporter: Copy Contaminants.yaml → Frontmatter YAML files.
    
    NO API CLIENT REQUIRED.
    NO VALIDATION REQUIRED (already validated in Contaminants.yaml).
    NO COMPLETENESS CHECKS REQUIRED (already complete in Contaminants.yaml).
    NO QUALITY SCORING REQUIRED (already scored in Contaminants.yaml).
    
    Just simple field mapping and YAML writing.
    """
    
    def __init__(self):
        """Initialize with output directory and load contaminants data."""
        super().__init__('contaminants', 'contaminants')
        
        # Load source data
        self.contaminants_data = self._load_contaminants()
        
        self.logger.info(f"✅ Loaded {len(self.contaminants_data.get('contamination_patterns', {}))} contamination patterns")
    
    def _load_domain_data(self) -> Dict[str, Any]:
        """
        Abstract method implementation: Return contaminants data for base class.
        
        Returns:
            Dict containing contamination_patterns and metadata
        """
        return self.contaminants_data
    
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
    
    # DEPRECATED: Replaced by centralized DomainLinkagesService
    # def _build_domain_linkages(self, pattern_data: Dict, slug: str) -> Dict:
    #     """
    #     OLD METHOD - Now using shared/services/domain_linkages_service.py
    #     
    #     This method has been replaced by DomainLinkagesService.generate_linkages()
    #     for consistency across all exporters.
    #     """
    #     pass
    
    def export_all(self, force: bool = True) -> Dict[str, bool]:
        """
        Export all contamination patterns to frontmatter files.
        
        Args:
            force: Overwrite existing files (default: False)
        
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
        
        # Build frontmatter in STANDARD ORDER (normalized across all domains)
        # Order: id, name, slug, category, subcategory, content_type, schema_version,
        #        datePublished, dateModified, author, [domain-specific], breadcrumb, domain_linkages
        
        frontmatter = {}
        
        # 1-3: Identity fields
        frontmatter['id'] = slug
        source_name = pattern_data.get('name', pattern_id.replace('-', ' ').replace('_', ' ').title())
        frontmatter['name'] = source_name
        frontmatter['slug'] = slug
        
        # 4-5: Category and subcategory (REQUIRED, convert underscores to hyphens)
        if 'category' not in pattern_data:
            raise ValueError(f"Pattern '{pattern_id}' missing required 'category' field")
        if 'subcategory' not in pattern_data:
            raise ValueError(f"Pattern '{pattern_id}' missing required 'subcategory' field")
        
        category = pattern_data['category'].replace('_', '-')
        subcategory = pattern_data['subcategory'].replace('_', '-')
        
        frontmatter['category'] = category
        frontmatter['subcategory'] = subcategory
        
        # 6-7: Content Type & Schema (BEFORE dates for normalization)
        frontmatter['content_type'] = 'unified_contamination'
        frontmatter['schema_version'] = '4.0.0'
        
        # 8-9: Publishing Dates
        current_timestamp = self.generate_timestamp()
        frontmatter['datePublished'] = current_timestamp
        frontmatter['dateModified'] = current_timestamp
        
        # 10: Author (AFTER dates for normalization)
        author_field = pattern_data.get('author', {})
        author_id = author_field.get('id') if isinstance(author_field, dict) else author_field
        
        if author_id:
            try:
                frontmatter['author'] = self.enrich_author_data(author_id)
            except KeyError:
                self.logger.warning(f"⚠️  Invalid author ID {author_id} for pattern {pattern_id}")
                frontmatter['author'] = {'id': author_id}
        else:
            # No author - set to None
            frontmatter['author'] = None
        
        # 11: Metadata (voice tracking) - REMOVED per user request, keeping _metadata for now
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
            frontmatter['contamination_description'] = self.strip_generation_metadata(pattern_data['description'])
        
        # 13: Breadcrumb (Phase 1: Add navigation structure)
        frontmatter['breadcrumb'] = self._build_breadcrumb(pattern_data, slug)
        
        # 14: Images (Phase 1: Add images structure)
        frontmatter['images'] = self._build_images_structure(pattern_data, slug)
        
        # Domain-specific fields (in logical order)
        if 'micro' in pattern_data:
            frontmatter['micro'] = self.strip_generation_metadata(pattern_data['micro'])
        
        if 'context_notes' in pattern_data:
            frontmatter['context_notes'] = pattern_data['context_notes']
        
        if 'laser_properties' in pattern_data:
            frontmatter['laser_properties'] = self.strip_generation_metadata(pattern_data['laser_properties'])
        
        if 'eeat' in pattern_data:
            frontmatter['eeat'] = self.strip_generation_metadata(pattern_data['eeat'])
        
        # Generate domain_linkages from centralized associations (replaces hardcoded copy)
        frontmatter['domain_linkages'] = self.linkages_service.generate_linkages(slug, 'contaminants')
        
        # PRESERVE manually-researched produces_compounds safety data from existing frontmatter
        # Safety data enhancement (Dec 17, 2025): exposure_limits, concentration_range, etc.
        # This data is manually researched and should NOT be overwritten.
        # Priority: Existing manual data > Defaults from Compounds.yaml
        existing_frontmatter_path = self.output_dir / f"{slug}.yaml"
        if existing_frontmatter_path.exists():
            try:
                with open(existing_frontmatter_path, 'r', encoding='utf-8') as f:
                    existing_data = yaml.safe_load(f)
                    if existing_data and 'domain_linkages' in existing_data:
                        existing_linkages = existing_data['domain_linkages']
                        if 'produces_compounds' in existing_linkages:
                            # Preserve produces_compounds section from existing file
                            frontmatter['domain_linkages']['produces_compounds'] = existing_linkages['produces_compounds']
                            self.logger.debug(f"   ✓ Preserved produces_compounds safety data for {slug}")
            except Exception as e:
                self.logger.warning(f"⚠️  Could not preserve produces_compounds for {slug}: {e}")
        
        # ENRICH produces_compounds with concentration_range and hazard_class from Compounds.yaml
        # Phase 2 (Dec 17, 2025): Add default safety data for compounds missing these fields
        # This happens AFTER preservation so we only enrich compounds that don't already have the data
        if 'produces_compounds' in frontmatter['domain_linkages']:
            compounds = frontmatter['domain_linkages']['produces_compounds']
            if compounds:
                enriched = enrich_produces_compounds(compounds)
                frontmatter['domain_linkages']['produces_compounds'] = enriched
                self.logger.debug(f"   ✓ Enriched produces_compounds with defaults from Compounds.yaml")
        
        # Backward compatibility: also export valid_materials if present
        if 'valid_materials' in pattern_data:
            frontmatter['valid_materials'] = pattern_data['valid_materials']
        
        if 'appearance' in pattern_data:
            frontmatter['appearance'] = self.strip_generation_metadata(pattern_data['appearance'])
        
        if 'commonality_score' in pattern_data:
            frontmatter['commonality_score'] = pattern_data['commonality_score']
        
        # Write to file using base class method (handles field ordering + YAML writing)
        filename = f"{slug}.yaml"
        self.write_frontmatter_yaml(frontmatter, filename)
        
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
