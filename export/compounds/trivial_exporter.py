"""
Compounds Exporter
Exports compound safety profiles to frontmatter YAML format for deployment.
"""

import logging
from typing import Dict, Any, Optional
from pathlib import Path
import yaml

from domains.compounds.data_loader import CompoundDataLoader

logger = logging.getLogger(__name__)


class CompoundExporter:
    """
    Exports compound data to frontmatter format.
    Hydrates author references, adds breadcrumbs, prepares for web deployment.
    """
    
    def __init__(self):
        self.data_loader = CompoundDataLoader()
        
        # Output directory
        self.output_dir = Path(__file__).parent.parent.parent / "frontmatter" / "compounds"
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        logger.info(f"CompoundExporter initialized, output: {self.output_dir}")
    
    def export_compound(self, compound_id: str, force: bool = False) -> bool:
        """
        Export single compound to frontmatter YAML.
        
        Args:
            compound_id: Compound identifier
            force: Overwrite existing file
            
        Returns:
            True if exported successfully
        """
        # Load compound data
        compound = self.data_loader.get_compound(compound_id)
        if not compound:
            logger.error(f"Compound not found: {compound_id}")
            return False
        
        # Prepare output file with -compound suffix
        output_file = self.output_dir / f"{compound['slug']}-compound.yaml"
        if output_file.exists() and not force:
            logger.warning(
                f"Frontmatter already exists: {output_file} "
                f"(use force=True to overwrite)"
            )
            return False
        
        # Build frontmatter
        frontmatter = self._build_frontmatter(compound)
        
        # Write to file with sort_keys=False to preserve field order
        with open(output_file, 'w', encoding='utf-8') as f:
            yaml.dump(frontmatter, f, default_flow_style=False, allow_unicode=True, sort_keys=False)
        
        logger.info(f"✅ Exported {compound['name']} to {output_file}")
        return True
    
    def export_all(self, force: bool = False) -> Dict[str, bool]:
        """
        Export all compounds to frontmatter.
        
        Args:
            force: Overwrite existing files
            
        Returns:
            Dict mapping compound_id -> success status
        """
        results = {}
        compound_ids = self.data_loader.list_compound_ids()
        
        logger.info(f"Exporting {len(compound_ids)} compounds to frontmatter...")
        
        for compound_id in compound_ids:
            try:
                success = self.export_compound(compound_id, force=force)
                results[compound_id] = success
            except Exception as e:
                logger.error(f"Failed to export {compound_id}: {e}")
                results[compound_id] = False
        
        success_count = sum(results.values())
        logger.info(
            f"Export complete: {success_count}/{len(compound_ids)} compounds exported"
        )
        
        return results
    
    def _build_frontmatter(self, compound: Dict[str, Any]) -> Dict[str, Any]:
        """
        Build frontmatter structure for a compound.
        
        Args:
            compound: Compound data from Compounds.yaml
            
        Returns:
            Dict ready for YAML export
        """
        # Hydrate author data
        author_id = compound['author']['id']

        
        from shared.data.author_loader import get_author
        author_data = get_author(author_id)
        if not author_data:
            raise ValueError(f"Author not found: {author_id}")
        
        # Build frontmatter
        frontmatter = {
            # Core identification - id should match filename (slug without extension)
            'id': f"{compound['slug']}-compound",  # Include -compound suffix to match filename
            'name': compound['name'],
            'display_name': compound['display_name'],
            'slug': compound['slug'],
            
            # Chemical properties
            'chemical_formula': compound['chemical_formula'],
            'cas_number': compound.get('cas_number'),
            'molecular_weight': compound.get('molecular_weight'),
            
            # Classification
            'category': compound['category'],
            'subcategory': compound.get('subcategory'),
            'hazard_class': compound['hazard_class'],
            
            # Exposure limits
            'exposure_limits': compound.get('exposure_limits', {}),
            
            # Safety data
            'health_effects_keywords': compound.get('health_effects_keywords', []),
            'monitoring_required': compound.get('monitoring_required', False),
            'typical_concentration_range': compound.get('typical_concentration_range'),
            'sources_in_laser_cleaning': compound.get('sources_in_laser_cleaning', []),
            
            # Generated content
            'description': compound.get('description'),
            'health_effects': compound.get('health_effects'),
            'exposure_guidelines': compound.get('exposure_guidelines'),
            'detection_methods': compound.get('detection_methods'),
            'first_aid': compound.get('first_aid'),
            
            # Domain linkages (bidirectional relationships)
            'domain_linkages': compound.get('domain_linkages', {}),
            
            # Author (full data from Authors.yaml)
            'author': author_data.copy(),
            
            # Breadcrumbs
            'breadcrumbs': [
                {'label': 'Home', 'url': '/'},
                {'label': 'Hazardous Compounds', 'url': '/compounds'},
                {'label': compound['name'], 'url': f"/compounds/{compound['slug']}"}
            ],
            
            # Metadata
            'type': 'compound',
            'domain': 'compounds',
            'last_updated': None  # Set by deployment process
        }
        
        return frontmatter
    
    def get_export_stats(self) -> Dict[str, Any]:
        """
        Get statistics about exported frontmatter files.
        
        Returns:
            Dict with export statistics
        """
        total_compounds = len(self.data_loader.list_compound_ids())
        exported_files = list(self.output_dir.glob("*.yaml"))
        
        return {
            'total_compounds': total_compounds,
            'exported_count': len(exported_files),
            'export_percentage': (len(exported_files) / total_compounds * 100) if total_compounds > 0 else 0,
            'output_directory': str(self.output_dir)
        }
