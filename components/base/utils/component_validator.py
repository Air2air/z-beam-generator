"""
Unified validation utilities for Z-Beam Generator components.

Consolidates all validation logic previously scattered across multiple modules
into a single, comprehensive validation system.
"""

import logging
import yaml
import json
import re
from typing import Dict, Any, List, Optional, Union

logger = logging.getLogger(__name__)


class ComponentValidator:
    """Unified validator for all component content and structure validation."""
    
    @staticmethod
    def validate_content(content: str, rules: Dict[str, Any]) -> str:
        """Validate content against comprehensive rules.
        
        Args:
            content: Content to validate
            rules: Validation rules dictionary containing:
                - min_length: Minimum character length
                - max_length: Maximum character length  
                - min_words: Minimum word count
                - max_words: Maximum word count
                - required_format: Expected format (yaml, json, text)
                - allow_empty: Whether empty content is allowed
                
        Returns:
            str: Validated and cleaned content
            
        Raises:
            ValueError: If validation fails
        """
        # Check for empty content
        if not content or not content.strip():
            if not rules.get('allow_empty', False):
                raise ValueError("Content cannot be empty")
            return content.strip() if content else ""
        
        content = content.strip()
        
        # Validate length
        if 'min_length' in rules and len(content) < rules['min_length']:
            raise ValueError(f"Content too short: {len(content)} chars, minimum required: {rules['min_length']}")
        
        if 'max_length' in rules and len(content) > rules['max_length']:
            raise ValueError(f"Content too long: {len(content)} chars, maximum allowed: {rules['max_length']}")
        
        # Validate word count
        words = content.split()
        if 'min_words' in rules and len(words) < rules['min_words']:
            raise ValueError(f"Content too short: {len(words)} words, minimum required: {rules['min_words']}")
        
        if 'max_words' in rules and len(words) > rules['max_words']:
            raise ValueError(f"Content too long: {len(words)} words, maximum allowed: {rules['max_words']}")
        
        # Validate format
        if 'required_format' in rules:
            format_type = rules['required_format']
            if format_type == 'yaml':
                ComponentValidator._validate_yaml_format(content)
            elif format_type == 'json':
                ComponentValidator._validate_json_format(content)
        
        return content
    
    @staticmethod
    def validate_structure(data: Dict[str, Any], schema: Dict[str, Any]) -> Dict[str, Any]:
        """Validate data structure against schema requirements.
        
        Args:
            data: Data dictionary to validate
            schema: Schema containing validation rules:
                - required_fields: List of required field names
                - field_types: Dict mapping field names to expected types
                - nested_validation: Dict of nested field validation rules
                
        Returns:
            Dict: Validated data structure
            
        Raises:
            ValueError: If structure validation fails
        """
        if not isinstance(data, dict):
            raise ValueError("Data must be a dictionary")
        
        # Check required fields
        if 'required_fields' in schema:
            missing_fields = [field for field in schema['required_fields'] if field not in data]
            if missing_fields:
                raise ValueError(f"Missing required fields: {missing_fields}")
        
        # Check field types
        if 'field_types' in schema:
            for field, expected_type in schema['field_types'].items():
                if field in data:
                    value = data[field]
                    if expected_type == 'string' and not isinstance(value, str):
                        raise ValueError(f"Field '{field}' must be a string, got {type(value).__name__}")
                    elif expected_type == 'list' and not isinstance(value, list):
                        raise ValueError(f"Field '{field}' must be a list, got {type(value).__name__}")
                    elif expected_type == 'dict' and not isinstance(value, dict):
                        raise ValueError(f"Field '{field}' must be a dictionary, got {type(value).__name__}")
        
        # Nested validation
        if 'nested_validation' in schema:
            for field, nested_schema in schema['nested_validation'].items():
                if field in data and isinstance(data[field], dict):
                    data[field] = ComponentValidator.validate_structure(data[field], nested_schema)
        
        return data
    
    @staticmethod
    def validate_consistency(content: str, metadata: Dict[str, Any]) -> bool:
        """Validate consistency between content and metadata.
        
        Args:
            content: Content to validate
            metadata: Metadata containing expected values:
                - category: Expected category
                - article_type: Expected article type
                - subject: Expected subject
                
        Returns:
            bool: True if consistent
            
        Raises:
            ValueError: If inconsistencies are detected
        """
        # Extract frontmatter if present
        frontmatter_pattern = r'---\s+(.*?)\s+---'
        frontmatter_match = re.search(frontmatter_pattern, content, re.DOTALL)
        
        if not frontmatter_match:
            # For non-frontmatter content, just check for basic consistency
            content_lower = content.lower()
            if 'subject' in metadata:
                subject_lower = metadata['subject'].lower()
                if subject_lower not in content_lower:
                    logger.warning(f"Subject '{metadata['subject']}' not found in content")
            return True
        
        frontmatter_text = frontmatter_match.group(1)
        
        try:
            frontmatter = yaml.safe_load(frontmatter_text)
        except yaml.YAMLError as e:
            raise ValueError(f"Invalid YAML in frontmatter: {e}")
        
        # Check consistency
        if 'category' in metadata and 'category' in frontmatter:
            if frontmatter['category'].lower() != metadata['category'].lower():
                raise ValueError(f"Category mismatch: '{frontmatter['category']}' in frontmatter vs '{metadata['category']}' expected")
        
        if 'article_type' in metadata and 'article_type' in frontmatter:
            if frontmatter['article_type'].lower() != metadata['article_type'].lower():
                raise ValueError(f"Article type mismatch: '{frontmatter['article_type']}' in frontmatter vs '{metadata['article_type']}' expected")
        
        if 'subject' in metadata and 'subject' in frontmatter:
            if frontmatter['subject'].lower() != metadata['subject'].lower():
                raise ValueError(f"Subject mismatch: '{frontmatter['subject']}' in frontmatter vs '{metadata['subject']}' expected")
        
        return True
    
    @staticmethod
    def _validate_yaml_format(content: str) -> None:
        """Validate YAML format."""
        try:
            parsed = yaml.safe_load(content)
            if parsed is None:
                raise ValueError("YAML content is empty")
        except yaml.YAMLError as e:
            raise ValueError(f"Invalid YAML format: {e}")
    
    @staticmethod
    def _validate_json_format(content: str) -> None:
        """Validate JSON format."""
        try:
            parsed = json.loads(content)
            if parsed is None:
                raise ValueError("JSON content is empty")
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON format: {e}")
    
    @staticmethod
    def validate_line_count(lines: List[str], min_count: int, 
                           max_count: Optional[int] = None, 
                           error_prefix: str = "Generated") -> List[str]:
        """Validate that the number of lines meets requirements.
        
        Args:
            lines: List of content lines
            min_count: Minimum required line count
            max_count: Maximum allowed line count (optional)
            error_prefix: Prefix for error message
            
        Returns:
            List[str]: Original or truncated lines
            
        Raises:
            ValueError: If line count is below minimum
        """
        if len(lines) < min_count:
            raise ValueError(f"{error_prefix} {len(lines)} lines, minimum required: {min_count}")
        
        if max_count and len(lines) > max_count:
            # Truncate to max count
            return lines[:max_count]
            
        return lines
    
    @staticmethod
    def validate_frontmatter_structure(data: Dict[str, Any], component_name: str = "frontmatter") -> Dict[str, Any]:
        """Validate frontmatter-specific structure."""
        required_fields = ['name', 'title', 'headline', 'description']
        
        # Check required fields
        missing_fields = [field for field in required_fields if field not in data]
        if missing_fields:
            raise ValueError(f"Frontmatter missing required fields: {missing_fields}")
        
        # Validate nested structures
        if 'images' in data and not isinstance(data['images'], dict):
            raise ValueError("Images must be a dictionary")
        
        if 'openGraph' in data and not isinstance(data['openGraph'], dict):
            raise ValueError("openGraph must be a dictionary")
        
        return data
    
    @staticmethod
    def validate_jsonld_structure(data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate JSON-LD specific structure."""
        required_fields = ['@context', '@type', 'name']
        
        # Check required fields
        missing_fields = [field for field in required_fields if field not in data]
        if missing_fields:
            raise ValueError(f"JSON-LD missing required fields: {missing_fields}")
        
        # Validate context
        if '@context' in data:
            context = data['@context']
            if not (isinstance(context, str) or isinstance(context, list) or isinstance(context, dict)):
                raise ValueError("@context must be a string, list, or dictionary")
        
        return data
    
    @staticmethod
    def validate_metatags_structure(data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate metatags specific structure."""
        required_fields = ['meta_title', 'meta_description']
        
        # Check required fields
        missing_fields = [field for field in required_fields if field not in data]
        if missing_fields:
            raise ValueError(f"Metatags missing required fields: {missing_fields}")
        
        # Validate nested structures
        if 'openGraph' in data and not isinstance(data['openGraph'], dict):
            raise ValueError("openGraph must be a dictionary")
        
        if 'twitter' in data and not isinstance(data['twitter'], dict):
            raise ValueError("twitter must be a dictionary")
        
        return data
    
    @staticmethod
    def get_component_validation_rules(component_name: str) -> Dict[str, Any]:
        """Get validation rules for specific components.
        
        Args:
            component_name: Name of the component
            
        Returns:
            Dict: Validation rules for the component
        """
        rules = {
            'frontmatter': {
                'required_format': 'yaml',
                'min_length': 100,
                'required_fields': ['name', 'title', 'headline', 'description'],
                'validator': ComponentValidator.validate_frontmatter_structure
            },
            'jsonld': {
                'required_format': 'yaml',  # YAML representation of JSON-LD
                'min_length': 50,
                'required_fields': ['@context', '@type', 'name'],
                'validator': ComponentValidator.validate_jsonld_structure
            },
            'metatags': {
                'required_format': 'yaml',
                'min_length': 50,
                'required_fields': ['meta_title', 'meta_description'],
                'validator': ComponentValidator.validate_metatags_structure
            },
            'caption': {
                'required_format': 'text',
                'min_length': 20,
                'max_length': 500,
                'min_words': 5,
                'max_words': 100
            },
            'content': {
                'required_format': 'text',
                'min_length': 100,
                'min_words': 50
            },
            'bullets': {
                'required_format': 'text',
                'min_length': 50,
                'min_words': 10
            },
            'table': {
                'required_format': 'text',
                'min_length': 50
            },
            'tags': {
                'required_format': 'text',
                'min_length': 10,
                'min_words': 2
            },
            'propertiestable': {
                'required_format': 'text',
                'min_length': 50
            }
        }
        
        return rules.get(component_name, {
            'required_format': 'text',
            'min_length': 10
        })
