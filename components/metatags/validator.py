#!/usr/bin/env python3
"""
Metatags Component Validator

Component-specific validation logic for metatags components.
"""

from typing import List, Dict, Any
import yaml


def validate_metatags_yaml(content: str, format_rules: Dict[str, Any] = None) -> List[str]:
    """
    Validate metatags YAML structure.
    
    Args:
        content: The metatags content to validate
        format_rules: Optional format rules dictionary
        
    Returns:
        List of validation errors (empty if valid)
    """
    errors = []
    
    try:
        yaml_end = content.find('---', 3)
        if yaml_end == -1:
            errors.append("YAML frontmatter not properly closed with '---'")
            return errors
        
        yaml_content = content[3:yaml_end].strip()
        parsed_yaml = yaml.safe_load(yaml_content)
        
        if not parsed_yaml:
            errors.append("Empty or invalid YAML frontmatter")
            return errors
        
        # Metatags-specific YAML validation
        if 'meta_tags' in parsed_yaml and not isinstance(parsed_yaml['meta_tags'], list):
            errors.append("meta_tags must be a list")
        if 'opengraph' in parsed_yaml and not isinstance(parsed_yaml['opengraph'], list):
            errors.append("opengraph must be a list")
            
    except yaml.YAMLError as e:
        errors.append(f"Invalid YAML syntax: {e}")
    except Exception as e:
        errors.append(f"Error parsing YAML: {e}")
        
    return errors


def validate_metatags_content(content: str) -> List[str]:
    """
    Validate metatags content requirements.
    
    Args:
        content: The metatags content to validate
        
    Returns:
        List of validation errors (empty if valid)
    """
    errors = []
    
    # Check for placeholder content
    if 'TBD' in content or 'TODO' in content or '[' in content and ']' in content:
        errors.append("Contains placeholder content (TBD, TODO, or [brackets])")
    
    # Check for required meta tag fields
    required_elements = ['title:', 'meta_tags:', 'description']
    missing_elements = [elem for elem in required_elements if elem not in content]
    if missing_elements:
        errors.append(f"Missing required elements: {', '.join(missing_elements)}")
    
    return errors


def validate_metatags_seo(content: str) -> List[str]:
    """
    Validate metatags SEO requirements.
    
    Args:
        content: The metatags content to validate
        
    Returns:
        List of validation warnings (empty if acceptable)
    """
    warnings = []
    
    try:
        yaml_end = content.find('---', 3)
        if yaml_end != -1:
            yaml_content = content[3:yaml_end].strip()
            parsed_yaml = yaml.safe_load(yaml_content)
            
            if parsed_yaml and 'meta_tags' in parsed_yaml:
                meta_tags = parsed_yaml['meta_tags']
                if isinstance(meta_tags, list):
                    # Check for description length
                    for tag in meta_tags:
                        if isinstance(tag, dict) and tag.get('name') == 'description':
                            desc_content = tag.get('content', '')
                            if len(desc_content) < 120:
                                warnings.append("Meta description may be too short (recommended: 150-160 characters)")
                            elif len(desc_content) > 170:
                                warnings.append("Meta description may be too long (recommended: 150-160 characters)")
                    
                    # Check for essential meta tags
                    tag_names = [tag.get('name', '') for tag in meta_tags if isinstance(tag, dict)]
                    essential_tags = ['description', 'keywords', 'author']
                    missing_tags = [tag for tag in essential_tags if tag not in tag_names]
                    if missing_tags:
                        warnings.append(f"Consider adding meta tags: {', '.join(missing_tags)}")
                        
    except Exception:
        # If parsing fails, the YAML validation will catch it
        pass
    
    return warnings
