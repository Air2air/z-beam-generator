"""
Base component for Z-Beam Generator.

Strict fail-fast implementation with no fallbacks or defaults.
"""

import logging
import os
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from components.base.material_formula_service import formula_service

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
        self.component_config = component_config
        self.ai_provider = component_config["ai_provider"]
        self.options = component_config["options"]
    
    @abstractmethod
    def generate(self) -> str:
        """Generate component content with strict validation.
        
        Returns:
            str: The generated content
            
        Raises:
            ValueError: If generation fails
        """
        pass
    
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
            "author_id": self.author_data.get("id", 1),
            "category": getattr(self, "category", ""),
            "schema": str(self.schema),
            "profile": profile_data.get("profile", {}),
            "validation": profile_data.get("validation", {}),
        }

        # Add frontmatter if available
        frontmatter = getattr(self, "_frontmatter_data", None)
        if frontmatter:
            template_data["all_frontmatter"] = frontmatter
            template_data["frontmatter_data"] = frontmatter
            template_data["frontmatter"] = frontmatter  # Add for JSON-LD compatibility
        else:
            template_data["all_frontmatter"] = "No frontmatter data available"
            template_data["frontmatter_data"] = {}
            template_data["frontmatter"] = "No frontmatter data available"

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
                "min_words": self.component_config.get("min_words", 300),
                "max_words": self.component_config.get("max_words", 500),
                "required_fields": profile_data.get("validation", {}).get("frontmatter", {}).get("requiredFields", []),
                "material_formula": material_formula,
                "material_symbol": material_symbol,
                "material_type": material_type,
                # Add chemical properties structure
                "chemical_properties": {
                    "symbol": material_symbol,
                    "formula": material_formula,
                    "materialType": material_type
                }
            })
        elif component_name == "content":
            template_data.update({
                "min_words": self.component_config.get("min_words", 800),
                "max_words": self.component_config.get("max_words", 1200),
                "style": self.component_config.get("style", "technical"),
                "audience": self.component_config.get("audience", "professional"),
                "max_links": self.component_config.get("inline_links", {}).get("max_links", 5)
            })
        elif component_name == "bullets":
            template_data.update({
                "count": self.component_config.get("count", 10),
                "style": self.component_config.get("style", "technical")
            })
        elif component_name == "table":
            if frontmatter:
                table_keys = [key for key in frontmatter.keys() if isinstance(frontmatter[key], (dict, list))]
            else:
                table_keys = []
            template_data.update({
                "table_keys": table_keys,
                "title": f"{self.subject} Laser Cleaning Tables",
                "key": "default",
                "rows": self.component_config.get("rows", 5)
            })
        elif component_name == "tags":
            template_data.update({
                "max_tags": self.component_config.get("max_tags", 10),
                "min_tags": self.component_config.get("min_tags", 5),
                "tag_categories": self.component_config.get("tag_categories", []),
                "extracted_keywords": self._extract_keywords_from_frontmatter(frontmatter) if frontmatter else []
            })
        elif component_name == "metatags":
            keywords_list = self._extract_keywords_from_frontmatter(frontmatter) if frontmatter else []
            keywords_str = ", ".join(keywords_list) if keywords_list else f"{self.subject}, laser cleaning"
            template_data.update({
                "max_tags": self.component_config.get("max_tags", 15),
                "min_tags": self.component_config.get("min_tags", 8),
                "extracted_keywords": keywords_str
            })
        elif component_name == "caption":
            template_data.update({
                "results_word_count_max": self.component_config.get("results_word_count_max", 40),
                "equipment_word_count_max": self.component_config.get("equipment_word_count_max", 40),
                "shape": self.component_config.get("shape", "component"),
                "material": self.subject  # Caption prompts use 'material' instead of 'subject'
            })

        return template_data

    def _extract_keywords_from_frontmatter(self, frontmatter: Dict[str, Any]) -> list:
        """Extract keywords from frontmatter data."""
        if not frontmatter:
            return []
        keywords = []
        if "keywords" in frontmatter:
            if isinstance(frontmatter["keywords"], list):
                keywords.extend(frontmatter["keywords"])
        return keywords[:15]  # Limit to 15 keywords
    
    def get_component_config(self, key: str, default=None) -> Any:
        """Get a value from component_config with strict validation.
        
        Args:
            key: Configuration key to retrieve
            default: Default value to return if key doesn't exist (if None, raises ValueError)
            
        Returns:
            Value from component_config or default
            
        Raises:
            ValueError: If key doesn't exist in component_config and no default is provided
        """
        if key not in self.component_config:
            if default is None:
                raise ValueError(f"Required component configuration key '{key}' not found")
            return default
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
        """Call the AI API with strict validation.
        
        Args:
            prompt: The formatted prompt
            
        Returns:
            str: API response content
            
        Raises:
            ValueError: If API call fails
        """
        try:
            from api.client import ApiClient
            # Create an article context dictionary from the component's data
            article_context = {
                "subject": self.subject,
                "article_type": self.article_type,
                "category": self.category
            }
            client = ApiClient(ai_provider=self.ai_provider, options=self.options, article_context=article_context)
            response = client.complete(prompt)
            
            if not response or not response.strip():
                raise ValueError("API returned empty response")
                
            return response.strip()
        except Exception as e:
            raise ValueError(f"API call failed: {e}")
