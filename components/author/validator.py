#!/usr/bin/env python3
"""
Author Component Validator

Component-specific validation logic for author components.
"""

from typing import Any, Dict, List

from utils.validation.base_validator import BaseComponentValidator


class AuthorValidator(BaseComponentValidator):
    """Validator for author component using consolidated base class"""

    def __init__(self):
        super().__init__("author")

    def validate_format(
        self, content: str, format_rules: Dict[str, Any] = None
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

        # Author should be simple text content (no special format requirements)
        # Basic content validation is handled by base class

        return errors

    def validate_content(self, content: str) -> List[str]:
        """
        Validate author content requirements.

        Args:
            content: The author content to validate

        Returns:
            List of validation errors (empty if valid)
        """
        errors = []

        # Additional content-specific validation beyond base class
        # Check content length (authors should have reasonable length)
        errors.extend(self.validate_content_length(content, min_length=5, max_length=200))

        return errors

    def validate_author_data_quality(self, content: str) -> List[str]:
        """
        Validate author data quality (warnings, not errors).

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


# Keep legacy function interfaces for backward compatibility
def validate_author_format(
    content: str, format_rules: Dict[str, Any] = None
) -> List[str]:
    """Legacy function interface - delegates to class-based validator"""
    validator = AuthorValidator()
    return validator.validate_format(content, format_rules)


def validate_author_content(content: str) -> List[str]:
    """Legacy function interface - delegates to class-based validator"""
    validator = AuthorValidator()
    basic_errors = validator.validate_basic_content(content)
    if basic_errors:
        return basic_errors
    return validator.validate_content(content)


def validate_author_data(content: str) -> List[str]:
    """Legacy function interface - delegates to class-based validator"""
    validator = AuthorValidator()
    return validator.validate_author_data_quality(content)
