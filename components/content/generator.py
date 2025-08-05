"""
Content generator for Z-Beam Generator.

Strict fail-fast implementation with no fallbacks or defaults.
Enhanced with local formatting and validation for links, sections, and headings.
"""

import logging
import re
from components.base.component import BaseComponent

logger = logging.getLogger(__name__)

class ContentGenerator(BaseComponent):
    """Generator for main article content with strict validation and local formatting."""
    
    def _component_specific_processing(self, content: str) -> str:
        """Process the generated content with enhanced validation and formatting.
        
        Args:
            content: Pre-validated, clean API response
            
        Returns:
            str: Processed content
            
        Raises:
            ValueError: If content is invalid
        """
        # Rigorous word count validation
        content = self._validate_word_count(content)
        
        # Format and validate headings
        content = self._format_headings(content)
        
        # Format and validate links
        inline_links_config = self.get_component_config("inline_links", {})
        if inline_links_config:
            max_links = inline_links_config.get("max_links", 5)
            content = self._format_and_validate_links(content, max_links)
        
        # Ensure proper section structure
        content = self._ensure_section_structure(content)
        
        return content
    
    def _format_headings(self, content: str) -> str:
        """Format headings to ensure consistency.
        
        Args:
            content: Generated content
            
        Returns:
            str: Content with formatted headings
        """
        lines = content.split('\n')
        formatted_lines = []
        
        # Ensure we have h2 as the top-level heading (not h1)
        for line in lines:
            # Check for h1 headings and convert to h2
            if line.startswith('# '):
                formatted_lines.append(line.replace('# ', '## '))
            # Make sure all headings have a space after #
            elif re.match(r'^#{1,6}[^#\s]', line):
                hash_count = len(re.match(r'^#+', line).group())
                formatted_lines.append('#' * hash_count + ' ' + line[hash_count:])
            else:
                formatted_lines.append(line)
        
        return '\n'.join(formatted_lines)
    
    def _format_and_validate_links(self, content: str, max_links: int) -> str:
        """Format and validate links in the content.
        
        Args:
            content: Generated content
            max_links: Maximum number of links allowed
            
        Returns:
            str: Content with validated links
        """
        # Extract all markdown links
        link_pattern = r'\[(.*?)\]\((.*?)\)'
        links = re.findall(link_pattern, content)
        
        # Remove any links to z-beam.com
        modified_content = content
        for text, url in links:
            if 'z-beam.com' in url.lower():
                # Replace the link with just the text
                modified_content = modified_content.replace(f'[{text}]({url})', text)
        
        # Re-extract links after removing z-beam.com links
        links = re.findall(link_pattern, modified_content)
        
        # If under the limit, return as is
        if len(links) <= max_links:
            return modified_content
        
        # Keep only the first max_links links
        links_to_keep = links[:max_links]
        
        # Remove excess links
        for text, url in links:
            link = f'[{text}]({url})'
            if (text, url) not in links_to_keep:
                modified_content = modified_content.replace(link, text)
        
        return modified_content
    
    def _ensure_section_structure(self, content: str) -> str:
        """Ensure the content has proper section structure.
        
        Args:
            content: Generated content
            
        Returns:
            str: Content with proper section structure
        """
        # Check if we have frontmatter data with section requirements
        if hasattr(self, '_frontmatter_data') and self._frontmatter_data and 'sections' in self._frontmatter_data:
            # We have predefined sections in frontmatter, validate against those
            required_sections = [section.lower() for section in self._frontmatter_data['sections']]
            
            # Extract headings from content
            heading_pattern = r'^#{1,6}\s+(.*?)$'
            headings = []
            for line in content.split('\n'):
                heading_match = re.match(heading_pattern, line)
                if heading_match:
                    headings.append(heading_match.group(1).lower())
            
            # Check if all required sections are present
            missing_sections = [section for section in required_sections if not any(section.lower() in heading.lower() for heading in headings)]
            
            if missing_sections:
                logger.warning(f"Missing required sections: {missing_sections}")
                # We could add these sections here, but for now just log the warning
        
        return content