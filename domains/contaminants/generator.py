#!/usr/bin/env python3
"""
Contaminant Frontmatter Generator

Modular generator for contaminant frontmatter following materials architecture.
Uses specialized modules for metadata, laser properties, media, etc.

Data Source: data/contaminants/Contaminants.yaml
Output: frontmatter/contaminants/*.yaml

Architecture:
- Loads from Contaminants.yaml (single source of truth)
- Uses modular components (metadata, laser, media, eeat)
- Trivial YAML-to-YAML export (no generation, just extraction)
- Fail-fast on missing data
"""

import logging
from typing import Dict, Any, Optional
from pathlib import Path
import yaml

from export.core.base_generator import BaseFrontmatterGenerator, GenerationContext
from shared.generators.component_generators import ComponentResult
from shared.validation.errors import GenerationError, ConfigurationError

logger = logging.getLogger(__name__)


class ContaminantFrontmatterGenerator(BaseFrontmatterGenerator):
    """
    Contaminant frontmatter generator.
    
    Generates structured frontmatter for contaminant types including:
    - Rust and corrosion products
    - Paint and coatings
    - Biological growth
    - Industrial residues
    - Oxide layers
    - Grease and oils
    """
    
    def __init__(
        self,
        api_client: Optional[Any] = None,
        config: Optional[Dict[str, Any]] = None,
        **kwargs
    ):
        """
        Initialize contaminant generator with modular components.
        
        Args:
            api_client: API client (not used - trivial export)
            config: Configuration dictionary (optional)
            **kwargs: Additional parameters
        """
        super().__init__(
            content_type='contaminant',
            api_client=api_client,
            config=config,
            **kwargs
        )
        
        # Initialize modules
        from .modules import (
            MetadataModule,
            LaserModule,
            MediaModule,
            EEATModule,
            OpticalModule,
            RemovalModule,
            SafetyModule,
            SEOModule,
            QuickFactsModule,
            IndustriesModule,
            AppearanceModule,
            CrosslinkingModule,
            AuthorModule,
        )
        
        # Basic modules (v1.0)
        self.metadata_module = MetadataModule()
        self.laser_module = LaserModule()
        self.media_module = MediaModule()
        self.eeat_module = EEATModule()
        self.optical_module = OpticalModule()
        self.removal_module = RemovalModule()
        self.safety_module = SafetyModule()
        self.author_module = AuthorModule()
        
        # Enhanced modules (v2.0 - Spec compliant)
        self.seo_module = SEOModule()
        self.quick_facts_module = QuickFactsModule()
        self.industries_module = IndustriesModule()
        self.appearance_module = AppearanceModule()
        self.crosslinking_module = CrosslinkingModule()
        
        self.logger.info("ContaminantFrontmatterGenerator initialized with 13 modules")
    
    def _load_type_data(self):
        """
        Load contaminant data from Contaminants.yaml
        
        Raises:
            ConfigurationError: If Contaminants.yaml not found or invalid
        """
        # Load from centralized data file
        data_file = Path('data/contaminants/Contaminants.yaml')
        
        if not data_file.exists():
            raise ConfigurationError(f"Contaminants.yaml not found: {data_file}")
        
        try:
            with open(data_file, 'r') as f:
                data = yaml.safe_load(f)
                self._contaminants = data.get('contamination_patterns', {})
                
                if not self._contaminants:
                    raise ConfigurationError("contamination_patterns not found in Contaminants.yaml")
                
                self.logger.info(f"Loaded {len(self._contaminants)} contaminants from {data_file}")
                
        except yaml.YAMLError as e:
            raise ConfigurationError(f"Invalid YAML in {data_file}: {e}")
    
    def _validate_identifier(self, identifier: str) -> bool:
        """
        Validate that contaminant exists in Contaminants.yaml.
        
        Args:
            identifier: Contaminant slug (e.g., 'adhesive-residue')
            
        Returns:
            True if contaminant is valid
            
        Raises:
            GenerationError: If contaminant not found
        """
        # Normalize identifier (slug format with hyphens)
        identifier_key = identifier.lower().replace(' ', '-').replace('_', '-')
        
        if identifier_key not in self._contaminants:
            available = ', '.join(sorted(self._contaminants.keys())[:10])  # Show first 10
            raise GenerationError(
                f"Contaminant '{identifier}' not found. "
                f"Available (sample): {available}..."
            )
        return True
    

    
    def _get_schema_name(self) -> str:
        """
        Get schema name for validation.
        
        Returns:
            Schema name for this content type
        """
        return f'contaminant_frontmatter'
    
    def _get_output_filename(self, identifier: str) -> str:
        """
        Get output filename for frontmatter file.
        
        Args:
            identifier: Content identifier (slug format)
            
        Returns:
            Output filename (e.g., "adhesive-residue.yaml")
        """
        # Normalize identifier: lowercase, replace spaces/underscores with hyphens
        normalized = identifier.lower().replace(' ', '-').replace('_', '-')
        return f"{normalized}.yaml"

    def _build_frontmatter_data(
        self,
        identifier: str,
        context: GenerationContext
    ) -> Dict[str, Any]:
        """
        Build complete contaminant frontmatter using modular components.
        
        This is a trivial YAML-to-YAML export - all data already exists
        in Contaminants.yaml (description, micro, eeat, laser_properties, etc.)
        
        Args:
            identifier: Contaminant slug (e.g., 'adhesive-residue')
            context: Generation context with author data
            
        Returns:
            Complete frontmatter dictionary
            
        Raises:
            GenerationError: If frontmatter construction fails
        """
        try:
            self.logger.info(f"Building frontmatter for contaminant: {identifier}")
            
            # Normalize identifier
            identifier_key = identifier.lower().replace(' ', '-').replace('_', '-')
            contaminant_data = self._contaminants[identifier_key]
            
            # Build frontmatter using modules
            frontmatter = {}
            
            # 1. Metadata (name, title, slug, description, category)
            metadata = self.metadata_module.generate(identifier_key, contaminant_data)
            frontmatter.update(metadata)
            
            # 2. Author data (enriched from registry)
            author = self.author_module.generate(contaminant_data)
            if author:
                frontmatter['author'] = author
            elif context.author_data:
                frontmatter['author'] = context.author_data
            
            # Add _metadata for voice tracking (after author enrichment)
            if 'author' in frontmatter:
                frontmatter['_metadata'] = {
                    'voice': {
                        'author_name': frontmatter['author'].get('name', 'Unknown'),
                        'author_country': frontmatter['author'].get('country', 'Unknown'),
                        'voice_applied': True,
                        'content_type': 'contaminant'
                    }
                }
            
            # 3. Media (micro, images)
            media = self.media_module.generate(contaminant_data)
            if media:
                frontmatter.update(media)
            
            # 4. Laser properties
            laser_props = self.laser_module.generate(contaminant_data)
            if laser_props:
                frontmatter['laser_properties'] = laser_props
            
            # 5. Optical properties
            optical_props = self.optical_module.generate(contaminant_data)
            if optical_props:
                frontmatter['optical_properties'] = optical_props
            
            # 6. Removal characteristics
            removal_chars = self.removal_module.generate(contaminant_data)
            if removal_chars:
                frontmatter['removal_characteristics'] = removal_chars
            
            # 7. Safety data
            safety_data = self.safety_module.generate(contaminant_data)
            if safety_data:
                frontmatter['safety_data'] = safety_data
            
            # 8. EEAT
            eeat = self.eeat_module.generate(contaminant_data)
            if eeat:
                frontmatter['eeat'] = eeat
            
            # === ENHANCED SECTIONS (v2.0 - Spec Compliant) ===
            
            # 9. SEO Optimization (meta_description, keywords, canonical_url)
            seo = self.seo_module.generate(identifier_key, contaminant_data)
            if seo:
                frontmatter.update(seo)
            
            # 10. Quick Facts (above-fold value proposition)
            quick_facts = self.quick_facts_module.generate(contaminant_data)
            if quick_facts:
                frontmatter['quick_facts'] = quick_facts
            
            # 11. Industries Served (lead qualification)
            industries = self.industries_module.generate(contaminant_data)
            if industries:
                frontmatter['industries_served'] = industries
            
            # 12. Appearance by Category (visual characteristics)
            appearance = self.appearance_module.generate(contaminant_data)
            if appearance:
                frontmatter['appearance_by_category'] = appearance
            
            # 13. Crosslinking (affected_materials, related_content)
            pattern_id = identifier_key  # Use slug as pattern_id
            crosslinking = self.crosslinking_module.generate(contaminant_data, pattern_id)
            if crosslinking:
                frontmatter.update(crosslinking)
            
            # 14. Context notes (if present)
            if 'context_notes' in contaminant_data:
                frontmatter['context_notes'] = contaminant_data['context_notes']
            
            # 15. Layout
            frontmatter['layout'] = 'contaminant'
            
            # Update _metadata with generator details (merge with voice metadata if exists)
            if '_metadata' not in frontmatter:
                frontmatter['_metadata'] = {}
            
            frontmatter['_metadata'].update({
                'generator': 'ContaminantFrontmatterGenerator',
                'version': '2.0.0',
                'content_type': 'contaminant',
                'export_method': 'modular_trivial_export',
                'data_source': 'Contaminants.yaml',
                'spec_compliance': 'CONTAMINATION_FRONTMATTER_SPEC.md',
                'enhancements': [
                    'seo_optimization',
                    'quick_facts',
                    'industries_served',
                    'appearance_by_category',
                    'crosslinking_strategies'
                ]
            })
            
            self.logger.info(f"✅ Built complete frontmatter for: {identifier}")
            return frontmatter
            
        except KeyError as e:
            raise GenerationError(
                f"Missing required field in contaminant data for '{identifier}': {e}"
            )
        except Exception as e:
            raise GenerationError(
                f"Failed to build contaminant frontmatter for '{identifier}': {e}"
            )
