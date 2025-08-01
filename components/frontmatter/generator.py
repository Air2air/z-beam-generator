"""
Frontmatter generator for Z-Beam Generator.

Strict fail-fast implementation with no fallbacks or defaults.
"""

import logging
import yaml
from components.base.enhanced_component import EnhancedBaseComponent

logger = logging.getLogger(__name__)

class FrontmatterGenerator(EnhancedBaseComponent):
    """Generator for article frontmatter with strict validation."""
    
    def _post_process(self, content: str) -> str:
        """Post-process the generated frontmatter.
        
        Args:
            content: Raw API response
            
        Returns:
            str: Validated frontmatter
            
        Raises:
            ValueError: If content is invalid
        """
        # Validate and clean input
        content = self._validate_non_empty(content, "API returned empty or invalid frontmatter")
        
        # Strip markdown code blocks if present
        content = self._strip_markdown_code_blocks(content)
        
        # Attempt to parse as YAML to validate structure
        try:
            parsed = yaml.safe_load(content)
            if not isinstance(parsed, dict):
                raise ValueError("Frontmatter must be a valid YAML dictionary")
        except yaml.YAMLError as e:
            raise ValueError(f"Invalid YAML in frontmatter: {e}")
        
        # Validate required fields are present
        profile_key = f"{self.article_type}Profile"
        validation = self.schema[profile_key]["validation"]["frontmatter"]
        required_fields = validation["requiredFields"]
        
        # NOTE: All schemas require 'name' field (not 'title') in frontmatter
        # Make sure the prompt template uses 'name' and not 'title'
        missing_fields = [field for field in required_fields if field not in parsed]
        
        # Special handling for common error: using 'title' instead of 'name'
        if 'name' in missing_fields and 'title' in parsed:
            raise ValueError("Found 'title' field but 'name' is required. Please use 'name' instead of 'title' in the frontmatter.")
            
        if missing_fields:
            raise ValueError(f"Missing required frontmatter fields: {missing_fields}")
        
        # Enforce frontmatter value length limits
        # Title and headline should be concise
        if "title" in parsed and len(parsed["title"]) > 100:
            raise ValueError(f"Title too long: {len(parsed['title'])} chars, maximum should be 100 chars")
        
        if "headline" in parsed and len(parsed["headline"]) > 150:
            raise ValueError(f"Headline too long: {len(parsed['headline'])} chars, maximum should be 150 chars")
        
        # Description and summary should be reasonable length
        if "description" in parsed and len(parsed["description"]) > 250:
            raise ValueError(f"Description too long: {len(parsed['description'])} chars, maximum should be 250 chars")
        
        # Keywords should be limited in number and length
        if "keywords" in parsed and isinstance(parsed["keywords"], list):
            if len(parsed["keywords"]) > 15:
                raise ValueError(f"Too many keywords: {len(parsed['keywords'])}, maximum should be 15")
            
            for keyword in parsed["keywords"]:
                if len(keyword) > 50:
                    raise ValueError(f"Keyword too long: '{keyword}' ({len(keyword)} chars), maximum should be 50 chars")
        
        return content
        # Use base class schema-driven data preparation
        data = self.get_template_data()
        prompt = self._format_prompt(data)
        content = self._call_api(prompt)
        return self._post_process(content)
    
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
        
        # Strip markdown code blocks if present
        content = content.strip()
        if content.startswith('```yaml') and content.endswith('```'):
            # Remove the opening ```yaml and closing ```
            content = content[7:-3].strip()
        elif content.startswith('```') and content.endswith('```'):
            # Remove generic code block markers
            content = content[3:-3].strip()
        
        # Attempt to parse as YAML to validate structure
        try:
            parsed = yaml.safe_load(content)
            if not isinstance(parsed, dict):
                raise ValueError("Frontmatter must be a valid YAML dictionary")
        except yaml.YAMLError as e:
            raise ValueError(f"Invalid YAML in frontmatter: {e}")
        
        # Validate required fields are present
        profile_key = f"{self.article_type}Profile"
        validation = self.schema[profile_key]["validation"]["frontmatter"]
        required_fields = validation["requiredFields"]
        
        # NOTE: All schemas require 'name' field (not 'title') in frontmatter
        # Make sure the prompt template uses 'name' and not 'title'
        missing_fields = [field for field in required_fields if field not in parsed]
        
        # Special handling for common error: using 'title' instead of 'name'
        if 'name' in missing_fields and 'title' in parsed:
            raise ValueError("Found 'title' field but 'name' is required. Please use 'name' instead of 'title' in the frontmatter.")
            
        if missing_fields:
            raise ValueError(f"Missing required frontmatter fields: {missing_fields}")
        
        # Enforce frontmatter value length limits
        # Title and headline should be concise
        if "title" in parsed and len(parsed["title"]) > 100:
            raise ValueError(f"Title too long: {len(parsed['title'])} chars, maximum should be 100 chars")
        
        if "headline" in parsed and len(parsed["headline"]) > 150:
            raise ValueError(f"Headline too long: {len(parsed['headline'])} chars, maximum should be 150 chars")
        
        # Description and summary should be reasonable length
        if "description" in parsed and len(parsed["description"]) > 250:
            raise ValueError(f"Description too long: {len(parsed['description'])} chars, maximum should be 250 chars")
        
        # Keywords should be limited in number and length
        if "keywords" in parsed and isinstance(parsed["keywords"], list):
            if len(parsed["keywords"]) > 15:
                raise ValueError(f"Too many keywords: {len(parsed['keywords'])}, maximum should be 15")
            
            for keyword in parsed["keywords"]:
                if len(keyword) > 50:
                    raise ValueError(f"Keyword too long: '{keyword}' ({len(keyword)} chars), maximum should be 50 chars")
        
        # Ensure nested properties have reasonable lengths
        for key, value in parsed.items():
            if isinstance(value, dict):
                for nested_key, nested_value in value.items():
                    if isinstance(nested_value, str) and len(nested_value) > 500:
                        raise ValueError(f"Nested value too long: {key}.{nested_key} ({len(nested_value)} chars), maximum should be 500 chars")
            elif isinstance(value, list) and all(isinstance(item, str) for item in value):
                for i, item in enumerate(value):
                    if len(item) > 250:
                        raise ValueError(f"List item too long: {key}[{i}] ({len(item)} chars), maximum should be 250 chars")
        
        return content
