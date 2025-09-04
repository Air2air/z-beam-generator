#!/usr/bin/env python3
"""
Enhanced Content Generator with AI Detection Integration
Provides iterative content improvement using AI detection feedback
"""

import logging
import sys
from typing import Dict, Optional
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from components.text.generators.fail_fast_generator import create_fail_fast_generator, ConfigurationError, GenerationError
from ai_detection.service import AIDetectionService

logger = logging.getLogger(__name__)

class ComponentResult:
    """Standard component result with success tracking."""
    def __init__(self, success: bool, content: str = "", error_message: str = "",
                 metadata: Optional[Dict] = None):
        self.success = success
        self.content = content
        self.error_message = error_message
        self.metadata = metadata or {}

class EnhancedContentComponentGenerator:
    """
    Enhanced content component generator with AI detection integration.
    Uses the centralized AI detection service through the base generator.
    """

    def __init__(self, enable_scoring: bool = True, human_threshold: float = 75.0,
                 ai_detection_service: Optional[AIDetectionService] = None,
                 max_iterations: int = 3):
        """Initialize enhanced content generator with AI detection service."""

        self.enable_scoring = enable_scoring
        self.human_threshold = human_threshold
        self.ai_detection_service = ai_detection_service
        self.max_iterations = max_iterations  # Kept for backward compatibility

        # Initialize base generator
        try:
            self.base_generator = create_fail_fast_generator(
                enable_scoring=enable_scoring,
                human_threshold=human_threshold
            )
            logger.info("✅ Base generator initialized successfully")
        except Exception as e:
            logger.error(f"❌ Base generator initialization failed: {e}")
            raise ConfigurationError(f"Base generator initialization failed: {e}")

        # AI detection service is now handled by the base generator
        logger.info("ℹ️ AI detection integrated through base generator")

    def generate(self, material_name: str, material_data: Dict,
                api_client=None, author_info: Optional[Dict] = None,
                frontmatter_data: Optional[Dict] = None,
                schema_fields: Optional[Dict] = None) -> ComponentResult:
        """
        Generate content with optional Winston iterative improvement.

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

            # Generate content using base generator (which handles AI detection internally)
            result = self.base_generator.generate(
                material_name=material_name,
                material_data=material_data,
                api_client=api_client,
                author_info=author_info,
                frontmatter_data=frontmatter_data,
                schema_fields=schema_fields
            )

            if not result.success:
                logger.error(f"❌ Content generation failed for {material_name}: {result.error_message}")
                return ComponentResult(
                    success=False,
                    error_message=result.error_message,
                    metadata=result.metadata
                )

            logger.info(f"✅ Enhanced content generation successful for {material_name}")
            return result

        except Exception as e:
            logger.error(f"❌ Enhanced content generation failed for {material_name}: {e}")
            return ComponentResult(
                success=False,
                error_message=str(e),
                metadata={'error_type': type(e).__name__}
            )
