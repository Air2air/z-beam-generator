#!/usr/bin/env python3
"""
AI Detection module for text component.

Provides AI detection prompt chaining functionality.
"""

from .prompt_chain import (
    get_ai_detection_prompt,
    update_ai_detection_flags,
    validate_ai_detection_support,
    ai_detection_chain
)

__all__ = [
    'get_ai_detection_prompt',
    'update_ai_detection_flags', 
    'validate_ai_detection_support',
    'ai_detection_chain'
]
