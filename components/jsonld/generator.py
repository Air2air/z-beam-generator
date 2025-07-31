"""
JSON-LD generator for Z-Beam Generator.

Strict fail-fast implementation with no fallbacks or defaults.
"""

import logging
import json
import re
from typing import Dict, Any
from components.base.component import BaseComponent

logger = logging.getLogger(__name__)

class JsonldGenerator(BaseComponent):
    """Generator for JSON-LD structured data with fail-fast validation."""
    
    def generate(self) -> str:
        """Generate JSON-LD content with strict validation.
        
        Returns:
            str: The generated JSON-LD
            
        Raises:
            ValueError: If required data is missing or invalid
        """
        # Strict validation - no fallbacks
        data = self._prepare_data()
        prompt = self._format_prompt(data)
        content = self._call_api(prompt)
        return self._post_process(content)
    
    def _prepare_data(self) -> Dict[str, Any]:
        """Prepare data for JSON-LD generation with strict validation.
        
        Returns:
            Dict[str, Any]: Validated data for prompt formatting
            
        Raises:
            ValueError: If frontmatter is missing or invalid
        """
        data = super()._prepare_data()
        
        # Frontmatter is required - no defaults
        frontmatter = self.get_frontmatter_data()
        if not frontmatter:
            raise ValueError("Frontmatter data is required for JSON-LD generation")
        
        # Required fields validation
        required_fields = ["name", "description"]
        for field in required_fields:
            if field not in frontmatter or not frontmatter[field]:
                raise ValueError(f"Required frontmatter field '{field}' is missing or empty")
        
        # Add validated frontmatter data
        data.update({
            "frontmatter_data": frontmatter,
            "available_keys": list(frontmatter.keys()),
            "schema_type": self._get_schema_type(),
        })
        
        return data
    
    def _get_schema_type(self) -> str:
        """Get schema type based on article type - strict mapping.
        
        Returns:
            str: Schema.org type
            
        Raises:
            ValueError: If article type is not supported
        """
        type_mapping = {
            "material": "Product",
            "application": "TechArticle", 
            "region": "Place",
            "thesaurus": "DefinedTerm"
        }
        
        if self.article_type not in type_mapping:
            raise ValueError(f"Unsupported article type: {self.article_type}")
        
        return type_mapping[self.article_type]
    
    def _post_process(self, content: str) -> str:
        """Extract and validate JSON-LD from API response.
        
        Args:
            content: The API response content
            
        Returns:
            str: Formatted JSON-LD script tag
            
        Raises:
            ValueError: If valid JSON-LD cannot be extracted
        """
        jsonld = self._extract_jsonld(content)
        if not jsonld:
            raise ValueError("Failed to extract valid JSON-LD from API response")
        
        self._validate_jsonld(jsonld)
        return self._format_jsonld(jsonld)
    
    def _extract_jsonld(self, content: str) -> Dict[str, Any]:
        """Extract JSON-LD from content with strict validation.
        
        Args:
            content: Content containing JSON-LD
            
        Returns:
            Dict[str, Any]: Extracted JSON-LD data
            
        Raises:
            ValueError: If JSON-LD cannot be extracted or parsed
        """
        # Try extracting from code blocks first
        json_str = self._extract_json_from_code_blocks(content)
        if json_str:
            try:
                return json.loads(json_str)
            except json.JSONDecodeError as e:
                logger.debug(f"Invalid JSON in code blocks: {e}")
        
        # Try script tag extraction
        script_pattern = r'<script[^>]*type=["\']application/ld\+json["\'][^>]*>\s*(.*?)\s*</script>'
        match = re.search(script_pattern, content, re.DOTALL)
        if match:
            try:
                return json.loads(match.group(1).strip())
            except json.JSONDecodeError as e:
                logger.debug(f"Invalid JSON in script tag: {e}")
        
        # Try JSON object with @context
        json_pattern = r'(\{\s*"@context"[^}]*(?:\{[^}]*\}[^}]*)*\})'
        match = re.search(json_pattern, content, re.DOTALL)
        if match:
            try:
                return json.loads(match.group(1).strip())
            except json.JSONDecodeError as e:
                logger.debug(f"Invalid JSON object: {e}")
        
        raise ValueError("No valid JSON-LD found in API response")
    
    def _validate_jsonld(self, jsonld: Dict[str, Any]) -> None:
        """Validate JSON-LD structure.
        
        Args:
            jsonld: JSON-LD data to validate
            
        Raises:
            ValueError: If JSON-LD structure is invalid
        """
        required_fields = ["@context", "@type"]
        for field in required_fields:
            if field not in jsonld:
                raise ValueError(f"Required JSON-LD field '{field}' is missing")
        
        if not isinstance(jsonld["@context"], str) or not jsonld["@context"]:
            raise ValueError("@context must be a non-empty string")
        
        if not isinstance(jsonld["@type"], str) or not jsonld["@type"]:
            raise ValueError("@type must be a non-empty string")
    
    def _format_jsonld(self, jsonld: Dict[str, Any]) -> str:
        """Format JSON-LD as script tag with strict validation.
        
        Args:
            jsonld: Valid JSON-LD data
            
        Returns:
            str: Formatted JSON-LD script tag
            
        Raises:
            ValueError: If JSON-LD cannot be serialized
        """
        try:
            json_str = json.dumps(jsonld, indent=2, ensure_ascii=False)
            return f'<script type="application/ld+json">\n{json_str}\n</script>'
        except (TypeError, ValueError) as e:
            raise ValueError(f"Failed to serialize JSON-LD: {e}")
