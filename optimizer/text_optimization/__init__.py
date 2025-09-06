"""
Text Component Optimization Module

This module contains optimization-related functionality for the text component,
separated from the core text generation logic for better organization.

Contents:
- AI Detection Configuration Optimizer
- AI Detection Prompt Optimizer
- Dynamic Prompt Generator
- Dynamic Prompt System
"""

from .ai_detection_config_optimizer import AIDetectionConfigOptimizer

__version__ = "1.0.0"
__all__ = [
    "AIDetectionConfigOptimizer",
]
