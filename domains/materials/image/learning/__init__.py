"""
Image Generation Learning System

Tracks generation attempts, identifies failure patterns,
and optimizes parameters based on historical data.
"""

from .image_generation_logger import ImageGenerationLogger, create_logger

__all__ = ['ImageGenerationLogger', 'create_logger']
