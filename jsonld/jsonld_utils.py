#!/usr/bin/env python3
"""
JSON-LD Utilities - Helper functions for JSON-LD generation
"""
import json
import logging
from typing import Dict, Any
from pathlib import Path

logger = logging.getLogger(__name__)

def format_jsonld_as_script(jsonld_data: Dict[str, Any]) -> str:
    """Format JSON-LD as HTML script tag"""
    json_str = json.dumps(jsonld_data, indent=2)
    return f'<script type="application/ld+json">\n{json_str}\n</script>'

def format_jsonld_as_yaml_block(jsonld_data: Dict[str, Any]) -> str:
    """Format JSON-LD as YAML block for markdown"""
    json_str = json.dumps(jsonld_data, indent=2)
    return f"```json\n{json_str}\n```"

def validate_jsonld_structure(jsonld_data: Dict[str, Any]) -> tuple[bool, list[str]]:
    """Validate JSON-LD structure"""
    errors = []
    
    # Check required fields
    required_fields = ["@context", "@type"]
    for field in required_fields:
        if field not in jsonld_data:
            errors.append(f"Missing required field: {field}")
    
    # Check @type
    if "@type" in jsonld_data and not jsonld_data["@type"]:
        errors.append("@type cannot be empty")
    
    # Check about section
    if "about" in jsonld_data:
        about = jsonld_data["about"]
        if isinstance(about, dict) and "@type" not in about:
            errors.append("about section missing @type")
    
    return len(errors) == 0, errors

def save_jsonld_file(jsonld_data: Dict[str, Any], output_path: str) -> None:
    """Save JSON-LD to file"""
    output_file = Path(output_path)
    output_file.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(jsonld_data, f, indent=2, ensure_ascii=False)
    
    logger.info(f"📄 JSON-LD saved to: {output_file}")

def merge_jsonld_contexts(base_context: Dict[str, Any], additional_context: Dict[str, Any]) -> Dict[str, Any]:
    """Merge JSON-LD contexts"""
    if isinstance(base_context, dict) and isinstance(additional_context, dict):
        merged = base_context.copy()
        merged.update(additional_context)
        return merged
    return base_context