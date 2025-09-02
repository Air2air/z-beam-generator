#!/usr/bin/env python3
"""
Content Component Generator Wrapper

Simple wrapper that integrates fail_fast_generator with the ComponentGeneratorFactory system.
"""

import logging
from typing import Dict, Optional
from dataclasses import dataclass

logger = logging.getLogger(__name__)

@dataclass
class ComponentResult:
    """Result of component generation"""
    component_type: str
    content: str
    success: bool
    error_message: Optional[str] = None

class ContentComponentGenerator:
    """Lightweight wrapper for fail_fast_generator integration"""
    
    def __init__(self):
        self.component_type = "content"
        
    def generate(self, material_name: str, material_data: Dict, 
                api_client=None, author_info: Optional[Dict] = None,
                frontmatter_data: Optional[Dict] = None,
                schema_fields: Optional[Dict] = None) -> ComponentResult:
        """Generate content using fail_fast_generator"""
        
        try:
            # Import the fail_fast_generator
            from components.content.generators.fail_fast_generator import create_fail_fast_generator
            
            # Create generator with NO FALLBACKS - scoring disabled to avoid dependencies
            generator = create_fail_fast_generator(
                max_retries=0,  # NO RETRIES - fail immediately
                retry_delay=0.0,
                enable_scoring=False,  # NO SCORING - avoid dependencies
                human_threshold=0.0
            )
            
            # Require real API client - no mocks or fallbacks
            if not api_client:
                return ComponentResult(
                    component_type=self.component_type,
                    content="",
                    success=False,
                    error_message="API client is required - no mock fallbacks available"
                )
            
            # Call the generator with the parameters it expects
            result = generator.generate(
                material_name=material_name,
                material_data=material_data,
                api_client=api_client,
                author_info=author_info,
                frontmatter_data=frontmatter_data
            )
            
            # Convert to ComponentResult format
            return ComponentResult(
                component_type=self.component_type,
                content=result.content,
                success=result.success,
                error_message=result.error_message if not result.success else None
            )
            
        except Exception as e:
            logger.error(f"Error in content generator: {e}")
            return ComponentResult(
                component_type=self.component_type,
                content="",
                success=False,
                error_message=str(e)
            )