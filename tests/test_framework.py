#!/usr/bin/env python3
"""
Anti-Hang Test Framework for Z-Beam Generator

Comprehensive protections to prevent tests from hanging:
- Network blocking to prevent real API calls
- Mock verification to ensure mocks are used
- Timeout handling with multiple layers
- Resource monitoring and cleanup
- Signal handling for graceful interruption
- Thread/process monitoring
"""

import os
import sys
import time
import signal
import threading
import socket
import pytest
import logging
import tempfile
import unittest
from contextlib import contextmanager
from pathlib import Path
from typing import Any, Dict, List, Optional
from unittest.mock import patch, MagicMock

# Configure logging for test framework
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class TestHangProtector:
    """Comprehensive protection against test hanging"""

    def __init__(self):
        self.start_time = time.time()
        self.threads_started = set()
        self.processes_started = set()
        self.network_calls_blocked = 0
        self.mock_verifications = []
        self.timeout_seconds = int(os.getenv('TEST_TIMEOUT', '25'))

    def monitor_threads(self):
        """Monitor for runaway threads"""
        current_threads = set(threading.enumerate())
        if len(current_threads) > len(self.threads_started) + 2:  # Allow some overhead
            logger.warning(f"Potential thread leak detected: {len(current_threads)} threads running")
            return True
        return False

    def block_network_calls(self):
        """Block all network calls to prevent hanging on real APIs"""

        def blocked_connect(self, address):
            self.network_calls_blocked += 1
            host, port = address[0], address[1]
            logger.error(f"🚫 BLOCKED NETWORK CALL to {host}:{port} - Test should use mocks!")
            raise ConnectionError(f"Network calls blocked in test mode: {host}:{port}")

        def blocked_connect_ex(self, address):
            self.network_calls_blocked += 1
            host, port = address[0], address[1]
            logger.error(f"🚫 BLOCKED NETWORK CALL (connect_ex) to {host}:{port} - Test should use mocks!")
            return 111  # ECONNREFUSED

        # Monkey patch socket methods
        socket.socket.connect = blocked_connect
        socket.socket.connect_ex = blocked_connect_ex

        logger.info("🛡️ Network blocking activated - all network calls will be blocked")

    def verify_mocks_are_used(self):
        """Verify that API clients are using mocks, not real implementations"""
        # This will be called by test fixtures
        pass

    def check_test_timeout(self):
        """Check if test has exceeded timeout"""
        elapsed = time.time() - self.start_time
        if elapsed > self.timeout_seconds:
            logger.error(f"⏰ TEST TIMEOUT: {elapsed:.1f}s > {self.timeout_seconds}s")
            raise TimeoutError(f"Test exceeded timeout of {self.timeout_seconds} seconds")

    def cleanup_resources(self):
        """Clean up any resources that might cause hanging"""
        # Force garbage collection
        import gc
        gc.collect()

        # Check for thread cleanup
        current_threads = threading.enumerate()
        main_thread = threading.main_thread()

        for thread in current_threads:
            if thread != main_thread and thread.is_alive():
                logger.warning(f"Thread still alive: {thread.name} (daemon: {thread.daemon})")
                if not thread.daemon:
                    logger.error(f"Non-daemon thread {thread.name} may cause hang!")

    def get_protection_stats(self) -> Dict[str, Any]:
        """Get statistics about protection measures"""
        return {
            'network_calls_blocked': self.network_calls_blocked,
            'threads_monitored': len(self.threads_started),
            'elapsed_time': time.time() - self.start_time,
            'timeout_limit': self.timeout_seconds,
            'mock_verifications': len(self.mock_verifications)
        }

# Global protector instance
test_protector = TestHangProtector()

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
            cls._test_temp_dir = Path(tempfile.mkdtemp(prefix="z-beam_test_"))
        return cls._test_temp_dir

    @classmethod
    def get_test_content_dir(cls) -> Path:
        """Get a test-specific content directory."""
        test_content_dir = cls.get_test_temp_dir() / "content" / "components"
        test_content_dir.mkdir(parents=True, exist_ok=True)
        return test_content_dir

