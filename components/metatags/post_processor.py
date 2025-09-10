"""
Metatags component post-processor for YAML frontmatter content cleanup and enhancement.
"""
import logging
import re
from typing import Dict, Any, List

import yaml

logger = logging.getLogger(__name__)


def post_process_metatags_yaml(content: str, material_name: str = "") -> str:
    """
    Post-process metatags YAML content for consistency and quality.

    Args:
        content: Generated metatags YAML content
        material_name: Name of the material being processed

    Returns:
        str: Post-processed metatags YAML content
    """
    if not content or not content.strip():
        return content

    try:
        # Parse the YAML content
        if not (content.strip().startswith('---') and content.strip().endswith('---')):
            logger.warning("Content is not properly formatted YAML frontmatter")
            return content

        # Extract YAML content between delimiters
        yaml_content = content.strip()[3:-3].strip()
        parsed_data = yaml.safe_load(yaml_content)

        if not parsed_data:
            logger.warning("Failed to parse YAML content")
            return content

        # Apply post-processing enhancements
        processed_data = _enhance_yaml_content(parsed_data, material_name)

        # Convert back to YAML string
        processed_yaml = yaml.dump(
            processed_data,
            default_flow_style=False,
            sort_keys=False,
            allow_unicode=True
        )

        return f"---\n{processed_yaml.strip()}\n---"

    except yaml.YAMLError as e:
        logger.error(f"YAML parsing error in post-processing: {e}")
        return content
    except Exception as e:
        logger.error(f"Error in YAML post-processing: {e}")
        return content


def _enhance_yaml_content(data: Dict[str, Any], material_name: str) -> Dict[str, Any]:
    """
    Enhance the parsed YAML content with additional processing.

    Args:
        data: Parsed YAML data
        material_name: Material name for context

    Returns:
        Enhanced YAML data
    """
    enhanced_data = data.copy()

    # Enhance meta tags
    if 'meta_tags' in enhanced_data and isinstance(enhanced_data['meta_tags'], list):
        enhanced_data['meta_tags'] = _enhance_meta_tags(enhanced_data['meta_tags'], material_name)

    # Enhance OpenGraph tags
    if 'opengraph' in enhanced_data and isinstance(enhanced_data['opengraph'], list):
        enhanced_data['opengraph'] = _enhance_opengraph_tags(enhanced_data['opengraph'], material_name)

    # Enhance Twitter tags
    if 'twitter' in enhanced_data and isinstance(enhanced_data['twitter'], list):
        enhanced_data['twitter'] = _enhance_twitter_tags(enhanced_data['twitter'], material_name)

    return enhanced_data


def _enhance_meta_tags(meta_tags: List[Dict[str, str]], material_name: str) -> List[Dict[str, str]]:
    """
    Enhance meta tags with additional processing.

    Args:
        meta_tags: List of meta tag dictionaries
        material_name: Material name for context

    Returns:
        Enhanced meta tags
    """
    enhanced_tags = []

    for tag in meta_tags:
        if not isinstance(tag, dict):
            enhanced_tags.append(tag)
            continue

        enhanced_tag = tag.copy()

        # Clean and enhance content
        if 'content' in enhanced_tag:
            enhanced_tag['content'] = _clean_yaml_content(enhanced_tag['content'], material_name)

        enhanced_tags.append(enhanced_tag)

    return enhanced_tags


def _enhance_opengraph_tags(og_tags: List[Dict[str, str]], material_name: str) -> List[Dict[str, str]]:
    """
    Enhance OpenGraph tags with additional processing.

    Args:
        og_tags: List of OpenGraph tag dictionaries
        material_name: Material name for context

    Returns:
        Enhanced OpenGraph tags
    """
    enhanced_tags = []

    for tag in og_tags:
        if not isinstance(tag, dict):
            enhanced_tags.append(tag)
            continue

        enhanced_tag = tag.copy()

        # Clean and enhance content
        if 'content' in enhanced_tag:
            enhanced_tag['content'] = _clean_yaml_content(enhanced_tag['content'], material_name)

        enhanced_tags.append(enhanced_tag)

    return enhanced_tags


def _enhance_twitter_tags(twitter_tags: List[Dict[str, str]], material_name: str) -> List[Dict[str, str]]:
    """
    Enhance Twitter tags with additional processing.

    Args:
        twitter_tags: List of Twitter tag dictionaries
        material_name: Material name for context

    Returns:
        Enhanced Twitter tags
    """
    enhanced_tags = []

    for tag in twitter_tags:
        if not isinstance(tag, dict):
            enhanced_tags.append(tag)
            continue

        enhanced_tag = tag.copy()

        # Clean and enhance content
        if 'content' in enhanced_tag:
            enhanced_tag['content'] = _clean_yaml_content(enhanced_tag['content'], material_name)

        enhanced_tags.append(enhanced_tag)

    return enhanced_tags


