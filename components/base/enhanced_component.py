"""
Enhanced base component for Z-Beam Generator.

Provides additional common functionality to reduce code duplication in component generators.
"""

import logging
import os
import yaml
from abc import abstractmethod
from typing import Dict, Any, Optional, List, Tuple
from components.base.component import BaseComponent

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
        if not content or not content.strip():
            raise ValueError(error_message)
        return content.strip()
    
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
        if len(lines) < min_count:
            raise ValueError(f"{error_prefix} {len(lines)} lines, minimum required: {min_count}")
        
        if max_count and len(lines) > max_count:
            # Truncate to max count
            return lines[:max_count]
            
        return lines
    
    def _strip_markdown_code_blocks(self, content: str) -> str:
        """Remove markdown code block delimiters if present.
        
        Args:
            content: Content that may contain markdown code blocks
            
        Returns:
            str: Content with code block markers removed
        """
        content = content.strip()
        
        # Handle triple backtick code blocks with language specifier
        if content.startswith('```') and content.endswith('```'):
            lines = content.split('\n')
            if len(lines) > 2:  # At least opening, content, and closing
                # Remove first and last lines (opening and closing ```)
                return '\n'.join(lines[1:-1])
        
        return content
    
    @abstractmethod
    def _post_process(self, content: str) -> str:
        """Post-process the generated content. Must be implemented by subclasses.
        
        Args:
            content: Raw API response
            
        Returns:
            str: Processed content
            
        Raises:
            ValueError: If content is invalid
        """
        pass