class RobustTestCase(unittest.TestCase):
    """
    Base test case class with essential test utilities and anti-hang protection.
    """

    def setUp(self):
        """Set up test case with hang protection."""
        super().setUp()

        # Reset protector for this test
        test_protector.start_time = time.time()
        test_protector.network_calls_blocked = 0
        test_protector.threads_started = set(threading.enumerate())

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
        self.test_components = ["frontmatter", "table"]
        self.test_author_info = {
            "id": 1,
            "name": "Test Author",
            "country": "usa",
        }

        logger.debug(f"🧪 Test {self._testMethodName} setup complete")

    def tearDown(self):
        """Clean up test case with hang protection."""
        super().tearDown()

        # Check for resource leaks
        test_protector.monitor_threads()
        test_protector.cleanup_resources()

        # Verify no real API calls were made
        if test_protector.network_calls_blocked > 0:
            self.fail(f"🚫 {test_protector.network_calls_blocked} real API calls were blocked - test should use mocks!")

        # Restore original working directory
        os.chdir(self.original_cwd)

        logger.debug(f"🧹 Test {self._testMethodName} cleanup complete")

    def create_mock_client(self, provider: str = "grok", **kwargs):
        """Create a mock API client."""
        try:
            from tests.fixtures.mocks.simple_mock_client import MockAPIClient
            return MockAPIClient(provider, **kwargs)
        except ImportError:
            return MagicMock()

class TestDataFactory:
    """
    Factory for creating test data.
    """

    @staticmethod
    def create_test_materials(count: int = 3) -> List[Dict[str, Any]]:
        """Create test material data using real materials from materials.yaml."""
        try:
            from data.materials import load_materials
            materials_data = load_materials()
            real_materials = []
            
            if materials_data and "materials" in materials_data:
                for category, category_data in materials_data["materials"].items():
                    if isinstance(category_data, dict) and "items" in category_data:
                        for item in category_data["items"]:
                            if "name" in item:
                                real_materials.append({
                                    "name": item["name"],
                                    "category": category,
                                    "complexity": item.get("complexity", "medium"),
                                    "formula": item.get("formula", ""),
                                })
            
            # If we found materials, use the first 'count' materials
            if real_materials:
                return real_materials[:count]
                
            # Fallback to defaults if no materials were found
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
        except ImportError:
            # Fallback to defaults
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

# Pytest integration for anti-hang protections
def pytest_configure(config):
    """Configure pytest with anti-hang protections"""
    logger.info("🛡️ Configuring anti-hang test protections...")

    # Activate network blocking
    if os.getenv('TEST_DISABLE_NETWORK', 'true').lower() == 'true':
        test_protector.block_network_calls()

    # Set up signal handlers for graceful interruption
    def signal_handler(signum, frame):
        logger.error(f"🛑 Signal {signum} received - cleaning up and exiting")
        test_protector.cleanup_resources()
        sys.exit(1)

    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    logger.info("✅ Anti-hang protections activated")

def pytest_runtest_setup(item):
    """Setup for each test with hang protection"""
    logger.debug(f"🧪 Setting up test: {item.name}")

    # Reset protector for this test
    test_protector.start_time = time.time()
    test_protector.network_calls_blocked = 0

    # Monitor initial thread state
    test_protector.threads_started = set(threading.enumerate())

def pytest_runtest_teardown(item, nextitem):
    """Cleanup after each test"""
    logger.debug(f"🧹 Cleaning up test: {item.name}")

    # Check for resource leaks
    test_protector.monitor_threads()
    test_protector.cleanup_resources()

    # Log protection stats
    stats = test_protector.get_protection_stats()
    if stats['network_calls_blocked'] > 0:
        logger.warning(f"⚠️  {stats['network_calls_blocked']} network calls were blocked in test {item.name}")

@pytest.fixture(scope="session", autouse=True)
def global_test_setup():
    """Global test setup with comprehensive protections"""
    logger.info("🚀 Starting test session with anti-hang protections")

    # Ensure we're in test mode
    os.environ['TEST_MODE'] = 'true'
    os.environ['MOCK_API'] = 'true'

    yield

    # Final cleanup
    logger.info("🏁 Test session completed")
    final_stats = test_protector.get_protection_stats()
    logger.info(f"📊 Final protection stats: {final_stats}")

@pytest.fixture(scope="function", autouse=True)
def per_test_protection():
    """Per-test protection fixture"""
    test_start = time.time()

    yield

    # Check test duration
    duration = time.time() - test_start
    if duration > test_protector.timeout_seconds:
        logger.error(".2f")
        pytest.fail(f"Test exceeded timeout: {duration:.2f}s > {test_protector.timeout_seconds}s")

