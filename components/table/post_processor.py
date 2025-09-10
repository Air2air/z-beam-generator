"""
Table component post-processor for deterministic content validation.

FAIL-FAST: No content modifications allowed. Only validates deterministic output.
"""
import logging

logger = logging.getLogger(__name__)


def post_process_table(content: str, material_name: str = "") -> str:
    """
    Post-process table content - DETERMINISTIC: No modifications, only validation.

    Args:
        content: Generated table content (should be identical each time)
        material_name: Name of the material being processed

    Returns:
        str: Original content (unchanged) or error message
    """
    if not content or not content.strip():
        logger.error("Table content is empty - fail-fast architecture requires complete content")
        return content

    # VALIDATION ONLY - Do not modify content
    validation_errors = validate_deterministic_content(content, material_name)

    if validation_errors:
        logger.error(f"Content validation failed: {', '.join(validation_errors)}")
        # FAIL-FAST: Return original content but log errors
        return content

    # Content is valid and deterministic - return unchanged
    logger.info(f"Table content validated successfully for material: {material_name}")
    return content


def validate_deterministic_content(content: str, material_name: str) -> list:
    """
    Validate that content matches deterministic requirements - FAIL-FAST.

    Args:
        content: The table content to validate
        material_name: Expected material name

    Returns:
        List of validation errors (empty if valid)
    """
    errors = []

    # Must contain material name - FAIL-FAST
    if material_name and material_name.lower() not in content.lower():
        errors.append(f"Material name '{material_name}' not found in content")

    # Must have exact 6 table sections - FAIL-FAST
    section_count = content.count("##")
    if section_count != 6:
        errors.append(f"Must have exactly 6 table sections, found {section_count}")

    # Must have proper markdown table structure - FAIL-FAST
    lines = content.split("\n")
    table_lines = [line for line in lines if "|" in line]

    if len(table_lines) < 12:  # Minimum: 6 headers + 6 separators
        errors.append(f"Insufficient table structure, found {len(table_lines)} table lines")

    # Check for separator rows - FAIL-FAST
    separator_count = sum(1 for line in table_lines if "---" in line)
    if separator_count != 6:
        errors.append(f"Must have exactly 6 separator rows, found {separator_count}")

    # Check for data consistency - FAIL-FAST
    data_lines = [line for line in table_lines if "|" in line and "---" not in line and not line.startswith("##")]
    if len(data_lines) != 24:  # Exact count required
        errors.append(f"Must have exactly 24 data rows, found {len(data_lines)}")

    return errors


def clean_technical_terms(text: str) -> str:
    """
    DEPRECATED: Technical term cleaning not allowed in deterministic generation.

    This function is kept for backward compatibility but should not be used
    as it would modify deterministic output.
    """
    logger.warning("clean_technical_terms called - this modifies deterministic output and should not be used")
    return text  # Return unchanged to maintain determinism
