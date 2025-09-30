#!/usr/bin/env python3
"""
Component Base Utilities

Shared utilities and base classes for component generators.
Consolidates common patterns and reduces code duplication.
"""

import logging
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any, Dict, Optional

import yaml

from generators.component_generators import ComponentResult
# Component config loading moved to utils.config_loader for centralization


def load_template(template_path: Path) -> Optional[Dict[str, Any]]:
    """Load a YAML template file."""
    try:
        with open(template_path, "r", encoding="utf-8") as f:
            return yaml.safe_load(f)
    except Exception as e:
        logging.warning(f"Failed to load template {template_path}: {e}")
    return None


def create_standard_logger(component_type: str) -> logging.Logger:
    """Create a standard logger for a component"""
    return logging.getLogger(f"components.{component_type}")


def handle_generation_error(
    component_type: str, error: Exception, context: str = ""
) -> ComponentResult:
    """Standard error handling for component generation"""
    logger = create_standard_logger(component_type)
    error_msg = f"Error generating {component_type} content"
    if context:
        error_msg += f" ({context})"
    error_msg += f": {error}"

    logger.error(error_msg)
    return ComponentResult(
        component_type=component_type,
        content="",
        success=False,
        error_message=str(error),
    )


# Common validation functions moved to utils.validation.base_validator for centralization


def sanitize_material_name(material_name: str) -> str:
    """Sanitize material name for file operations"""
    return material_name.lower().replace(" ", "-").replace("/", "-")


def get_component_output_path(component_type: str, material_name: str) -> Path:
    """Get the standard output path for a component"""
    safe_name = sanitize_material_name(material_name)
    return (
        Path("content/components") / component_type / f"{safe_name}-laser-cleaning.md"
    )
