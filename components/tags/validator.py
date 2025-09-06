#!/usr/bin/env python3
"""
Tags Component Validator

Component-specific validation logic for tags components.
"""

import re
from typing import Any, Dict, List


def validate_tags_format(
    content: str, format_rules: Dict[str, Any] = None
) -> List[str]:
    """
    Validate tags-specific format requirements.

    Args:
        content: The tags content to validate
        format_rules: Optional format rules dictionary

    Returns:
        List of validation errors (empty if valid)
    """
    errors = []

    # Tags should be comma-separated
    if not content.strip():
        errors.append("Tags component cannot be empty")
        return errors

    # Basic format validation
    content = content.strip()

    # Check for proper comma separation
    if "," not in content and len(content.split()) > 1:
        errors.append("Multiple tags must be separated by commas")

    # Check tag format
    tags = [tag.strip() for tag in content.split(",")]
    for tag in tags:
        if not tag:
            errors.append("Empty tags are not allowed")
            continue

        # Tags should be lowercase with hyphens
        if not re.match(r"^[a-z0-9-]+$", tag):
            errors.append(f"Tag '{tag}' should be lowercase with hyphens only")

        # Tags should not be too short or too long
        if len(tag) < 3:
            errors.append(f"Tag '{tag}' is too short (minimum 3 characters)")
        elif len(tag) > 30:
            errors.append(f"Tag '{tag}' is too long (maximum 30 characters)")

    return errors


def validate_tags_content(content: str) -> List[str]:
    """
    Validate tags content requirements.

    Args:
        content: The tags content to validate

    Returns:
        List of validation errors (empty if valid)
    """
    errors = []

    # Check for placeholder content
    if "TBD" in content or "TODO" in content or "[" in content and "]" in content:
        errors.append("Contains placeholder content (TBD, TODO, or [brackets])")

    # Parse tags
    tags = [tag.strip() for tag in content.split(",") if tag.strip()]

    # Check minimum and maximum number of tags
    if len(tags) < 3:
        errors.append(f"Too few tags ({len(tags)}, minimum 3)")
    elif len(tags) > 15:
        errors.append(f"Too many tags ({len(tags)}, maximum 15)")

    # Check for duplicate tags
    if len(tags) != len(set(tags)):
        duplicates = [tag for tag in set(tags) if tags.count(tag) > 1]
        errors.append(f"Duplicate tags found: {', '.join(duplicates)}")

    # Check for required tag categories
    required_categories = ["laser-cleaning", "material"]
    found_categories = 0
    for category in required_categories:
        if any(category in tag for tag in tags):
            found_categories += 1

    if found_categories < 1:
        errors.append(
            "Tags should include at least one of: laser-cleaning, material-related"
        )

    return errors


def validate_tags_quality(content: str) -> List[str]:
    """
    Validate tags quality requirements.

    Args:
        content: The tags content to validate

    Returns:
        List of validation warnings (empty if acceptable)
    """
    warnings = []

    tags = [tag.strip() for tag in content.split(",") if tag.strip()]

    # Check for good tag variety
    technical_tags = sum(
        1
        for tag in tags
        if any(
            word in tag
            for word in ["laser", "industrial", "surface", "precision", "cleaning"]
        )
    )
    application_tags = sum(
        1
        for tag in tags
        if any(
            word in tag
            for word in ["automotive", "aerospace", "manufacturing", "medical"]
        )
    )

    if technical_tags == 0:
        warnings.append("Consider adding technical/process tags")
    if application_tags == 0:
        warnings.append("Consider adding application/industry tags")

    # Check for overly generic tags
    generic_tags = ["material", "process", "technology", "equipment"]
    found_generic = [tag for tag in tags if tag in generic_tags]
    if len(found_generic) > 2:
        warnings.append(f"Consider replacing generic tags: {', '.join(found_generic)}")

    return warnings
