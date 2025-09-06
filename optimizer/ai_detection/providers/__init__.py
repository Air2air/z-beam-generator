#!/usr/bin/env python3
"""
AI Detection Providers Package
"""

from .mock import MockProvider
from .winston import WinstonProvider

__all__ = ["WinstonProvider", "MockProvider"]
