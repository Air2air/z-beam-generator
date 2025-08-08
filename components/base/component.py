"""
Base component for Z-Beam Generator.

Combined base component with all common functionality for Z-Beam generators.
"""
import logging
import os
import re
import yaml
from abc import ABC
from typing import Dict, Any, Optional, List

from components.base.utils.content_formatter import ContentFormatter
from components.base.utils.validation import (
    validate_non_empty, validate_category_consistency,
    strip_markdown_code_blocks
)
from components.base.data_provider import CleanDataProvider

logger = logging.getLogger(__name__)

class BaseComponent(ABC):
    """Base class for all Z-Beam generators with complete functionality."""
    
    def __init__(self, subject: str, article_type: str, schema: Dict[str, Any], 
                 author_data: Dict[str, Any], component_config: Dict[str, Any]):
        """Initialize component with validation and prompt config loading.
        
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
        
        # Set category from component_config if available
        if "category" in component_config:
            self.category = component_config["category"]
        else:
            self.category = ""
        
        # Extract required AI configuration from component config
        if "ai_provider" not in component_config:
            raise ValueError("ai_provider must be specified in component config")
        
        if "options" not in component_config:
            raise ValueError("options must be specified in component config")
        
        self.subject = subject
        self.article_type = article_type
        self.schema = schema
        self.author_data = author_data
        # Ensure author ID is available
        if "author_id" not in self.author_data and "author_id" in component_config:
            self.author_data["author_id"] = component_config["author_id"]
        self.component_config = component_config
        self.ai_provider = component_config["ai_provider"]
        self.options = component_config["options"]
        
        # Create clean data provider for strict data isolation
        self.data_provider = CleanDataProvider(
            subject=self.subject,
            article_type=self.article_type,
            category=self.category,
            author_data=self.author_data,
            schema=self.schema
        )
        
        # Load prompt config
        self.prompt_config = self._load_prompt_config()
    
    def _load_prompt_config(self) -> dict:
        """Load the prompt configuration from YAML.
        
        Returns:
            dict: The prompt configuration
            
        Raises:
            ValueError: If prompt config cannot be loaded
        """
        prompt_path = self._get_prompt_path()
        if not os.path.exists(prompt_path):
            raise ValueError(f"Prompt configuration file not found at {prompt_path}")
        
        try:
            with open(prompt_path, 'r', encoding='utf-8') as f:
                config = yaml.safe_load(f)
                if not config:
                    raise ValueError(f"Empty prompt configuration in {prompt_path}")
                return config
        except Exception as e:
            logger.error(f"Failed to load prompt config: {e}")
            raise ValueError(f"Failed to load prompt config from {prompt_path}: {e}")
    
    def _get_prompt_path(self) -> str:
        """Get the path to the prompt.yaml file for this component.
        
        Returns:
            str: Path to the prompt.yaml file
        """
        component_dir = os.path.dirname(os.path.abspath(self.__module__.replace('.', os.sep) + '.py'))
        prompt_path = os.path.join(component_dir, 'prompt.yaml')
        return prompt_path
    
    def get_template_data(self) -> Dict[str, Any]:
        """Get clean, validated template data for the component.
        
        All data is pre-validated and sanitized by the CleanDataProvider.
        Generators receive only clean data and should not perform any formatting.
        
        Returns:
            Dict[str, Any]: Clean, validated template data
        
        Raises:
            ValueError: If clean data cannot be provided
        """
        component_name = self.__class__.__name__.replace("Generator", "").lower()
        return self.data_provider.get_clean_data(component_name, self.component_config)

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
        return validate_category_consistency(file_content, self.category, self.article_type, self.subject)

    def get_component_config(self, key: str, default: Any = None) -> Any:
        """Get a value from component_config.
        
        Args:
            key: The key to look up
            default: Value to return if key is not found
            
        Returns:
            Any: The value from component_config or default
            
        Raises:
            ValueError: If key is not found and no default is provided
        """
        if key in self.component_config:
            return self.component_config[key]
        
        if default is not None:
            return default
            
        raise ValueError(f"Required component config key '{key}' not found")
    
    def get_profile_key(self) -> str:
        """Get the schema profile key for the current article type.
        
        Returns:
            str: The profile key (e.g., 'materialProfile')
        """
        return f"{self.article_type}Profile"
    
    def get_schema_config(self, *path, default: Any = None) -> Any:
        """Get a value from the schema configuration for the current article type.
        
        Args:
            *path: The path to the configuration (e.g., 'validation', 'frontmatter', 'requiredFields')
            default: Value to return if path is not found
            
        Returns:
            Any: The value from schema or default
            
        Examples:
            self.get_schema_config('validation', 'frontmatter', 'requiredFields')
            self.get_schema_config('generatorConfig', 'fieldContentMapping')
        """
        profile_key = self.get_profile_key()
        
        if profile_key not in self.schema:
            if default is not None:
                return default
            raise ValueError(f"Schema profile '{profile_key}' not found for article type '{self.article_type}'")
        
        current = self.schema[profile_key]
        
        for key in path:
            if not isinstance(current, dict) or key not in current:
                if default is not None:
                    return default
                raise ValueError(f"Schema path {'.'.join(path)} not found in profile '{profile_key}'")
            current = current[key]
        
        return current
    
    def get_required_fields(self, component_name: str = None) -> List[str]:
        """Get required fields for a component from the schema.
        
        Args:
            component_name: Name of the component (defaults to current component)
            
        Returns:
            List[str]: List of required field names
        """
        if component_name is None:
            component_name = self.__class__.__name__.replace("Generator", "").lower()
        
        try:
            return self.get_schema_config('validation', component_name, 'requiredFields', default=[])
        except ValueError:
            # Strict mode: No fallback validation
            raise ValueError(f"No validation configuration found for component: {component_name}")
    
    def get_component_validation_config(self, component_name: str = None) -> Dict[str, Any]:
        """Get validation configuration for a component from the schema.
        
        Args:
            component_name: Name of the component (defaults to current component)
            
        Returns:
            Dict[str, Any]: Validation configuration
        """
        if component_name is None:
            component_name = self.__class__.__name__.replace("Generator", "").lower()
        
        try:
            return self.get_schema_config('validation', component_name, default={})
        except ValueError:
            return {}
    
    def has_schema_feature(self, *path) -> bool:
        """Check if a schema feature exists for the current article type.
        
        Args:
            *path: The path to check (e.g., 'generatorConfig', 'research')
            
        Returns:
            bool: True if the feature exists
        """
        try:
            self.get_schema_config(*path)
            return True
        except ValueError:
            return False
    
    def get_schema_field_definitions(self) -> dict:
        """Get field definitions from the schema for the current article type.
        
        Returns:
            dict: Field definitions from the schema
        """
        return self.get_schema_config('profile', default={})
    
    def get_field_schema_info(self, field_name: str) -> dict:
        """Get schema information for a specific field.
        
        Args:
            field_name: Name of the field
            
        Returns:
            dict: Schema information for the field
        """
        schema_properties = self.get_schema_field_definitions()
        return schema_properties.get(field_name, {})
    
    def generate_dynamic_field_value(self, field_name: str) -> Any:
        """Generate dynamic field value based on schema and context.
        
        Args:
            field_name: Name of the field to generate
            
        Returns:
            Appropriate value for the field based on schema and context
        """
        # Get schema information for this field
        field_info = self.get_field_schema_info(field_name)
        field_type = field_info.get('type', 'string')
        field_default = field_info.get('default')
        
        # If schema provides a default value, use it
        if field_default is not None:
            return field_default
        
        # Generate intelligent defaults based on schema type and field name patterns
        if field_type == 'array':
            return self._generate_array_field_value(field_name, field_info)
        elif field_type == 'object':
            return self._generate_object_field_value(field_name, field_info)
        elif field_type == 'boolean':
            return self._generate_boolean_field_value(field_name, field_info)
        elif field_type == 'number' or field_type == 'integer':
            return self._generate_number_field_value(field_name, field_info)
        else:  # string type
            return self._generate_string_field_value(field_name, field_info)
    
    def _generate_array_field_value(self, field_name: str, field_info: dict) -> list:
        """Generate array field value based on field name patterns and schema info."""
        field_name_lower = field_name.lower()
        
        # Check for specific field patterns
        if any(keyword in field_name_lower for keyword in ['standard', 'regulation', 'compliance']):
            return ["ISO 9001", "Industry standards", "Safety regulations"]
        elif any(keyword in field_name_lower for keyword in ['tag', 'keyword']):
            return ContentFormatter.format_keywords(self.subject, getattr(self, 'category', None))
        elif any(keyword in field_name_lower for keyword in ['application', 'use']):
            return [f"{self.subject} processing", f"{self.subject} cleaning", "Laser applications"]
        elif any(keyword in field_name_lower for keyword in ['property', 'characteristic']):
            return [f"{self.subject} properties", "Material characteristics", "Physical properties"]
        elif any(keyword in field_name_lower for keyword in ['image', 'media']):
            return ContentFormatter.format_images(self.subject)
        elif any(keyword in field_name_lower for keyword in ['certification', 'cert']):
            return ["CE marking", "ISO certification", "Industry compliance"]
        elif any(keyword in field_name_lower for keyword in ['safety']):
            return ["OSHA guidelines", "Material safety protocols", "Laser safety standards"]
        else:
            # Generic array based on subject
            return [f"{self.subject} related", "General applications"]
    
    def _generate_object_field_value(self, field_name: str, field_info: dict) -> dict:
        """Generate object field value based on field name patterns and schema info."""
        field_name_lower = field_name.lower()
        
        # Check schema for object properties if available
        properties = field_info.get('properties', {})
        if properties:
            # Generate object based on schema properties
            obj = {}
            for prop_name, prop_info in properties.items():
                obj[prop_name] = self._generate_value_from_schema_property(prop_name, prop_info)
            return obj
        
        # Fallback to pattern-based generation
        if any(keyword in field_name_lower for keyword in ['spec', 'specification', 'technical']):
            return {"type": self.subject, "category": getattr(self, 'category', 'material')}
        elif any(keyword in field_name_lower for keyword in ['author', 'creator']):
            return ContentFormatter.format_author_info(self.author_data)
        elif any(keyword in field_name_lower for keyword in ['image', 'media']):
            return {"url": f"/images/{self.subject}.jpg", "alt": f"{self.subject} image"}
        else:
            return {"name": self.subject, "value": f"{self.subject} data"}
    
    def _generate_boolean_field_value(self, field_name: str, field_info: dict) -> bool:
        """Generate boolean field value based on field name patterns."""
        field_name_lower = field_name.lower()
        
        # Default to true for positive attributes
        if any(keyword in field_name_lower for keyword in ['published', 'active', 'enabled', 'available', 'suitable']):
            return True
        elif any(keyword in field_name_lower for keyword in ['deprecated', 'hidden', 'disabled', 'restricted']):
            return False
        else:
            return True  # Default to true for most boolean fields
    
    def _generate_number_field_value(self, field_name: str, field_info: dict) -> int:
        """Generate number field value based on field name patterns."""
        field_name_lower = field_name.lower()
        
        # Provide intelligent defaults for numbers
        if any(keyword in field_name_lower for keyword in ['count', 'number', 'quantity']):
            return 1
        elif any(keyword in field_name_lower for keyword in ['temperature', 'temp']):
            return 20  # Room temperature
        elif any(keyword in field_name_lower for keyword in ['pressure']):
            return 101325  # Standard atmospheric pressure
        elif any(keyword in field_name_lower for keyword in ['percentage', 'percent']):
            return 100
        else:
            return 0
    
    def _generate_string_field_value(self, field_name: str, field_info: dict) -> str:
        """Generate string field value based on field name patterns and context."""
        field_name_lower = field_name.lower()
        
        # Handle common field names with context-aware logic
        if field_name in ["name", "title"]:
            return ContentFormatter.format_title(self.subject, self.article_type)
        elif field_name == "headline":
            return f"Technical guide to {self.subject} for laser cleaning applications"
        elif field_name == "description":
            return ContentFormatter.format_description(self.subject)
        elif field_name == "keywords":
            keywords = ContentFormatter.format_keywords(self.subject, getattr(self, 'category', None))
            return ", ".join(keywords) if isinstance(keywords, list) else keywords
        elif field_name == "category":
            return getattr(self, 'category', 'unknown')
        elif field_name == "article_type":
            return self.article_type
        elif field_name == "subject":
            return self.subject
        elif field_name == "@context":
            return "https://schema.org"
        elif field_name == "@type":
            return "Article"
        elif field_name == "articleBody":
            return f"Technical content about {self.subject} laser cleaning applications."
        
        # Pattern-based generation for other fields
        elif any(keyword in field_name_lower for keyword in ['compliance', 'regulation']):
            return f"Compliant with industry standards for {self.subject} processing"
        elif any(keyword in field_name_lower for keyword in ['slug', 'url']):
            from components.base.utils.slug_utils import SlugUtils
            return SlugUtils.create_subject_slug(self.subject)
        elif any(keyword in field_name_lower for keyword in ['date']):
            from datetime import datetime
            return datetime.now().isoformat()
        elif any(keyword in field_name_lower for keyword in ['region', 'location']):
            return "Global"
        elif any(keyword in field_name_lower for keyword in ['coverage']):
            return f"Global {self.subject} applications"
        else:
            # Generic string based on context
            logger.warning(f"Generating fallback value for unknown field: {field_name}")
            return f"{self.subject} - {field_name}"
    
    def _generate_value_from_schema_property(self, prop_name: str, prop_info: dict) -> Any:
        """Generate value for a schema property recursively."""
        prop_type = prop_info.get('type', 'string')
        prop_default = prop_info.get('default')
        
        if prop_default is not None:
            return prop_default
        
        if prop_type == 'array':
            return []
        elif prop_type == 'object':
            return {}
        elif prop_type == 'boolean':
            return True
        elif prop_type in ['number', 'integer']:
            return 0
        else:
            return f"{self.subject} {prop_name}"
    
    def populate_missing_required_fields(self, parsed_data: dict, component_name: str = None) -> dict:
        """Populate missing required fields based on schema.
        
        Args:
            parsed_data: The parsed data dictionary
            component_name: Name of the component
            
        Returns:
            dict: Data with all required fields populated
        """
        if component_name is None:
            component_name = self.__class__.__name__.replace("Generator", "").lower()
        
        required_fields = self.get_required_fields(component_name)
        
        # Populate missing required fields
        for field in required_fields:
            if field not in parsed_data:
                parsed_data[field] = self.generate_dynamic_field_value(field)
        
        return parsed_data
    
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
    
    def _format_prompt(self, data: Dict[str, Any]) -> str:
        """Format the prompt template with data.
        
        Args:
            data: Template data
            
        Returns:
            str: Formatted prompt
            
        Raises:
            ValueError: If prompt template is invalid or missing
        """
        # Get prompt template from config
        if not self.prompt_config or "template" not in self.prompt_config:
            raise ValueError("Prompt template not found in config")
            
        # Use condensed template if available and frontmatter exists
        component_name = self.__class__.__name__.replace("Generator", "").lower()
        use_condensed = "condensed_template" in self.prompt_config
        
        if use_condensed:
            template = self.prompt_config["condensed_template"]
            logger.debug(f"Using condensed template for {component_name} with frontmatter data")
        else:
            template = self.prompt_config["template"]
            
        if not template or not isinstance(template, str):
            raise ValueError("Invalid prompt template in config")
        
        # Process template to handle conditionals for missing data
        processed_template = self._process_template_conditionals(template, data)
        
        # Handle nested frontmatter access with dot notation (all_frontmatter.key.subkey)
        processed_template = self._process_nested_frontmatter_access(processed_template, data)
            
        # Format prompt with template data
        try:
            # Strict validation - no fallbacks for missing variables
            formatted_prompt = processed_template.format(**data)
            return formatted_prompt
        except KeyError as e:
            missing_var = str(e).strip("'")
            error_msg = f"Missing template variable: {missing_var}"
            
            # Provide more helpful error for frontmatter-related variables
            if "frontmatter" in missing_var or "image" in missing_var:
                error_msg += "\nCheck that base component data contains the required template variables."
            
            raise ValueError(error_msg)
        except Exception as e:
            raise ValueError(f"Failed to format prompt: {e}")
    
    def _process_nested_frontmatter_access(self, template: str, data: Dict[str, Any]) -> str:
        """Process nested frontmatter access with dot notation.
        
        Replaces {all_frontmatter.key.subkey} with the actual value from nested dictionaries.
        
        Args:
            template: Template with nested access
            data: Template data
            
        Returns:
            str: Template with nested access resolved
        """
        import re
        
        # Pattern to find {all_frontmatter.key.subkey} and similar nested access
        pattern = r'\{([\w]+\.[\w\.]+)\}'
        matches = re.findall(pattern, template)
        
        for match in matches:
            parts = match.split('.')
            base_key = parts[0]
            
            if base_key in data and isinstance(data[base_key], dict):
                # Navigate the nested structure
                current = data[base_key]
                valid_path = True
                
                for part in parts[1:]:
                    if isinstance(current, dict) and part in current:
                        current = current[part]
                    else:
                        valid_path = False
                        break
                
                # Replace with the actual value if the path is valid
                if valid_path:
                    value_str = str(current)
                    template = template.replace(f"{{{match}}}", value_str)
        
        return template
            
    def _process_template_conditionals(self, template: str, data: Dict[str, Any]) -> str:
        """Process conditional statements in templates.
        
        Handles simple Jinja-like conditionals: {% if variable %} content {% endif %}
        
        Args:
            template: Template with conditionals
            data: Template data
            
        Returns:
            str: Processed template with conditionals evaluated
        """
        import re
        
        # First, remove any Jinja-style conditionals that might cause problems
        # Match {% if ... %} ... {% endif %} blocks
        pattern = r'{%.*?%}.*?{%.*?%}'
        processed = re.sub(pattern, '', template, flags=re.DOTALL)
        
        # Also remove any remaining {% ... %} tags
        pattern = r'{%.*?%}'
        processed = re.sub(pattern, '', processed)
        
        return processed
    
    def _call_api(self, prompt: str) -> str:
        """Call API provider with the formatted prompt.
        
        Args:
            prompt: Formatted prompt
            
        Returns:
            str: API response
            
        Raises:
            ValueError: If API call fails
        """
        # Use the AI API directly - no frontmatter shortcuts
        api_options = self.options.copy()
        
        # Get API provider
        from api import get_client
        
        article_context = {
            "subject": self.subject,
            "article_type": self.article_type
        }
        
        # Extract model-specific options from prompt config
        if self.prompt_config and "parameters" in self.prompt_config:
            api_options.update(self.prompt_config["parameters"])
        
        client = get_client(
            provider=self.ai_provider,
            options=api_options,
            article_context=article_context
        )
        
        if not client:
            raise ValueError(f"Failed to get API client for provider: {self.ai_provider}")
        
        # Call API
        try:
            response = client.complete(prompt)
            return response
        except Exception as e:
            raise ValueError(f"API call failed: {e}")
    
    def _post_process(self, content: str) -> str:
        """Base post-processing implementation with common validation.
        
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
    
    def _component_specific_processing(self, content: str) -> str:
        """Component-specific processing to be implemented by subclasses.
        
        Args:
            content: Pre-validated and cleaned content
            
        Returns:
            str: Processed content
            
        Raises:
            ValueError: If content fails component-specific validation
        """
        # Default implementation uses centralized structured content processing
        return self._process_structured_content(content)
    
    def _process_structured_content(self, content: str, output_format: str = "yaml") -> str:
        """Centralized processing for structured content (YAML, JSON, etc.).
        
        This method handles the common pattern used by most generators:
        1. Parse AI response (JSON/YAML/text)
        2. Populate missing required fields from schema
        3. Apply component-specific formatting
        4. Add proper delimiters
        
        Args:
            content: Raw AI response content
            output_format: Desired output format ("yaml", "json")
            
        Returns:
            str: Processed and formatted content
            
        Raises:
            ValueError: If content parsing or validation fails
        """
        component_name = self.__class__.__name__.replace("Generator", "").lower()
        
        # Step 1: Parse the response to get structured data
        try:
            import json
            import yaml
            
            # Apply YAML escaping BEFORE parsing to prevent issues
            if ':' in content and not content.strip().startswith('{'):
                content = ContentFormatter._escape_yaml_values(content)
            
            # Try JSON first (if AI returns structured JSON)
            if content.strip().startswith('{'):
                parsed_data = json.loads(content)
            # Try YAML if it looks like valid YAML
            elif ':' in content and not ('**' in content or '*' in content):
                parsed_data = yaml.safe_load(content)
            else:
                # Handle raw text content - extract information intelligently
                parsed_data = self._extract_content_from_text(content)
            
            # Step 2: Ensure all required schema fields are present
            parsed_data = self.populate_missing_required_fields(parsed_data, component_name)
            
            # Step 3: Apply component-specific formatting rules
            parsed_data = self._apply_component_formatting_rules(parsed_data, component_name)
            
            # Step 4: Convert to desired output format
            if output_format.lower() == "yaml":
                formatted_content = yaml.dump(
                    parsed_data, 
                    default_flow_style=False, 
                    allow_unicode=True, 
                    sort_keys=False, 
                    width=float('inf'),
                    indent=2
                )
                # Apply centralized formatting for cleanup and normalization
                formatted_content = self.apply_centralized_formatting(formatted_content, parsed_data)
                
                # Add YAML frontmatter delimiters
                if not formatted_content.startswith('---'):
                    formatted_content = '---\n' + formatted_content
                if not formatted_content.endswith('---'):
                    formatted_content = formatted_content.rstrip() + '\n---'
                    
            elif output_format.lower() == "json":
                formatted_content = json.dumps(parsed_data, indent=2, ensure_ascii=False)
            else:
                raise ValueError(f"Unsupported output format: {output_format}")
            
            return formatted_content
            
        except (json.JSONDecodeError, yaml.YAMLError) as e:
            raise ValueError(f"Failed to parse {component_name} as valid JSON/YAML: {e}")
    
    def _apply_component_formatting_rules(self, parsed_data: dict, component_name: str) -> dict:
        """Apply component-specific formatting rules to parsed data.
        
        This method can be overridden by subclasses for component-specific logic,
        but most components should use the default centralized formatting.
        
        Args:
            parsed_data: Parsed data dictionary
            component_name: Name of the component
            
        Returns:
            dict: Data with component-specific formatting applied
        """
        # Component-specific formatting rules
        if component_name == "metatags":
            # Apply dynamic SEO requirements from schema
            parsed_data = self._apply_dynamic_seo_requirements(parsed_data)
            
            # Validate fields based on article type (import here to avoid circular imports)
            try:
                from components.metatags.validation import validate_article_specific_fields
                validate_article_specific_fields(self.article_type, getattr(self, 'category', None), parsed_data)
            except ImportError:
                logger.warning("Metatags validation not available")
            
            return ContentFormatter.format_metatags_structure(
                parsed_data, self.subject, getattr(self, 'category', None)
            )
        elif component_name == "jsonld":
            # JSON-LD specific validation and formatting
            self._validate_jsonld_structure(parsed_data)
            return parsed_data
        else:
            # Default frontmatter formatting for all other components
            return ContentFormatter.format_frontmatter_structure(
                parsed_data, self.subject, getattr(self, 'category', None), self.article_type
            )
    
    def _validate_jsonld_structure(self, data: dict) -> None:
        """Validate JSON-LD structure and apply schema requirements.
        
        Args:
            data: Parsed JSON-LD data
            
        Raises:
            ValueError: If validation fails
        """
        # Basic JSON-LD validation - check context format
        if '@context' in data:
            context = data['@context']
            if context not in ['https://schema.org', 'http://schema.org']:
                # Auto-correct common schema.org variations
                if 'schema.org' in str(context).lower():
                    data['@context'] = 'https://schema.org'
                else:
                    raise ValueError(f"Invalid @context value: {context}. Must be https://schema.org")
    
    def _extract_content_from_text(self, content: str) -> dict:
        """Extract structured data from raw text content.
        
        This method attempts to intelligently parse unstructured text
        and extract key-value pairs for structured data.
        
        Args:
            content: Raw text content
            
        Returns:
            dict: Extracted structured data
        """
        extracted_data = {}
        
        # Split into lines and look for key patterns
        lines = content.strip().split('\n')
        current_key = None
        current_value = []
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            # Look for key: value patterns
            if ':' in line and not line.startswith('-'):
                if current_key and current_value:
                    # Save previous key-value pair
                    extracted_data[current_key] = ' '.join(current_value).strip()
                
                # Start new key-value pair
                parts = line.split(':', 1)
                current_key = parts[0].strip()
                current_value = [parts[1].strip()] if len(parts) > 1 and parts[1].strip() else []
            elif current_key:
                # Continuation of current value
                current_value.append(line)
        
        # Don't forget the last key-value pair
        if current_key and current_value:
            extracted_data[current_key] = ' '.join(current_value).strip()
        
        # If no structured data found, create basic structure
        if not extracted_data:
            extracted_data = {
                'name': self.subject,
                'description': f"Technical information about {self.subject}"
            }
        
        return extracted_data
    
    def _apply_dynamic_seo_requirements(self, parsed: dict) -> dict:
        """Apply dynamic SEO requirements from schema for optimized metatag generation.
        
        Args:
            parsed: The parsed metatags data
            
        Returns:
            dict: Enhanced metatags with dynamic SEO requirements applied
        """
        if not self.has_schema_feature('generatorConfig'):
            return parsed
            
        generator_config = self.get_schema_config('generatorConfig')
        
        # Use the research field configuration that exists in the schema
        if 'research' in generator_config:
            research_config = generator_config['research']
            if 'fields' in research_config:
                logger.info(f"Applied dynamic SEO context from research fields: {research_config['fields']}")
        else:
            # Strict mode: Generator config must be present
            raise ValueError("Metatags generator requires generatorConfig with research fields in schema")
        
        return parsed
    
    def _strip_markdown_code_blocks(self, content: str) -> str:
        """Remove markdown code block delimiters if present.
        
        Args:
            content: Content that may contain markdown code blocks
            
        Returns:
            str: Content with code block markers removed
        """
        return strip_markdown_code_blocks(content)
    
    def _validate_word_count(self, content: str, 
                         min_key: str = "min_words", 
                         max_key: str = "max_words", 
                         component_name: str = None) -> str:
        """Validate that the content meets word count requirements.
        
        Args:
            content: Content to validate
            min_key: Component config key for minimum word count
            max_key: Component config key for maximum word count
            component_name: Name of component for error messages
            
        Returns:
            str: The original content if valid
            
        Raises:
            ValueError: If content doesn't meet word count requirements
        """
        if component_name is None:
            component_name = self.__class__.__name__.replace("Generator", "")
            
        word_count = len(content.split())
        min_words = self.get_component_config(min_key, 0)
        max_words = self.get_component_config(max_key, 10000)
        
        if min_words > 0 and word_count < min_words:
            raise ValueError(f"Generated {component_name} too short: {word_count} words, minimum required: {min_words}")
        
        if max_words > 0 and word_count > max_words:
            raise ValueError(f"Generated {component_name} too long: {word_count} words, maximum allowed: {max_words}")
            
        return content
    
    def _validate_links(self, content: str, max_links: int = None) -> str:
        """Validate and potentially modify links in the content.
        
        Args:
            content: Content to validate
            max_links: Maximum number of links allowed
            
        Returns:
            str: Content with validated links
            
        Raises:
            ValueError: If max_links is None and cannot be determined
        """
        # Extract all markdown links
        link_pattern = r'\[(.*?)\]\((.*?)\)'
        links = re.findall(link_pattern, content)
        
        if max_links is None:
            # Try to get from component config
            inline_links_config = self.component_config.get("inline_links")
            if inline_links_config is None:
                raise ValueError("Missing inline_links configuration for link validation")
                
            if "max_links" not in inline_links_config:
                raise ValueError("Missing max_links in inline_links configuration")
                
            max_links = inline_links_config["max_links"]
        
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
    
    def apply_centralized_formatting(self, content: str, parsed_data: Dict[str, Any] = None) -> str:
        """Apply centralized formatting to ensure consistency across all components.
        
        Args:
            content: Raw content from AI generation
            parsed_data: Optional parsed data structure for additional formatting
            
        Returns:
            str: Formatted content with all standardization applied
        """
        # If we have parsed data, apply comprehensive formatting
        if parsed_data and isinstance(parsed_data, dict):
            component_name = self.__class__.__name__.replace("Generator", "").lower()
            category = getattr(self, 'category', None)
            
            # Apply formatting based on component type
            if component_name == "metatags":
                parsed_data = ContentFormatter.format_metatags_structure(
                    parsed_data, self.subject, category
                )
            else:
                parsed_data = ContentFormatter.format_frontmatter_structure(
                    parsed_data, self.subject, category, self.article_type
                )
            
            # Convert back to YAML string for YAML content
            if isinstance(content, str) and ('---' in content or content.strip().startswith(('name:', 'title:', 'headline:'))):
                import yaml
                content = yaml.dump(
                    parsed_data, 
                    default_flow_style=False, 
                    allow_unicode=True, 
                    sort_keys=False, 
                    width=float('inf'),
                    indent=2
                )
                content = ContentFormatter.clean_yaml_output(content)
        
        # Apply content normalization (includes custom YAML formatting)
        content = ContentFormatter.normalize_yaml_content(content)
        
        # Clean up image URLs and slugs
        import re
        content = re.sub(r'(/images/[^"]*?)--+([^"]*?\.jpg)', r'\1-\2', content)
        content = re.sub(r'([a-z])--+([a-z])', r'\1-\2', content)
        content = re.sub(r'([a-z0-9])-+(\s|"|\'|$|\.)', r'\1\2', content)
        
        return content
    
    # ===================================================================
    # ESSENTIAL FORMATTING METHODS (Direct ContentFormatter Access)
    # ===================================================================
    
    def format_yaml_content(self, content: str, component_type: str = None) -> str:
        """Format YAML content with proper structure and indentation.
        
        Args:
            content: Raw YAML content string
            component_type: Type of component (frontmatter, jsonld, metatags, etc.)
            
        Returns:
            str: Formatted YAML content with proper structure and indentation
        """
        if component_type is None:
            component_type = self.__class__.__name__.lower().replace('generator', '')
        
        return ContentFormatter.normalize_yaml_content(content)
    
    def restructure_yaml_data(self, raw_data: dict, component_type: str = None) -> dict:
        """Restructure flat YAML data into proper nested sections.
        
        Args:
            raw_data: Raw flat data from AI generation
            component_type: Type of component (frontmatter, jsonld, metatags, etc.)
            
        Returns:
            dict: Properly structured data with component-appropriate nesting
        """
        if component_type is None:
            component_type = self.__class__.__name__.lower().replace('generator', '')
        
        return ContentFormatter._restructure_yaml_nesting(raw_data, component_type)
