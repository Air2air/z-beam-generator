"""
Enhanced base component for Z-Beam Generator.

Provides additional common functionality to reduce code duplication in component generators.
"""

import logging
import os
import re
import yaml
from typing import Dict, Any, Optional, List
from components.base.component import BaseComponent
from components.base.validation_utils import (
    validate_non_empty, validate_category_consistency as validate_category,
    validate_line_count, strip_markdown_code_blocks
)

logger = logging.getLogger(__name__)

class EnhancedBaseComponent(BaseComponent):
    """Enhanced base class for Z-Beam generators with additional shared functionality."""
    
    def __init__(self, subject: str, article_type: str, schema: Dict[str, Any], 
                 author_data: Dict[str, Any], component_config: Dict[str, Any]):
        """Initialize component with prompt config loading.
        
        Args:
            subject: The subject of the article
            article_type: Type of article
            schema: Schema configuration
            author_data: Author information
            component_config: Component configuration
        """
        super().__init__(subject, article_type, schema, author_data, component_config)
        # Load prompt config
        self.prompt_config = self._load_prompt_config()
    
    def _load_prompt_config(self) -> dict:
        """Load the prompt configuration from YAML.
        
        Returns:
            dict: The prompt configuration
        """
        prompt_path = self._get_prompt_path()
        if not os.path.exists(prompt_path):
            return {"validation": {}}
        
        try:
            with open(prompt_path, 'r', encoding='utf-8') as f:
                config = yaml.safe_load(f)
                return config
        except Exception as e:
            logger.error(f"Failed to load prompt config: {e}")
            return {"validation": {}}
            
    def validate_category_consistency(self, file_content: str) -> bool:
        """
        Validates category consistency in frontmatter metadata.
        
        Args:
            file_content: Content of the file to validate
            
        Returns:
            bool: True if consistent, False otherwise
            
        Raises:
            ValueError: If inconsistencies are detected
        """
        return validate_category(file_content, self.category, self.article_type, self.subject)
    
    def generate(self) -> str:
        """Generate content with standard processing flow.
        
        This implements the common pattern used by most generators:
        1. Get template data
        2. Format prompt
        3. Call API
        4. Post-process results
        
        Returns:
            str: The generated content
            
        Raises:
            ValueError: If generation fails
        """
        # Use base class schema-driven data preparation
        data = self.get_template_data()
        prompt = self._format_prompt(data)
        content = self._call_api(prompt)
        return self._post_process(content)
    
    def _validate_non_empty(self, content: str, error_message: str = "API returned empty or invalid content") -> str:
        """Validate that content is not empty.
        
        Args:
            content: Content to validate
            error_message: Custom error message
            
        Returns:
            str: Trimmed content
            
        Raises:
            ValueError: If content is empty
        """
        return validate_non_empty(content, error_message)
    
    def _validate_line_count(self, lines: List[str], min_count: int, 
                           max_count: Optional[int] = None, 
                           error_prefix: str = "Generated") -> List[str]:
        """Validate that the number of lines meets requirements.
        
        Args:
            lines: List of content lines
            min_count: Minimum required line count
            max_count: Maximum allowed line count (optional)
            error_prefix: Prefix for error message
            
        Returns:
            List[str]: Original or truncated lines
            
        Raises:
            ValueError: If line count is below minimum
        """
        return validate_line_count(lines, min_count, max_count, error_prefix)
    
    def _strip_markdown_code_blocks(self, content: str) -> str:
        """Remove markdown code block delimiters if present.
        
        Args:
            content: Content that may contain markdown code blocks
            
        Returns:
            str: Content with code block markers removed
        """
        return strip_markdown_code_blocks(content)
    
    def _post_process(self, content: str) -> str:
        """Base post-processing implementation with common validation.
        
        This provides the common validation logic that most generators need:
        1. Validates content is not empty
        2. Strips markdown code blocks
        3. Calls component-specific processing via _component_specific_processing
        
        Subclasses should override _component_specific_processing instead of this method
        unless they need to completely change the post-processing behavior.
        
        Args:
            content: Raw API response
            
        Returns:
            str: Processed content
            
        Raises:
            ValueError: If content is invalid
        """
        # Step 1: Basic validation - non-empty
        content = validate_non_empty(content, f"API returned empty or invalid {self.__class__.__name__.replace('Generator', '')}")
        
        # Step 2: Strip code blocks
        content = self._strip_markdown_code_blocks(content)
        
        # Step 3: Component-specific processing
        return self._component_specific_processing(content)
    
    def _validate_word_count(self, content: str, 
                         min_key: str = "min_words", 
                         max_key: str = "max_words", 
                         component_name: str = None) -> str:
        """Validate that the content meets word count requirements.
        
        Args:
            content: Content to validate
            min_key: Component config key for minimum word count
            max_key: Component config key for maximum word count
            component_name: Name of component for error messages (defaults to class name)
            
        Returns:
            str: The original content if valid
            
        Raises:
            ValueError: If content doesn't meet word count requirements
        """
        if not component_name:
            component_name = self.__class__.__name__.replace("Generator", "")
            
        word_count = len(content.split())
        
        # Get min/max from component config, with reasonable defaults if not specified
        min_words = self.get_component_config(min_key, 0)
        max_words = self.get_component_config(max_key, 10000)
        
        if min_words and word_count < min_words:
            raise ValueError(f"Generated {component_name} too short: {word_count} words, minimum required: {min_words}")
        
        if max_words and word_count > max_words:
            raise ValueError(f"Generated {component_name} too long: {word_count} words, maximum allowed: {max_words}")
            
        return content
        
    def _validate_links(self, content: str, max_links: int = None) -> str:
        """Validate and potentially modify links in the content.
        
        Args:
            content: Content to validate
            max_links: Maximum number of links allowed (defaults to component config)
            
        Returns:
            str: Content with validated links
        """
        # Extract all markdown links
        link_pattern = r'\[(.*?)\]\((.*?)\)'
        links = re.findall(link_pattern, content)
        
        if max_links is None:
            # Try to get from component config
            inline_links_config = self.get_component_config("inline_links", {})
            max_links = inline_links_config.get("max_links", 5)
        
        # If under the limit, return as is
        if len(links) <= max_links:
            return content
        
        # Keep only the first max_links links
        links_to_keep = links[:max_links]
        
        # Remove excess links
        modified_content = content
        for text, url in links:
            link = f'[{text}]({url})'
            if (text, url) not in links_to_keep:
                modified_content = modified_content.replace(link, text)
        
        return modified_content
        
    def _component_specific_processing(self, content: str) -> str:
        """Component-specific processing to be implemented by subclasses.
        
        Args:
            content: Pre-validated and cleaned content
            
        Returns:
            str: Processed content
            
        Raises:
            ValueError: If content fails component-specific validation
        """
        # Default implementation returns the content unchanged
        return content
