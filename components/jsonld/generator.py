#!/usr/bin/env python3
"""
JSON-LD Component Generator

Generates comprehensive JSON-LD structured data with dynamic frontmatter substitution.
Uses enhanced multi-schema approach with Article, Product, HowTo, BreadcrumbList, WebPage, Website, and FAQPage.
"""

# Import the enhanced generator and use it as the main generator
from .enhanced_generator import EnhancedJsonldGenerator

# Use the enhanced generator as the main JSON-LD generator
JsonldComponentGenerator = EnhancedJsonldGenerator
