#!/usr/bin/env python3
"""
Pytest Configuration and Session-Scoped Fixtures

This conftest.py provides session-scoped fixtures and pytest configuration
to optimize test execution performance and reduce setup overhead.
"""

import os
import sys
import pytest
import tempfile
from pathlib import Path
from typing import Dict, Any, List, Generator

# Add project root to path
project_root = Path(__file__).resolve().parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

# Commented out obsolete test framework imports
# from tests.test_framework import TestPathManager, TestDataFactory
# from tests.test_utils import mock_api_calls, mock_file_operations

@pytest.fixture(scope="session", autouse=True)
def session_setup():
    """Session-wide setup and environment configuration."""
    # Ensure test environment variables are set
    os.environ.setdefault('TEST_MODE', 'true')
    os.environ.setdefault('MOCK_API', 'true')
    os.environ.setdefault('TEST_USE_MOCK_API', 'true')
    os.environ.setdefault('TEST_DISABLE_NETWORK', 'true')
    os.environ.setdefault('TEST_FAIL_FAST', 'true')

    # Change to project root to avoid path issues
    original_cwd = os.getcwd()
    os.chdir(project_root)

    yield

    # Restore original directory
    os.chdir(original_cwd)

@pytest.fixture(scope="session")
def session_temp_dir() -> Generator[Path, None, None]:
    """Session-scoped temporary directory for all tests."""
    temp_dir = Path(tempfile.mkdtemp(prefix="z_beam_session_"))
    yield temp_dir

    # Cleanup after session
    import shutil
    try:
        shutil.rmtree(temp_dir, ignore_errors=True)
    except Exception:
        pass  # Ignore cleanup errors

@pytest.fixture(scope="session")
def session_content_dir(session_temp_dir: Path) -> Path:
    """Session-scoped content directory."""
    content_dir = session_temp_dir / "content" / "components"
    content_dir.mkdir(parents=True, exist_ok=True)
    return content_dir

@pytest.fixture(scope="session")
def session_test_data() -> Dict[str, Any]:
    """Pre-loaded test data for the entire session."""
    from tests.optimized_test_data import _OPTIMIZED_DATA
    return _OPTIMIZED_DATA

@pytest.fixture(scope="session")
def session_mock_client():
    """Session-scoped mock API client."""
    try:
        from tests.fixtures.mocks.simple_mock_client import MockAPIClient
        client = MockAPIClient("grok")
        # Configure for maximum speed
        client.response_delay = 0.0
        return client
    except ImportError:
        from unittest.mock import MagicMock
        return MagicMock()

@pytest.fixture
def fast_mock_context(session_mock_client):
    """Fast mock context using session-scoped client."""
    from unittest.mock import patch

    with patch('api.client_manager.get_api_client_for_component', return_value=session_mock_client), \
         patch('api.client_manager.create_api_client', return_value=session_mock_client), \
         patch('generators.workflow_manager.get_api_client_for_component', return_value=session_mock_client), \
         patch('generators.dynamic_generator.get_api_client_for_component', return_value=session_mock_client):
        yield session_mock_client

@pytest.fixture
def optimized_file_ops(session_content_dir):
    """Optimized file operations using session content directory."""
    from unittest.mock import patch

    def mock_save_component(material, component_type, content):
        safe_material = material.lower().replace(" ", "-")
        filename = f"{safe_material}-laser-cleaning.md"

        component_dir = session_content_dir / component_type
        component_dir.mkdir(parents=True, exist_ok=True)

        filepath = component_dir / filename
        filepath.write_text(content, encoding="utf-8")
        return str(filepath)

    with patch("utils.file_operations.save_component_to_file_original", side_effect=mock_save_component), \
         patch("generators.workflow_manager.save_component_to_file_original", side_effect=mock_save_component):
        yield

@pytest.fixture
def test_material_data(session_test_data):
    """Quick access to test material data."""
    return session_test_data["materials"][0]  # Default to first material

@pytest.fixture
def test_author_data(session_test_data):
    """Quick access to test author data."""
    return session_test_data["authors"][0]  # Default to first author

@pytest.fixture
def test_component_config(session_test_data):
    """Quick access to test component configurations."""
    return session_test_data["component_configs"]

