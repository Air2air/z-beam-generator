"""
Shared Image Generation Module

Generic image generation infrastructure (learning, prompts, monitoring).
Reusable across all domains for AI-powered image generation.

Author: AI Assistant  
Date: November 26, 2025 (Extracted from materials domain)
"""

from shared.image.learning import (
    ImageGenerationLogger,
    create_logger
)
from shared.image.utils import (
    SharedPromptBuilder,
    PromptOptimizer,
    get_pipeline_monitor,
    FailureStage,
    FailureType
)

__all__ = [
    'ImageGenerationLogger',
    'create_logger',
    'SharedPromptBuilder',
    'PromptOptimizer',
    'get_pipeline_monitor',
    'FailureStage',
    'FailureType',
]
