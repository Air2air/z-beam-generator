#!/usr/bin/env python3
"""
JSON-LD Component Generator

Generates JSON-LD structured data using ONLY frontmatter data.
Simplified approach for reliable generation.
"""

# Import the simplified generator and use it as the main generator
from .simple_generator import SimpleJsonldGenerator

# Use the simple generator as the main JSON-LD generator
JsonldComponentGenerator = SimpleJsonldGenerator