# Performance monitoring fixtures
@pytest.fixture(scope="session")
def performance_stats():
    """Track performance statistics across the test session."""
    import time
    from collections import defaultdict

    stats = {
        "start_time": time.time(),
        "test_count": 0,
        "test_times": [],
        "slow_tests": [],
        "fixture_setup_times": defaultdict(list)
    }

    yield stats

    # Print performance summary
    end_time = time.time()
    total_time = end_time - stats["start_time"]

    print("\n=== PERFORMANCE SUMMARY ===")
    print(f"Total session time: {total_time:.2f}s")
    print(f"Tests executed: {stats['test_count']}")
    if stats["test_times"]:
        avg_time = sum(stats["test_times"]) / len(stats["test_times"])
        print(f"Average test time: {avg_time:.2f}s")
        print(f"Fastest test: {min(stats['test_times']):.2f}s")
        print(f"Slowest test: {max(stats['test_times']):.2f}s")

    if stats["slow_tests"]:
        print(f"Slow tests (>5s): {len(stats['slow_tests'])}")
        for test_name, duration in stats["slow_tests"][:5]:  # Show top 5
            print(f"  - {test_name}: {duration:.2f}s")

@pytest.fixture(autouse=True)
def track_test_performance(request, performance_stats):
    """Automatically track test performance."""
    import time

    start_time = time.time()
    yield
    end_time = time.time()

    duration = end_time - start_time
    performance_stats["test_count"] += 1
    performance_stats["test_times"].append(duration)

    if duration > 5.0:  # Track slow tests
        performance_stats["slow_tests"].append((request.node.name, duration))

# Parallel execution configuration
def pytest_configure(config):
    """Configure pytest for optimized execution."""
    # Set parallel execution if available
    if hasattr(config.option, 'numprocesses'):
        # pytest-xdist is available
        if config.option.numprocesses is None:
            config.option.numprocesses = 4  # Default to 4 workers

    # Configure markers for better organization
    config.addinivalue_line("markers", "slow: marks tests as slow (deselect with '-m \"not slow\"')")
    config.addinivalue_line("markers", "parallel: marks tests safe for parallel execution")

def pytest_collection_modifyitems(config, items):
    """Modify test collection for optimization."""
    # Mark slow tests
    for item in items:
        # Mark tests that typically take longer
        if any(keyword in item.keywords for keyword in ['e2e', 'integration', 'slow']):
            item.add_marker(pytest.mark.slow)

        # Mark tests safe for parallel execution (most unit tests)
        if any(keyword in item.keywords for keyword in ['unit', 'smoke']):
            item.add_marker(pytest.mark.parallel)

# Custom command line options for performance tuning
def pytest_addoption(parser):
    """Add custom command line options."""
    parser.addoption(
        "--performance-report",
        action="store_true",
        default=False,
        help="Generate detailed performance report"
    )

    parser.addoption(
        "--skip-slow",
        action="store_true",
        default=False,
        help="Skip slow tests for faster CI runs"
    )

@pytest.fixture(autouse=True)
def skip_slow_tests(request):
    """Skip slow tests if requested."""
    if request.config.getoption("--skip-slow"):
        if request.node.get_closest_marker("slow"):
            pytest.skip("Skipping slow test")

# Optimized test data fixtures for common scenarios
@pytest.fixture
def single_material_workflow_data(session_test_data):
    """Pre-configured data for single material workflow tests."""
    return {
        "material": session_test_data["materials"][0]["name"],  # Extract name from dict
        "components": ["frontmatter", "text", "metatags"],
        "author": session_test_data["authors"][0],
        "expected_success_rate": 0.8
    }

@pytest.fixture
def batch_processing_data(session_test_data):
    """Pre-configured data for batch processing tests."""
    return {
        "materials": [m["name"] for m in session_test_data["materials"][:3]],  # Extract names from dicts
        "components": ["frontmatter", "text", "table"],
        "author_id": 1,
        "expected_min_components": 6  # 3 materials × 3 components × 0.67 success rate
    }

@pytest.fixture
def performance_test_data(session_test_data):
    """Pre-configured data for performance tests."""
    return {
        "material": session_test_data["materials"][0]["name"],  # Extract name from dict
        "components": ["frontmatter", "text", "metatags"],
        "author": session_test_data["authors"][0],
        "iterations": 3,
        "max_avg_time": 4.0,
        "max_peak_time": 6.0,
        "max_variance": 2.0
    }

@pytest.fixture
def error_recovery_data(session_test_data):
    """Pre-configured data for error recovery tests."""
    return {
        "material": session_test_data["materials"][0]["name"],  # Extract name from dict
        "components": ["frontmatter", "text", "metatags"],
        "author": session_test_data["authors"][0],
        "error_rate": 0.3,  # 30% failure rate for testing
        "expected_min_success": 1  # At least some components should succeed
    }
