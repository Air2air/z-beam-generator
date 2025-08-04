"""
Frontmatter generator for Z-Beam Generator.

Strict fail-fast implementation with no fallbacks or defaults.
"""

import logging
import yaml
from components.base.component import BaseComponent
from components.base.utils.validation import (
    validate_length, validate_required_fields
)
from components.base.utils.formatting import format_frontmatter_with_comment

logger = logging.getLogger(__name__)

class FrontmatterGenerator(BaseComponent):
    """Generator for article frontmatter with strict validation."""
    
    def _component_specific_processing(self, content: str) -> str:
        """Process the generated frontmatter.
        
        Args:
            content: Pre-validated, clean API response
            
        Returns:
            str: Validated and formatted frontmatter
            
        Raises:
            ValueError: If content is invalid
        """
        # Attempt to parse as YAML to validate structure
        try:
            parsed = yaml.safe_load(content)
            if not isinstance(parsed, dict):
                raise ValueError("Frontmatter must be a valid YAML dictionary")
        except yaml.YAMLError as e:
            # Additional debugging
            logger.error(f"YAML parsing error: {e}")
            logger.error(f"Content causing error: {content}")
            raise ValueError(f"Invalid YAML in frontmatter: {e}")
        
        # Validate required fields are present
        profile_key = f"{self.article_type}Profile"
        validation = self.schema[profile_key]["validation"]["frontmatter"]
        required_fields = validation["requiredFields"]
        
        validate_required_fields(parsed, required_fields, "frontmatter")
        
        # Special handling for common error: using 'title' instead of 'name'
        if 'name' not in parsed and 'title' in parsed:
            raise ValueError("Found 'title' field but 'name' is required. Please use 'name' instead of 'title' in the frontmatter.")
        
        # Enforce frontmatter value length limits
        # Title and headline should be concise
        if "title" in parsed:
            validate_length(parsed["title"], 0, 100, "Title", "chars")
        
        if "headline" in parsed:
            validate_length(parsed["headline"], 0, 150, "Headline", "chars")
        
        # Description and summary should be reasonable length
        if "description" in parsed:
            validate_length(parsed["description"], 0, 250, "Description", "chars")
        
        # Keywords should be limited in number and length
        if "keywords" in parsed and isinstance(parsed["keywords"], list):
            if len(parsed["keywords"]) > 15:
                raise ValueError(f"Too many keywords: {len(parsed['keywords'])}, maximum should be 15")
            
            for keyword in parsed["keywords"]:
                validate_length(keyword, 0, 50, "Keyword", "chars")
        
        # Ensure the name field contains exactly the subject
        if "name" in parsed and parsed["name"] != self.subject:
            raise ValueError(f"Name must be exactly the subject name: '{parsed['name']}' should be '{self.subject}'")
        
        # Ensure nested properties have reasonable lengths
        for key, value in parsed.items():
            if isinstance(value, dict):
                for nested_key, nested_value in value.items():
                    if isinstance(nested_value, str):
                        validate_length(nested_value, 0, 500, f"Nested value {key}.{nested_key}", "chars")
            elif isinstance(value, list) and all(isinstance(item, str) for item in value):
                for i, item in enumerate(value):
                    validate_length(item, 0, 250, f"List item {key}[{i}]", "chars")
        
        # Clean content (use yaml.dump to ensure valid YAML format)
        cleaned_content = yaml.dump(parsed, default_flow_style=False, sort_keys=False)
        
        # Store parsed frontmatter for other components to access
        self._frontmatter_data = parsed
        
        # Get category from instance attribute
        category = getattr(self, 'category', '')
        
        # Format frontmatter with HTML comment (metadata comment first, then frontmatter)
        final_content = format_frontmatter_with_comment(
            cleaned_content, category, self.article_type, self.subject
        )
        
        # Validate category consistency
        try:
            self.validate_category_consistency(final_content)
        except ValueError as e:
            logger.warning(f"Category validation error: {e}")
        
        return final_content
