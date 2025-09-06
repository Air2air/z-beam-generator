#!/usr/bin/env python3
"""
Mock Infrastructure for Testing

This module provides reusable mock classes and fixtures for testing,
preventing import issues and providing consistent test infrastructure.
"""

import unittest.mock as mock
from typing import Dict, Any, Optional, List
from unittest.mock import MagicMock, Mock


class MockAPIClient:
    """Mock API client for testing component generators."""

    def __init__(self, responses: Optional[Dict[str, Any]] = None):
        self.responses = responses or {}
        self.call_history: List[Dict[str, Any]] = []

    def generate_content(self, prompt: str) -> Dict[str, Any]:
        """Mock generate_content method."""
        self.call_history.append({
            'method': 'generate_content',
            'prompt': prompt,
            'timestamp': mock.Mock()
        })

        # Return a default successful response
        return self.responses.get('generate_content', {
            'success': True,
            'content': f"Mock response for: {prompt[:50]}...",
            'usage': {'tokens': 100}
        })

    def get_status(self) -> Dict[str, Any]:
        """Mock get_status method."""
        return self.responses.get('get_status', {
            'status': 'ready',
            'model': 'mock-model'
        })

    def reset_statistics(self):
        """Reset call statistics."""
        self.call_history = []


class MockComponentGenerator:
    """Base mock component generator for testing."""

    def __init__(self, component_type: str = "mock"):
        self.component_type = component_type
        self.call_count = 0

    def generate(self, *args, **kwargs) -> Dict[str, Any]:
        """Mock generate method."""
        self.call_count += 1
        return {
            'component_type': self.component_type,
            'content': f"Mock {self.component_type} content",
            'success': True,
            'call_count': self.call_count
        }


class MockAuthorComponentGenerator(MockComponentGenerator):
    """Mock author component generator."""

    def __init__(self):
        super().__init__("author")

    def generate(self, material_name: str, material_data: Dict[str, Any],
                 api_client=None, **kwargs) -> Dict[str, Any]:
        result = super().generate(material_name, material_data, api_client, **kwargs)
        result['content'] = f"Mock author content for {material_name}"
        return result


class MockTableComponentGenerator(MockComponentGenerator):
    """Mock table component generator."""

    def __init__(self):
        super().__init__("table")

    def generate(self, material_name: str, material_data: Dict[str, Any],
                 api_client=None, **kwargs) -> Dict[str, Any]:
        result = super().generate(material_name, material_data, api_client, **kwargs)
        result['content'] = f"| Property | Value |\n|----------|-------|\n| Mock | Data |"
        return result


class MockFrontmatterComponentGenerator(MockComponentGenerator):
    """Mock frontmatter component generator."""

    def __init__(self):
        super().__init__("frontmatter")

    def generate(self, material_name: str, material_data: Dict[str, Any],
                 api_client=None, **kwargs) -> Dict[str, Any]:
        result = super().generate(material_name, material_data, api_client, **kwargs)
        result['content'] = f"---\nmaterial: {material_name}\ncategory: mock\n---"
        return result


class MockBadgesymbolComponentGenerator(MockComponentGenerator):
    """Mock badgesymbol component generator."""

    def __init__(self):
        super().__init__("badgesymbol")

    def generate(self, material_name: str, material_data: Dict[str, Any],
                 api_client=None, **kwargs) -> Dict[str, Any]:
        result = super().generate(material_name, material_data, api_client, **kwargs)
        result['content'] = f"🏷️ {material_name.upper()}"
        return result


class MockJsonldComponentGenerator(MockComponentGenerator):
    """Mock JSON-LD component generator."""

    def __init__(self):
        super().__init__("jsonld")

    def generate(self, material_name: str, material_data: Dict[str, Any],
                 api_client=None, **kwargs) -> Dict[str, Any]:
        result = super().generate(material_name, material_data, api_client, **kwargs)
        result['content'] = f'{{"@type": "Material", "name": "{material_name}"}}'
        return result


class MockMetatagsComponentGenerator(MockComponentGenerator):
    """Mock metatags component generator."""

    def __init__(self):
        super().__init__("metatags")

    def generate(self, material_name: str, material_data: Dict[str, Any],
                 api_client=None, **kwargs) -> Dict[str, Any]:
        result = super().generate(material_name, material_data, api_client, **kwargs)
        result['content'] = f'<meta name="description" content="About {material_name}">'
        return result


