#!/usr/bin/env python3
"""
Contaminant Frontmatter Generator

Generator for contaminant-specific frontmatter content. Contaminants are substances
that need to be removed from surfaces via laser cleaning (rust, paint, oxide layers,
biological growth, etc.).

This follows the equal-weight content type architecture - contaminant has the same
status as material, region, application, and thesaurus.
"""

import logging
from typing import Dict, Any, Optional
from datetime import datetime

from components.frontmatter.core.base_generator import BaseFrontmatterGenerator, GenerationContext
from shared.generators.component_generators import ComponentResult
from shared.validation.errors import GenerationError

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
        Initialize contaminant generator.
        
        Args:
            api_client: API client for AI-assisted generation (optional)
            config: Configuration dictionary (optional)
            **kwargs: Additional parameters
        """
        super().__init__(
            content_type='contaminant',
            api_client=api_client,
            config=config,
            **kwargs
        )
        
        self.logger.info("ContaminantFrontmatterGenerator initialized")
    
    def _load_type_data(self):
        """
        Load contaminant-specific data from data/contaminants.yaml
        """
        import yaml
        from pathlib import Path
        
        data_file = Path(__file__).parent.parent.parent.parent.parent / 'data' / 'contaminants.yaml'
        
        try:
            with open(data_file, 'r') as f:
                data = yaml.safe_load(f)
                self._contaminant_types = data.get('contaminants', {})
                self._laser_guidelines = data.get('laser_guidelines', {})
                self.logger.info(f"Loaded {len(self._contaminant_types)} contaminant types from {data_file}")
        except FileNotFoundError:
            self.logger.error(f"Contaminant data file not found: {data_file}")
            self._contaminant_types = {}
            self._laser_guidelines = {}
        except Exception as e:
            self.logger.error(f"Failed to load contaminant data: {e}")
            self._contaminant_types = {}
            self._laser_guidelines = {}
    
    def _validate_identifier(self, identifier: str) -> bool:
        """
        Validate that contaminant type exists.
        
        Args:
            identifier: Contaminant name/type
            
        Returns:
            True if contaminant is valid
            
        Raises:
            GenerationError: If contaminant type not found
        """
        # Normalize identifier
        identifier_key = identifier.lower().replace(' ', '_')
        
        if identifier_key not in self._contaminant_types:
            raise GenerationError(
                f"Contaminant type '{identifier}' not found. "
                f"Available types: {', '.join(self._contaminant_types.keys())}"
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
            identifier: Content identifier
            
        Returns:
            Output filename (e.g., "rust-laser-cleaning.yaml")
        """
        # Normalize identifier: lowercase, replace spaces with hyphens
        normalized = identifier.lower().replace(' ', '-').replace('_', '-')
        return f"{normalized}-laser-cleaning.yaml"

    def _build_frontmatter_data(
        self,
        identifier: str,
        context: GenerationContext
    ) -> Dict[str, Any]:
        """
        Build complete contaminant frontmatter data.
        
        Args:
            identifier: Contaminant name/type
            context: Generation context with author data
            
        Returns:
            Complete frontmatter dictionary
            
        Raises:
            GenerationError: If frontmatter construction fails
        """
        try:
            # Normalize identifier
            identifier_key = identifier.lower().replace(' ', '_')
            contaminant_data = self._contaminant_types[identifier_key]
            
            # Build base structure
            frontmatter = {
                'layout': 'contaminant',
                'title': f"{contaminant_data['name']} Laser Cleaning",
                'contaminant': contaminant_data['name'],
                'description': f"Laser cleaning parameters for {contaminant_data['name']} removal",
                'generated': datetime.utcnow().isoformat() + 'Z',
                'placeholder': True,  # Mark as placeholder content
            }
            
            # Add contaminant-specific properties
            frontmatter['contaminantProperties'] = {
                'description': contaminant_data['description'],
                'removal_difficulty': 'moderate',  # Placeholder
                'typical_thickness': 'varies',  # Placeholder
                'common_substrates': contaminant_data.get('common_substrates', [])
            }
            
            # Add chemical info if available
            if 'chemical_formula' in contaminant_data:
                frontmatter['contaminantProperties']['chemical_formula'] = contaminant_data['chemical_formula']
            
            if 'types' in contaminant_data:
                frontmatter['contaminantProperties']['types'] = contaminant_data['types']
            
            # Add placeholder laser parameters
            frontmatter['laserParameters'] = {
                'wavelength': {
                    'min': 1064,
                    'max': 1064,
                    'unit': 'nm',
                    'note': 'Placeholder - requires research'
                },
                'power': {
                    'min': 100,
                    'max': 500,
                    'unit': 'W',
                    'note': 'Placeholder - requires research'
                },
                'pulseWidth': {
                    'min': 100,
                    'max': 200,
                    'unit': 'ns',
                    'note': 'Placeholder - requires research'
                }
            }
            
            # Add applications
            frontmatter['applications'] = [
                'Surface Cleaning',
                'Restoration',
                'Industrial Maintenance'
            ]
            
            # Add author data if provided
            if context.author_data:
                frontmatter['author'] = context.author_data
            
            # Add metadata
            frontmatter['_metadata'] = {
                'generator': 'ContaminantFrontmatterGenerator',
                'version': '1.0.0',
                'content_type': 'contaminant',
                'status': 'placeholder',
                'requires_research': True
            }
            
            self.logger.info(f"Built placeholder frontmatter for contaminant: {identifier}")
            return frontmatter
            
        except Exception as e:
            raise GenerationError(
                f"Failed to build contaminant frontmatter for '{identifier}': {e}"
            )
