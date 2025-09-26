#!/usr/bin/env python3
"""
JSON-LD Component Validator

Component-specific validation logic for JSON-LD components.
"""

import json
from typing import Any, Dict, List


def validate_jsonld_structure(
    content: str, format_rules: Dict[str, Any] = None
) -> List[str]:
    """
    Validate JSON-LD structure requirements.

    Args:
        content: The JSON-LD content to validate
        format_rules: Optional format rules dictionary

    Returns:
        List of validation errors (empty if valid)
    """
    errors = []

    try:
        # Check if content is wrapped in code blocks
        json_start = content.find("```json")
        json_end = content.find("```", json_start + 7) if json_start != -1 else -1

        if json_start != -1 and json_end != -1:
            # Extract from code blocks
            json_content = content[json_start + 7 : json_end].strip()
        else:
            # Assume entire content is JSON-LD
            json_content = content.strip()

        # Validate JSON syntax
        try:
            parsed_json = json.loads(json_content)
        except json.JSONDecodeError as e:
            errors.append(f"Invalid JSON syntax: {e}")
            return errors

        # Validate JSON-LD structure
        if not isinstance(parsed_json, dict):
            errors.append("JSON-LD must be a JSON object")
            return errors

        # Check for required JSON-LD fields
        if "@context" not in parsed_json:
            errors.append("Missing required JSON-LD field: @context")
        
        # Check for @type field - can be at root or in @graph items
        if "@type" not in parsed_json:
            # If no @type at root, check if using @graph structure
            if "@graph" in parsed_json and isinstance(parsed_json["@graph"], list):
                # @graph structure is valid, check if items have @type
                graph_items_with_type = [item for item in parsed_json["@graph"] if isinstance(item, dict) and "@type" in item]
                if not graph_items_with_type:
                    errors.append("No @type found in JSON-LD structure (neither at root nor in @graph items)")
            else:
                errors.append("Missing required JSON-LD field: @type")

        # Validate @context
        if (
            "@context" in parsed_json
            and parsed_json["@context"] != "https://schema.org"
        ):
            errors.append(
                "@context should be 'https://schema.org' for schema.org compliance"
            )

    except Exception as e:
        errors.append(f"Error validating JSON-LD structure: {e}")

    return errors


def validate_jsonld_content(content: str) -> List[str]:
    """
    Validate JSON-LD content requirements.

    Args:
        content: The JSON-LD content to validate

    Returns:
        List of validation errors (empty if valid)
    """
    errors = []

    # Check for specific placeholder patterns (not general brackets since JSON uses them)
    placeholder_patterns = ["TBD", "TODO", "[INSERT", "[PLACEHOLDER", "{{", "}}", "XXXX"]
    found_placeholders = [p for p in placeholder_patterns if p in content]
    
    if found_placeholders:
        errors.append(f"Contains placeholder content: {', '.join(found_placeholders)}")

    # Basic content validation
    if not content.strip():
        errors.append("JSON-LD component cannot be empty")

    return errors


def validate_jsonld_schema(content: str) -> List[str]:
    """
    Validate JSON-LD schema.org compliance.

    Args:
        content: The JSON-LD content to validate

    Returns:
        List of validation warnings (empty if acceptable)
    """
    warnings = []

    try:
        # Extract JSON content
        json_start = content.find("```json")
        json_end = content.find("```", json_start + 7) if json_start != -1 else -1

        if json_start != -1 and json_end != -1:
            json_content = content[json_start + 7 : json_end].strip()
            parsed_json = json.loads(json_content)

            # Check for recommended Article fields
            if parsed_json.get("@type") == "Article":
                recommended_fields = [
                    "headline",
                    "description",
                    "author",
                    "datePublished",
                    "keywords",
                ]
                missing_fields = [
                    field for field in recommended_fields if field not in parsed_json
                ]
                if missing_fields:
                    warnings.append(
                        f"Consider adding Article fields: {', '.join(missing_fields)}"
                    )

            # Check keyword count
            if "keywords" in parsed_json:
                keywords = parsed_json["keywords"]
                if isinstance(keywords, list) and len(keywords) < 5:
                    warnings.append("Consider adding more keywords for better SEO")

    except Exception:
        # If parsing fails, the structure validation will catch it
        pass

    return warnings
