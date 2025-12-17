"""
Domain Linkages Service
========================

Centralized service for generating domain linkages across all exporters.

Part of Export Architecture Improvement Plan (Dec 16, 2025)
Priority 4: Centralize domain linkages (2 hours)

Single source of truth for:
- Material ↔ Contaminant associations
- Contaminant ↔ Compound associations
- Material ↔ Compound (transitive via contaminants)

Replaces duplicate _build_domain_linkages() methods in:
- export/core/trivial_exporter.py (materials)
- export/settings/trivial_exporter.py (settings)
- export/contaminants/trivial_exporter.py (contaminants)
- export/compounds/trivial_exporter.py (compounds)

Usage:
    from shared.services.domain_linkages_service import DomainLinkagesService
    
    service = DomainLinkagesService()
    
    # Materials domain
    linkages = service.generate_linkages('aluminum-laser-cleaning', 'materials')
    # Returns: {'related_contaminants': [...], 'related_compounds': [...]}
    
    # Contaminants domain
    linkages = service.generate_linkages('rust-contamination', 'contaminants')
    # Returns: {'produces_compounds': [...], 'related_materials': [...]}
    
    # Compounds domain
    linkages = service.generate_linkages('iron-oxide-compound', 'compounds')
    # Returns: {'produced_by_contaminants': [...]}
"""

import logging
from typing import Dict, List, Any, Optional
from shared.validation.domain_associations import DomainAssociationsValidator

logger = logging.getLogger(__name__)


class DomainLinkagesService:
    """
    Centralized domain linkage generation for all exporters.
    
    Single source of truth for bidirectional associations across domains.
    """
    
    def __init__(self, associations_path: Optional[str] = None):
        """
        Initialize service with domain associations data.
        
        Args:
            associations_path: Path to DomainAssociations.yaml
                             (default: data/associations/DomainAssociations.yaml)
        """
        self.logger = logging.getLogger(__name__)
        
        # Initialize domain associations validator
        self.associations_validator = DomainAssociationsValidator()
        
        if associations_path:
            self.associations_validator.load(associations_path)
        else:
            self.associations_validator.load()
        
        self.logger.info("✅ DomainLinkagesService initialized")
    
    def generate_linkages(
        self, 
        item_id: str, 
        source_domain: str
    ) -> Dict[str, Any]:
        """
        Generate domain linkages for any item in any domain.
        
        Args:
            item_id: ID of the item with domain suffix
                    - Materials: 'aluminum-laser-cleaning'
                    - Contaminants: 'rust-contamination'
                    - Compounds: 'iron-oxide-compound'
            source_domain: Source domain ('materials', 'contaminants', 'compounds', 'settings')
            
        Returns:
            Dictionary of linkages to other domains
            
        Example:
            >>> service.generate_linkages('aluminum-laser-cleaning', 'materials')
            {
                'related_contaminants': [
                    {'id': 'rust-contamination', 'name': 'Rust'}
                ],
                'related_compounds': [
                    {'id': 'iron-oxide-compound', 'name': 'Iron Oxide'}
                ]
            }
        """
        if source_domain == 'materials':
            return self._generate_material_linkages(item_id)
        elif source_domain == 'settings':
            return self._generate_settings_linkages(item_id)
        elif source_domain == 'contaminants':
            return self._generate_contaminant_linkages(item_id)
        elif source_domain == 'compounds':
            return self._generate_compound_linkages(item_id)
        else:
            self.logger.warning(f"Unknown domain: {source_domain}")
            return {}
    
    def _generate_material_linkages(self, material_id: str) -> Dict[str, Any]:
        """
        Generate linkages for materials domain.
        
        Creates:
        - related_contaminants: Contaminants that affect this material
        - related_compounds: Compounds produced (transitive via contaminants)
        
        Args:
            material_id: Material ID (e.g., 'aluminum-laser-cleaning')
            
        Returns:
            Dict with linkages
        """
        linkages = {}
        
        # Get contaminants that affect this material (bidirectional)
        related_contaminants = self.associations_validator.get_contaminants_for_material(material_id)
        if related_contaminants:
            linkages['related_contaminants'] = related_contaminants
        
        # Get compounds (transitive: Material → Contaminant → Compound)
        related_compounds = []
        seen_compounds = set()
        
        for contaminant in related_contaminants:
            contaminant_id = contaminant.get('id')
            if contaminant_id:
                compounds = self.associations_validator.get_compounds_for_contaminant(contaminant_id)
                for compound in compounds:
                    compound_id = compound.get('id')
                    if compound_id and compound_id not in seen_compounds:
                        seen_compounds.add(compound_id)
                        related_compounds.append(compound)
        
        if related_compounds:
            linkages['related_compounds'] = related_compounds
        
        return linkages
    
    def _generate_settings_linkages(self, material_slug: str) -> Dict[str, Any]:
        """
        Generate linkages for settings domain.
        
        Settings pages link to same contaminants/compounds as their material.
        
        Args:
            material_slug: Material slug without suffix (e.g., 'aluminum')
            
        Returns:
            Dict with linkages
        """
        linkages = {}
        
        # Convert slug to material ID
        material_id = f"{material_slug}-laser-cleaning"
        
        # Get contaminants for this material
        contaminants = self.associations_validator.get_contaminants_for_material(material_id)
        if contaminants:
            linkages['contaminants'] = sorted([c['id'] for c in contaminants])
        
        # Get compounds for contaminants (transitive)
        all_compounds = set()
        for contaminant in contaminants:
            compounds = self.associations_validator.get_compounds_for_contaminant(contaminant['id'])
            all_compounds.update(c['id'] for c in compounds)
        
        if all_compounds:
            linkages['compounds'] = sorted(all_compounds)
        
        return linkages if linkages else {}
    
    def _generate_contaminant_linkages(self, contaminant_id: str) -> Dict[str, Any]:
        """
        Generate linkages for contaminants domain.
        
        Creates:
        - produces_compounds: Compounds produced by this contaminant
        - related_materials: Materials affected by this contaminant
        
        Args:
            contaminant_id: Contaminant ID (e.g., 'rust-contamination')
            
        Returns:
            Dict with linkages
        """
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
    
    def _generate_compound_linkages(self, compound_id: str) -> Dict[str, Any]:
        """
        Generate linkages for compounds domain.
        
        Creates:
        - produced_by_contaminants: Contaminants that produce this compound
        
        Args:
            compound_id: Compound ID (e.g., 'iron-oxide-compound')
            
        Returns:
            Dict with linkages
        """
        linkages = {}
        
        # Get contaminants that produce this compound (reverse lookup)
        produced_by = self.associations_validator.get_contaminants_for_compound(compound_id)
        
        if produced_by:
            linkages['produced_by_contaminants'] = produced_by
        
        # Future: Add related_materials when Material↔Compound associations populated
        # related_materials = self.associations_validator.get_materials_for_compound(compound_id)
        # if related_materials:
        #     linkages['related_materials'] = related_materials
        
        return linkages
    
    def get_linkage_stats(self) -> Dict[str, int]:
        """
        Get statistics about domain linkages.
        
        Returns:
            Dict with linkage counts
        """
        # Get all associations from validator's data structure
        material_contaminant = len(self.associations_validator.material_contaminant_associations)
        contaminant_compound = len(self.associations_validator.contaminant_compound_associations)
        
        return {
            'material_contaminant': material_contaminant,
            'contaminant_compound': contaminant_compound,
            'total': material_contaminant + contaminant_compound
        }
