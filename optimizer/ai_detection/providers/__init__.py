#!/usr/bin/env python3
"""
AI Detection Providers Package
"""

from .winston import WinstonProvider
from .mock import MockProvider

__all__ = [
    'WinstonProvider',
    'MockProvider'
]
