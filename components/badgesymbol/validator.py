#!/usr/bin/env python3
"""
Badge Symbol Component Validator

Component-specific validation logic for badge symbol components.
"""

from typing import Any, Dict, List

from utils.validation import validate_placeholder_content


def validate_badgesymbol_format(
    content: str, format_rules: Dict[str, Any] = None
) -> List[str]:
    """
    Validate badge symbol format requirements.

    Args:
        content: The badge symbol content to validate
        format_rules: Optional format rules dictionary

    Returns:
        List of validation errors (empty if valid)
    """
    errors = []

    # Badge symbol should be simple text content
    if not content.strip():
        errors.append("Badge symbol component cannot be empty")

    return errors


def validate_badgesymbol_content(content: str) -> List[str]:
    """
    Validate badge symbol content requirements.

    Args:
        content: The badge symbol content to validate

    Returns:
        List of validation errors (empty if valid)
    """
    errors = []

    # Check for placeholder content
    errors.extend(validate_placeholder_content(content))

    return errors


def validate_badgesymbol_data(content: str) -> List[str]:
    """
    Validate badge symbol data quality.

    Args:
        content: The badge symbol content to validate

    Returns:
        List of validation warnings (empty if acceptable)
    """
    warnings = []

    # Check for reasonable symbol length
    if len(content.strip()) > 50:
        warnings.append("Badge symbol may be too long for badge display")
    elif len(content.strip()) < 2:
        warnings.append("Badge symbol may be too short to be meaningful")

    return warnings
