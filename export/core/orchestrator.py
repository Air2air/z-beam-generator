#!/usr/bin/env python3
"""
Frontmatter Orchestrator

Multi-type coordinator that routes generation requests to appropriate generators.
Manages generator lifecycle, author voice injection, and batch operations.

Responsibilities:
- Dynamic generator registration and discovery
- Request routing to appropriate content type generator
- Author data management and injection
- Batch generation coordination
- Configuration distribution
- Error aggregation and reporting

Supported Content Types:
- material: Material frontmatter
- contaminant: Contaminant frontmatter
- settings: Settings frontmatter

Usage:
    from export.core.orchestrator import FrontmatterOrchestrator
    
    # Initialize with API client
    orchestrator = FrontmatterOrchestrator(api_client=api_client)
    
    # Generate single content
    result = orchestrator.generate(
        content_type='material',
        identifier='Aluminum',
        author_data={'name': 'Todd Dunning', 'country': 'United States'}
    )
    
    # Batch generation
    results = orchestrator.generate_batch(
        content_type='material',
        identifiers=['Aluminum', 'Steel', 'Copper'],
        author_data={'name': 'Todd Dunning', 'country': 'United States'}
    )
"""

import logging
from pathlib import Path
from typing import Any, Dict, List, Optional

from shared.generators.component_generators import ComponentResult
from shared.validation.errors import ConfigurationError, GenerationError

logger = logging.getLogger(__name__)


