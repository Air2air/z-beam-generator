#!/usr/bin/env python3
"""
Application Frontmatter Generator

Generator for application-specific frontmatter content. Currently in placeholder mode.

This follows the equal-weight content type architecture - application has the same
status as material, contaminant, and other content types.
"""

import logging
from typing import Dict, Any, Optional
from datetime import datetime

from components.frontmatter.core.base_generator import BaseFrontmatterGenerator, GenerationContext
from shared.validation.errors import GenerationError

logger = logging.getLogger(__name__)


class ApplicationFrontmatterGenerator(BaseFrontmatterGenerator):
    """
    Application frontmatter generator (placeholder mode).
    
    Future: Full implementation with data-driven content
    Current: Generates placeholder frontmatter structures
    """
    
    def __init__(
        self,
        api_client: Optional[Any] = None,
        config: Optional[Dict[str, Any]] = None,
        **kwargs
    ):
        """
        Initialize application generator.
        
        Args:
            api_client: API client for AI-assisted generation (optional)
            config: Configuration dictionary (optional)
            **kwargs: Additional parameters
        """
        super().__init__(
            content_type='application',
            api_client=api_client,
            config=config,
            **kwargs
        )
        
        self.logger.info("ApplicationFrontmatterGenerator initialized (placeholder mode)")
    
    def _load_type_data(self):
        """
        Load application-specific data from data/applications.yaml
        """
        import yaml
        from pathlib import Path
        
        data_file = Path(__file__).parent.parent.parent.parent.parent / 'data' / 'applications.yaml'
        
        try:
            with open(data_file, 'r') as f:
                data = yaml.safe_load(f)
                self._applications = data.get('applications', {})
                self.logger.info(f"Loaded {len(self._applications)} applications from {data_file}")
        except FileNotFoundError:
            self.logger.error(f"Application data file not found: {data_file}")
            self._applications = {}
        except Exception as e:
            self.logger.error(f"Failed to load application data: {e}")
            self._applications = {}
    
    def _validate_identifier(self, identifier: str) -> bool:
        """
        Validate that application identifier exists.
        
        Args:
            identifier: Application name/identifier
            
        Returns:
            True if application is valid
            
        Raises:
            GenerationError: If application not found
        """
        # Normalize identifier
        identifier_key = identifier.lower().replace(' ', '_').replace('-', '_')
        
        if identifier_key not in self._applications:
            raise GenerationError(
                f"Application '{identifier}' not found. "
                f"Available applications: {', '.join(self._applications.keys())}"
            )
        return True
    

    
    def _get_schema_name(self) -> str:
        """
        Get schema name for validation.
        
        Returns:
            Schema name for this content type
        """
        return f'application_frontmatter'
    
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
        Build complete application frontmatter data from data file.
        
        Args:
            identifier: Application name/identifier
            context: Generation context with author data
            
        Returns:
            Complete frontmatter dictionary
            
        Raises:
            GenerationError: If frontmatter construction fails
        """
        try:
            # Normalize identifier
            identifier_key = identifier.lower().replace(' ', '_').replace('-', '_')
            app_data = self._applications[identifier_key]
            
            # Build structure from data file
            frontmatter = {
                'layout': 'application',
                'title': f"{app_data['name']} - Laser Cleaning Application",
                'application': app_data['name'],
                'description': app_data.get('description', f"Laser cleaning for {app_data['name']}"),
                'generated': datetime.utcnow().isoformat() + 'Z',
                'placeholder': True,  # Still placeholder as needs full research
            }
            
            # Add application properties from data
            frontmatter['applicationProperties'] = {
                'name': app_data['name'],
                'industry_sector': app_data.get('industry_sector', 'General Industrial'),
                'typical_use_cases': app_data.get('use_cases', []),
                'complexity': app_data.get('complexity', 'moderate')
            }
            
            # Add use cases
            if 'use_cases' in app_data:
                frontmatter['useCases'] = app_data['use_cases']
            
            # Add common materials
            if 'common_materials' in app_data:
                frontmatter['commonMaterials'] = app_data['common_materials']
            
            # Add common contaminants
            if 'common_contaminants' in app_data:
                frontmatter['commonContaminants'] = app_data['common_contaminants']
            
            # Add process requirements
            if 'process_requirements' in app_data:
                frontmatter['processRequirements'] = app_data['process_requirements']
            
            # Add benefits
            if 'benefits' in app_data:
                frontmatter['benefits'] = app_data['benefits']
            
            # Add challenges
            if 'challenges' in app_data:
                frontmatter['challenges'] = app_data['challenges']
            
            # Add typical parameters if available
            if 'typical_parameters' in app_data:
                frontmatter['typicalParameters'] = app_data['typical_parameters']
            
            # Add author data if provided
            if context.author_data:
                frontmatter['author'] = context.author_data
            
            # Add metadata
            frontmatter['_metadata'] = {
                'generator': 'ApplicationFrontmatterGenerator',
                'version': '1.0.0',
                'content_type': 'application',
                'status': 'data_driven_placeholder',
                'data_source': 'data/applications.yaml',
                'requires_research': True
            }
            
            self.logger.info(f"Built data-driven frontmatter for application: {identifier}")
            return frontmatter
            
        except Exception as e:
            raise GenerationError(
                f"Failed to build application frontmatter for '{identifier}': {e}"
            )
