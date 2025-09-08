#!/usr/bin/env python3
"""
Test Configuration and Fixtures

Provides pytest fixtures and configuration for the test suite.
"""

from pathlib import Path
from typing import Any, Dict, List

import pytest

from tests.fixtures.mocks.mock_api_client import MockAPIClient
from tests.test_framework import TestDataFactory, TestPathManager


@pytest.fixture(scope="session")
def project_root() -> Path:
    """Get the project root directory."""
    return TestPathManager.get_project_root()


@pytest.fixture(scope="session")
def test_temp_dir() -> Path:
    """Create a temporary directory for the test session."""
    return TestPathManager.get_test_temp_dir()


@pytest.fixture
def mock_api_client():
    """Provide a mock API client for tests."""
    return MockAPIClient("deepseek")


@pytest.fixture
def sample_workflow_data() -> Dict[str, Any]:
    """Provide sample workflow data for testing."""
    return {
        "material": "Steel",
        "component_type": "frontmatter",
        "author_info": {"id": 1, "name": "Test Author", "country": "USA"},
        "material_data": {
            "name": "Steel",
            "category": "metal",
            "properties": ["hardness", "ductility"],
        },
    }


@pytest.fixture
def test_materials() -> List[Dict[str, Any]]:
    """Provide test material data."""
    return TestDataFactory.create_test_materials(3)


@pytest.fixture
def test_author_info() -> Dict[str, Any]:
    """Provide test author information."""
    return TestDataFactory.create_test_author_info(1)


@pytest.fixture
def mock_file_operations():
    """Mock file operations for testing."""
    from tests.test_framework import patch_file_operations

    return patch_file_operations()


# Configure pytest
def pytest_configure(config):
    """Configure pytest with custom markers."""
    config.addinivalue_line("markers", "e2e: End-to-end tests that may be slow")
    config.addinivalue_line("markers", "integration: Integration tests")
    config.addinivalue_line("markers", "unit: Unit tests")


def pytest_collection_modifyitems(config, items):
    """Modify test collection to add markers and skip slow tests."""
    for item in items:
        # Add e2e marker to tests in e2e directory
        if "e2e" in str(item.fspath):
            item.add_marker(pytest.mark.e2e)

        # Add integration marker to tests in integration directory
        if "integration" in str(item.fspath):
            item.add_marker(pytest.mark.integration)

        # Add unit marker to tests in unit directory
        if "unit" in str(item.fspath):
            item.add_marker(pytest.mark.unit)
