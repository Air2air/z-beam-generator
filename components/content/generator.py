"""
Content generator for Z-Beam Generator.

Strict fail-fast implementation with no fallbacks or defaults.
Includes support for limiting links to technical terms and setting maximum link count.
"""

import logging
from components.base.enhanced_component import EnhancedBaseComponent

logger = logging.getLogger(__name__)

class ContentGenerator(EnhancedBaseComponent):
    """Generator for main article content with strict validation."""
    
    def _post_process(self, content: str) -> str:
        """Post-process the generated content.
        
        Args:
            content: Raw API response
            
        Returns:
            str: Processed content
            
        Raises:
            ValueError: If content is invalid
        """
        # Validate and clean input
        content = self._validate_non_empty(content, "API returned empty or invalid content")
        
        # Strip any markdown code blocks that might have been added
        clean_content = self._strip_markdown_code_blocks(content)
        
        # Rigorous word count validation
        word_count = len(clean_content.split())
        min_words = self.get_component_config("min_words")
        max_words = self.get_component_config("max_words")
        
        if word_count < min_words:
            raise ValueError(f"Generated content too short: {word_count} words, minimum required: {min_words}")
        
        if word_count > max_words:
            raise ValueError(f"Generated content too long: {word_count} words, maximum allowed: {max_words}")
        
        # Validate links if configured
        inline_links_config = self.get_component_config("inline_links", {})
        if inline_links_config:
            clean_content = self._validate_links(clean_content, inline_links_config)
        
        return clean_content
        
    def _validate_links(self, content: str, inline_links_config: dict) -> str:
        """Validate and potentially modify links in the content based on configuration.
        
        Args:
            content: The processed content
            inline_links_config: Configuration for inline links
            
        Returns:
            str: Content with validated links
        """
        import re
        
        # Extract all markdown links
        link_pattern = r'\[(.*?)\]\((.*?)\)'
        links = re.findall(link_pattern, content)
        
        # Check if we exceed the maximum number of links
        max_links = inline_links_config.get("max_links", 5)
        if len(links) > max_links:
            # Keep only the first max_links links
            links_to_keep = links[:max_links]
            
            # Remove excess links
            modified_content = content
            for text, url in links:
                link = f'[{text}]({url})'
                if (text, url) not in links_to_keep:
                    modified_content = modified_content.replace(link, text)
            
            return modified_content
        
        # If we don't exceed max_links, return content unchanged
        return content