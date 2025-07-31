"""
Frontmatter generator for Z-Beam Generator.

Strict fail-fast implementation with no fallbacks or defaults.
"""

import logging
import yaml
from typing import Dict, Any
from components.base.component import BaseComponent

logger = logging.getLogger(__name__)

class FrontmatterGenerator(BaseComponent):
    """Generator for article frontmatter with strict validation."""
    
    def generate(self) -> str:
        """Generate frontmatter content with strict validation.
        
        Returns:
            str: The generated frontmatter
            
        Raises:
            ValueError: If generation fails
        """
        # Strict validation - no fallbacks
        data = self._prepare_data()
        prompt = self._format_prompt(data)
        content = self._call_api(prompt)
        return self._post_process(content)
    
    def _prepare_data(self) -> Dict[str, Any]:
        """Prepare data for frontmatter generation with strict validation.
        
        Returns:
            Dict[str, Any]: Validated data for generation
            
        Raises:
            ValueError: If required data is missing
        """
        data = super()._prepare_data()
        
        # Get component configuration
        component_config = self.get_component_config()
        
        # Validate schema is available
        if not self.schema:
            raise ValueError("Schema is required for frontmatter generation")
        
        # Find the profile dynamically based on article type
        profile_key = f"{self.article_type}Profile"
        if profile_key not in self.schema:
            raise ValueError(f"Profile '{profile_key}' not found in schema for article type '{self.article_type}'")
        
        # Extract profile and validation rules
        profile_data = self.schema[profile_key]
        
        if "profile" not in profile_data:
            raise ValueError(f"Profile data not found in {profile_key}")
        
        if "validation" not in profile_data or "frontmatter" not in profile_data["validation"]:
            raise ValueError(f"Frontmatter validation rules not found in {profile_key}")
        
        profile = profile_data["profile"]
        validation = profile_data["validation"]["frontmatter"]
        
        # Validate required fields exist in validation
        if "requiredFields" not in validation:
            raise ValueError("Required fields not defined in schema validation")
        
        data.update({
            "profile": profile,
            "validation": validation,
            "required_fields": validation["requiredFields"],
            "website_url": "https://www.z-beam.com",
            "min_words": component_config.get("min_words", 300),
            "max_words": component_config.get("max_words", 500),
            "author_id": self.author_data.get("id", 1)  # Get author ID from author data
        })
        
        return data
    
    def _post_process(self, content: str) -> str:
        """Post-process the generated frontmatter.
        
        Args:
            content: Raw API response
            
        Returns:
            str: Validated frontmatter
            
        Raises:
            ValueError: If content is invalid
        """
        if not content or not content.strip():
            raise ValueError("API returned empty or invalid frontmatter")
        
        # Attempt to parse as YAML to validate structure
        try:
            parsed = yaml.safe_load(content.strip())
            if not isinstance(parsed, dict):
                raise ValueError("Frontmatter must be a valid YAML dictionary")
        except yaml.YAMLError as e:
            raise ValueError(f"Invalid YAML in frontmatter: {e}")
        
        # Validate required fields are present
        profile_key = f"{self.article_type}Profile"
        validation = self.schema[profile_key]["validation"]["frontmatter"]
        required_fields = validation["requiredFields"]
        
        missing_fields = [field for field in required_fields if field not in parsed]
        if missing_fields:
            raise ValueError(f"Missing required frontmatter fields: {missing_fields}")
        
        return content.strip()
