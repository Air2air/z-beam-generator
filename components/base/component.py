"""
Base component for Z-Beam Generator.

MODULE DIRECTIVES FOR AI ASSISTANTS:
1. FRONTMATTER-DRIVEN: All content must be extracted from frontmatter
2. NO HARDCODEED SECTIONS: Section structure must be derived from frontmatter
3. DYNAMIC FORMATTING: Format content based on article_type from frontmatter
4. ERROR HANDLING: Raise exceptions when required frontmatter fields are missing
5. SCHEMA AWARENESS: Be aware of the schema structure for different article types
"""

import logging
import yaml
import re
from typing import Dict, Any, Optional, List, Union

logger = logging.getLogger(__name__)

class BaseComponent:
    """Base class for all content generation components."""
    
    def __init__(self, context: Dict[str, Any], schema: Dict[str, Any] = None, ai_provider: str = None):
        """Initialize the component with standard parameters.
        
        Args:
            context: Application context with subject, article_type, etc.
            schema: Schema definition for component
            ai_provider: AI provider to use (defaults to context's ai_provider)
        """
        # Extract required parameters from context
        self.subject = context.get("subject", "")
        self.article_type = context.get("article_type", "material")
        
        # Store context and schema
        self.context = context
        self.schema = schema or {}
        
        # Get AI provider from context if not provided
        if ai_provider is None:
            ai_provider = context.get("ai_provider", "deepseek")
        self.ai_provider = ai_provider
        
        # Initialize API client
        from api.client import ApiClient
        self.api_client = ApiClient(ai_provider=ai_provider)
        
        # Initialize storage for frontmatter and previous outputs
        self._frontmatter_data = {}
        self._previous_outputs = {}
        
        # Log initialization
        logger.info(f"{self.__class__.__name__} initialized for subject: {self.subject}")

    def generate(self) -> str:
        """Generate content for this component.
        
        This must be implemented by subclasses.
        
        Returns:
            str: The generated content
        """
        raise NotImplementedError("Subclasses must implement generate()")
        
    def generate_safe(self) -> str:
        """Generate content with error handling.
        
        Returns:
            str: The generated content or error message
        """
        try:
            return self.generate()
        except Exception as e:
            logger.error(f"Error generating {self.__class__.__name__}: {str(e)}")
            return self._create_error_markdown(str(e))
    
    def set_frontmatter(self, frontmatter_data: Dict[str, Any]) -> 'BaseComponent':
        """Set frontmatter data for the component.
        
        Args:
            frontmatter_data: Dictionary of frontmatter data
            
        Returns:
            Self for method chaining
        """
        self._frontmatter_data = frontmatter_data or {}
        return self
    
    def get_frontmatter_data(self) -> Dict[str, Any]:
        """Get the frontmatter data.
        
        Returns:
            Dict[str, Any]: The frontmatter data
        """
        return self._frontmatter_data
    
    def set_previous_outputs(self, previous_outputs: Dict[str, Any]) -> 'BaseComponent':
        """Set outputs from previous components.
        
        Args:
            previous_outputs: Dictionary of outputs from previous components
            
        Returns:
            Self for method chaining
        """
        self._previous_outputs = previous_outputs or {}
        return self
    
    def get_previous_outputs(self) -> Dict[str, Any]:
        """Get outputs from previous components.
        
        Returns:
            Dict[str, Any]: The previous outputs
        """
        return self._previous_outputs
    
    def _prepare_data(self) -> Dict[str, Any]:
        """Prepare data for prompt formatting.
        
        Returns:
            Dict[str, Any]: Data for prompt formatting
        """
        # Create base data dictionary
        data = {
            "subject": self.subject,
            "article_type": self.article_type,
            "frontmatter": self._frontmatter_data
        }
        
        return data
    
    def _format_prompt(self, data: Dict[str, Any]) -> str:
        """Format prompt template with data.
        
        Args:
            data: Data for prompt formatting
            
        Returns:
            str: Formatted prompt
        """
        try:
            # Load template
            template = self._load_prompt_template()
            
            # Format template with data
            # First, try using format() with named placeholders
            try:
                return template.format(**data)
            except KeyError as e:
                logger.warning(f"Missing key in template formatting: {e}")
                
                # Fallback to basic formatting with common fields
                return template.format(
                    subject=data.get("subject", ""),
                    article_type=data.get("article_type", ""),
                    frontmatter=data.get("frontmatter", {})
                )
        except Exception as e:
            logger.error(f"Error formatting prompt: {str(e)}")
            return f"Generate content for {data.get('subject', '')} as {data.get('article_type', '')}"
    
    def _load_prompt_template(self) -> str:
        """Load prompt template for this component.
        
        Looks for a template file in the component's directory.
        
        Returns:
            str: The prompt template
        """
        try:
            import os
            
            # Get component name for file path
            component_name = self.__class__.__name__.lower().replace("generator", "").replace("component", "")
            
            # Check for template files in priority order
            template_paths = [
                os.path.join("components", component_name, "prompts", f"{self.article_type}.yaml"),  # Article-type specific
                os.path.join("components", component_name, "prompt.yaml"),                          # General component prompt
                os.path.join("components", component_name, "prompts", "default.yaml")               # Default fallback
            ]
            
            for template_path in template_paths:
                if os.path.exists(template_path):
                    with open(template_path, 'r', encoding='utf-8') as f:
                        config = yaml.safe_load(f)
                        template = config.get("template", "")
                        if template:
                            logger.debug(f"Loaded prompt template from {template_path}")
                            return template
            
            # If no template files found, use default
            logger.debug(f"No prompt template found for {component_name}, using default")
            return f"Generate {component_name} for {{subject}} as {{article_type}}."
            
        except Exception as e:
            logger.error(f"Error loading prompt template: {str(e)}")
            return f"Generate content for {{subject}} as {{article_type}}."
    
    def _call_api(self, prompt: str) -> str:
        """Call API with prompt.
        
        Args:
            prompt: The prompt to send to the API
            
        Returns:
            str: The API response
        """
        try:
            # Log prompt length for debugging
            logger.debug(f"Sending prompt to {self.ai_provider} API (length: {len(prompt)} chars)")
            
            # Get component-specific options
            component_name = self.__class__.__name__.lower().replace("generator", "").replace("component", "")
            component_config = self.context.get("components", {}).get(component_name, {})
            options = component_config.get("options", {})
            
            # Call API client with options
            return self.api_client.complete(prompt, options)
        except Exception as e:
            logger.error(f"API call error: {str(e)}")
            raise
    
    def _post_process(self, content: str) -> str:
        """Post-process API response.
        
        Args:
            content: The API response content
            
        Returns:
            str: The post-processed content
        """
        if not content:
            return "<!-- No content generated -->"
            
        # Process code blocks
        processed = self._process_markdown(content)
        
        return processed
    
    def _process_markdown(self, content: str, add_heading: bool = False) -> str:
        """Process markdown content for consistency.
        
        Args:
            content: The markdown content
            add_heading: Whether to add a heading if none exists
            
        Returns:
            str: Processed markdown content
        """
        if not content:
            return ""
        
        # Remove triple backtick language identifiers
        content = re.sub(r'```[a-zA-Z0-9_+]*\n', '```\n', content)
        
        # Add heading if requested and no heading exists
        if add_heading and not re.match(r'^#+ ', content.lstrip()):
            title = self.subject.capitalize()
            content = f"# {title}\n\n{content}"
        
        return content
    
    def _process_yaml_content(self, content: str) -> str:
        """Process content containing YAML.
        
        Args:
            content: Content that might contain YAML
            
        Returns:
            str: Processed YAML content
        """
        # Check if content already has frontmatter
        if content.startswith('---'):
            return content
        
        # Try to extract YAML from code blocks
        yaml_pattern = r'```ya?ml\s*([\s\S]*?)\s*```'
        match = re.search(yaml_pattern, content)
        if match:
            yaml_content = match.group(1).strip()
            return f"---\n{yaml_content}\n---"
        
        # If no YAML block found, check if content is valid YAML
        try:
            # See if content parses as valid YAML
            data = yaml.safe_load(content)
            if isinstance(data, dict):
                return f"---\n{content}\n---"
        except Exception:
            pass
            
        # If all else fails, return as-is
        return content
    
    def is_enabled(self) -> bool:
        """Check if this component is enabled in configuration.
        
        Returns:
            bool: True if component is enabled
        """
        # Get component name
        component_name = self.__class__.__name__.lower().replace("generator", "").replace("component", "")
        
        # Check if component is enabled in configuration
        component_config = self.context.get("components", {}).get(component_name, {})
        return component_config.get("enabled", True)
    
    def get_component_config(self, key: str = None, default: Any = None) -> Any:
        """Get component-specific configuration value.
        
        Args:
            key: Configuration key to get
            default: Default value if key not found
            
        Returns:
            Any: Configuration value or entire config dict if key is None
        """
        # Get component name
        component_name = self.__class__.__name__.lower().replace("generator", "").replace("component", "")
        
        # Get component config
        component_config = self.context.get("components", {}).get(component_name, {})
        
        # Return specific key or entire config
        if key is not None:
            return component_config.get(key, default)
        return component_config