#!/usr/bin/env python3
"""
Frontmatter Component Validator

Component-specific validation logic for frontmatter components.
"""

from typing import List, Dict, Any
import yaml


def validate_frontmatter_yaml(content: str, format_rules: Dict[str, Any]) -> List[str]:
    """
    Validate frontmatter YAML structure.
    
    Args:
        content: The frontmatter content to validate
        format_rules: Format rules dictionary (required)
        
    Returns:
        List of validation errors (empty if valid)
    """
    errors = []
    
    try:
        # Check for multiple opening delimiters
        if content.startswith('---\n---'):
            errors.append("Multiple opening YAML delimiters detected (---)")
        
        # Check for empty object placeholders
        if ': {}' in content:
            errors.append("Empty object placeholders ({}) found in YAML")
        
        yaml_end = content.find('---', 3)
        if yaml_end == -1:
            errors.append("YAML frontmatter not properly closed with '---'")
            return errors
        
        yaml_content = content[3:yaml_end].strip()
        parsed_yaml = yaml.safe_load(yaml_content)
        
        if not parsed_yaml:
            errors.append("Empty or invalid YAML frontmatter")
            return errors
        
        # Check required fields
        required_fields = format_rules['required_fields']  # Must exist, no fallback
        for field in required_fields:
            if field not in parsed_yaml:
                errors.append(f"Missing required field: {field}")
                
    except yaml.YAMLError as e:
        errors.append(f"Invalid YAML syntax: {e}")
    except Exception as e:
        errors.append(f"Error parsing YAML: {e}")
        
    return errors


def validate_frontmatter_content(content: str, format_rules: Dict[str, Any]) -> List[str]:
    """
    Validate frontmatter content quality.
    
    Args:
        content: The frontmatter content to validate
        format_rules: Format rules dictionary (required)
        
    Returns:
        List of validation errors (empty if valid)
    """
    errors = []
    
    # Basic structure check
    if 'name:' not in content or '---' not in content:
        errors.append("Missing required frontmatter fields")
    
    # Check for placeholder content
    if 'TBD' in content or 'TODO' in content or '[' in content and ']' in content:
        errors.append("Contains placeholder content (TBD, TODO, or [brackets])")
    
    return errors


def validate_frontmatter_properties(content: str) -> List[str]:
    """
    Validate frontmatter properties structure.
    
    Args:
        content: The frontmatter content to validate
        
    Returns:
        List of validation warnings (empty if acceptable)
    """
    warnings = []
    
    try:
        yaml_end = content.find('---', 3)
        if yaml_end != -1:
            yaml_content = content[3:yaml_end].strip()
            parsed_yaml = yaml.safe_load(yaml_content)
            
            if parsed_yaml:
                # Check for essential property sections
                essential_sections = ['properties', 'chemicalProperties', 'category']
                missing_sections = [section for section in essential_sections if section not in parsed_yaml]
                if missing_sections:
                    warnings.append(f"Consider adding sections: {', '.join(missing_sections)}")
                
                # Check properties completeness
                if 'properties' in parsed_yaml and isinstance(parsed_yaml['properties'], dict):
                    props = parsed_yaml['properties']
                    essential_props = ['density', 'meltingPoint', 'thermalConductivity']
                    missing_props = [prop for prop in essential_props if prop not in props]
                    if missing_props:
                        warnings.append(f"Consider adding properties: {', '.join(missing_props)}")
                        
    except Exception:
        # If parsing fails, the YAML validation will catch it
        pass
    
    return warnings
