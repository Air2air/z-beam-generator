"""
Metatags generator for Z-Beam Generator.

Generates HTML meta tags for SEO and social sharing.
"""

import logging
import re
from components.base.component import BaseComponent

logger = logging.getLogger(__name__)

class MetatagsGenerator(BaseComponent):
    """Generator for HTML meta tags with strict validation."""
    
    def generate(self) -> str:
        """Generate meta tags content with strict validation.
        
        Returns:
            str: The generated HTML meta tags
            
        Raises:
            ValueError: If generation fails
        """
        # Use base class schema-driven data preparation
        data = self.get_template_data()
        prompt = self._format_prompt(data)
        content = self._call_api(prompt)
        return self._post_process(content)
    
    def _post_process(self, content: str) -> str:
        """Post-process the generated meta tags.
        
        Args:
            content: Raw API response
            
        Returns:
            str: Processed HTML meta tags
            
        Raises:
            ValueError: If content is invalid
        """
        if not content or not content.strip():
            raise ValueError("API returned empty or invalid meta tags")
        
        # Extract meta tags from the response
        meta_tags = []
        
        # Extract standard HTML meta tags
        html_meta_pattern = r'<meta[^>]+>'
        html_meta_matches = re.findall(html_meta_pattern, content)
        if html_meta_matches:
            meta_tags.extend(html_meta_matches)
        
        # Extract Open Graph and Twitter tags
        og_pattern = r'<meta\s+property="og:[^"]+"[^>]+>'
        twitter_pattern = r'<meta\s+name="twitter:[^"]+"[^>]+>'
        
        og_matches = re.findall(og_pattern, content)
        twitter_matches = re.findall(twitter_pattern, content)
        
        meta_tags.extend(og_matches)
        meta_tags.extend(twitter_matches)
        
        # If no valid meta tags were found, try to create them from the content
        if not meta_tags:
            lines = content.strip().split('\n')
            for line in lines:
                line = line.strip()
                if line.startswith('<meta'):
                    meta_tags.append(line)
        
        # Validate the minimum number of tags
        min_tags = self.get_component_config("min_tags")
        if len(meta_tags) < min_tags:
            raise ValueError(f"Generated only {len(meta_tags)} meta tags, minimum required: {min_tags}")
        
        # Format the meta tags output
        formatted_output = "<!-- Meta Tags for SEO and Social Sharing -->\n"
        formatted_output += "\n".join(meta_tags)
        
        return formatted_output
