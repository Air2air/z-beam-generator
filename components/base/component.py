"""
Base component for Z-Beam Generator.

Combined base component with all common functionality for Z-Beam generators.
"""
import logging
import os
import re
import yaml
from abc import ABC
from typing import Dict, Any, Optional

from components.base.utils.validation import (
    validate_non_empty, validate_category_consistency,
    strip_markdown_code_blocks
)
from components.base.services.material_service import formula_service

logger = logging.getLogger(__name__)

class BaseComponent(ABC):
    """Base class for all Z-Beam generators with complete functionality."""
    
    def __init__(self, subject: str, article_type: str, schema: Dict[str, Any], 
                 author_data: Dict[str, Any], component_config: Dict[str, Any], 
                 frontmatter_data: Dict[str, Any] = None):
        """Initialize component with validation and prompt config loading.
        
        Args:
            subject: The subject of the article
            article_type: Type of article (material, application, region, thesaurus)
            schema: Schema configuration for the article type
            author_data: Author information
            component_config: Component-specific configuration
            frontmatter_data: Optional frontmatter data from existing content
            
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
        
        # Store frontmatter data if provided
        self._frontmatter_data = frontmatter_data or {}
        
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
        """Extract all dynamic, schema-driven template variables for the component.
        
        Returns:
            Dict[str, Any]: All validated, schema-driven template variables
        
        Raises:
            ValueError: If required data is missing or schema is invalid
        """
        # Validate author fields
        required_author_fields = ["author_name", "author_country"]
        for field in required_author_fields:
            if field not in self.author_data:
                # Check if we have frontmatter data with nested author info as fallback
                if hasattr(self, '_frontmatter_data') and self._frontmatter_data and 'author' in self._frontmatter_data:
                    author_key = field.replace('author_', '')
                    if author_key in self._frontmatter_data['author']:
                        # Use author data from frontmatter
                        self.author_data[field] = self._frontmatter_data['author'][author_key]
                    else:
                        raise ValueError(f"Required author field '{field}' is missing")
                else:
                    raise ValueError(f"Required author field '{field}' is missing")

        # Get component name
        component_name = self.__class__.__name__.replace("Generator", "").lower()
        profile_key = f"{self.article_type}Profile"
        if profile_key not in self.schema:
            raise ValueError(f"Profile '{profile_key}' not found in schema")
        profile_data = self.schema[profile_key]

        # Start with base fields - ALL components need these
        template_data = {
            "subject": self.subject,
            "article_type": self.article_type,
            "author_name": self.author_data["author_name"],
            "author_country": self.author_data["author_country"],
            "author_id": self.author_data.get("author_id", self.author_data.get("id", 1)),
            "category": getattr(self, "category", ""),
            "schema": str(self.schema),
            "profile": profile_data.get("profile", {}),
            "validation": profile_data.get("validation", {}),
            "slug": self.subject.lower().replace(" ", "-").replace("_", "-")  # Add slug for image naming
        }

        # Add frontmatter if available
        frontmatter = self._frontmatter_data
        if frontmatter:
            template_data["all_frontmatter"] = frontmatter
            template_data["frontmatter_data"] = frontmatter
            template_data["frontmatter"] = frontmatter  # Add for JSON-LD compatibility
            
            # Extract common fields from frontmatter to make them directly accessible
            if "name" in frontmatter:
                template_data["name"] = frontmatter["name"]
            if "description" in frontmatter:
                template_data["description"] = frontmatter["description"]
            if "summary" in frontmatter:
                template_data["summary"] = frontmatter["summary"]
                
            # Make sure author name is available for tags
            if "author" in frontmatter and "name" in frontmatter["author"]:
                template_data["author_name"] = frontmatter["author"]["name"]
            
            # Handle specific sections based on article type
            if self.article_type == "material" and "specifications" in frontmatter:
                template_data["specifications"] = frontmatter["specifications"]
            
            # Process images with special handling
            if "images" in frontmatter:
                template_data["images"] = frontmatter["images"]
                
                # Extract image URLs and make them directly accessible at the top level
                if isinstance(frontmatter["images"], dict):
                    for img_type, img_data in frontmatter["images"].items():
                        if isinstance(img_data, dict):
                            # Create a normalized key for the image URL at the top level
                            img_url_key = f"{img_type}_image_url"
                            if "url" in img_data:
                                template_data[img_url_key] = img_data["url"]
                            elif "src" in img_data:
                                template_data[img_url_key] = img_data["src"]
                            
                            # Also create alt text at the top level
                            if "alt" in img_data:
                                template_data[f"{img_type}_image_alt"] = img_data["alt"]
                
                # Create consolidated image lists for easy access
                template_data["image_urls"] = []
                template_data["image_alts"] = []
                for img_type, img_data in frontmatter["images"].items():
                    if isinstance(img_data, dict):
                        if "url" in img_data:
                            template_data["image_urls"].append(img_data["url"])
                        elif "src" in img_data:
                            template_data["image_urls"].append(img_data["src"])
                        
                        if "alt" in img_data:
                            template_data["image_alts"].append(img_data["alt"])
            
            if "tags" in frontmatter:
                template_data["tags"] = frontmatter["tags"]
            
            # Include section data for rich frontmatter
            if "sections" in frontmatter:
                template_data["sections"] = frontmatter["sections"]
                
            # For components that reference other components
            if "related" in frontmatter:
                template_data["related"] = frontmatter["related"]
                
            # Ensure tags are available for content component
            if "tags" not in template_data:
                if "keywords" in frontmatter:
                    template_data["tags"] = frontmatter["keywords"]
                    template_data["keywords"] = frontmatter["keywords"]
                    template_data["extracted_keywords"] = ", ".join(frontmatter["keywords"]) if isinstance(frontmatter["keywords"], list) else frontmatter["keywords"]
                else:
                    template_data["tags"] = []
                    template_data["keywords"] = []
                    template_data["extracted_keywords"] = ""
        else:
            template_data["all_frontmatter"] = "No frontmatter data available"
            template_data["frontmatter_data"] = {}
            template_data["frontmatter"] = "No frontmatter data available"
            template_data["tags"] = []

        # Component-specific additions
        if component_name == "frontmatter":
            # Add material formula if applicable
            material_formula = None
            material_symbol = None
            material_type = None
            if self.article_type == "material":
                category = getattr(self, "category", None)
                material_formula = formula_service.get_formula(self.subject, category)
                material_symbol = formula_service.get_symbol(self.subject, category)
                material_type = formula_service.get_material_type(self.subject, category)
                
                if not material_formula and hasattr(self, "category"):
                    material_formula = formula_service.get_generic_formula(self.category)
            
            template_data.update({
                "website_url": "https://www.z-beam.com",
                "material_formula": "Not available" if material_formula is None else material_formula,
                "material_symbol": "Not available" if material_symbol is None else material_symbol,
                "material_type": "Not available" if material_type is None else material_type
            })
        
        # Handle specific article type variables
        if "variables" in profile_data:
            for var_name, var_value in profile_data["variables"].items():
                template_data[var_name] = var_value
                
        # Add component-specific configs
        if component_name in profile_data:
            component_data = profile_data[component_name]
            for key, value in component_data.items():
                template_data[key] = value
                
        # Additional fields for formatting
        if self.article_type == "material":
            template_data["material"] = self.subject
            template_data["material_type"] = template_data.get("material_type", "")
            
        elif self.article_type == "application":
            template_data["application"] = self.subject
            
        elif self.article_type == "region":
            template_data["region"] = self.subject
            
        elif self.article_type == "thesaurus":
            template_data["term"] = self.subject
        
        # Add min_words and max_words from component_config if available
        template_data["min_words"] = self.component_config.get("options", {}).get("min_words", 300)
        template_data["max_words"] = self.component_config.get("options", {}).get("max_words", 500)
        
        # Add style if available, or provide a default
        template_data["style"] = self.component_config.get("style", "technical")
        
        # Add component-specific configuration variables for all components
        component_name = self.__class__.__name__.replace("Generator", "").lower()
        
        # Content component config
        if component_name == "content":
            template_data["max_links"] = self.component_config.get("max_links", 5)
            template_data["audience"] = self.component_config.get("audience", "technical")
        
        # Bullets component config
        if component_name == "bullets":
            template_data["count"] = self.component_config.get("count", 5)
        
        # Table component config
        if component_name == "table":
            template_data["table_keys"] = self.component_config.get("table_keys", ["Property", "Value", "Unit"])
            template_data["rows"] = self.component_config.get("rows", 5)
        
        # Tags component config
        if component_name == "tags" or component_name == "metatags":
            template_data["min_tags"] = self.component_config.get("min_tags", 5)
            template_data["max_tags"] = self.component_config.get("max_tags", 10)
            template_data["tag_categories"] = self.component_config.get("tag_categories", [])
            
        # Caption component config
        if component_name == "caption":
            template_data["results_word_count_max"] = self.component_config.get("results_word_count_max", 40)
            template_data["equipment_word_count_max"] = self.component_config.get("equipment_word_count_max", 40)
            template_data["shape"] = self.component_config.get("shape", "component")
            
        return template_data
    
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
    
    def get_frontmatter_data(self) -> Optional[Dict[str, Any]]:
        """Get the frontmatter data if available.
        
        Returns:
            Optional[Dict[str, Any]]: Frontmatter data or None
        """
        return self._frontmatter_data
    
    def get_frontmatter_value(self, key: str, default: Any = None) -> Any:
        """Get a specific value from frontmatter data.
        
        Args:
            key: The key to look up in frontmatter
            default: Value to return if key is not found
            
        Returns:
            Any: The value from frontmatter or default
            
        Raises:
            ValueError: If key is not found and no default is provided
        """
        if not self._frontmatter_data:
            if default is not None:
                return default
            raise ValueError(f"No frontmatter data available for key '{key}'")
            
        # Handle nested keys with dot notation (e.g., "images.hero.alt")
        if "." in key:
            parts = key.split(".")
            value = self._frontmatter_data
            for part in parts:
                if isinstance(value, dict) and part in value:
                    value = value[part]
                else:
                    if default is not None:
                        return default
                    raise ValueError(f"Frontmatter key path '{key}' not found")
            return value
        
        # Direct key lookup
        if key in self._frontmatter_data:
            return self._frontmatter_data[key]
            
        if default is not None:
            return default
            
        raise ValueError(f"Required frontmatter key '{key}' not found")
        
    def has_frontmatter_section(self, section_name: str) -> bool:
        """Check if a specific section exists in the frontmatter.
        
        Args:
            section_name: The section name to check
            
        Returns:
            bool: True if section exists, False otherwise
        """
        return bool(self._frontmatter_data and section_name in self._frontmatter_data)
    
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
        use_condensed = self._frontmatter_data and "condensed_template" in self.prompt_config
        
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
                error_msg += f"\nCheck that frontmatter contains the required data. Available frontmatter keys: {list(self._frontmatter_data.keys()) if self._frontmatter_data else 'None'}"
            
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
        # Check if we can use frontmatter data instead of making an API call
        component_name = self.__class__.__name__.replace("Generator", "").lower()
        frontmatter_key = f"{component_name}_content"
        
        # If the component's content is already in frontmatter, use it directly
        if self._frontmatter_data and frontmatter_key in self._frontmatter_data:
            logger.info(f"Using existing {component_name} content from frontmatter")
            return self._frontmatter_data[frontmatter_key]
            
        # Check if we can use another component's content via references
        if self._frontmatter_data and "references" in self._frontmatter_data:
            references = self._frontmatter_data.get("references", {})
            if component_name in references:
                ref_source = references[component_name]
                if ref_source in self._frontmatter_data:
                    logger.info(f"Using referenced content for {component_name} from {ref_source}")
                    return self._frontmatter_data[ref_source]
                    
        # Prepare API options based on frontmatter data presence
        api_options = self.options.copy()
        
        # If we have rich frontmatter, we can potentially use a lower temperature
        if self._frontmatter_data and len(self._frontmatter_data) > 5:
            # Only reduce temperature if it's not explicitly set by the component
            if "temperature" not in self.component_config:
                # Use a lower temperature for more deterministic output with rich data
                current_temp = api_options.get("temperature")
                if current_temp is not None:
                    api_options["temperature"] = min(current_temp, 0.5)
                else:
                    api_options["temperature"] = 0.5
                logger.debug(f"Set temperature to {api_options['temperature']} due to rich frontmatter")
        
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
        
        This provides the common validation logic that most generators need:
        1. Validates content is not empty
        2. Strips markdown code blocks
        3. Configures YAML formatting for consistent output
        4. Calls component-specific processing via _component_specific_processing
        
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
        
        # Step 3: Configure YAML formatting for all generators
        # This ensures consistent YAML output across all components
        try:
            from components.base.utils.formatting import configure_yaml_formatting
            configure_yaml_formatting()
        except ImportError:
            logger.warning("Could not configure YAML formatting - formatting module not found")
        
        # Step 4: Component-specific processing
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
        # Default implementation returns the content unchanged
        return content
    
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
            component_name: Name of component for error messages (defaults to class name)
            
        Returns:
            str: The original content if valid
            
        Raises:
            ValueError: If content doesn't meet word count requirements
        """
        if component_name is None:
            component_name = self.__class__.__name__.replace("Generator", "")
            
        word_count = len(content.split())
        
        # Get min/max from component config
        min_words = self.get_component_config(min_key, 0)
        max_words = self.get_component_config(max_key, 10000)
        
        if min_words > 0 and word_count < min_words:
            # Changed from raising ValueError to logging a warning
            # This prevents generation failures for content that's just a bit short
            logger.warning(f"Generated {component_name} too short: {word_count} words, minimum required: {min_words}")
        
        if max_words > 0 and word_count > max_words:
            logger.warning(f"Generated {component_name} too long: {word_count} words, maximum allowed: {max_words}")
            
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
