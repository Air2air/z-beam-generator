#!/usr/bin/env python3
"""
Table Component Validator

Component-specific validation logic for table components.
"""

from typing import Any, Dict, List


def validate_table_format(
    content: str, format_rules: Dict[str, Any] = None
) -> List[str]:
    """
    Validate table-specific format requirements.

    Args:
        content: The table content to validate
        format_rules: Optional format rules dictionary

    Returns:
        List of validation errors (empty if valid)
    """
    errors = []

    # Table should have proper markdown table format
    lines = [line.strip() for line in content.split("\n") if line.strip()]
    if not lines:
        errors.append("Table component cannot be empty")
    else:
        has_header = any("|" in line for line in lines[:2])
        has_separator = any("|-" in line or "-|" in line for line in lines[:3])
        if not has_header:
            errors.append("Table must have header row with | separators")
        if not has_separator:
            errors.append("Table must have separator row with | and - characters")

    return errors


def validate_table_structure(content: str) -> List[str]:
    """
    Validate table structure requirements.

    Args:
        content: The table content to validate

    Returns:
        List of validation errors (empty if valid)
    """
    errors = []

    # Check for placeholder content
    if "TBD" in content or "TODO" in content or "[" in content and "]" in content:
        errors.append("Contains placeholder content (TBD, TODO, or [brackets])")

    # Check for proper table headers
    lines = [line.strip() for line in content.split("\n") if line.strip()]
    if lines:
        # Look for section headers (##)
        has_section_headers = any(line.startswith("##") for line in lines)
        if not has_section_headers:
            errors.append("Tables should have descriptive section headers (##)")

    return errors


def validate_table_quality(content: str) -> List[str]:
    """
    Validate table quality requirements.

    Args:
        content: The table content to validate

    Returns:
        List of validation warnings (empty if acceptable)
    """
    warnings = []

    lines = [line.strip() for line in content.split("\n") if line.strip()]

    # Count actual table rows (lines with |)
    table_rows = [
        line for line in lines if "|" in line and not ("|-" in line or "-|" in line)
    ]
    if len(table_rows) < 4:  # Header + at least 3 data rows
        warnings.append("Tables may need more data rows for comprehensive information")

    # Check for consistent column structure
    if table_rows:
        column_counts = [line.count("|") for line in table_rows]
        if len(set(column_counts)) > 1:
            warnings.append("Inconsistent column structure detected across table rows")

    return warnings
