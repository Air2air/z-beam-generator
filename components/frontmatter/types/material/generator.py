#!/usr/bin/env python3
"""
Material Frontmatter Generator

Adapter for StreamlinedFrontmatterGenerator that provides compatibility with
the new BaseFrontmatterGenerator architecture while preserving all existing functionality.

This is Phase 1 - creating a thin wrapper that allows both architectures to coexist.
Full refactoring to inherit from BaseFrontmatterGenerator will happen in Phase 2.

Design:
- Wraps existing StreamlinedFrontmatterGenerator
- Implements BaseFrontmatterGenerator interface methods
- Delegates to legacy generator for actual work
- Adds author voice post-processing layer
- Maintains 100% backward compatibility
"""

import logging
from pathlib import Path
from typing import Dict, Any, Optional

from components.frontmatter.core.base_generator import BaseFrontmatterGenerator, GenerationContext
from components.frontmatter.core.streamlined_generator import StreamlinedFrontmatterGenerator
from generators.component_generators import ComponentResult
from validation.errors import MaterialDataError, GenerationError

logger = logging.getLogger(__name__)


class MaterialFrontmatterGenerator(BaseFrontmatterGenerator):
    """
    Material frontmatter generator with new architecture compatibility.
    
    Phase 1 Implementation:
    - Wraps StreamlinedFrontmatterGenerator
    - Adds BaseFrontmatterGenerator interface
    - Provides author voice integration
    - Maintains full backward compatibility
    
    Future Phase 2:
    - Extract logic directly from StreamlinedFrontmatterGenerator
    - Remove wrapper pattern
    - Full native BaseFrontmatterGenerator implementation
    """
    
    def __init__(
        self,
        api_client: Optional[Any] = None,
        config: Optional[Dict[str, Any]] = None,
        **kwargs
    ):
        """
        Initialize material generator with backward compatibility.
        
        Args:
            api_client: API client for AI-assisted generation (optional)
            config: Configuration dictionary (optional)
            **kwargs: Additional parameters for legacy generator
        """
        # Initialize base class
        super().__init__(
            content_type='material',
            api_client=api_client,
            config=config,
            **kwargs
        )
        
        # Create wrapped legacy generator
        # This preserves all existing functionality while we transition
        self._legacy_generator = StreamlinedFrontmatterGenerator(
            api_client=api_client,
            config=config,
            **kwargs
        )
        
        self.logger.info("MaterialFrontmatterGenerator initialized (Phase 1 wrapper)")
    
    def _load_type_data(self):
        """
        Load material-specific data structures.
        
        Phase 1: Delegate to legacy generator's initialization
        (already done in StreamlinedFrontmatterGenerator.__init__)
        """
        # Data loading handled by StreamlinedFrontmatterGenerator
        # No additional loading needed in Phase 1
        self.logger.debug("Material data loading handled by legacy generator")
    
    def _validate_identifier(self, identifier: str) -> bool:
        """
        Validate that material exists in data structures.
        
        Args:
            identifier: Material name
            
        Returns:
            True if material is valid
            
        Raises:
            MaterialDataError: If material not found
        """
        # Use materials.py data access functions
        from data.materials import get_material_by_name_cached
        
        try:
            material_data = get_material_by_name_cached(identifier)
            if not material_data:
                raise MaterialDataError(
                    f"Material '{identifier}' not found in materials.yaml"
                )
            return True
        except Exception as e:
            raise MaterialDataError(f"Material validation failed for '{identifier}': {e}")
    
    def _build_frontmatter_data(
        self,
        identifier: str,
        context: GenerationContext
    ) -> Dict[str, Any]:
        """
        Build complete material frontmatter data.
        
        Phase 1: Delegate to legacy generator
        
        Args:
            identifier: Material name
            context: Generation context
            
        Returns:
            Complete frontmatter dictionary
            
        Raises:
            GenerationError: If frontmatter construction fails
        """
        try:
            # Use legacy generator's comprehensive generate() method
            # This preserves ALL existing functionality:
            # - Property enhancement
            # - Range calculations
            # - Template processing
            # - Machine settings
            # - Environmental impact
            # - Industry applications
            # - Regulatory standards
            result = self._legacy_generator.generate(
                material_name=identifier,
                # Pass through any additional parameters from context
                **(context.additional_params or {})
            )
            
            if not result.success:
                raise GenerationError(
                    f"Legacy generator failed: {result.error_message}"
                )
            
            # Extract frontmatter data from result
            # The legacy generator returns ComponentResult with content
            frontmatter_data = result.content
            
            return frontmatter_data
            
        except Exception as e:
            raise GenerationError(f"Failed to build material frontmatter: {e}")
    
    def _get_schema_name(self) -> str:
        """
        Get schema name for material validation.
        
        Returns:
            Schema filename
        """
        return 'material_schema.json'
    
    def _get_output_filename(self, identifier: str) -> str:
        """
        Generate output filename for material.
        
        Args:
            identifier: Material name
            
        Returns:
            Safe filename with appropriate extension
        """
        from utils.filename import generate_safe_filename
        
        # Generate safe filename (e.g., "aluminum-laser-cleaning.yaml")
        safe_name = generate_safe_filename(identifier)
        return f"{safe_name}-laser-cleaning.yaml"
    
    def generate(
        self,
        identifier: str = None,
        material_name: str = None,
        author_data: Optional[Dict[str, str]] = None,
        **kwargs
    ) -> ComponentResult:
        """
        Generate material frontmatter with author voice.
        
        Supports both new interface (identifier) and legacy interface (material_name).
        
        Args:
            identifier: Material name (new interface)
            material_name: Material name (legacy interface)
            author_data: Author information for voice processing
            **kwargs: Additional generation parameters
            
        Returns:
            ComponentResult with success/failure status
        """
        # Support both interfaces
        material = identifier or material_name
        
        if not material:
            return ComponentResult(
                component_name='material',
                success=False,
                error_message="Material name required (use 'identifier' or 'material_name')"
            )
        
        # Use base class generate() which includes author voice processing
        return super().generate(
            identifier=material,
            author_data=author_data,
            **kwargs
        )


# Backward compatibility alias
# Allows existing code to import StreamlinedFrontmatterGenerator from new location
class StreamlinedFrontmatterGeneratorAlias(MaterialFrontmatterGenerator):
    """
    Backward compatibility alias.
    
    Allows code like:
        from components.frontmatter.types.material.generator import StreamlinedFrontmatterGenerator
    
    To continue working during the transition period.
    """
    pass
