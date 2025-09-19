#!/usr/bin/env python3
"""
Frontmatter Component Validator

Component-specific validation logic for frontmatter components.
"""

import re
from typing import Any, Dict, List

import yaml

from utils.validation.base_validator import BaseComponentValidator
from utils.validation import validate_placeholder_content

duplicate_pattern = r"(\w+):\s*\n\s*\1:\s*(\{\}|$)"


class FrontmatterValidator(BaseComponentValidator):
    """Validator for frontmatter components using base validation framework."""

    def __init__(self):
        super().__init__("frontmatter")

    def validate_format(self, content: str, format_rules: Dict[str, Any] = None) -> List[str]:
        """
        Validate frontmatter format and structure.

        Args:
            content: The frontmatter content to validate
            format_rules: Optional format validation rules

        Returns:
            List of validation errors (empty if valid)
        """
        errors = []

        try:
            if re.search(duplicate_pattern, content):
                errors.append("Duplicate field names detected in YAML structure")

            yaml_end = content.find("---", 3)
            if yaml_end == -1:
                errors.append("YAML frontmatter not properly closed with '---'")
                return errors

            yaml_content = content[3:yaml_end].strip()
            parsed_yaml = yaml.safe_load(yaml_content)

            if not parsed_yaml:
                errors.append("Empty or invalid YAML frontmatter")
                return errors

            # Check required fields
            required_fields = (
                format_rules.get("required_fields", []) if format_rules else []
            )
            for field in required_fields:
                if field not in parsed_yaml:
                    errors.append(f"Missing required field: {field}")

        except yaml.YAMLError as e:
            errors.append(f"Invalid YAML syntax: {e}")
        except Exception as e:
            errors.append(f"Error parsing YAML: {e}")

        return errors

    def validate_content(self, content: str) -> List[str]:
        """
        Validate frontmatter content requirements.

        Args:
            content: The frontmatter content to validate

        Returns:
            List of validation errors (empty if valid)
        """
        errors = []

        # Basic structure check
        if "name:" not in content or "---" not in content:
            errors.append("Missing required frontmatter fields")

        # Check for placeholder content
        errors.extend(validate_placeholder_content(content))

        return errors

    def validate_properties(self, content: str) -> List[str]:
        """
        Validate frontmatter properties structure.

        Args:
            content: The frontmatter content to validate

        Returns:
            List of validation warnings (empty if acceptable)
        """
        warnings = []

        try:
            yaml_end = content.find("---", 3)
            if yaml_end != -1:
                yaml_content = content[3:yaml_end].strip()
                parsed_yaml = yaml.safe_load(yaml_content)

                if parsed_yaml:
                    # Check for essential property sections
                    essential_sections = ["properties", "chemicalProperties", "category"]
                    missing_sections = [
                        section
                        for section in essential_sections
                        if section not in parsed_yaml
                    ]
                    if missing_sections:
                        warnings.append(
                            f"Consider adding sections: {', '.join(missing_sections)}"
                        )

                    # Check properties completeness
                    if "properties" in parsed_yaml and isinstance(
                        parsed_yaml["properties"], dict
                    ):
                        props = parsed_yaml["properties"]
                        essential_props = ["density", "meltingPoint", "thermalConductivity"]
                        missing_props = [
                            prop for prop in essential_props if prop not in props
                        ]
                        if missing_props:
                            warnings.append(
                                f"Consider adding properties: {', '.join(missing_props)}"
                            )

        except Exception:
            # If parsing fails, the YAML validation will catch it
            pass

        return warnings


# Backward compatibility functions - delegate to class methods
def validate_frontmatter_format(content: str, format_rules: Dict[str, Any] = None) -> List[str]:
    """Legacy function for backward compatibility."""
    validator = FrontmatterValidator()
    return validator.validate_format(content, format_rules)


def validate_frontmatter_content(content: str) -> List[str]:
    """Legacy function for backward compatibility."""
    validator = FrontmatterValidator()
    return validator.validate_content(content)


def validate_frontmatter_properties(content: str) -> List[str]:
    """Legacy function for backward compatibility."""
    validator = FrontmatterValidator()
    return validator.validate_properties(content)
