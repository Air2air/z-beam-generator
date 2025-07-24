"""
MODULE DIRECTIVES FOR AI ASSISTANTS:
1. INTERFACE DEFINITION: This defines the component interface - do not modify core methods
2. NO CACHING: No caching of resources, data, or objects anywhere in the system
3. FRESH DATA LOADING: All data must be loaded fresh from disk or source on each access
4. DYNAMIC SCHEMA: Components should use schema for content generation without hardcoding
5. PURE FUNCTIONS: Prefer pure functions over stateful methods when possible
6. ERROR HANDLING: Components must gracefully handle API failures
7. GRACEFUL FALLBACK: Generate useful error messages in content when API fails
8. ERROR REPORTING: Log detailed error messages for debugging
9. SCHEMA ADHERENCE: Always follow the schema definition when generating content
10. NO DEFAULT IMPLEMENTATIONS: Abstract methods should not have implementations
"""

import logging
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List

from components.base.api_client_factory import ApiClientFactory
from components.base.config_manager import ComponentConfigManager
from components.base.error_handler import ErrorHandler
from components.base.utils import FrontmatterUtils, MarkdownUtils

logger = logging.getLogger(__name__)

class BaseComponent(ABC):
    """Base class for all content generation components."""
    
    def __init__(self, *args, **kwargs):
        """Initialize the base component.
    
        This constructor is designed to handle both legacy and new initialization patterns:
        - Legacy: (context, schema, ai_provider)
        - New: (subject, article_type, component_type, config)
    
        It intelligently determines which pattern is being used and sets up the component accordingly.
        """
        # Extract parameters based on argument count and types
        if len(args) >= 2 and isinstance(args[0], dict) and (isinstance(args[1], dict) or args[1] is None):
            # Legacy initialization pattern: (context, schema, ai_provider)
            self.context = args[0] or {}
            self.schema = args[1] or {}
            self.ai_provider = args[2] if len(args) > 2 else kwargs.get('ai_provider', 'deepseek')
            
            # Extract subject and article_type from context
            self.subject = self.context.get("subject", "")
            self.article_type = self.context.get("article_type", "")
            self.component_type = kwargs.get('component_type', None)
            self.config = self.context  # For compatibility with new style
        else:
            # New initialization pattern: (subject, article_type, component_type, config)
            # Check if first argument is a dict with 'subject' key (happens when assembler passes config as subject)
            if len(args) > 0 and isinstance(args[0], dict) and 'subject' in args[0]:
                config_dict = args[0]
                self.subject = config_dict.get('subject', '')
                self.article_type = config_dict.get('article_type', '')
                
                # Component type from third argument or class name
                if len(args) > 2:
                    self.component_type = args[2]
                else:
                    class_name = self.__class__.__name__
                    self.component_type = ComponentConfigManager.extract_component_name(class_name)
                        
                # Use first argument as both context and config for compatibility
                self.context = config_dict
                self.config = config_dict
            else:
                # Standard new initialization
                self.subject = args[0] if len(args) > 0 else kwargs.get('subject', '')
                self.article_type = args[1] if len(args) > 1 else kwargs.get('article_type', '')
                self.component_type = args[2] if len(args) > 2 else kwargs.get('component_type', None)
                
                # Get config from args or kwargs
                config = args[3] if len(args) > 3 else kwargs.get('config', None)
                self.config = config if config is not None else {}
                self.context = self.config  # For compatibility with old style
            
            # Extract AI provider
            if isinstance(self.config, dict) and 'ai_provider' in self.config:
                self.ai_provider = self.config['ai_provider']
            else:
                self.ai_provider = kwargs.get('ai_provider', 'deepseek')
    
        # Initialize frontmatter_data explicitly
        self.frontmatter_data = {}
        self.previous_outputs = {}
        
        # Initialize API client
        self.api_client = ApiClientFactory.create_client_from_context(
            self.context, 
            self.get_component_config()
        )
        
        # Log initialization
        logger.debug(f"BaseComponent initialized: subject={self.subject}, article_type={self.article_type}")
    
    @abstractmethod
    def generate(self) -> str:
        """Generate component output content."""
        pass
    
    def set_frontmatter(self, frontmatter_data):
        """Store frontmatter data for use by this component."""
        logger.debug(f"Setting frontmatter on {self.__class__.__name__}: {len(frontmatter_data) if isinstance(frontmatter_data, dict) else 'non-dict'} fields")
        
        # Make sure we're storing a dictionary
        if not isinstance(frontmatter_data, dict):
            logger.warning(f"Received non-dict frontmatter: {type(frontmatter_data)}")
            frontmatter_data = {"data": frontmatter_data}
            
        # Store the data
        self.frontmatter_data = frontmatter_data
    
    def set_previous_outputs(self, previous_outputs: Dict[str, str]) -> None:
        """Set previous component outputs."""
        self.previous_outputs = previous_outputs or {}
    
    def get_frontmatter_data(self) -> Dict[str, Any]:
        """Get frontmatter data for the component."""
        # Check if frontmatter_data exists and is not empty
        if hasattr(self, 'frontmatter_data') and self.frontmatter_data:
            return self.frontmatter_data
            
        logger.warning(f"No frontmatter data available for {self.__class__.__name__}")
        return {}
    
    def get_component_config(self) -> Dict[str, Any]:
        """Get component-specific configuration from the context."""
        # Check if context exists, if not, fall back to config
        if not hasattr(self, 'context') or not self.context:
            # If we don't have context, use self.config if available
            if hasattr(self, 'config') and isinstance(self.config, dict):
                components = self.config.get("components", {})
                component_name = ComponentConfigManager.extract_component_name(self.__class__.__name__)
                return components.get(component_name, {})
            else:
                logger.warning(f"No context or config available for {self.__class__.__name__}")
                return {}
        
        # Use the component config manager
        return ComponentConfigManager.get_component_config(self.context, self.__class__.__name__)
    
    def generate_safe(self) -> str:
        """Safe wrapper for generate with error handling."""
        try:
            # Ensure API client is initialized
            if not self.api_client:
                self.api_client = ApiClientFactory.create_client_from_context(
                    self.context, 
                    self.get_component_config()
                )
                if not self.api_client:
                    return self._create_error_markdown("API client initialization failed")
            
            # Generate content
            return self.generate()
            
        except ValueError as e:
            # Handle configuration errors
            error_message = f"Configuration error: {str(e)}"
            logger.error(error_message)
            return self._create_error_markdown(error_message)
            
        except ImportError as e:
            # Handle missing package errors
            error_message = f"Missing package: {str(e)}"
            logger.error(error_message)
            return self._create_error_markdown(error_message)
            
        except RuntimeError as e:
            # Handle API runtime errors
            error_message = f"API error: {str(e)}"
            logger.error(error_message)
            return self._create_error_markdown(error_message)
            
        except Exception as e:
            # Handle all other errors
            error_message = f"Error: {str(e)}"
            logger.error(error_message, exc_info=True)
            return self._create_error_markdown(error_message)
    
    def _create_error_markdown(self, error_message: str) -> str:
        """Create markdown content for error conditions."""
        return ErrorHandler.create_error_markdown(
            self.__class__.__name__, 
            error_message,
            self.subject,
            self.article_type
        )
    
    def format_section_title(self, key: str) -> str:
        """Convert a camelCase or snake_case key to Title Case."""
        return MarkdownUtils.format_section_title(key)
    
    def _format_list_items(self, items: List[str], prefix: str = "*") -> str:
        """Format a list of items as markdown bullets."""
        return MarkdownUtils.format_list_items(items, prefix)

    def _format_table(self, data: Dict[str, Any], headers: List[str] = None) -> str:
        """Format data as a markdown table."""
        return MarkdownUtils.format_table(data, headers, self.format_section_title)

    def _generate_section(self, section_key: str, frontmatter_data: Dict[str, Any]) -> str:
        """Generate content for a specific frontmatter section."""
        return MarkdownUtils.generate_section(
            section_key, 
            frontmatter_data, 
            self.format_section_title, 
            self._format_list_items, 
            self._format_table
        )

    def load_prompt_template(self) -> str:
        """Load prompt template from configuration."""
        try:
            # Load prompt config if not already loaded
            if not hasattr(self, 'prompt_config') or not self.prompt_config:
                self.prompt_config = self.load_prompt_config()
        
            # Extract template
            template = self.prompt_config.get("template", "")
            
            # Return template
            return template
        except Exception as e:
            logger.error(f"Error loading prompt template: {str(e)}")
            return ""
    
    def load_prompt_config(self) -> Dict[str, Any]:
        """Load prompt configuration for this component."""
        component_name = ComponentConfigManager.extract_component_name(self.__class__.__name__)
        return ComponentConfigManager.load_prompt_config(component_name)

    @staticmethod
    def extract_frontmatter(content: str) -> Dict[str, Any]:
        """Extract frontmatter data from content.
        
        This is a compatibility method that redirects to FrontmatterUtils.
        
        Args:
            content: Markdown content with frontmatter
            
        Returns:
            Dictionary containing frontmatter data
        """
        from components.base.utils import FrontmatterUtils
        return FrontmatterUtils.extract_frontmatter(content)