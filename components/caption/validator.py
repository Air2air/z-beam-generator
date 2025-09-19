#!/usr/bin/env python3
"""
Caption Component Validator

Component-specific validation logic for caption components.
"""

from typing import Any, Dict, List

from utils.validation.base_validator import BaseComponentValidator
from utils.validation import validate_placeholder_content


class CaptionValidator(BaseComponentValidator):
    """Validator for caption components using base validation framework."""

    def __init__(self):
        super().__init__("caption")

    def validate_format(self, content: str, format_rules: Dict[str, Any] = None) -> List[str]:
        """
        Validate caption-specific format requirements.

        Args:
            content: The caption content to validate
            format_rules: Optional format rules dictionary

        Returns:
            List of validation errors (empty if valid)
        """
        errors = []

        # Caption should be two lines with bold formatting
        lines = [line.strip() for line in content.split("\n") if line.strip()]
        if len(lines) != 2:
            errors.append("Caption must have exactly 2 lines")
        else:
            for i, line in enumerate(lines):
                if not line.startswith("**") or "**" not in line[2:]:
                    errors.append(f"Line {i+1} must start with bold formatting (**text**)")

        return errors

    def validate_content(self, content: str) -> List[str]:
        """
        Validate caption content requirements.

        Args:
            content: The caption content to validate

        Returns:
            List of validation errors (empty if valid)
        """
        errors = []

        # Check for placeholder content
        errors.extend(validate_placeholder_content(content))

        # Basic content validation
        if not content.strip():
            errors.append("Caption component cannot be empty")

        return errors


# Backward compatibility functions - delegate to class methods
def validate_caption_format(content: str, format_rules: Dict[str, Any] = None) -> List[str]:
    """Legacy function for backward compatibility."""
    validator = CaptionValidator()
    return validator.validate_format(content, format_rules)


def validate_caption_content(content: str) -> List[str]:
    """Legacy function for backward compatibility."""
    validator = CaptionValidator()
    return validator.validate_content(content)
