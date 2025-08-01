"""
Metatags generator for Z-Beam Generator.

Generates Next.js compatible meta tags in YAML frontmatter format.
"""

import logging
import yaml
from components.base.enhanced_component import EnhancedBaseComponent

logger = logging.getLogger(__name__)

class MetatagsGenerator(EnhancedBaseComponent):
    """Generator for Next.js compatible meta tags in YAML frontmatter format with strict validation."""
    
    def _get_prompt_path(self) -> str:
        """Override to use the correct directory name.
        
        Returns:
            str: Path to prompt template
        """
        return "components/metatags/prompt.yaml"
    
    def _post_process(self, content: str) -> str:
        """Post-process the generated metatags, ensuring proper Next.js compatible YAML frontmatter format.
        
        Args:
            content: Raw API response
            
        Returns:
            str: Processed Next.js compatible YAML frontmatter metatags
            
        Raises:
            ValueError: If content is invalid
        """
        # Validate and clean input
        content = self._validate_non_empty(content, "API returned empty or invalid metatags")
        
        # Extract YAML content
        yaml_content = content.strip()
        
        # Handle frontmatter delimiters
        if yaml_content.startswith('---'):
            parts = yaml_content.split('---', 2)
            if len(parts) >= 3:
                yaml_content = parts[1].strip()
            elif len(parts) == 2:
                yaml_content = parts[1].strip()
        
        # Parse the YAML content
        try:
            meta_data = yaml.safe_load(yaml_content)
            if not isinstance(meta_data, dict):
                raise ValueError("Generated metadata is not a valid YAML dictionary")
        except yaml.YAMLError as e:
            raise ValueError(f"Invalid YAML format in generated metadata: {str(e)}")
        
        # Validate required fields for Next.js compatibility
        required_fields = self.prompt_config.get('validation', {}).get('required_fields', ["title", "description", "openGraph", "twitter"])
        for field in required_fields:
            if field not in meta_data:
                raise ValueError(f"Required field '{field}' missing from generated metadata")
        
        # Check for required OpenGraph properties
        og_required = ["title", "description"]
        for field in og_required:
            if field not in meta_data.get("openGraph", {}):
                raise ValueError(f"Required openGraph property '{field}' missing from generated metadata")
        
        # Validate we have enough metadata fields
        min_tags = self.get_component_config("min_tags")
        flat_fields_count = self._count_metadata_fields(meta_data)
        if flat_fields_count < min_tags:
            raise ValueError(f"Generated only {flat_fields_count} meta properties, minimum required: {min_tags}")
        
        # Check maximum tags limit
        max_tags = self.get_component_config("max_tags")
        if flat_fields_count > max_tags:
            raise ValueError(f"Generated {flat_fields_count} meta properties, maximum allowed: {max_tags}")
        
        # Format as YAML frontmatter
        formatted_yaml = yaml.dump(meta_data, default_flow_style=False, sort_keys=False)
        return f"---\n{formatted_yaml}---\n"
    
    def _count_metadata_fields(self, meta_data: dict, prefix="") -> int:
        """Count the total number of metadata fields, including nested ones.
        
        Args:
            meta_data: The metadata dictionary
            prefix: Prefix for nested fields
            
        Returns:
            int: Total number of fields
        """
        count = 0
        for key, value in meta_data.items():
            full_key = f"{prefix}.{key}" if prefix else key
            if isinstance(value, dict):
                count += self._count_metadata_fields(value, full_key)
            elif isinstance(value, list):
                # Count each item in a list as one field (for arrays like images)
                count += 1
            else:
                count += 1
        return count
