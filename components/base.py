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
from typing import Dict, Any, Optional, List
import yaml
import os

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
        
        # Initialize frontmatter_data explicitly
        self.frontmatter_data = {}
        
        # Initialize API client
        self.api_client = ApiClient(ai_provider)
    
    @abstractmethod
    def generate(self) -> str:
        """Generate component output content."""
        pass
    
    def set_frontmatter(self, frontmatter_data):
        """Store frontmatter data for use by this component.
        
        This is the standard method for providing frontmatter data to components.
        The ArticleAssembler calls this method for each component after extracting frontmatter.
        
        Args:
            frontmatter_data: Dictionary containing frontmatter fields
        """
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
        """Get frontmatter data for the component.
        
        This is the standardized method for accessing frontmatter data in all components.
        Components should use this method rather than accessing self.frontmatter_data directly
        or implementing custom frontmatter retrieval methods.
        
        Returns:
            Dictionary containing frontmatter fields or empty dict if none available
        """
        # Check if frontmatter_data exists and is not empty
        if hasattr(self, 'frontmatter_data') and self.frontmatter_data:
            return self.frontmatter_data
            
        logger.warning(f"No frontmatter data available for {self.__class__.__name__}")
        return {}
    
    @classmethod
    def extract_frontmatter(cls, content: str) -> Dict[str, Any]:
        """Extract frontmatter data from markdown content.
        
        This static method can be used by any component to extract frontmatter
        from markdown content.
        
        Args:
            content: Markdown content with frontmatter
            
        Returns:
            Dictionary containing frontmatter data, or empty dict if extraction fails
        """
        try:
            # Basic validation
            if not content or "---" not in content:
                logger.warning("No frontmatter delimiters found")
                return {}
                
            # Extract content between first two --- markers
            parts = content.split('---', 2)
            if len(parts) < 3:
                logger.warning("Invalid frontmatter format (missing closing delimiter)")
                return {}
                
            # The middle part is the YAML content
            yaml_content = parts[1].strip()
            
            if not yaml_content:
                logger.warning("Empty frontmatter content")
                return {}
                
            # Parse the YAML content
            try:
                parsed_data = yaml.safe_load(yaml_content)
                
                # Handle the case when frontmatter is a list instead of a dict
                if isinstance(parsed_data, list):
                    # Wrap the list in a dictionary with a "providers" key
                    frontmatter_data = {"providers": parsed_data}
                    logger.info("Converted list frontmatter to dictionary with providers key")
                elif isinstance(parsed_data, dict):
                    frontmatter_data = parsed_data
                else:
                    logger.warning(f"Unexpected frontmatter type: {type(parsed_data)}")
                    frontmatter_data = {"content": str(parsed_data)}
                    
                logger.info(f"Extracted frontmatter with {len(frontmatter_data)} fields")
                return frontmatter_data
                
            except yaml.YAMLError as e:
                logger.error(f"Error parsing frontmatter YAML: {e}")
                return {}
                
        except Exception as e:
            logger.error(f"Error extracting frontmatter: {e}")
            return {}

    @classmethod
    def extract_frontmatter_from_file(cls, file_path: str) -> Dict[str, Any]:
        """Extract frontmatter from a markdown file.
        
        Args:
            file_path: Path to the markdown file
            
        Returns:
            Dictionary containing frontmatter data, or empty dict if extraction fails
        """
        try:
            with open(file_path, 'r') as file:
                content = file.read()
            return cls.extract_frontmatter(content)
        except Exception as e:
            logger.error(f"Error reading file {file_path}: {e}")
            return {}

    @staticmethod
    def create_frontmatter(data: Dict[str, Any]) -> str:
        """Create frontmatter string from data.
        
        Args:
            data: Dictionary containing frontmatter fields
            
        Returns:
            Formatted frontmatter string with delimiters
        """
        try:
            if not data:
                return ""
                
            yaml_content = yaml.safe_dump(data, default_flow_style=False, sort_keys=False)
            return f"---\n{yaml_content}---\n"
            
        except Exception as e:
            logger.error(f"Error creating frontmatter: {e}")
            return ""

    @staticmethod
    def validate_frontmatter(data: Dict[str, Any], required_fields: list = None) -> bool:
        """Validate frontmatter data against required fields.
        
        Args:
            data: Frontmatter data dictionary
            required_fields: List of required field names
            
        Returns:
            True if valid, False otherwise
        """
        if not data:
            logger.warning("Empty frontmatter data")
            return False
            
        if required_fields:
            missing_fields = [field for field in required_fields if field not in data]
            if missing_fields:
                logger.warning(f"Missing required frontmatter fields: {', '.join(missing_fields)}")
                return False
                
        return True
    
    # Keep the existing well-typed implementation of get_component_config
    def get_component_config(self) -> Dict[str, Any]:
        """Get component-specific configuration from the context.
        
        This is the standardized method for retrieving component configuration
        throughout the Z-Beam system. All components should use this method
        rather than implementing custom configuration retrieval.
        
        Returns:
            Dictionary containing component configuration
        """
        # Extract component name from class name
        component_name = self.__class__.__name__.lower()
        if "generator" in component_name:
            component_name = component_name.replace("generator", "")
        if "component" in component_name:
            component_name = component_name.replace("component", "")
        
        # Get configuration from context
        components = self.context.get("components", {})
        return components.get(component_name, {})
    
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
    
    def format_section_title(self, key: str) -> str:
        """Convert a camelCase or snake_case key to Title Case.
        
        This method provides standard formatting for section titles derived from
        frontmatter keys or field names. All components should use this method
        for consistent formatting across the document.
        
        Args:
            key: The key to format (e.g., 'technicalSpecifications', 'safety_info')
            
        Returns:
            Formatted title (e.g., 'Technical Specifications', 'Safety Info')
        """
        # Remove underscores and handle camelCase
        if '_' in key:
            words = key.split('_')
        else:
            import re
            # Insert space before uppercase letters that follow lowercase
            words = re.findall(r'[A-Z]?[a-z]+|[A-Z]+(?=[A-Z]|$)', key)
    
        # Title case each word
        return ' '.join(word.capitalize() for word in words)
    
    def _format_list_items(self, items: List[str], prefix: str = "*") -> str:
        """Format a list of items as markdown bullets.
        
        Args:
            items: List of string items
            prefix: Bullet character or string to use (default: *)
            
        Returns:
            Markdown formatted list
        """
        if not items:
            return ""
            
        return "\n".join(f"{prefix} {item}" for item in items)

    def _format_table(self, data: Dict[str, Any], headers: List[str] = None) -> str:
        """Format data as a markdown table.
        
        Args:
            data: Dictionary of data to format (key-value pairs)
            headers: Custom header names (optional)
            
        Returns:
            Markdown formatted table
        """
        if not data:
            return ""
            
        # Use provided headers or format keys as headers
        if not headers:
            headers = ["Property", "Value"]
            
        table_rows = [
            f"| {headers[0]} | {headers[1]} |",
            f"|{'-'*10}|{'-'*10}|"
        ]
        
        for key, value in data.items():
            key_formatted = self.format_section_title(key)
            
            # Handle different value types
            if isinstance(value, list):
                value_str = ", ".join(str(v) for v in value)
            elif isinstance(value, dict):
                value_str = ", ".join(f"{k}: {v}" for k, v in value.items())
            else:
                value_str = str(value)
                
            table_rows.append(f"| {key_formatted} | {value_str} |")
            
        return "\n".join(table_rows)

    def _generate_section(self, section_key: str, frontmatter_data: Dict[str, Any]) -> str:
        """Generate content for a specific frontmatter section.
        
        Args:
            section_key: Key of the section in frontmatter data
            frontmatter_data: Frontmatter data dictionary
            
        Returns:
            Formatted markdown section or empty string if section doesn't exist
        """
        section_data = frontmatter_data.get(section_key)
        if not section_data:
            return ""
            
        title = self.format_section_title(section_key)
        content = [f"## {title}"]
        
        if isinstance(section_data, list):
            content.append(self._format_list_items(section_data))
        elif isinstance(section_data, dict):
            content.append(self._format_table(section_data))
        else:
            content.append(str(section_data))
            
        return "\n\n".join(content)

    def load_prompt_template(self) -> str:
        """Load prompt template for the component.
        
        Looks for a prompt.yaml file in the component's directory
        and loads the template from it.
        
        Returns:
            String template for prompt formatting
        """
        try:
            # Get component class name and convert to snake_case for directory name
            component_type = self.__class__.__name__.replace('Generator', '').lower()
            
            # Try to load from component-specific directory
            prompt_file = os.path.join('components', component_type, 'prompt.yaml')
            
            if not os.path.exists(prompt_file):
                # Try alternate location
                prompt_file = os.path.join('components', component_type, 'prompts', 'default.yaml')
        
            if not os.path.exists(prompt_file):
                logger.warning(f"No prompt file found for {component_type}")
                return self._get_default_prompt_template()
                
            with open(prompt_file, 'r') as f:
                prompt_config = yaml.safe_load(f)
                
            logger.info(f"Loaded prompt configuration from {prompt_file}")
            
            # Extract template from config
            if isinstance(prompt_config, dict) and 'template' in prompt_config:
                return prompt_config['template']
            elif isinstance(prompt_config, str):
                return prompt_config
            else:
                logger.warning(f"Invalid prompt format in {prompt_file}")
                return self._get_default_prompt_template()
                
        except Exception as e:
            logger.error(f"Error loading prompt template: {e}")
            return self._get_default_prompt_template()
            
    def _get_default_prompt_template(self) -> str:
        """Return a minimal default prompt template."""
        return (
            "Generate content about {subject} for a {article_type} article.\n\n"
            "Focus on providing accurate, helpful information suitable for the target audience."
        )