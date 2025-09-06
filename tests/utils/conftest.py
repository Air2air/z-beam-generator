#!/usr/bin/env python3
"""
Test Fixtures and Utilities

Provides common test fixtures, utilities, and setup/teardown
functions for the test suite.
"""

import json
import shutil
import sys
import time
from pathlib import Path
from typing import Any, Dict

import pytest

from tests.fixtures.mocks.mock_api_client import create_fast_mock_client


class TestDataCache:
    """Cache for test data to improve test performance"""

    def __init__(self):
        self.cache_dir = Path("test_cache")
        self.cache_dir.mkdir(exist_ok=True)

    def clear_cache(self):
        """Clear the test cache directory"""
        if self.cache_dir.exists():
            shutil.rmtree(self.cache_dir)
            self.cache_dir.mkdir(exist_ok=True)


# Global cache instance
test_data_cache = TestDataCache()


@pytest.fixture
def test_config():
    """Provide test configuration"""
    return {"test_mode": True, "mock_responses": True}


@pytest.fixture
def get_test_api_client():
    """Provide a mock API client for testing"""
    return create_fast_mock_client()


def assert_api_response_format(response):
    """Assert that API response has expected format"""
    assert isinstance(response, dict)
    assert "success" in response
    assert "content" in response


if __name__ == "__main__":
    # Test the fixtures
    print("Testing fixtures...")

    # Test configuration
    print(f"Test config: {test_config.get_config()}")

    # Test mock client
    client = get_test_api_client()
    response = client.generate_content("Test prompt")
    print(f"Mock client response: {response['success']}")

    # Test utilities
    assert_api_response_format(response)
    print("All fixture tests passed!")
