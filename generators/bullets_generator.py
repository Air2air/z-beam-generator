#!/usr/bin/env python3
"""
Bullets Component Generator

Generates bullet point content with author-specific formatting rules.
"""

import logging
from generators.component_generators import APIComponentGenerator

logger = logging.getLogger(__name__)

class BulletsComponentGenerator(APIComponentGenerator):
    """Generator for bullets components with author-specific formatting"""
    
    def __init__(self):
        super().__init__("bullets")

def create_bullets_generator():
    """Factory function to create a bullets generator"""
    return BulletsComponentGenerator()
