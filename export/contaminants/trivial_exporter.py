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
    
    def _create_slug(self, name: str) -> str:
        """
        Create URL-friendly slug from contamination pattern name.
        
        Removes parentheses for consistency with material slugs.
        Appends '-contamination' suffix for clarity.
        """
        slug = name.lower().replace(' ', '-').replace('_', '-')
        slug = slug.replace('(', '').replace(')', '')
        # Remove consecutive hyphens
        while '--' in slug:
            slug = slug.replace('--', '-')
        return slug.strip('-')
    
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
        # Start with pattern ID and name
        frontmatter = {
            'id': pattern_id,
            'name': pattern_data.get('id', pattern_id)  # Use 'id' field if present, fallback to pattern_id
        }
        
        # Create slug for URL
        slug = self._create_slug(pattern_id)
        frontmatter['slug'] = slug
        
        # Enrich author data from registry
        author_field = pattern_data.get('author', {})
        author_id = author_field.get('id') if isinstance(author_field, dict) else author_field
        
        if author_id:
            # Get full author data from registry
            from data.authors.registry import get_author
            try:
                author_data = get_author(author_id)
                frontmatter['author'] = author_data.copy()
                
                # Add _metadata for voice tracking
                frontmatter['_metadata'] = {
                    'voice': {
                        'author_name': author_data.get('name', 'Unknown'),
                        'author_country': author_data.get('country', 'Unknown'),
                        'voice_applied': True,
                        'content_type': 'contaminant'
                    }
                }
            except KeyError:
                self.logger.warning(f"⚠️  Invalid author ID {author_id} for pattern {pattern_id}")
        
        # Define fields to export (exclude internal/debug fields)
        EXPORTABLE_FIELDS = {
            'category', 'context_notes', 'description', 'micro',
            'laser_properties', 'eeat', 'valid_materials',
            'appearance', 'commonality_score'
        }
        
        # Copy exportable fields
        for key, value in pattern_data.items():
            if key in EXPORTABLE_FIELDS:
                # Strip generation metadata
                frontmatter[key] = self._strip_generation_metadata(value)
        
        # Add title (human-readable version)
        if 'id' in pattern_data:
            # Convert ID to title (e.g., 'adhesive_residue' → 'Adhesive Residue')
            title = pattern_data['id'].replace('_', ' ').title()
            frontmatter['title'] = title
        
        # Write to file with -contamination suffix
        filename = f"{slug}-contamination.yaml"
        output_path = self.output_dir / filename
        
        with open(output_path, 'w', encoding='utf-8') as f:
            yaml.dump(
                frontmatter,
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
