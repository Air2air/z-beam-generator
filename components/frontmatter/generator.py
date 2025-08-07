"""
Frontmatter generator for Z-Beam Generator.

Enhanced implementation with robust error handling and auto-recovery.
"""

import logging
import yaml
import re

from components.base.component import BaseComponent
from components.base.utils.validation import (
    validate_length, validate_required_fields, validate_category_consistency
)
from components.base.utils.formatting import format_frontmatter_with_comment
from components.base.utils.slug_utils import SlugUtils
from components.base.utils.content_formatter import ContentFormatter
from components.base.image_handler import ImageHandler

logger = logging.getLogger(__name__)

class FrontmatterGenerator(BaseComponent):
    """Generator for article frontmatter with robust validation and auto-recovery."""
    
    def _get_prompt_path(self) -> str:
        """Override to use the correct directory name.
        
        Returns:
            str: Path to prompt template
        """
        return "components/frontmatter/prompt.yaml"
    
    def _get_base_data(self) -> dict:
        """Get base data for the prompt template."""
        data = super()._get_base_data()
        
        # Add subject-name-with-hyphens to support the image URL formatting
        data['subject-name-with-hyphens'] = SlugUtils.create_subject_slug(self.subject)
        
        return data
    
    def _ensure_schema_structure(self, parsed: dict) -> dict:
        """Ensure the frontmatter follows the schema structure for the article type.
        
        Args:
            parsed: The parsed frontmatter data
            
        Returns:
            dict: The frontmatter with enforced schema structure
        """
        if not self.has_schema_feature('generatorConfig'):
            logger.warning(f"No generatorConfig found for article type: {self.article_type}")
            return parsed
            
        config = self.get_schema_config('generatorConfig')
        
        # Extract any field mapping or structure information
        if "fieldContentMapping" in config:
            field_mappings = config["fieldContentMapping"]
            
            # Ensure all mapped fields exist in the frontmatter
            for field_name in field_mappings.keys():
                if field_name not in parsed:
                    logger.warning(f"Adding missing field from schema mapping: {field_name}")
                    parsed[field_name] = f"Information about {field_name} for {self.subject}"
        
        # Check for research structure if available
        if "research" in config and "dataStructure" in config["research"]:
            data_structure = config["research"]["dataStructure"]
            
            # Validate complex nested structures based on schema
            for field_name, field_structure in data_structure.items():
                if field_name in parsed:
                    # Check if field should be an object but isn't
                    if field_structure.get("type") == "object" and not isinstance(parsed[field_name], dict):
                        logger.warning(f"Field {field_name} should be an object, converting")
                        parsed[field_name] = {}
                        
                    # Check if field should be an array but isn't
                    if field_structure.get("type") == "array" and not isinstance(parsed[field_name], list):
                        logger.warning(f"Field {field_name} should be an array, converting")
                        parsed[field_name] = []
        
        return parsed
        
    def _component_specific_processing(self, content: str) -> str:
        """Process the generated frontmatter using centralized formatting.
        
        Args:
            content: Pre-validated, clean API response
            
        Returns:
            str: Validated and formatted frontmatter
            
        Raises:
            ValueError: If content is invalid
        """
        # First, apply basic content normalization
        content = ContentFormatter.normalize_yaml_content(content)
        
        # Extract YAML content from various formats the AI might generate
        yaml_content = self._extract_yaml_content(content)
        
        # Attempt to parse as YAML to validate structure
        try:
            parsed = yaml.safe_load(yaml_content)
            if not isinstance(parsed, dict):
                raise ValueError("Frontmatter must be a valid YAML dictionary")
        except yaml.YAMLError as e:
            # Additional debugging
            logger.error(f"YAML parsing error: {e}")
            logger.error(f"Content causing error: {yaml_content}")
            raise ValueError(f"Invalid YAML in frontmatter: {e}")
        
        # Handle materialProfile wrapper (sometimes the model wraps everything in this object)
        if len(parsed.keys()) == 1 and 'materialProfile' in parsed and isinstance(parsed['materialProfile'], dict):
            logger.warning("Found 'materialProfile' wrapper, extracting contents")
            profile_data = parsed.pop('materialProfile')
            # Merge the profile data into the main dictionary
            parsed.update(profile_data)
            logger.info(f"Extracted fields from materialProfile: {list(profile_data.keys())}")
        
        # Special handling for common error: using 'title' instead of 'name'
        if 'name' not in parsed and 'title' in parsed:
            # Auto-fix instead of error
            logger.warning("Found 'title' field but 'name' is required. Copying 'title' to 'name'.")
            parsed['name'] = parsed['title']
        
        # Apply centralized formatting
        formatted_content = self.apply_centralized_formatting(content, parsed)
        
        # Ensure frontmatter has proper YAML delimiters
        # Re-parse to get the formatted data structure
        try:
            formatted_parsed = yaml.safe_load(formatted_content)
            if not isinstance(formatted_parsed, dict):
                raise ValueError("Formatted frontmatter must be a valid YAML dictionary")
        except yaml.YAMLError as e:
            logger.error(f"YAML parsing error after formatting: {e}")
            raise ValueError(f"Invalid YAML in formatted frontmatter: {e}")
        
        # Get category from instance attribute
        category = getattr(self, 'category', '')
        
        # Enhanced dynamic schema-based field validation and auto-population using base component
        parsed = self.validate_and_populate_required_fields(parsed, 'frontmatter')
        
        # Apply schema structure validation after auto-fixes
        parsed = self._ensure_schema_structure(parsed)
        
        # Convert to YAML string and add proper frontmatter delimiters
        yaml_content = yaml.dump(parsed, default_flow_style=False, sort_keys=False, allow_unicode=True)
        final_content = format_frontmatter_with_comment(
            yaml_content, category, self.article_type, self.subject
        )
        
        return final_content
    
    def _extract_yaml_content(self, content: str) -> str:
        """Extract clean YAML content from various AI response formats.
        
        Args:
            content: Raw AI response content
            
        Returns:
            str: Clean YAML content
        """
        # Use centralized base component method
        return self.extract_yaml_content(content)

    def _sanitize_content(self, content: str) -> str:
        """Remove malformed content and standardize image URLs."""
        # Remove standalone URL fragments
        lines = content.split('\n')
        cleaned_lines = []
        
        for line in lines:
            # Skip standalone lines with broken URL fragments
            if re.match(r'^-*>*-*laser-cleaning.*\.jpg$', line.strip()):
                logger.info(f"Removing broken URL line: {line.strip()}")
                continue
            cleaned_lines.append(line)
        
        content = '\n'.join(cleaned_lines)
        
        # Fix URLs with arrow characters
        content = re.sub(r'-+>+-*', '-', content)
        content = re.sub(r'([^a-z])>+-*', r'\1', content)
        
        # Fix missing hyphens between subject and laser-cleaning
        content = re.sub(r'(/images/[a-z0-9-]+)laser-cleaning', r'\1-laser-cleaning', content)
        
        # Fix double dashes in image URLs - this is our additional safeguard
        content = re.sub(r'(/images/[^"]*?)--+([^"]*?\.jpg)', r'\1-\2', content)
        
        return content
    
    def validate_category_consistency(self, content: str) -> bool:
        """Validates category consistency in frontmatter.
        
        Args:
            content: Frontmatter content
            
        Returns:
            bool: True if consistent
        """
        category = getattr(self, 'category', None)
        if not category:
            return True
            
        return validate_category_consistency(content, category, self.article_type, self.subject)
    
    def _process_response(self, response_data):
        """Process the raw response data from the AI model."""
        # Let the base class process the response first
        data = super()._process_response(response_data)
        
        # Process image URLs in case they bypass component_specific_processing
        data = ImageHandler.process_image_data(data, self.subject)
        data = ImageHandler.add_missing_images(data, self.subject)
        
        return data
