#!/usr/bin/env python3
"""
Table Component Validator

Validates deterministic table generation with fail-fast requirements.
Ensures exact format matching example_table.md with no variations.
"""

from typing import Dict, List


def validate_table_format(
    content: str, format_rules: Dict[str, any] = None
) -> List[str]:
    """
    Validate deterministic table format requirements - FAIL-FAST: Must match exact structure.

    Args:
        content: The table content to validate
        format_rules: Optional format rules dictionary

    Returns:
        List of validation errors (empty if valid)
    """
    errors = []

    # Table cannot be empty - FAIL-FAST
    if not content or not content.strip():
        errors.append("Table component cannot be empty - fail-fast architecture requires complete content")
        return errors

    lines = [line.strip() for line in content.split("\n") if line.strip()]

    # Must have exact 6 tables - FAIL-FAST
    section_headers = [line for line in lines if line.startswith("##")]
    if len(section_headers) != 6:
        errors.append(f"Must have exactly 6 table sections, found {len(section_headers)} - fail-fast requires exact structure")

    # Must have exact section headers in correct order - FAIL-FAST
    required_headers = [
        "## Material Properties",
        "## Material Grades and Purity",
        "## Performance Metrics",
        "## Standards and Compliance",
        "## Environmental Data",
        "## Laser Cleaning Parameters"
    ]

    for i, required_header in enumerate(required_headers):
        if i >= len(section_headers) or section_headers[i] != required_header:
            errors.append(f"Missing or incorrect section header at position {i+1}: expected '{required_header}' - fail-fast requires exact order")

    # Validate each table has proper markdown structure - FAIL-FAST
    table_sections = []
    current_section = []
    for line in lines:
        if line.startswith("##"):
            if current_section:
                table_sections.append(current_section)
            current_section = [line]
        else:
            current_section.append(line)
    if current_section:
        table_sections.append(current_section)

    for i, section in enumerate(table_sections):
        if len(section) < 3:  # Header + separator + at least 1 data row
            errors.append(f"Table section {i+1} incomplete - fail-fast requires minimum table structure")

        # Check markdown table structure
        table_lines = [line for line in section if "|" in line]
        if len(table_lines) < 2:
            errors.append(f"Table section {i+1} missing proper markdown structure - fail-fast requires | separators")

        # Check for separator row
        has_separator = any("---" in line for line in table_lines)
        if not has_separator:
            errors.append(f"Table section {i+1} missing separator row (---) - fail-fast requires proper markdown format")

    return errors


def validate_table_structure(content: str) -> List[str]:
    """
    Validate deterministic table structure - FAIL-FAST: Must match exact row counts.

    Args:
        content: The table content to validate

    Returns:
        List of validation errors (empty if valid)
    """
    errors = []

    lines = [line.strip() for line in content.split("\n") if line.strip()]

    # Count total table rows (excluding headers and separators)
    table_data_lines = [
        line for line in lines
        if "|" in line and not line.startswith("##") and "---" not in line
    ]

    # Must have exactly 24 data rows (6 tables × 4 rows each) - FAIL-FAST
    if len(table_data_lines) != 24:
        errors.append(f"Must have exactly 24 data rows, found {len(table_data_lines)} - fail-fast requires exact row count")

    # Validate each table has exactly 4 data rows
    sections = []
    current_section = []
    for line in lines:
        if line.startswith("##"):
            if current_section:
                sections.append(current_section)
            current_section = []
        current_section.append(line)
    if current_section:
        sections.append(current_section)

    for i, section in enumerate(sections):
        data_rows = [
            line for line in section
            if "|" in line and not line.startswith("##") and "---" not in line
        ]
        if len(data_rows) != 4:
            errors.append(f"Table section {i+1} must have exactly 4 data rows, found {len(data_rows)} - fail-fast requires exact structure")

    return errors


def validate_table_quality(content: str) -> List[str]:
    """
    Validate table quality for deterministic generation - FAIL-FAST: No placeholders allowed.

    Args:
        content: The table content to validate

    Returns:
        List of validation warnings (empty if acceptable)
    """
    warnings = []

    # Check for placeholder content - FAIL-FAST: Not allowed
    placeholder_patterns = [
        "placeholder", "example", "sample", "test", "mock",
        "TODO", "FIXME", "TBD", "N/A", "unknown"
    ]

    content_lower = content.lower()
    for pattern in placeholder_patterns:
        if pattern in content_lower:
            warnings.append(f"Placeholder content detected: '{pattern}' - fail-fast architecture should not contain placeholders")

    # Check for consistent column structure (should be exactly 3 columns)
    lines = [line.strip() for line in content.split("\n") if line.strip()]
    table_lines = [line for line in lines if "|" in line and "---" not in line and not line.startswith("##")]

    for line in table_lines:
        column_count = line.count("|")
        if column_count != 5:  # | col1 | col2 | col3 | = 5 separators
            warnings.append(f"Inconsistent column structure: expected 3 columns, found {column_count-1} - should be | Property | Value | Unit |")

    # Check for technical content quality
    if not any(char.isdigit() for char in content):
        warnings.append("Table should contain numerical values for technical specifications")

    if not any(unit in content for unit in ["°C", "MPa", "W/m·K", "g/cm³"]):
        warnings.append("Table should contain appropriate technical units")

    return warnings


def validate_material_specific_content(content: str, material_name: str) -> List[str]:
    """
    Validate material-specific content is present and accurate - FAIL-FAST: Must be material-specific.

    Args:
        content: The table content to validate
        material_name: The material name for validation

    Returns:
        List of validation errors (empty if valid)
    """
    errors = []
    content_lower = content.lower()
    material_lower = material_name.lower()

    # Material name should appear in content - FAIL-FAST
    if material_lower not in content_lower:
        errors.append(f"Material name '{material_name}' not found in table content - fail-fast requires material-specific content")

    # Material-specific validation
    if material_lower == "copper":
        required_copper_content = ["8.96", "1085", "401", "c10100", "ofhc"]
        for item in required_copper_content:
            if item not in content_lower:
                errors.append(f"Missing copper-specific content: '{item}' - fail-fast requires exact material data")

    elif material_lower == "steel":
        required_steel_content = ["7.85", "1370", "aisi 1018", "aisi 304"]
        for item in required_steel_content:
            if item not in content_lower:
                errors.append(f"Missing steel-specific content: '{item}' - fail-fast requires exact material data")

    elif material_lower == "aluminum":
        required_aluminum_content = ["2.70", "660", "237", "aa 1100", "aa 2024"]
        for item in required_aluminum_content:
            if item not in content_lower:
                errors.append(f"Missing aluminum-specific content: '{item}' - fail-fast requires exact material data")

    return errors