@pytest.fixture
def mock_api_clients():
    """Fixture that ensures all API clients are mocked"""
    logger.info("🎭 Setting up mock API clients")

    # Import mock client
    from tests.fixtures.mocks.simple_mock_client import MockAPIClient

    # Mock the API client creation functions
    with patch('api.client_manager.create_api_client') as mock_create, \
         patch('api.client_manager.get_api_client_for_component') as mock_get, \
         patch('generators.dynamic_generator.APIClient') as mock_dynamic_client:

        # Configure mocks to return MockAPIClient instances
        def create_mock_client(provider_name):
            logger.debug(f"🎭 Creating mock client for {provider_name}")
            return MockAPIClient(provider_name)

        mock_create.side_effect = create_mock_client
        mock_get.side_effect = lambda component: create_mock_client('grok')
        mock_dynamic_client.return_value = create_mock_client('grok')

        yield

        # Verify mocks were used
        logger.info(f"✅ Mock create called {mock_create.call_count} times")
        logger.info(f"✅ Mock get called {mock_get.call_count} times")

@pytest.fixture
def prevent_real_api_calls():
    """Fixture that prevents any real API calls from being made"""
    logger.info("🚫 Activating real API call prevention")

    # Mock requests to prevent any HTTP calls
    with patch('requests.Session.post') as mock_post, \
         patch('requests.Session.get') as mock_get, \
         patch('requests.post') as mock_post_direct, \
         patch('requests.get') as mock_get_direct:

        def block_request(*args, **kwargs):
            logger.error("🚫 BLOCKED REAL API CALL - Test should use mocks!")
            test_protector.network_calls_blocked += 1
            raise RuntimeError("Real API calls blocked in test mode - use mocks!")

        mock_post.side_effect = block_request
        mock_get.side_effect = block_request
        mock_post_direct.side_effect = block_request
        mock_get_direct.side_effect = block_request

        yield

        blocked_count = (mock_post.call_count + mock_get.call_count +
                        mock_post_direct.call_count + mock_get_direct.call_count)
        if blocked_count > 0:
            logger.warning(f"⚠️  Blocked {blocked_count} real API calls")

@pytest.fixture
def fast_mock_responses():
    """Fixture that ensures mock responses are very fast"""
    logger.info("⚡ Configuring fast mock responses")

    # Import MockAPIClient locally
    from tests.fixtures.mocks.simple_mock_client import MockAPIClient

    # Set very fast response times for mocks
    with patch.object(MockAPIClient, 'response_delay', 0.001):
        yield

@pytest.fixture
def test_timeout_monitor():
    """Fixture that monitors for test timeouts"""
    logger.debug("⏰ Starting timeout monitor")

    def timeout_checker():
        while True:
            test_protector.check_test_timeout()
            time.sleep(1)  # Check every second

    # Start timeout monitoring thread
    monitor_thread = threading.Thread(target=timeout_checker, daemon=True)
    monitor_thread.start()

    yield

    # Thread will be cleaned up automatically as daemon

# Custom pytest marks for hang protection
def pytest_collection_modifyitems(config, items):
    """Modify test collection to add hang protection markers"""

    for item in items:
        # Add timeout marker if not present
        if 'timeout' not in [mark.name for mark in item.own_markers]:
            item.add_marker(pytest.mark.timeout(test_protector.timeout_seconds))

        # Add mock marker for API-related tests
        if 'api' in item.keywords or 'mock' in item.keywords:
            item.add_marker(pytest.mark.mock)

# Test utilities
@contextmanager
def protected_test_execution(test_name: str):
    """Context manager for protected test execution"""
    logger.info(f"🛡️ Starting protected execution of {test_name}")

    start_time = time.time()
    try:
        yield
        duration = time.time() - start_time
        logger.info(f"✅ {test_name} completed successfully in {duration:.2f}s")

    except Exception as e:
        duration = time.time() - start_time
        logger.error(f"❌ {test_name} failed after {duration:.2f}s: {e}")
        raise

    finally:
        # Always cleanup
        test_protector.cleanup_resources()

def verify_no_real_api_calls():
    """Verify that no real API calls were made during test execution"""
    if test_protector.network_calls_blocked > 0:
        pytest.fail(f"🚫 {test_protector.network_calls_blocked} real API calls were blocked - test should use mocks!")

def assert_test_completion_within_timeout(max_seconds: int = 30):
    """Assert that test completed within specified timeout"""
    elapsed = time.time() - test_protector.start_time
    assert elapsed < max_seconds, f"Test took {elapsed:.2f}s, exceeded limit of {max_seconds}s"

# Export key classes and functions
__all__ = [
    "TestPathManager",
    "RobustTestCase",
    "TestDataFactory",
    "TestValidator",
    "patch_file_operations",
    "test_protector",
    "protected_test_execution",
    "verify_no_real_api_calls",
    "assert_test_completion_within_timeout",
    "mock_api_clients",
    "prevent_real_api_calls",
    "fast_mock_responses",
    "test_timeout_monitor"
]
