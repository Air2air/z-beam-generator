#!/usr/bin/env python3
"""
Properties Table Component

Generates standardized properties tables from frontmatter data.
"""

from .generator import (
    PropertiesTableGenerator,
    create_properties_table_template,
    generate_properties_table_content
)

__all__ = [
    'PropertiesTableGenerator',
    'create_properties_table_template', 
    'generate_properties_table_content'
]
