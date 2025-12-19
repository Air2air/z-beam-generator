"""
Shared Image Learning Module

Image generation logging and learning infrastructure.
Reusable across all domains.

Author: AI Assistant  
Date: November 26, 2025 (Extracted from materials domain)
"""

from shared.image.learning.image_generation_logger import (
    ImageGenerationLogger,
    create_logger,
)

__all__ = [
    'ImageGenerationLogger',
    'create_logger',
]
