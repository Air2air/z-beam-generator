#!/usr/bin/env python3
"""
Frontmatter Component Generator - Modular Architecture

This is the main entry point for frontmatter generation, now using
a clean modular architecture with separated concerns:

- core/generator.py: Core generation logic
- ordering/field_ordering_service.py: Field ordering functionality  
- enhancement/property_enhancement_service.py: Property enhancement
- core/validation_helpers.py: Validation and correction helpers

This maintains backward compatibility while providing a much cleaner
codebase with better separation of concerns.
"""

# Import the streamlined generator from core module
from components.frontmatter.core.streamlined_generator import StreamlinedFrontmatterGenerator

# Re-export for backward compatibility
FrontmatterComponentGenerator = StreamlinedFrontmatterGenerator
__all__ = ['FrontmatterComponentGenerator']
