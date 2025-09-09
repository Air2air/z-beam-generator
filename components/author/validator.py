#!/usr/bin/env python3
"""
Author Component Validator

Component-specific validation logic for author components.
"""

from typing import Any, Dict, List

from utils.validation import validate_placeholder_content


def validate_author_format(
    content: str, format_rules: Dict[str, Any] = None
) -> List[str]:
    """
    Validate author-specific format requirements.

    Args:
        content: The author content to validate
        format_rules: Optional format rules dictionary

    Returns:
        List of validation errors (empty if valid)
    """
    errors = []

    # Author should be simple text content
    if not content.strip():
        errors.append("Author component cannot be empty")

    return errors


def validate_author_content(content: str) -> List[str]:
    """
    Validate author content requirements.

    Args:
        content: The author content to validate

    Returns:
        List of validation errors (empty if valid)
    """
    errors = []

    # Check for placeholder content
    errors.extend(validate_placeholder_content(content))

    return errors


def validate_author_data(content: str) -> List[str]:
    """
    Validate author data quality.

    Args:
        content: The author content to validate

    Returns:
        List of validation warnings (empty if acceptable)
    """
    warnings = []

    # Check for proper author attribution
    if len(content.strip()) < 10:
        warnings.append("Author information may be too brief")

    # Check for professional indicators
    professional_indicators = ["Dr.", "PhD", "Professor", "Engineer", "Specialist"]
    if not any(indicator in content for indicator in professional_indicators):
        warnings.append("Consider adding professional credentials or title")

    return warnings
