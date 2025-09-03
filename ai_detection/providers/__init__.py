#!/usr/bin/env python3
"""
AI Detection Providers Package
"""

from .gptzero import GPTZeroProvider
from .mock import MockProvider

__all__ = [
    'GPTZeroProvider',
    'MockProvider'
]