def _clean_yaml_content(content: str, material_name: str) -> str:
    """
    Clean and enhance YAML content values.

    Args:
        content: Content string to clean
        material_name: Material name for context

    Returns:
        Cleaned content string
    """
    if not content:
        return content

    # Normalize whitespace
    content = re.sub(r"\s+", " ", content.strip())

    # Material-specific enhancements
    if material_name:
        material_lower = material_name.lower()
        if material_lower in content.lower() and material_name not in content:
            content = re.sub(
                rf"\b{re.escape(material_lower)}\b",
                material_name,
                content,
                flags=re.IGNORECASE,
            )

    # Clean up technical terms for YAML context
    technical_replacements = {
        "laser cleaning": "laser cleaning",
        "surface treatment": "surface treatment",
        "industrial processing": "industrial processing",
        "contaminant removal": "contaminant removal",
    }

    for old_term, new_term in technical_replacements.items():
        content = re.sub(
            rf"\b{re.escape(old_term)}\b", new_term, content, flags=re.IGNORECASE
        )

    # Ensure proper sentence structure for descriptions
    if len(content) > 50:  # Likely a description
        if content and content[0].islower():
            content = content[0].upper() + content[1:]
        if not content.endswith("."):
            content += "."

    return content


def validate_yaml_metatags(content: str) -> List[str]:
    """
    Validate YAML metatags content structure.

    Args:
        content: YAML metatags content to validate

    Returns:
        List of validation warnings/errors
    """
    warnings = []

    try:
        if not (content.strip().startswith('---') and content.strip().endswith('---')):
            warnings.append("Content is not properly formatted YAML frontmatter")
            return warnings

        yaml_content = content.strip()[3:-3].strip()
        parsed_data = yaml.safe_load(yaml_content)

        if not parsed_data:
            warnings.append("Empty or invalid YAML content")
            return warnings

        # Check for required sections
        required_sections = ['title', 'meta_tags', 'opengraph', 'twitter']
        for section in required_sections:
            if section not in parsed_data:
                warnings.append(f"Missing required section: {section}")

        # Validate meta_tags structure
        if 'meta_tags' in parsed_data:
            meta_tags = parsed_data['meta_tags']
            if not isinstance(meta_tags, list):
                warnings.append("meta_tags must be a list")
            elif len(meta_tags) < 5:  # Reduced threshold for basic validation
                warnings.append("meta_tags should contain at least 5 entries")

        # Validate OpenGraph structure (optional for basic validation)
        if 'opengraph' in parsed_data:
            og_tags = parsed_data['opengraph']
            if not isinstance(og_tags, list):
                warnings.append("opengraph must be a list")

        # Validate Twitter structure (optional for basic validation)
        if 'twitter' in parsed_data:
            twitter_tags = parsed_data['twitter']
            if not isinstance(twitter_tags, list):
                warnings.append("twitter must be a list")

    except yaml.YAMLError as e:
        warnings.append(f"YAML syntax error: {e}")
    except Exception as e:
        warnings.append(f"Validation error: {e}")

    return warnings


def optimize_yaml_metatags(content: str) -> str:
    """
    Optimize YAML metatags for better SEO and social media performance.

    Args:
        content: YAML metatags content to optimize

    Returns:
        Optimized YAML content
    """
    try:
        if not (content.strip().startswith('---') and content.strip().endswith('---')):
            return content

        yaml_content = content.strip()[3:-3].strip()
        parsed_data = yaml.safe_load(yaml_content)

        if not parsed_data:
            return content

        # Apply optimizations
        optimized_data = _optimize_yaml_structure(parsed_data)

        # Convert back to YAML
        optimized_yaml = yaml.dump(
            optimized_data,
            default_flow_style=False,
            sort_keys=False,
            allow_unicode=True
        )

        return f"---\n{optimized_yaml.strip()}\n---"

    except Exception as e:
        logger.error(f"Error optimizing YAML metatags: {e}")
        return content


def _optimize_yaml_structure(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Optimize the structure of YAML metatags data.

    Args:
        data: Parsed YAML data

    Returns:
        Optimized YAML data
    """
    optimized_data = data.copy()

    # Ensure proper ordering of sections
    section_order = ['title', 'meta_tags', 'opengraph', 'twitter', 'canonical', 'alternate']
    ordered_data = {}

    for section in section_order:
        if section in optimized_data:
            ordered_data[section] = optimized_data[section]

    # Add any remaining sections
    for key, value in optimized_data.items():
        if key not in ordered_data:
            ordered_data[key] = value

def post_process_metatags(content: str, material_name: str = "") -> str:
    """
    Backward compatibility function for post-processing metatags content.
    Now delegates to YAML-specific processing.

    Args:
        content: Generated metatags content (YAML format)
        material_name: Name of the material being processed

    Returns:
        str: Post-processed metatags YAML content
    """
    return post_process_metatags_yaml(content, material_name)