class MockPropertiestableComponentGenerator(MockComponentGenerator):
    """Mock propertiestable component generator."""

    def __init__(self):
        super().__init__("propertiestable")

    def generate(self, material_name: str, material_data: Dict[str, Any],
                 api_client=None, **kwargs) -> Dict[str, Any]:
        result = super().generate(material_name, material_data, api_client, **kwargs)
        result['content'] = f"| Property | Value |\n|----------|-------|\n| Density | Mock |"
        return result


class MockTagsComponentGenerator(MockComponentGenerator):
    """Mock tags component generator."""

    def __init__(self):
        super().__init__("tags")

    def generate(self, material_name: str, material_data: Dict[str, Any],
                 api_client=None, **kwargs) -> Dict[str, Any]:
        result = super().generate(material_name, material_data, api_client, **kwargs)
        result['content'] = f"laser-cleaning, {material_name.lower()}, material"
        return result


class MockBulletsComponentGenerator(MockComponentGenerator):
    """Mock bullets component generator."""

    def __init__(self):
        super().__init__("bullets")

    def generate(self, material_name: str, material_data: Dict[str, Any],
                 api_client=None, **kwargs) -> Dict[str, Any]:
        result = super().generate(material_name, material_data, api_client, **kwargs)
        result['content'] = f"- Mock bullet point for {material_name}\n- Another bullet point"
        return result


class MockCaptionComponentGenerator(MockComponentGenerator):
    """Mock caption component generator."""

    def __init__(self):
        super().__init__("caption")

    def generate(self, material_name: str, material_data: Dict[str, Any],
                 api_client=None, **kwargs) -> Dict[str, Any]:
        result = super().generate(material_name, material_data, api_client, **kwargs)
        result['content'] = f"Mock caption for {material_name}"
        return result


class MockTextComponentGenerator(MockComponentGenerator):
    """Mock text component generator."""

    def __init__(self):
        super().__init__("text")

    def generate(self, material_name: str, material_data: Dict[str, Any],
                 api_client=None, **kwargs) -> Dict[str, Any]:
        result = super().generate(material_name, material_data, api_client, **kwargs)
        result['content'] = f"Mock detailed content about {material_name} for laser cleaning applications."
        return result


# Factory function for creating mock generators
def create_mock_generator(component_type: str) -> MockComponentGenerator:
    """Factory function to create appropriate mock generator."""
    mock_generators = {
        'author': MockAuthorComponentGenerator,
        'table': MockTableComponentGenerator,
        'frontmatter': MockFrontmatterComponentGenerator,
        'badgesymbol': MockBadgesymbolComponentGenerator,
        'jsonld': MockJsonldComponentGenerator,
        'metatags': MockMetatagsComponentGenerator,
        'propertiestable': MockPropertiestableComponentGenerator,
        'tags': MockTagsComponentGenerator,
        'bullets': MockBulletsComponentGenerator,
        'caption': MockCaptionComponentGenerator,
        'text': MockTextComponentGenerator,
    }

    generator_class = mock_generators.get(component_type, MockComponentGenerator)
    return generator_class()


# Utility functions for testing
def mock_api_response(success: bool = True, content: str = "Mock content",
                     error: Optional[str] = None) -> Dict[str, Any]:
    """Create a mock API response."""
    return {
        'success': success,
        'content': content,
        'error': error,
        'usage': {'tokens': 100} if success else None
    }


def create_mock_material_data(material_name: str = "Aluminum") -> Dict[str, Any]:
    """Create mock material data for testing."""
    return {
        'name': material_name,
        'category': 'Metal',
        'properties': {
            'density': '2.7 g/cm³',
            'melting_point': '660°C'
        },
        'chemicalProperties': {
            'formula': 'Al',
            'symbol': 'Al'
        }
    }


# Export all mock classes
__all__ = [
    'MockAPIClient',
    'MockComponentGenerator',
    'MockAuthorComponentGenerator',
    'MockTableComponentGenerator',
    'MockFrontmatterComponentGenerator',
    'MockBadgesymbolComponentGenerator',
    'MockJsonldComponentGenerator',
    'MockMetatagsComponentGenerator',
    'MockPropertiestableComponentGenerator',
    'MockTagsComponentGenerator',
    'MockBulletsComponentGenerator',
    'MockCaptionComponentGenerator',
    'MockTextComponentGenerator',
    'create_mock_generator',
    'mock_api_response',
    'create_mock_material_data',
]
