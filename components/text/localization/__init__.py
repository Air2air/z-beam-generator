"""
Text Component Localization Module

This module provides essential localization functionality for all text generation.
Localization is MANDATORY for all text generation requests.
"""

from .prompt_chain import (
    LocalizationPromptChain,
    localization_chain,
    get_required_localization_prompt,
    validate_localization_support
)

__all__ = [
    'LocalizationPromptChain',
    'localization_chain', 
    'get_required_localization_prompt',
    'validate_localization_support'
]
