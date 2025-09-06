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

from tests.mocks.mock_api_client import create_fast_mock_client

        if self.cache_dir.exists():
            shutil.rmtree(self.cache_dir)
            self.cache_dir.mkdir(exist_ok=True)


# Global cache instance
test_data_cache = TestDataCache()


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
