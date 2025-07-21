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

"""
Base component class for all content generators.
"""

import logging
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional

from api.client import ApiClient
from utils.registry_factory import RegistryFactory
from utils.string_utils import StringUtils

logger = logging.getLogger(__name__)

class BaseComponent(ABC):
    """Base class for all content generation components."""
    
    def __init__(self, context: Dict[str, Any], schema: Dict[str, Any], ai_provider: str = "deepseek"):
        """Initialize base component.
        
        Args:
            context: Context data for generation
            schema: Schema definition for the component
            ai_provider: AI provider to use
        """
        self.context = context or {}
        self.schema = schema or {}
        self.subject = context.get("subject", "")
        self.article_type = context.get("article_type", "")
        self.ai_provider = ai_provider
        
        # CRITICAL: Initialize frontmatter_data explicitly
        self.frontmatter_data = {}
        
        # Initialize API client
        self.api_client = ApiClient(ai_provider)
    
    @abstractmethod
    def generate(self) -> str:
        """Generate component output content."""
        pass
    
    def set_frontmatter(self, frontmatter_data):
        """Store frontmatter data for use by this component."""
        # Use debug log to see what's happening
        logger.debug(f"Setting frontmatter on {self.__class__.__name__}: {len(frontmatter_data)} fields")
        
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
        """Retrieve frontmatter data."""
        # Check if frontmatter_data exists and is not empty
        if hasattr(self, 'frontmatter_data') and self.frontmatter_data:
            return self.frontmatter_data
            
        logger.warning(f"No frontmatter data available for {self.__class__.__name__}")
        return {}
    
    def format_section_title(self, key: str) -> str:
        """Convert a camelCase or snake_case key to Title Case."""
        return StringUtils.format_title(key)
    
    def load_prompt_template(self, component_name: str = None) -> str:
        """Load prompt template for this component."""
        if not component_name:
            # Derive component name from class name
            component_name = self.__class__.__name__.lower()
            for suffix in ['component', 'generator']:
                if component_name.endswith(suffix):
                    component_name = component_name[:-len(suffix)]
        
        # Get fresh prompt from registry
        prompt_registry = RegistryFactory.prompt_registry()
        prompt_config = prompt_registry.get_prompt(component_name)
        
        return prompt_config.get('template', '')
    
    def get_schema_fields(self) -> Dict[str, Any]:
        """Get schema fields from schema definition."""
        return self.schema.get("schema", {})
    
    def generate_safe(self) -> str:
        """Safe wrapper for generate with error handling."""
        try:
            # Ensure API client is initialized
            if not self.api_client:
                self._init_api_client()
                if not self.api_client:
                    return self._create_error_markdown("API client initialization failed")
            
            # Generate content
            return self.generate()
            
        except ValueError as e:
            # Handle configuration errors
            error_message = f"Configuration error in {self.__class__.__name__}: {str(e)}"
            logger.error(error_message)
            return self._create_error_markdown(error_message)
            
        except ImportError as e:
            # Handle missing package errors
            error_message = f"Missing package in {self.__class__.__name__}: {str(e)}"
            logger.error(error_message)
            return self._create_error_markdown(error_message)
            
        except RuntimeError as e:
            # Handle API runtime errors
            error_message = f"API error in {self.__class__.__name__}: {str(e)}"
            logger.error(error_message)
            return self._create_error_markdown(error_message)
            
        except Exception as e:
            # Handle all other errors
            error_message = f"Error in {self.__class__.__name__}: {str(e)}"
            logger.error(error_message, exc_info=True)
            return self._create_error_markdown(error_message)
    
    def _create_error_markdown(self, error_message: str) -> str:
        """Create markdown content for error conditions.
        
        Args:
            error_message: Error message to include
            
        Returns:
            Markdown content with error information
        """
        import datetime
        component_name = self.__class__.__name__
        
        # Special handling for frontmatter component to prevent downstream failures
        if component_name.lower().startswith('frontmatter'):
            # Generate minimal valid frontmatter when the frontmatter component fails
            current_date = datetime.datetime.now().strftime('%Y-%m-%dT%H:%M:%S')
            # Escape quotes in error message to prevent YAML parsing errors
            safe_error = error_message.replace('"', "'")
            
            return f"""---
title: "{self.subject}"
subtitle: "Content Generation Failed"
description: "Could not generate content for {self.subject} due to an error."
slug: "{StringUtils.create_slug(self.subject)}"
date: "{current_date}"
article_type: "{self.article_type}"
error: true
error_message: "{safe_error}"
---

<!-- ERROR: {error_message} -->

## Error Generating {StringUtils.format_title(component_name)}

An error occurred while generating the frontmatter content.

### Error Details
```
{error_message}
```

Please check the logs for more information.
"""
        
        # Create a standardized error message in markdown format
        markdown = f"""<!-- ERROR: {error_message} -->

## Error Generating {StringUtils.format_title(component_name)}

An error occurred while generating the content for {StringUtils.format_title(component_name)}.

### Error Details

```
{error_message}
```

Please check the logs for more information.
"""
        return markdown

    # Add this method as an alias to whatever the existing method is
    def get_component_config(self):
        """Alias for compatibility with newer component implementations."""
        # Try to delegate to existing methods that might have similar functionality
        if hasattr(self, 'get_config'):
            return self.get_config()
        
        # Extract component name from class name
        component_name = self.__class__.__name__.lower()
        if "generator" in component_name:
            component_name = component_name.replace("generator", "")
        if "component" in component_name:
            component_name = component_name.replace("component", "")
        
        # Try to get component configuration from context
        components = self.context.get("components", {})
        return components.get(component_name, {})

class ComponentTemplate:
    """Base template for component generation."""
    
    def __init__(self, context, schema, provider):
        self.context = context
        self.schema = schema
        self.provider = provider
        self.api_client = ApiClient(provider)
        
    def generate(self):
        """Template method pattern for component generation."""
        try:
            # 1. Prepare data
            data = self._prepare_data()
            
            # 2. Create prompt
            prompt = self._create_prompt(data)
            
            # 3. Generate content
            content = self._generate_content(prompt)
            
            # 4. Post-process content
            return self._post_process(content)
        except Exception as e:
            logging.error(f"Error in {self.__class__.__name__}: {str(e)}")
            return self._get_error_output(str(e))
            
    # Abstract methods to be implemented by subclasses
    def _prepare_data(self):
        """Prepare data for prompt creation."""
        raise NotImplementedError
        
    def _create_prompt(self, data):
        """Create the prompt for the AI."""
        raise NotImplementedError
        
    def _generate_content(self, prompt):
        """Generate content using the API client."""
        return self.api_client.generate_content(prompt)
        
    def _post_process(self, content):
        """Post-process the generated content."""
        return content
        
    def _get_error_output(self, error_message):
        """Get output to return in case of error."""
        return f"<!-- Error in {self.__class__.__name__}: {error_message} -->"