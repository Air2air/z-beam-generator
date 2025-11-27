"""
Shared Text Generation System

Provides utilities, templates, and validation for text generation across all domains.
Matches the image generation architecture for consistency.
"""

from shared.text.utils.prompt_builder import PromptBuilder
from shared.text.utils.component_specs import ComponentRegistry, DomainContext
from shared.text.utils.length_manager import LengthManager
from shared.text.utils.sentence_calculator import SentenceCalculator

__all__ = [
    'PromptBuilder',
    'ComponentRegistry',
    'DomainContext',
    'LengthManager',
    'SentenceCalculator',
]