class FrontmatterOrchestrator:
    """
    Orchestrator for multi-type frontmatter generation.
    
    Manages generator lifecycle and routes requests to appropriate generators.
    """
    
    def __init__(
        self,
        api_client: Optional[Any] = None,
        config: Optional[Dict[str, Any]] = None,
        **kwargs
    ):
        """
        Initialize orchestrator with shared dependencies.
        
        Args:
            api_client: API client for AI-assisted generation (optional)
            config: Global configuration dictionary (optional)
            **kwargs: Additional parameters passed to generators
            
        Raises:
            ConfigurationError: If critical configuration is missing
        """
        self.logger = logging.getLogger(__name__)
        self.api_client = api_client
        self.config = config or {}
        self.init_kwargs = kwargs
        
        # Generator registry: content_type -> generator_class
        self._generator_registry: Dict[str, type] = {}
        
        # Generator instances cache: content_type -> generator_instance
        self._generator_cache: Dict[str, Any] = {}
        
        # Register default generators
        self._register_default_generators()
        
        self.logger.info("FrontmatterOrchestrator initialized")
    
    def _register_default_generators(self):
        """Register default generator types"""
        # Register material generator
        try:
            from materials.generator import MaterialFrontmatterGenerator
            self.register_generator('material', MaterialFrontmatterGenerator)
            self.logger.info("✅ Registered material generator (Phase 1 wrapper with author voice)")
        except ImportError as e:
            # Fallback to legacy generator for backward compatibility
            self.logger.warning(f"New material generator not available, using legacy: {e}")
            try:
                # NOTE: StreamlinedFrontmatterGenerator removed Dec 19, 2025 - use UniversalFrontmatterExporter
                self.register_generator('material', StreamlinedFrontmatterGenerator)
                self.logger.info("✅ Registered legacy material generator (streamlined)")
            except ImportError as e2:
                self.logger.warning(f"Material generator not available: {e2}")
        
        # Register contaminant generator
        try:
            from domains.contaminants.generator import ContaminantFrontmatterGenerator
            self.register_generator('contaminant', ContaminantFrontmatterGenerator)
            self.logger.info("✅ Registered contaminant generator (modular v2.0)")
        except ImportError as e:
            self.logger.warning(f"Contaminant generator not available: {e}")
        
        # Register settings generator
        try:
            from domains.settings.generator import SettingsFrontmatterGenerator
            self.register_generator('settings', SettingsFrontmatterGenerator)
            self.logger.info("✅ Registered settings generator (modular v2.0)")
        except ImportError as e:
            self.logger.warning(f"Settings generator not available: {e}")
    
    def register_generator(self, content_type: str, generator_class: type):
        """
        Register a generator class for a content type.
        
        Args:
            content_type: Content type identifier (material, region, etc.)
            generator_class: Generator class (must inherit from BaseFrontmatterGenerator)
        """
        self._generator_registry[content_type] = generator_class
        self.logger.debug(f"Registered generator for '{content_type}': {generator_class.__name__}")
    
    def _get_generator(self, content_type: str) -> Any:
        """
        Get or create generator instance for content type.
        
        Args:
            content_type: Content type identifier
            
        Returns:
            Generator instance
            
        Raises:
            ConfigurationError: If generator not registered
        """
        # Check cache first
        if content_type in self._generator_cache:
            return self._generator_cache[content_type]
        
        # Check registry
        if content_type not in self._generator_registry:
            available_types = ', '.join(self._generator_registry.keys())
            raise ConfigurationError(
                f"No generator registered for content type '{content_type}'. "
                f"Available types: {available_types}"
            )
        
        # Create new instance
        generator_class = self._generator_registry[content_type]
        
        try:
            generator = generator_class(
                api_client=self.api_client,
                config=self.config,
                **self.init_kwargs
            )
            
            # Cache for reuse
            self._generator_cache[content_type] = generator
            
            self.logger.debug(f"Created generator instance for '{content_type}'")
            return generator
            
        except Exception as e:
            raise ConfigurationError(
                f"Failed to initialize {content_type} generator: {e}"
            )
    
    def generate(
        self,
        content_type: str,
        identifier: str,
        author_data: Optional[Dict[str, str]] = None,
        **kwargs
    ) -> ComponentResult:
        """
        Generate frontmatter for a single content item.
        
        Args:
            content_type: Type of content (material, region, application, thesaurus)
            identifier: Content identifier (material name, region name, etc.)
            author_data: Author information for voice processing (optional)
            **kwargs: Additional generation parameters
            
        Returns:
            ComponentResult with success/failure status
            
        Raises:
            ConfigurationError: If content type not supported
            GenerationError: If generation fails
        """
        self.logger.info(f"Generating {content_type} frontmatter: {identifier}")
        
        try:
            # Get appropriate generator
            generator = self._get_generator(content_type)
            
            # Generate with author voice
            result = generator.generate(
                identifier=identifier,
                author_data=author_data,
                **kwargs
            )
            
            return result
            
        except (ConfigurationError, GenerationError) as e:
            self.logger.error(f"Generation failed: {e}")
            return ComponentResult(
                component_type=content_type,
                content="",
                success=False,
                error_message=str(e)
            )
        except Exception as e:
            self.logger.error(f"Unexpected error: {e}", exc_info=True)
            raise GenerationError(f"Generation failed for {identifier}: {e}")
    
    def generate_batch(
        self,
        content_type: str,
        identifiers: List[str],
        author_data: Optional[Dict[str, str]] = None,
        continue_on_error: bool = True,
        **kwargs
    ) -> List[ComponentResult]:
        """
        Generate frontmatter for multiple content items.
        
        Args:
            content_type: Type of content (material, region, etc.)
            identifiers: List of content identifiers
            author_data: Author information for voice processing
            continue_on_error: Whether to continue after individual failures
            **kwargs: Additional generation parameters
            
        Returns:
            List of ComponentResult objects (one per identifier)
        """
        self.logger.info(
            f"Starting batch generation: {len(identifiers)} {content_type}(s)"
        )
        
        results = []
        success_count = 0
        failure_count = 0
        
        for i, identifier in enumerate(identifiers, 1):
            self.logger.info(f"Processing {i}/{len(identifiers)}: {identifier}")
            
            try:
                result = self.generate(
                    content_type=content_type,
                    identifier=identifier,
                    author_data=author_data,
                    **kwargs
                )
                
                results.append(result)
                
                if result.success:
                    success_count += 1
                else:
                    failure_count += 1
                    if not continue_on_error:
                        self.logger.error(
                            f"Stopping batch generation after failure: {identifier}"
                        )
                        break
                        
            except Exception as e:
                self.logger.error(f"Error processing {identifier}: {e}")
                
                results.append(ComponentResult(
                    component_type=content_type,
                    content="",
                    success=False,
                    error_message=str(e)
                ))
                
                failure_count += 1
                
                if not continue_on_error:
                    self.logger.error("Stopping batch generation after error")
                    break
        
        self.logger.info(
            f"Batch generation complete: "
            f"{success_count} succeeded, {failure_count} failed"
        )
        
        return results
    
    def get_supported_types(self) -> List[str]:
        """
        Get list of supported content types.
        
        Returns:
            List of registered content type identifiers
        """
        return list(self._generator_registry.keys())
    
    def is_type_supported(self, content_type: str) -> bool:
        """
        Check if a content type is supported.
        
        Args:
            content_type: Content type identifier
            
        Returns:
            True if generator is registered for this type
        """
        return content_type in self._generator_registry
    
    def clear_cache(self):
        """Clear generator instance cache"""
        self._generator_cache.clear()
        self.logger.debug("Generator cache cleared")
