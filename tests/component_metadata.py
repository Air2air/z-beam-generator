#!/usr/bin/env python3
"""
Component Metadata System

Provides centralized metadata about all components in the system.
Documents component capabilities, requirements, and behavior patterns.
"""

from dataclasses import dataclass
from typing import Any, Dict, List


@dataclass
class ComponentMetadata:
    """Metadata for a component."""

    name: str
    type: str  # "api", "static", "hybrid"
    requires_api: bool
    static_fallback: bool
    description: str
    expected_file_pattern: str
    error_patterns: List[str]
    test_expectations: Dict[str, Any]


# Component metadata registry
COMPONENT_METADATA = {
    "frontmatter": ComponentMetadata(
        name="frontmatter",
        type="api",
        requires_api=True,
        static_fallback=False,
        description="YAML frontmatter generation for content metadata",
        expected_file_pattern="{material}-laser-cleaning.md",
        error_patterns=["API error", "Invalid request", "Authentication failed"],
        test_expectations={
            "should_use_api_client": True,
            "expected_error_propagation": "direct",
            "content_must_mention_material": False,  # Titles are generic
            "min_content_length": 50,
            "required_fields": ["title", "author", "date"],
        },
    ),
    "text": ComponentMetadata(
        name="text",
        type="api",
        requires_api=True,
        static_fallback=False,
        description="Technical content generation with author personas",
        expected_file_pattern="{material}-laser-cleaning.md",
        error_patterns=["generation failed", "API error", "Empty response"],
        test_expectations={
            "should_use_api_client": True,
            "expected_error_propagation": "wrapped",  # Wrapped in GenerationError
            "content_must_mention_material": True,
            "min_content_length": 500,
            "required_sections": ["introduction", "technical details"],
        },
    ),
    "table": ComponentMetadata(
        name="table",
        type="static",
        requires_api=False,
        static_fallback=True,
        description="Technical tables with material properties and specifications",
        expected_file_pattern="{material}-laser-cleaning.md",
        error_patterns=[],  # Static generation, minimal error cases
        test_expectations={
            "should_use_api_client": False,
            "expected_error_propagation": "none",
            "content_must_mention_material": False,  # Tables may not mention material in every cell
            "min_content_length": 200,
            "required_elements": ["|", "table markup"],
        },
    ),
    "bullets": ComponentMetadata(
        name="bullets",
        type="api",
        requires_api=True,
        static_fallback=False,
        description="Bullet point lists for key information",
        expected_file_pattern="{material}-laser-cleaning.md",
        error_patterns=["API error", "generation failed"],
        test_expectations={
            "should_use_api_client": True,
            "expected_error_propagation": "direct",
            "content_must_mention_material": True,
            "min_content_length": 100,
            "required_elements": ["•", "-", "*"],
        },
    ),
    "caption": ComponentMetadata(
        name="caption",
        type="api",
        requires_api=True,
        static_fallback=False,
        description="Image and figure captions for technical content",
        expected_file_pattern="{material}-laser-cleaning.md",
        error_patterns=["API error", "generation failed"],
        test_expectations={
            "should_use_api_client": True,
            "expected_error_propagation": "direct",
            "content_must_mention_material": True,
            "min_content_length": 50,
            "required_elements": ["caption", "figure"],
        },
    ),
}


class ComponentMetadataManager:
    """Manager for component metadata operations."""

    @staticmethod
    def get_component_metadata(component_type: str) -> ComponentMetadata:
        """Get metadata for a specific component."""
        if component_type not in COMPONENT_METADATA:
            raise ValueError(f"Unknown component type: {component_type}")
        return COMPONENT_METADATA[component_type]

    @staticmethod
    def get_api_dependent_components() -> List[str]:
        """Get list of components that require API access."""
        return [name for name, meta in COMPONENT_METADATA.items() if meta.requires_api]

    @staticmethod
    def get_static_components() -> List[str]:
        """Get list of static components."""
        return [
            name for name, meta in COMPONENT_METADATA.items() if not meta.requires_api
        ]

    @staticmethod
    def validate_component_behavior(component_type: str, **kwargs) -> Dict[str, Any]:
        """Validate component behavior against metadata expectations."""
        if component_type not in COMPONENT_METADATA:
            return {"valid": False, "errors": [f"Unknown component: {component_type}"]}

        metadata = COMPONENT_METADATA[component_type]
        validation = {"valid": True, "errors": [], "warnings": []}

        # Validate API usage expectations
        if "uses_api" in kwargs:
            expected_api_usage = metadata.test_expectations.get(
                "should_use_api_client", False
            )
            actual_api_usage = kwargs["uses_api"]
            if expected_api_usage != actual_api_usage:
                validation["errors"].append(
                    f"API usage mismatch: expected {expected_api_usage}, got {actual_api_usage}"
                )
                validation["valid"] = False

        # Validate content requirements
        if "content" in kwargs:
            content = kwargs["content"]
            min_length = metadata.test_expectations.get("min_content_length", 0)
            if len(content) < min_length:
                validation["errors"].append(
                    f"Content too short: {len(content)} < {min_length}"
                )
                validation["valid"] = False

        return validation

    @staticmethod
    def get_test_expectations(component_type: str) -> Dict[str, Any]:
        """Get test expectations for a component."""
        if component_type not in COMPONENT_METADATA:
            return {}
        return COMPONENT_METADATA[component_type].test_expectations.copy()


# Convenience functions
def is_api_component(component_type: str) -> bool:
    """Check if a component requires API access."""
    try:
        metadata = ComponentMetadataManager.get_component_metadata(component_type)
        return metadata.requires_api
    except ValueError:
        return False


def should_use_api_client(component_type: str) -> bool:
    """Check if a component should use API client in tests."""
    try:
        metadata = ComponentMetadataManager.get_component_metadata(component_type)
        return metadata.test_expectations.get("should_use_api_client", False)
    except ValueError:
        return False


def get_expected_error_patterns(component_type: str) -> List[str]:
    """Get expected error patterns for a component."""
    try:
        metadata = ComponentMetadataManager.get_component_metadata(component_type)
        return metadata.error_patterns.copy()
    except ValueError:
        return []


# Export key classes and functions
__all__ = [
    "ComponentMetadata",
    "COMPONENT_METADATA",
    "ComponentMetadataManager",
    "is_api_component",
    "should_use_api_client",
    "get_expected_error_patterns",
]
