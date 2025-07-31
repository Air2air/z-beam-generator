"""
Base component for Z-Beam Generator.

Strict fail-fast implementation with no fallbacks or defaults.
"""

import logging
import os
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)

class BaseComponent(ABC):
    """Abstract base class for all Z-Beam generators with strict validation."""
    
    def __init__(self, subject: str, article_type: str, schema: Dict[str, Any], 
                 author_data: Dict[str, Any], component_config: Dict[str, Any]):
        """Initialize component with strict validation.
        
        Args:
            subject: The subject of the article
            article_type: Type of article (material, application, region, thesaurus)
            schema: Schema configuration for the article type
            author_data: Author information
            component_config: Component-specific configuration
            
        Raises:
            ValueError: If any required parameter is missing or invalid
        """
        # Strict validation - no fallbacks
        if not subject or not isinstance(subject, str):
            raise ValueError("Subject must be a non-empty string")
        
        if not article_type or article_type not in ["material", "application", "region", "thesaurus"]:
            raise ValueError(f"Invalid article_type: {article_type}")
        
        if not schema or not isinstance(schema, dict):
            raise ValueError("Schema must be a non-empty dictionary")
        
        if not author_data or not isinstance(author_data, dict):
            raise ValueError("Author data must be a non-empty dictionary")
        
        if not component_config or not isinstance(component_config, dict):
            raise ValueError("Component config must be a non-empty dictionary")
        
        self.subject = subject
        self.article_type = article_type
        self.schema = schema
        self.author_data = author_data
        self.component_config = component_config
    
    @abstractmethod
    def generate(self) -> str:
        """Generate component content with strict validation.
        
        Returns:
            str: The generated content
            
        Raises:
            ValueError: If generation fails
        """
        pass
    
    def _prepare_data(self) -> Dict[str, Any]:
        """Prepare base data for generation with strict validation.
        
        Returns:
            Dict[str, Any]: Base data for prompt formatting
            
        Raises:
            ValueError: If required data is missing
        """
        # Validate required author fields
        required_author_fields = ["author_name", "author_country"]
        for field in required_author_fields:
            if field not in self.author_data:
                raise ValueError(f"Required author field '{field}' is missing")
        
        return {
            "subject": self.subject,
            "article_type": self.article_type,
            "author_name": self.author_data["author_name"],
            "author_country": self.author_data["author_country"],
            "schema": self.schema
        }
    
    def get_component_config(self, key: Optional[str] = None) -> Any:
        """Get component configuration with strict validation.
        
        Args:
            key: Optional specific config key to retrieve
            
        Returns:
            Any: Configuration value or entire config if no key specified
            
        Raises:
            ValueError: If key is not found
        """
        if key is None:
            return self.component_config
        
        if key not in self.component_config:
            raise ValueError(f"Required component config '{key}' is missing")
        
        return self.component_config[key]
    
    def get_frontmatter_data(self) -> Optional[Dict[str, Any]]:
        """Get frontmatter data if available.
        
        Returns:
            Dict[str, Any]: Frontmatter data or None if not available
        """
        # This will be populated by the orchestration layer
        # Components should validate if frontmatter is required for their operation
        return getattr(self, '_frontmatter_data', None)
    
    def _format_prompt(self, data: Dict[str, Any]) -> str:
        """Format prompt using component's prompt template.
        
        Args:
            data: Data for template formatting
            
        Returns:
            str: Formatted prompt
            
        Raises:
            ValueError: If prompt template cannot be loaded or formatted
        """
        prompt_path = self._get_prompt_path()
        
        if not os.path.exists(prompt_path):
            raise ValueError(f"Prompt template not found: {prompt_path}")
        
        try:
            with open(prompt_path, 'r', encoding='utf-8') as f:
                template = f.read()
        except Exception as e:
            raise ValueError(f"Failed to read prompt template: {e}")
        
        try:
            return template.format(**data)
        except KeyError as e:
            raise ValueError(f"Missing template variable: {e}")
    
    def _get_prompt_path(self) -> str:
        """Get path to component's prompt template.
        
        Returns:
            str: Path to prompt template
        """
        component_name = self.__class__.__name__.replace("Generator", "").lower()
        return f"components/{component_name}/prompt.yaml"
    
    def _call_api(self, prompt: str) -> str:
        """Call API with the formatted prompt.
        
        Args:
            prompt: Formatted prompt
            
        Returns:
            str: API response
            
        Raises:
            ValueError: If API call fails
        """
        from api.client import make_api_call
        
        try:
            return make_api_call(prompt, self.component_config)
        except Exception as e:
            raise ValueError(f"API call failed: {e}")
