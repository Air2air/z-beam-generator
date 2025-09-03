#!/usr/bin/env python3
"""
Content Component Generator
Wrapper for fail-fast content generator with component interface
"""

import logging
import sys
from typing import Dict, Optional
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from .generators.fail_fast_generator import create_fail_fast_generator, ConfigurationError, GenerationError

logger = logging.getLogger(__name__)

class ComponentResult:
    """Standard component result with success tracking."""
    def __init__(self, success: bool, content: str = "", error_message: str = "", 
                 metadata: Optional[Dict] = None):
        self.success = success
        self.content = content
        self.error_message = error_message
        self.metadata = metadata or {}

class ContentComponentGenerator:
    """
    Content component generator using fail-fast approach.
    No fallbacks - fails immediately on missing dependencies.
    """
    
    def __init__(self, enable_scoring: bool = True, human_threshold: float = 75.0):
        """Initialize content generator with scoring configuration."""
        self.enable_scoring = enable_scoring
        self.human_threshold = human_threshold
        
        # Create fail-fast generator immediately to validate configurations
        try:
            self.generator = create_fail_fast_generator(
                enable_scoring=enable_scoring,
                human_threshold=human_threshold
            )
            logger.info("✅ Content component generator initialized successfully")
        except Exception as e:
            logger.error(f"❌ Failed to initialize content generator: {e}")
            raise ConfigurationError(f"Content generator initialization failed: {e}")
    
    def generate(self, material_name: str, material_data: Dict,
                api_client=None, author_info: Optional[Dict] = None,
                frontmatter_data: Optional[Dict] = None,
                schema_fields: Optional[Dict] = None) -> ComponentResult:
        """
        Generate content using fail-fast generator.
        
        Args:
            material_name: Name of the material for content generation
            material_data: Material properties and characteristics
            api_client: API client for content generation (required)
            author_info: Author information including ID (required)
            frontmatter_data: Additional material context
            schema_fields: Schema field specifications
            
        Returns:
            ComponentResult with content or error information
        """
        try:
            # Fail fast on missing requirements
            if not api_client:
                raise GenerationError("API client is required for content generation")
            
            if not author_info or 'id' not in author_info:
                raise GenerationError("Valid author information with 'id' field is required")
            
            logger.info(f"🔄 Generating content for {material_name} with author {author_info.get('id')}")
            
            # Use fail-fast generator
            result = self.generator.generate(
                material_name=material_name,
                material_data=material_data,
                api_client=api_client,
                author_info=author_info,
                frontmatter_data=frontmatter_data,
                schema_fields=schema_fields
            )
            
            if result.success:
                logger.info(f"✅ Content generation successful for {material_name}")
                return ComponentResult(
                    success=True,
                    content=result.content,
                    metadata=result.metadata
                )
            else:
                logger.error(f"❌ Content generation failed for {material_name}: {result.error_message}")
                return ComponentResult(
                    success=False,
                    error_message=result.error_message,
                    metadata=result.metadata
                )
                
        except (ConfigurationError, GenerationError) as e:
            logger.error(f"❌ Content generation error for {material_name}: {e}")
            return ComponentResult(
                success=False,
                error_message=str(e),
                metadata={"error_type": "configuration_or_generation_error"}
            )
            
        except Exception as e:
            logger.error(f"❌ Unexpected error during content generation for {material_name}: {e}")
            return ComponentResult(
                success=False,
                error_message=f"Unexpected error: {e}",
                metadata={"error_type": "unexpected_error"}
            )