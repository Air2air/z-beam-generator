#!/usr/bin/env python3
"""
Placeholder Content Validation Utility

Consolidated validation logic for detecting placeholder content across all components.
This eliminates code duplication and centralizes placeholder validation.
"""

from typing import List


def validate_placeholder_content(content: str, extended_check: bool = False) -> List[str]:
    """
    Validate content for placeholder text (TBD, TODO, brackets).

    This function consolidates the placeholder validation logic that was
    previously duplicated across multiple component validators.

    Args:
        content: The content string to validate
        extended_check: If True, includes additional placeholder patterns

    Returns:
        List of validation error messages (empty if no placeholders found)
    """
    errors = []

    # Basic placeholder patterns
    basic_placeholders = ["TBD", "TODO"]
    found_basic = [p for p in basic_placeholders if p in content]

    # Check for brackets
    has_brackets = "[" in content and "]" in content

    if found_basic or has_brackets:
        if extended_check:
            # Extended patterns for more comprehensive checking
            extended_placeholders = [
                "[INSERT", "[PLACEHOLDER", "XXXX", "..."
            ]
            found_extended = [p for p in extended_placeholders if p in content.upper()]

            all_found = found_basic + found_extended
            if has_brackets:
                all_found.append("brackets")

            if all_found:
                errors.append(f"Contains placeholder content: {', '.join(all_found)}")
        else:
            # Basic check for backward compatibility
            placeholder_list = found_basic[:]
            if has_brackets:
                placeholder_list.append("brackets")

            if placeholder_list:
                errors.append("Contains placeholder content (TBD, TODO, or [brackets])")

    return errors


def has_placeholder_content(content: str) -> bool:
    """
    Check if content contains any placeholder text.

    Args:
        content: The content string to check

    Returns:
        True if placeholder content is found, False otherwise
    """
    return bool("TBD" in content or "TODO" in content or ("[" in content and "]" in content))
