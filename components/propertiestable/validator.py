#!/usr/bin/env python3
"""
Properties Table Component Validator

Component-specific validation logic for properties table components.
"""

from typing import Any, Dict, List


def validate_propertiestable_format(
    content: str, format_rules: Dict[str, Any] = None
) -> List[str]:
    """
    Validate properties table format requirements.

    Args:
        content: The properties table content to validate
        format_rules: Optional format rules dictionary

    Returns:
        List of validation errors (empty if valid)
    """
    errors = []

    # Properties table should have proper table format
    if "| Property |" not in content:
        errors.append("Not a valid properties table - missing '| Property |' header")

    # Check for proper table structure
    lines = [line.strip() for line in content.split("\n") if line.strip()]
    if lines:
        table_lines = [line for line in lines if "|" in line]
        if len(table_lines) < 3:  # Header + separator + at least one data row
            errors.append(
                "Properties table should have header, separator, and data rows"
            )

    return errors


def validate_propertiestable_content(content: str) -> List[str]:
    """
    Validate properties table content requirements.

    Args:
        content: The properties table content to validate

    Returns:
        List of validation errors (empty if valid)
    """
    errors = []

    # Check for placeholder content
    if "TBD" in content or "TODO" in content or "[" in content and "]" in content:
        errors.append("Contains placeholder content (TBD, TODO, or [brackets])")

    # Basic content validation
    if not content.strip():
        errors.append("Properties table component cannot be empty")

    # Check for essential properties
    essential_properties = ["Formula", "Symbol", "Category", "Density"]
    missing_properties = []
    for prop in essential_properties:
        if f"| {prop} |" not in content:
            missing_properties.append(prop)

    if missing_properties:
        errors.append(f"Missing essential properties: {', '.join(missing_properties)}")

    return errors


def validate_propertiestable_data(content: str) -> List[str]:
    """
    Validate properties table data quality.

    Args:
        content: The properties table content to validate

    Returns:
        List of validation warnings (empty if acceptable)
    """
    warnings = []

    lines = [line.strip() for line in content.split("\n") if line.strip()]
    table_lines = [
        line for line in lines if "|" in line and not ("|-" in line or "-|" in line)
    ]

    # Check for data completeness
    if table_lines:
        # Skip header row, check data rows
        data_rows = table_lines[1:] if len(table_lines) > 1 else []
        for row in data_rows:
            cells = [cell.strip() for cell in row.split("|") if cell.strip()]
            if len(cells) >= 2:  # Property | Value
                value = cells[1] if len(cells) > 1 else ""
                if value in ["N/A", "TBD", "", "Unknown"]:
                    warnings.append(
                        "Consider providing specific data instead of placeholder values"
                    )
                    break

    # Check for appropriate number of properties
    data_row_count = len(
        [line for line in table_lines if "|" in line and not line.startswith("|--")]
    )
    if data_row_count < 4:  # Less than 4 total rows (including header)
        warnings.append(
            "Consider adding more material properties for comprehensive coverage"
        )

    return warnings
