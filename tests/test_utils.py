#!/usr/bin/env python3
"""
Test Utilities

Provides essential test utilities.
"""

import contextlib
from pathlib import Path
from typing import Dict, Any, List, Generator
from unittest.mock import patch
import pytest

from tests.test_framework import TestPathManager, TestDataFactory, TestValidator


@pytest.fixture(scope="session")
def project_root() -> Path:
    """Get the project root directory."""
    return TestPathManager.get_project_root()


@pytest.fixture(scope="session")
def test_temp_dir() -> Generator[Path, None, None]:
    """Create a temporary directory for the test session."""
    temp_dir = TestPathManager.get_test_temp_dir()
    yield temp_dir


@pytest.fixture
def test_content_dir(test_temp_dir: Path) -> Path:
    """Provide a test content directory."""
    content_dir = test_temp_dir / "content" / "components"
    content_dir.mkdir(parents=True, exist_ok=True)
    return content_dir


@pytest.fixture
def mock_api_client():
    """Provide a mock API client."""
    try:
        from tests.fixtures.mocks.mock_api_client import MockAPIClient
        return MockAPIClient("grok")
    except ImportError:
        from unittest.mock import MagicMock
        return MagicMock()


@pytest.fixture
def sample_materials() -> List[Dict[str, Any]]:
    """Provide sample material data."""
    return TestDataFactory.create_test_materials(3)


@pytest.fixture
def sample_author_info() -> Dict[str, Any]:
    """Provide sample author information."""
    return TestDataFactory.create_test_author_info(1)


@contextlib.contextmanager
def mock_file_operations():
    """Context manager for mocking file operations."""
    test_content_dir = TestPathManager.get_test_content_dir()

    def mock_save_component_to_file_original(material, component_type, content):
        safe_material = material.lower().replace(" ", "-")
        filename = f"{safe_material}-laser-cleaning.md"

        component_dir = test_content_dir / component_type
        component_dir.mkdir(parents=True, exist_ok=True)

        filepath = component_dir / filename
        filepath.write_text(content, encoding='utf-8')
        return str(filepath)

    with patch('utils.file_operations.save_component_to_file_original',
               side_effect=mock_save_component_to_file_original), \
         patch('generators.workflow_manager.save_component_to_file_original',
               side_effect=mock_save_component_to_file_original):
        yield


@contextlib.contextmanager
def mock_api_calls(provider: str = "grok", error_rate: float = 0.0):
    """Context manager for mocking API calls."""
    try:
        from tests.fixtures.mocks.mock_api_client import MockAPIClient
        mock_client = MockAPIClient(provider)
    except ImportError:
        from unittest.mock import MagicMock
        mock_client = MagicMock()

    with patch('generators.workflow_manager.get_api_client_for_component',
               return_value=mock_client):
        yield mock_client


def create_test_component_config(component: str) -> Dict[str, Any]:
    """Create test component configuration."""
    return TestDataFactory.create_test_component_config(component)


def validate_generation_result(result: Dict[str, Any]) -> Dict[str, Any]:
    """Validate a generation result."""
    return TestValidator.validate_generation_result(result)


def validate_file_structure(content_dir: Path, expected_components: List[str]) -> Dict[str, Any]:
    """Validate file structure after generation."""
    return TestValidator.validate_file_structure(content_dir, expected_components)


def assert_test_files_exist(content_dir: Path, components: List[str]):
    """Assert that test files exist for given components."""
    for component in components:
        component_dir = content_dir / component
        assert component_dir.exists(), f"Component directory {component} not found"

        files = list(component_dir.glob("*.md"))
        assert len(files) > 0, f"No files found in {component} directory"


def assert_content_quality(content: str, component_type: str, material: str):
    """Assert that content meets quality standards."""
    assert isinstance(content, str), "Content must be a string"
    assert len(content) > 0, "Content must not be empty"

    if component_type == "frontmatter":
        assert "---" in content, "Frontmatter must have YAML delimiters"
        assert "title:" in content, "Frontmatter must have title"
    elif component_type == "text":
        assert len(content) > 100, "Text content must be substantial"
    elif component_type == "table":
        assert "|" in content, "Table content must contain table markup"


# Test data constants
TEST_MATERIALS = ["Steel", "Aluminum", "Copper", "Titanium", "Ceramic"]
TEST_COMPONENTS = ["frontmatter", "text", "table", "bullets", "caption"]
TEST_AUTHORS = [
    {"id": 1, "name": "Yi-Chun Lin", "country": "Taiwan"},
    {"id": 2, "name": "Maria Garcia", "country": "Spain"},
    {"id": 3, "name": "Hans Mueller", "country": "Germany"},
    {"id": 4, "name": "Sarah Johnson", "country": "USA"}
]

# Export key functions
__all__ = [
    'project_root',
    'test_temp_dir',
    'test_content_dir',
    'mock_api_client',
    'sample_materials',
    'sample_author_info',
    'mock_file_operations',
    'mock_api_calls',
    'create_test_component_config',
    'validate_generation_result',
    'validate_file_structure',
    'assert_test_files_exist',
    'assert_content_quality',
    'TEST_MATERIALS',
    'TEST_COMPONENTS',
    'TEST_AUTHORS',
]
