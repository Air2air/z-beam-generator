#!/usr/bin/env python3
"""
Simplified Test Framework

Provides essential test utilities with minimal bloat.
"""

import logging
import os
import sys
import tempfile
import unittest
from pathlib import Path
from typing import Any, Dict, List, Optional
from unittest.mock import MagicMock, patch

# Setup logging for tests
logging.basicConfig(level=logging.WARNING)
logger = logging.getLogger(__name__)


class TestPathManager:
    """
    Centralized path management for tests.
    """

    _project_root: Optional[Path] = None
    _test_temp_dir: Optional[Path] = None

    @classmethod
    def get_project_root(cls) -> Path:
        """Get the project root directory."""
        if cls._project_root is None:
            current = Path(__file__).resolve().parent.parent
            for parent in [current] + list(current.parents):
                if (parent / "requirements.txt").exists():
                    cls._project_root = parent
                    break
            else:
                cls._project_root = Path.cwd()
        return cls._project_root

    @classmethod
    def get_test_temp_dir(cls) -> Path:
        """Get a temporary directory for tests."""
        if cls._test_temp_dir is None:
            cls._test_temp_dir = Path(tempfile.mkdtemp(prefix="zbeam_test_"))
        return cls._test_temp_dir

    @classmethod
    def get_test_content_dir(cls) -> Path:
        """Get a test-specific content directory."""
        test_content_dir = cls.get_test_temp_dir() / "content" / "components"
        test_content_dir.mkdir(parents=True, exist_ok=True)
        return test_content_dir


class RobustTestCase(unittest.TestCase):
    """
    Base test case class with essential test utilities.
    """

    def setUp(self):
        """Set up test case."""
        super().setUp()
        # Ensure project root is in path
        project_root = TestPathManager.get_project_root()
        if str(project_root) not in sys.path:
            sys.path.insert(0, str(project_root))

        # Change to project root to avoid CWD issues
        self.original_cwd = os.getcwd()
        os.chdir(project_root)

        # Common test data
        self.test_content_dir = TestPathManager.get_test_content_dir()
        self.test_material = "Steel"
        self.test_components = ["frontmatter", "text", "table"]
        self.test_author_info = {
            "id": 1,
            "name": "Test Author",
            "country": "Test Country",
        }

    def tearDown(self):
        """Clean up test case."""
        super().tearDown()
        # Restore original working directory
        os.chdir(self.original_cwd)

    def create_mock_client(self, provider: str = "grok", **kwargs):
        """Create a mock API client."""
        try:
            from tests.fixtures.mocks.mock_api_client import MockAPIClient

            return MockAPIClient(provider, **kwargs)
        except ImportError:
            return MagicMock()


class TestDataFactory:
    """
    Factory for creating test data.
    """

    @staticmethod
    def create_test_materials(count: int = 3) -> List[Dict[str, Any]]:
        """Create test material data."""
        materials = ["Steel", "Aluminum", "Copper", "Titanium", "Ceramic"]
        return [
            {
                "name": materials[i % len(materials)],
                "category": "metal" if i < 4 else "ceramic",
                "complexity": "medium",
                "formula": "Fe" if materials[i % len(materials)] == "Steel" else "Al",
            }
            for i in range(count)
        ]

    @staticmethod
    def create_test_author_info(author_id: int = 1) -> Dict[str, Any]:
        """Create test author information."""
        authors = [
            {"id": 1, "name": "Yi-Chun Lin", "country": "Taiwan"},
            {"id": 2, "name": "Maria Garcia", "country": "Spain"},
            {"id": 3, "name": "Hans Mueller", "country": "Germany"},
            {"id": 4, "name": "Sarah Johnson", "country": "USA"},
        ]
        return authors[(author_id - 1) % len(authors)]

    @staticmethod
    def create_test_component_config(component: str) -> Dict[str, Any]:
        """Create test component configuration."""
        configs = {
            "frontmatter": {
                "type": "yaml",
                "required_fields": ["title", "author", "date"],
                "optional_fields": ["description", "tags", "category"],
            },
            "text": {
                "type": "markdown",
                "min_length": 100,
                "max_length": 2000,
                "required_sections": ["introduction", "process", "applications"],
            },
            "table": {
                "type": "markdown_table",
                "columns": ["Property", "Value", "Unit"],
                "min_rows": 3,
            },
        }
        return configs.get(component, {})


class TestValidator:
    """
    Validates test results.
    """

    @staticmethod
    def validate_generation_result(result: Dict[str, Any]) -> Dict[str, Any]:
        """Validate a generation result."""
        validation = {"valid": True, "errors": [], "warnings": [], "metrics": {}}

        required_fields = ["components_generated", "components_failed", "total_time"]
        for field in required_fields:
            if field not in result:
                validation["errors"].append(f"Missing required field: {field}")
                validation["valid"] = False

        if "components_generated" in result:
            for component in result["components_generated"]:
                if not isinstance(component, dict):
                    validation["errors"].append("Component result is not a dictionary")
                    validation["valid"] = False
                    continue
                if "type" not in component:
                    validation["errors"].append("Component missing 'type' field")
                    validation["valid"] = False

        if "components_generated" in result and "components_failed" in result:
            total = len(result["components_generated"]) + len(
                result["components_failed"]
            )
            success_rate = (
                len(result["components_generated"]) / total if total > 0 else 0
            )
            validation["metrics"]["success_rate"] = success_rate
            validation["metrics"]["total_components"] = total

        return validation

    @staticmethod
    def validate_file_structure(
        content_dir: Path, expected_components: List[str]
    ) -> Dict[str, Any]:
        """Validate file structure after generation."""
        validation = {"valid": True, "errors": [], "file_counts": {}, "total_files": 0}

        if not content_dir.exists():
            validation["errors"].append(
                f"Content directory does not exist: {content_dir}"
            )
            validation["valid"] = False
            return validation

        total_files = 0
        for component in expected_components:
            component_dir = content_dir / component
            if not component_dir.exists():
                validation["errors"].append(f"Component directory missing: {component}")
                validation["valid"] = False
                validation["file_counts"][component] = 0
                continue

            files = list(component_dir.glob("*.md"))
            file_count = len(files)
            validation["file_counts"][component] = file_count
            total_files += file_count

            if file_count == 0:
                validation["errors"].append(f"No files found in {component} directory")

        validation["total_files"] = total_files
        return validation


def patch_file_operations():
    """Patch file operations to use test directories."""
    test_content_dir = TestPathManager.get_test_content_dir()

    def mock_save_component_to_file_original(material, component_type, content):
        safe_material = material.lower().replace(" ", "-")
        filename = f"{safe_material}-laser-cleaning.md"

        component_dir = test_content_dir / component_type
        component_dir.mkdir(parents=True, exist_ok=True)

        filepath = component_dir / filename
        filepath.write_text(content, encoding="utf-8")
        return str(filepath)

    return patch(
        "utils.file_operations.save_component_to_file_original",
        side_effect=mock_save_component_to_file_original,
    )


# Export key classes and functions
__all__ = [
    "TestPathManager",
    "RobustTestCase",
    "TestDataFactory",
    "TestValidator",
    "patch_file_operations",
]
