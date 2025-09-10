#!/usr/bin/env python3
"""
Test Configuration and Fixtures with Anti-Hang Protections

Provides pytest fixtures and configuration for the test suite with
comprehensive protections against test hanging.
"""

import os
import pytest
from pathlib import Path
from typing import Any, Dict, List

from tests.fixtures.mocks.mock_api_client import MockAPIClient
from tests.test_framework import TestDataFactory, TestPathManager, test_protector, verify_no_real_api_calls

# Ensure test environment is properly configured for anti-hang protection
os.environ.setdefault('TEST_MODE', 'true')
os.environ.setdefault('MOCK_API', 'true')
os.environ.setdefault('TEST_DISABLE_NETWORK', 'true')
os.environ.setdefault('TEST_BLOCK_REAL_API', 'true')
os.environ.setdefault('TEST_MOCK_ALL_APIS', 'true')

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


# Anti-Hang Protection Fixtures

@pytest.fixture(autouse=True)
def enforce_mock_usage():
    """Automatically enforce that all tests use mocks and prevent real API calls"""
    yield
    # After each test, verify no real API calls were made
    verify_no_real_api_calls()


@pytest.fixture(autouse=True)
def prevent_test_timeout():
    """Ensure tests don't exceed timeout limits"""
    import time
    start_time = time.time()

    yield

    elapsed = time.time() - start_time
    max_time = test_protector.timeout_seconds

    if elapsed > max_time:
        pytest.fail(f"Test exceeded timeout: {elapsed:.2f}s > {max_time}s")


@pytest.fixture
def mock_all_api_clients():
    """Fixture that ensures all API client creation returns mocks"""
    from unittest.mock import patch

    def create_mock_client(provider_name):
        return MockAPIClient(provider_name)

    with patch('api.client_manager.create_api_client', side_effect=create_mock_client), \
         patch('api.client_manager.get_api_client_for_component', side_effect=lambda comp: create_mock_client('grok')):
        yield


@pytest.fixture
def block_real_network_calls():
    """Fixture that blocks all real network calls"""
    from unittest.mock import patch

    def block_request(*args, **kwargs):
        test_protector.network_calls_blocked += 1
        raise RuntimeError("Real network calls blocked in test mode - use mocks!")

    with patch('requests.Session.post', side_effect=block_request), \
         patch('requests.Session.get', side_effect=block_request), \
         patch('requests.post', side_effect=block_request), \
         patch('requests.get', side_effect=block_request):
        yield


# Plugin for hang protection summary
class HangProtectionPlugin:
    """Plugin to provide hang protection summary"""

    def __init__(self):
        self.network_calls_blocked = 0
        self.tests_with_blocked_calls = []
        self.hang_failures = []

    @pytest.hookimpl(trylast=True)
    def pytest_sessionfinish(self, session, exitstatus):
        """Print hang protection summary"""
        print("\n🛡️ HANG PROTECTION SUMMARY:")
        print(f"   🚫 Network calls blocked: {self.network_calls_blocked}")
        print(f"   📋 Tests with blocked calls: {len(self.tests_with_blocked_calls)}")
        print(f"   ⏰ Hang-related failures: {len(self.hang_failures)}")

        if self.tests_with_blocked_calls:
            print("   📋 Tests with blocked network calls:")
            for test in self.tests_with_blocked_calls[:5]:  # Show first 5
                print(f"      • {test}")
            if len(self.tests_with_blocked_calls) > 5:
                print(f"      ... and {len(self.tests_with_blocked_calls) - 5} more")

        if self.hang_failures:
            print("   ⏰ Tests with hang failures:")
            for test in self.hang_failures[:3]:  # Show first 3
                print(f"      • {test}")

    @pytest.hookimpl(tryfirst=True)
    def pytest_runtest_teardown(self, item):
        """Track blocked calls and hang failures per test"""
        stats = test_protector.get_protection_stats()
        blocked = stats.get('network_calls_blocked', 0)
        if blocked > 0:
            self.network_calls_blocked += blocked
            self.tests_with_blocked_calls.append(item.name)

        # Check for hang-related keywords in test results
        if hasattr(item, 'rep_call') and item.rep_call:
            if 'hang_failure' in item.rep_call.keywords:
                self.hang_failures.append(item.name)


# Configure pytest with anti-hang protections
def pytest_configure(config):
    """Configure pytest with custom markers and anti-hang protections."""
    config.addinivalue_line("markers", "e2e: End-to-end tests that may be slow")
    config.addinivalue_line("markers", "integration: Integration tests")
    config.addinivalue_line("markers", "unit: Unit tests")
    config.addinivalue_line("markers", "api: Tests that use API clients")
    config.addinivalue_line("markers", "mock: Tests that use mock clients")
    config.addinivalue_line("markers", "network: Tests that require network access")
    config.addinivalue_line("markers", "file_ops: Tests that perform file operations")
    config.addinivalue_line("markers", "timeout: Tests with custom timeout limits")

    # Register the hang protection plugin
    config.pluginmanager.register(HangProtectionPlugin(), "hang_protection")
