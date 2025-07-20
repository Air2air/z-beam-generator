"""
MODULE DIRECTIVES FOR AI ASSISTANTS:
1. INTERFACE DEFINITION: This defines the component interface - do not modify core methods
2. FRONTMATTER EXTRACTION: extract_frontmatter_data must remain consistent
3. CONTEXT HANDLING: All components must have access to full context
4. NO DEFAULT IMPLEMENTATIONS: Abstract methods should not have implementations
5. TYPE ANNOTATIONS: Maintain proper type annotations on all methods
"""

"""
Base component class for all content generators.
"""

import logging
import re
import yaml
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)

class BaseComponent(ABC):
    """Base class for all components that generate content."""
    
    def __init__(self, context: Dict[str, Any], schema: Dict[str, Any], ai_provider: str = "deepseek"):
        """Initialize base component.
        
        Args:
            context: Context data including subject, article_type, etc.
            schema: Schema definition for content generation
            ai_provider: AI provider to use (default: deepseek)
        """
        self.context = context or {}
        self.schema = schema or {}
        
        # Extract common attributes from context
        self.subject = self.context.get("subject", "")
        self.article_type = self.context.get("article_type", "material")
        self.ai_provider = ai_provider
        
        # Component state
        self.options = {}
        self.frontmatter = {}
        self.previous_outputs = {}
        
        # Initialize API client
        self.api_client = None
        self._init_api_client()
    
    def _init_api_client(self) -> None:
        """Initialize API client for AI content generation."""
        try:
            from api import get_client
            self.api_client = get_client(self.ai_provider)
            logger.debug(f"Initialized API client for {self.ai_provider}")
        except ImportError:
            logger.error("Could not import api.get_client")
        except Exception as e:
            logger.error(f"Error initializing API client: {e}")
    
    @abstractmethod
    def generate(self) -> str:
        """Generate component output content."""
        pass
    
    def set_options(self, options: Dict[str, Any]) -> 'BaseComponent':
        """Set component-specific options."""
        self.options = options or {}
        return self
    
    def set_frontmatter(self, frontmatter: Dict[str, Any]) -> 'BaseComponent':
        """Set frontmatter data for content generation."""
        self.frontmatter = frontmatter or {}
        return self
    
    def set_previous_outputs(self, previous_outputs: Dict[str, Any]) -> 'BaseComponent':
        """Set previous component outputs."""
        self.previous_outputs = previous_outputs or {}
        return self
    
    def extract_frontmatter_data(self) -> Dict[str, Any]:
        """Extract frontmatter data from various sources."""
        # First try direct frontmatter
        if self.frontmatter:
            return self.frontmatter
        
        # Then try previous outputs
        if self.previous_outputs:
            for output_name, output_content in self.previous_outputs.items():
                if output_name == "frontmatter" and isinstance(output_content, str):
                    frontmatter_match = re.search(r'---\s*(.*?)\s*---', output_content, re.DOTALL)
                    if frontmatter_match:
                        try:
                            return yaml.safe_load(frontmatter_match.group(1)) or {}
                        except Exception as e:
                            logger.error(f"Failed to parse frontmatter YAML: {e}")
        
        # Return empty dict if nothing found
        return {}
    
    def get_frontmatter_data(self) -> Dict[str, Any]:
        """Get frontmatter data (wrapper method to ensure consistent access)."""
        return self.extract_frontmatter_data()
    
    def format_section_title(self, key: str) -> str:
        """Convert a camelCase or snake_case key to Title Case for display."""
        # First handle camelCase
        if any(c.isupper() for c in key):
            # Insert spaces before uppercase letters
            display_name = re.sub(r'([A-Z])', r' \1', key).strip()
            # Special case for ID to avoid "I D"
            display_name = display_name.replace(" I D", " ID")
        else:
            # Handle snake_case
            display_name = key.replace('_', ' ')
        
        # Capitalize first letter of each word
        return ' '.join(word.capitalize() for word in display_name.split())
        
    def generate_safe(self) -> str:
        """Safe wrapper for generate with error handling."""
        try:
            if not self.api_client:
                logger.error("No API client available")
                return f"<!-- Error: No API client available for {self.__class__.__name__} -->\n\n"
                
            return self.generate()
        except Exception as e:
            logger.error(f"Error in {self.__class__.__name__}.generate(): {e}")
            return f"<!-- Error in {self.__class__.__name__}: {str(e)} -->\n\n"