#!/usr/bin/env python3
"""
Article Composer - Handles final article assembly and formatting
"""

import logging

logger = logging.getLogger(__name__)

class ArticleComposer:
    """Composes final article from generated sections"""
    
    @staticmethod
    def format_section(section_name, section_title, content):
        """Format section with appropriate headers - NO METADATA HANDLING"""
        return f"## {section_title}\n\n{content}\n"
    
    @staticmethod
    def combine_sections(sections, material):
        """Combine all generated sections into final article - NO METADATA"""
        header = f"# Laser Cleaning for {material}\n\n"
        article_body = "\n".join(sections)
        return header + article_body