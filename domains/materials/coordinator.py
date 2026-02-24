#!/usr/bin/env python3
"""
Unified Materials Content Generator

TEXT CONTENT GENERATOR for all material content (micro, FAQ, description).
Used by shared/commands/generation.py for all generation commands.

ARCHITECTURE (Updated December 2025 - Production Only):
Single-pass generation with quality logging for learning.

- Fast single-pass generation (~5-7 seconds)
- No quality gates blocking content
- Direct API call via Generator
- Cost: ~$0.015 per description
- Quality scores logged for learning improvement

REFACTORED (December 24, 2025):
Now extends DomainCoordinator to eliminate duplication.

Usage:
    generator = MaterialCoordinator(api_client)
    generator.generate('Bronze', 'micro')
"""

import logging
import random
import tempfile
from pathlib import Path
from typing import Any, Dict, Optional

from shared.domain.base_coordinator import DomainCoordinator

logger = logging.getLogger(__name__)


class MaterialsCoordinator(DomainCoordinator):
    """
    Coordinator for all materials content types.
    
    Extends DomainCoordinator to provide:
    - QualityEvaluatedGenerator initialization
    - Winston client integration
    - SubjectiveEvaluator setup
    - Domain config loading
    
    Domain-specific responsibilities:
    - Generate EEAT section (non-AI, random selection from regulatory_standards)
    - Load materials data from Materials.yaml
    - Save generated content to Materials.yaml
    """
    
    @property
    def domain_name(self) -> str:
        """Return domain name for config loading"""
        return "materials"
    
    def _create_data_loader(self):
        """Materials load data via _load_domain_data() in the base class."""
        return None

    def _load_materials_data(self) -> Dict:
        """Backwards-compatible wrapper — prefer _load_domain_data() directly."""
        return self._load_domain_data()

    def _get_item_data(self, item_id: str) -> Dict:
        """Get material data from Materials.yaml"""
        materials_data = self._load_domain_data()
        if item_id not in materials_data['materials']:
            raise ValueError(f"Material '{item_id}' not found in Materials.yaml")
        return materials_data['materials'][item_id]
    
    def _save_content(self, item_id: str, component_type: str, content: str, author_id: Optional[int] = None) -> None:
        """Save content to Materials.yaml - handled by QualityEvaluatedGenerator"""
        # Note: QualityEvaluatedGenerator already saves to Materials.yaml
        # This method exists to satisfy abstract base class
        pass

    def generate_material_content(
        self,
        material_id: str,
        component_type: str,
        force_regenerate: bool = False
    ) -> Dict[str, Any]:
        """
        Generate content for a specific material and component type.
        Alias for generate_content() with materials-specific naming.
        """
        return self.generate_content(material_id, component_type, force_regenerate)

    def generate_all_components_for_material(
        self,
        material_id: str,
        force_regenerate: bool = False
    ) -> Dict[str, Any]:
        """
        Generate all component types for a material.
        Delegates to base generate_all_components() using prompt-directory discovery.
        """
        return self.generate_all_components(material_id, force_regenerate)

    def generate_eeat(self, material_name: str, material_data: Dict) -> Optional[Dict]:
        """
        Generate EEAT section from regulatory_standards (pure Python, no AI).
        
        EEAT (Experience, Expertise, Authoritativeness, Trustworthiness):
        - reviewedBy: Fixed string "Z-Beam Quality Assurance Team"
        - citations: 1-3 random regulatory_standards descriptions
        - isBasedOn: 1 random regulatoryStandard with name and url
        
        Args:
            material_name: Name of material
            material_data: Material data from Materials.yaml
            
        Returns:
            EEAT dict or None if no regulatory_standards available
        """
        import yaml

        project_root = Path(__file__).parent.parent.parent
        data_file = project_root / self.domain_config['data_adapter']['data_path']

        logger.info(f"📊 Generating EEAT section for {material_name}")
        
        # Get regulatory_standards
        regulatory_standards = material_data.get('regulatoryStandards', [])
        
        # Filter to dict entries only (skip any legacy string entries)
        dict_standards = [
            std for std in regulatory_standards 
            if isinstance(std, dict) and 'description' in std and 'url' in std
        ]
        
        if not dict_standards:
            logger.warning(f"No valid regulatory_standards found for {material_name}")
            return None
        
        # Select 1-3 random standards for citations
        num_citations = random.randint(1, min(3, len(dict_standards)))
        citation_standards = random.sample(dict_standards, num_citations)
        
        # Convert to citation strings (just the description)
        citations = [std['description'] for std in citation_standards]
        
        # Select 1 random standard for isBasedOn
        based_on_standard = random.choice(dict_standards)
        is_based_on = {
            'name': based_on_standard['description'],
            'url': based_on_standard['url']
        }
        
        eeat_data = {
            'reviewedBy': 'Z-Beam Quality Assurance Team',
            'citations': citations,
            'isBasedOn': is_based_on
        }
        
        logger.info(f"   reviewedBy: {eeat_data['reviewedBy']}")
        logger.info(f"   citations: {num_citations} selected from {len(dict_standards)} standards")
        logger.info(f"   isBasedOn: {is_based_on['name'][:60]}...")

        # Write to Materials.yaml (EEAT doesn't use DynamicGenerator)
        materials_data = self._load_domain_data()
        materials_data['materials'][material_name]['eeat'] = eeat_data

        with tempfile.NamedTemporaryFile(
            mode='w',
            encoding='utf-8',
            dir=data_file.parent,
            delete=False,
            suffix='.yaml'
        ) as temp_f:
            yaml.dump(materials_data, temp_f, default_flow_style=False, allow_unicode=True, sort_keys=False)
            temp_path = temp_f.name

        Path(temp_path).replace(data_file)
        logger.info(f"✅ eeat written to Materials.yaml → materials.{material_name}.eeat")
        
        return eeat_data
    
    def generate(self, material_name: str, content_type: str, **kwargs):
        """
        Generate content for material with learning pipeline.
        
        Single-pass generation via QualityEvaluatedGenerator:
        - Generate content
        - Save to Materials.yaml
        - Evaluate quality (Winston + Subjective + Structural)
        - Log to winston_feedback.db for learning
        
        Args:
            material_name: Name of material
            content_type: Type of content ('micro', 'faq', 'description', 'eeat')
            **kwargs: Additional parameters (e.g., faq_count=8)
            
        Returns:
            Generated content (string for micro/description, list for faq)
        """
        # Handle EEAT separately (pure Python, no AI)
        if content_type == 'eeat':
            materials_data = self._load_domain_data()
            if material_name not in materials_data['materials']:
                raise ValueError(f"Material '{material_name}' not found in Materials.yaml")
            return self.generate_eeat(material_name, materials_data['materials'][material_name])
        
        # All other types use QualityEvaluatedGenerator with learning pipeline
        result = self.generator.generate(material_name, content_type, **kwargs)
        
        # QualityEvaluatedGenerator returns dict with 'content' key
        return result
    
    def list_materials(self) -> list:
        """Get list of all material IDs."""
        return list(self._load_domain_data()['materials'].keys())
    
    def get_material_data(self, material_id: str):
        """Get material data for context."""
        try:
            return self._get_item_data(material_id)
        except ValueError:
            return None
