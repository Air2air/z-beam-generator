#!/usr/bin/env python3
"""
Setup script for the Z-Beam Generator package.
This handles the import path setup when running from within the generator directory.
"""

import sys
import os

def setup_generator_path():
    """Add the generator directory to Python path for internal imports."""
    generator_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Add generator directory to path if not already there
    if generator_dir not in sys.path:
        sys.path.insert(0, generator_dir)
    
    # Also add parent directory for root-level imports
    parent_dir = os.path.dirname(generator_dir)
    if parent_dir not in sys.path:
        sys.path.insert(0, parent_dir)

# Auto-setup when this module is imported
setup_generator_path()
