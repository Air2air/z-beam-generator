"""
Simple Mock API Client for Testing

Minimal mock implementation for test purposes only.
"""

from typing import Any, Dict
from unittest.mock import Mock

from api.client import APIResponse


class SimpleMockAPIClient:
    """Minimal mock API client for testing"""

    def __init__(self, provider_name: str = "mock"):
        self.provider_name = provider_name
        self.call_count = 0

    def generate_simple(self, request_data: Dict[str, Any]) -> APIResponse:
        """Mock simple generation"""
        self.call_count += 1
        
        # Return simple mock response
        response = Mock()
        response.success = True
        response.content = f"Mock {self.provider_name} response for {request_data.get('material_name', 'unknown')}"
        response.token_count = 100
        response.response_time = 0.1
        return response

    def generate_streaming(self, request_data: Dict[str, Any]):
        """Mock streaming generation"""
        self.call_count += 1
        yield f"Mock streaming response from {self.provider_name}"

    def check_status(self) -> bool:
        """Mock status check"""
        return True


# Simple factory function 
def get_mock_client(provider_name: str = "mock") -> SimpleMockAPIClient:
    """Get a simple mock client"""
    return SimpleMockAPIClient(provider_name)


# Backward compatibility alias
MockAPIClient = SimpleMockAPIClient
