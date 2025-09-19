#!/usr/bin/env python3
"""
Bullets Component Validator

Component-specific validation logic for bullets components.
"""

from typing import Any, Dict, List

from utils.validation.base_validator import BaseComponentValidator
from utils.validation import validate_placeholder_content


class BulletsValidator(BaseComponentValidator):
    """Validator for bullets components using base validation framework."""

    def __init__(self):
        super().__init__("bullets")

    def validate_format(self, content: str, format_rules: Dict[str, Any] = None) -> List[str]:
        """
        Validate bullets-specific format requirements.

        Args:
            content: The bullets content to validate
            format_rules: Optional format rules dictionary

        Returns:
            List of validation errors (empty if valid)
        """
        errors = []

        # Bullets should have bullet points starting with •
        lines = [line.strip() for line in content.split("\n") if line.strip()]
        if not lines:
            errors.append("Bullets component cannot be empty")
        else:
            for line in lines:
                if not line.startswith("•"):
                    errors.append("All bullet points must start with • character")
                    break

        return errors

    def validate_content(self, content: str) -> List[str]:
        """
        Validate bullets content requirements.

        Args:
            content: The bullets content to validate

        Returns:
            List of validation errors (empty if valid)
        """
        errors = []

        # Check for placeholder content
        errors.extend(validate_placeholder_content(content))

        # Check minimum number of bullets
        lines = [line.strip() for line in content.split("\n") if line.strip()]
        if len(lines) < 3:
            errors.append("Bullets should contain at least 3 bullet points")

        return errors

    def validate_quality(self, content: str) -> List[str]:
        """
        Validate bullets quality requirements.

        Args:
            content: The bullets content to validate

        Returns:
            List of validation warnings (empty if acceptable)
        """
        warnings = []

        lines = [line.strip() for line in content.split("\n") if line.strip()]

        # Check for consistent formatting
        if len(lines) > 0:
            avg_length = sum(len(line) for line in lines) / len(lines)
            if avg_length < 30:
                warnings.append(
                    "Bullet points may be too brief for comprehensive information"
                )
            elif avg_length > 150:
                warnings.append("Bullet points may be too verbose for effective scanning")

        return warnings


# Backward compatibility functions - delegate to class methods
def validate_bullets_format(content: str, format_rules: Dict[str, Any] = None) -> List[str]:
    """Legacy function for backward compatibility."""
    validator = BulletsValidator()
    return validator.validate_format(content, format_rules)


def validate_bullets_content(content: str) -> List[str]:
    """Legacy function for backward compatibility."""
    validator = BulletsValidator()
    return validator.validate_content(content)


def validate_bullets_quality(content: str) -> List[str]:
    """Legacy function for backward compatibility."""
    validator = BulletsValidator()
    return validator.validate_quality(content)
