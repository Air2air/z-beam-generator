#!/usr/bin/env python3
"""
Metatags Component Generator

Generates HTML metatags using API calls.
Integrated with the modular component architecture.
"""

import sys
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).parent.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

# Import after path setup
try:
    from generators.component_generators import APIComponentGenerator
except ImportError:
    # Fallback if running standalone
    class APIComponentGenerator:
        def __init__(self, component_type): 
            self.component_type = component_type


class MetatagsComponentGenerator(APIComponentGenerator):
    """Generator for metatags components"""
    
    def __init__(self):
        super().__init__("metatags")
