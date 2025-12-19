"""
Compounds Domain Coordinator
Orchestrates content generation for hazardous compound safety profiles.
"""

import logging
from pathlib import Path
from typing import Any, Dict, Optional

from domains.compounds.data_loader import CompoundDataLoader
from generation.core.evaluated_generator import QualityEvaluatedGenerator
from postprocessing.evaluation.subjective_evaluator import SubjectiveEvaluator

logger = logging.getLogger(__name__)


class CompoundCoordinator:
    """
    Coordinates content generation for the compounds domain.
    Handles compound descriptions, health effects, exposure guidelines, etc.
    """
    
    def __init__(self, api_client=None):
        """
        Initialize compound coordinator.
        
        Args:
            api_client: API client for content generation (optional for testing)
        """
        self.data_loader = CompoundDataLoader()
        
        # If api_client provided, initialize generation components
        if api_client:
            self.api_client = api_client
            
            # Initialize SubjectiveEvaluator
            self.subjective_evaluator = SubjectiveEvaluator(api_client)
            
            # Initialize Winston client (optional - graceful degradation)
            try:
                from postprocessing.detection.winston_client import WinstonClient
                self.winston_client = WinstonClient()
                logger.info("✅ Winston client initialized")
            except Exception as e:
                self.winston_client = None
                logger.warning(f"⚠️  Winston not configured: {e}")
            
            # Initialize generator
            self.generator = QualityEvaluatedGenerator(
                api_client=api_client,
                subjective_evaluator=self.subjective_evaluator,
                winston_client=self.winston_client
            )
        else:
            # Testing/inspection mode - no generation capabilities
            self.api_client = None
            self.generator = None
            logger.info("CompoundCoordinator initialized in inspection mode (no generation)")
        
        # Load domain config
        domain_config_path = Path(__file__).parent / "config.yaml"
        if not domain_config_path.exists():
            raise FileNotFoundError(f"Domain config not found: {domain_config_path}")
        
        import yaml
        with open(domain_config_path, 'r') as f:
            self.domain_config = yaml.safe_load(f)
        
        logger.info("CompoundCoordinator initialized")
    
    def generate_compound_content(
        self,
        compound_id: str,
        component_type: str,
        force_regenerate: bool = False
    ) -> Dict[str, Any]:
        """
        Generate content for a specific compound and component type.
        
        Args:
            compound_id: Compound identifier (e.g., "formaldehyde")
            component_type: Type of content to generate (e.g., "compound_description")
            force_regenerate: Whether to regenerate even if content exists
            
        Returns:
            Dict with generation results:
                - success: bool
                - content: str (generated text)
                - component_type: str
                - compound_id: str
                - author_id: int
                - quality_scores: dict
                - attempts: int
                
        Raises:
            ValueError: If compound not found or component type invalid
            RuntimeError: If generation fails or coordinator not configured for generation
        """
        if not self.generator:
            raise RuntimeError(
                "Coordinator not configured for generation. "
                "Initialize with api_client to enable generation."
            )
        
        # Validate compound exists
        compound = self.data_loader.get_compound(compound_id)
        if not compound:
            raise ValueError(f"Compound not found: {compound_id}")
        
        # Validate component type
        if component_type not in self.domain_config['component_types']:
            valid_types = list(self.domain_config['component_types'].keys())
            raise ValueError(
                f"Invalid component type: {component_type}. "
                f"Valid types: {valid_types}"
            )
        
        # Check if content already exists (unless forcing regeneration)
        if not force_regenerate and compound.get(component_type):
            logger.info(
                f"Content already exists for {compound_id}.{component_type} "
                f"(use force_regenerate=True to override)"
            )
            return {
                'success': True,
                'content': compound[component_type],
                'component_type': component_type,
                'compound_id': compound_id,
                'author_id': compound['author']['id'],
                'skipped': True,
                'reason': 'content_exists'
            }
        
        # Get author ID (already assigned in data)
        author_id = compound['author']['id']
        
        logger.info(
            f"Generating {component_type} for compound '{compound['name']}' "
            f"(ID: {compound_id}, Author: {author_id})"
        )
        
        # Generate content using universal pipeline
        result = self.generator.generate(
            item_name=compound_id,
            component_type=component_type,
            author_id=author_id,
            domain='compounds'
        )
        
        if not result.success:
            raise RuntimeError(
                f"Generation failed for {compound_id}.{component_type}: "
                f"{result.error_message}"
            )
        
        logger.info(
            f"✅ Generated {component_type} for {compound['name']} "
            f"({len(result.content)} chars, {result.attempts} attempts)"
        )
        
        return {
            'success': True,
            'content': result.content,
            'component_type': component_type,
            'compound_id': compound_id,
            'author_id': author_id,
            'quality_scores': result.quality_scores,
            'attempts': result.attempts,
            'skipped': False
        }
    
    def generate_all_components_for_compound(
        self,
        compound_id: str,
        force_regenerate: bool = False
    ) -> Dict[str, Any]:
        """
        Generate all enabled component types for a compound.
        
        Args:
            compound_id: Compound identifier
            force_regenerate: Whether to regenerate existing content
            
        Returns:
            Dict with results for each component type
        """
        results = {}
        enabled_types = [
            comp_type for comp_type, config in self.domain_config['component_types'].items()
            if config.get('enabled', True)
        ]
        
        logger.info(
            f"Generating {len(enabled_types)} component types for {compound_id}: "
            f"{enabled_types}"
        )
        
        for component_type in enabled_types:
            try:
                result = self.generate_compound_content(
                    compound_id=compound_id,
                    component_type=component_type,
                    force_regenerate=force_regenerate
                )
                results[component_type] = result
            except Exception as e:
                logger.error(
                    f"Failed to generate {component_type} for {compound_id}: {e}"
                )
                results[component_type] = {
                    'success': False,
                    'error': str(e)
                }
        
        return results
    
    def get_compound_data(self, compound_id: str) -> Optional[Dict[str, Any]]:
        """Get compound data for context."""
        return self.data_loader.get_compound(compound_id)
    
    def list_compounds(self) -> list:
        """Get list of all compound IDs."""
        return self.data_loader.list_compound_ids()
