#!/usr/bin/env python3
"""
Test Fixtures and Utilities

Provides common test fixtures, utilities, and setup/teardown
functions for the test suite.
"""

import pytest
import sys
from pathlib import Path
from typing import Dict, Any

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from tests.test_config import test_config, get_test_api_client, setup_test_environment, teardown_test_environment


@pytest.fixture(scope="session", autouse=True)
def setup_test_session():
    """Setup for the entire test session"""
    setup_test_environment()
    yield
    teardown_test_environment()


@pytest.fixture
def mock_api_client():
    """Fixture providing a mock API client for fast testing"""
    return get_test_api_client()


@pytest.fixture
def fast_mock_client():
    """Fixture providing a very fast mock client for unit tests"""
    from tests.mocks.mock_api_client import create_fast_mock_client
    return create_fast_mock_client()


@pytest.fixture
def test_materials():
    """Fixture providing common test materials"""
    return {
        'steel': {
            'name': 'Steel',
            'formula': 'Fe',
            'category': 'metal',
            'properties': {
                'melting_point': 1538,
                'thermal_conductivity': 50.2,
                'density': 7850
            }
        },
        'aluminum': {
            'name': 'Aluminum',
            'formula': 'Al',
            'category': 'metal',
            'properties': {
                'melting_point': 660,
                'thermal_conductivity': 237,
                'density': 2700
            }
        },
        'titanium': {
            'name': 'Titanium',
            'formula': 'Ti',
            'category': 'metal',
            'properties': {
                'melting_point': 1668,
                'thermal_conductivity': 21.9,
                'density': 4507
            }
        }
    }


@pytest.fixture
def sample_frontmatter():
    """Fixture providing sample frontmatter data"""
    return {
        'title': 'Laser Cleaning Applications',
        'description': 'Comprehensive guide to laser cleaning technology',
        'material': 'Steel',
        'category': 'Industrial Applications',
        'author': 'Test Author',
        'date': '2025-01-01',
        'tags': ['laser', 'cleaning', 'industrial'],
        'properties': {
            'wavelength': '1064nm',
            'power': '100W',
            'material_thickness': '2mm'
        }
    }


@pytest.fixture
def sample_authors():
    """Fixture providing sample author data"""
    return [
        {
            'id': 1,
            'name': 'Yi-Chun Lin',
            'title': 'Ph.D.',
            'country': 'Taiwan',
            'expertise': 'Laser Materials Processing'
        },
        {
            'id': 2,
            'name': 'Alessandro Moretti',
            'title': 'Ph.D.',
            'country': 'Italy',
            'expertise': 'Laser-Based Additive Manufacturing'
        }
    ]


@pytest.fixture
def mock_component_result():
    """Fixture providing a mock component result"""
    class MockComponentResult:
        def __init__(self, component_type: str, content: str, success: bool = True):
            self.component_type = component_type
            self.content = content
            self.success = success
            self.error_message = None if success else "Mock error"

    return MockComponentResult


@pytest.fixture
def temp_test_dir(tmp_path):
    """Fixture providing a temporary directory for tests"""
    return tmp_path


# Test utilities
def assert_api_response_format(response: Dict[str, Any]):
    """Assert that an API response has the correct format"""
    assert isinstance(response, dict)
    assert 'success' in response
    assert 'content' in response
    assert 'usage' in response
    assert isinstance(response['usage'], dict)


def assert_component_result_format(result):
    """Assert that a component result has the correct format"""
    assert hasattr(result, 'component_type')
    assert hasattr(result, 'content')
    assert hasattr(result, 'success')
    assert result.component_type is not None
    assert isinstance(result.content, str)
    assert isinstance(result.success, bool)


def create_test_prompt(material: str, context: str = "") -> str:
    """Create a test prompt for content generation"""
    return f"""Generate technical content about laser cleaning of {material}.

Context: {context}

Requirements:
- Focus on technical specifications and process parameters
- Include material properties and their relevance to laser cleaning
- Describe optimal laser parameters for this material
- Discuss surface preparation and quality considerations

Please provide detailed, technical information suitable for industrial applications."""


def benchmark_api_call(client, prompt: str, iterations: int = 5) -> Dict[str, float]:
    """Benchmark API call performance"""
    import time

    times = []
    for _ in range(iterations):
        start_time = time.time()
        response = client.generate_content(prompt)
        end_time = time.time()
        times.append(end_time - start_time)
        assert response['success']

    return {
        'min_time': min(times),
        'max_time': max(times),
        'avg_time': sum(times) / len(times),
        'total_time': sum(times)
    }


# Custom pytest markers
def pytest_configure(config):
    """Configure custom pytest markers"""
    config.addinivalue_line("markers", "slow: mark test as slow running")
    config.addinivalue_line("markers", "integration: mark test as integration test")
    config.addinivalue_line("markers", "unit: mark test as unit test")
    config.addinivalue_line("markers", "mock: mark test as using mock clients")
    config.addinivalue_line("markers", "real_api: mark test as using real API calls")


# Test data caching utilities
class TestDataCache:
    """Simple cache for test data to avoid repeated API calls"""

    def __init__(self, cache_dir: str = "./test_cache"):
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(exist_ok=True)

    def get(self, key: str) -> Any:
        """Get cached data"""
        cache_file = self.cache_dir / f"{key}.json"
        if cache_file.exists():
            import json
            with open(cache_file, 'r') as f:
                return json.load(f)
        return None

    def set(self, key: str, data: Any):
        """Set cached data"""
        cache_file = self.cache_dir / f"{key}.json"
        import json
        with open(cache_file, 'w') as f:
            json.dump(data, f, indent=2)

    def clear(self):
        """Clear all cached data"""
        import shutil
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
