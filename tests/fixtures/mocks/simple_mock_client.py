"""
Simple Mock API Client for Testing

Minimal mock implementation for test purposes only.
"""

from typing import Any
from api.client import APIResponse

class SimpleMockAPIClient:
    """Minimal mock API client for testing"""

    def __init__(self, provider_name: str = "mock"):
        self.provider_name = provider_name
        self.call_count = 0

    def generate_simple(self, request_data: Any) -> APIResponse:
        """Mock simple generation"""
        self.call_count += 1
        
        # Handle both dict and GenerationRequest object inputs
        if hasattr(request_data, 'material_name'):
            material_name = request_data.material_name
        elif isinstance(request_data, dict):
            material_name = request_data.get('material_name', 'unknown')
        else:
            material_name = 'unknown'
        
        # Return proper APIResponse instance
        return APIResponse(
            success=True,
            content=f"Mock {self.provider_name} response for {material_name}",
            token_count=100,
            response_time=0.1
        )

    def generate(self, request_data: Any) -> APIResponse:
        """Mock standard generation - alias for generate_simple for compatibility"""
        return self.generate_simple(request_data)

    def generate_streaming(self, request_data: Any):
        """Mock streaming generation"""
        self.call_count += 1
        
        # Handle both dict and GenerationRequest object inputs for consistency
        if hasattr(request_data, 'material_name'):
            material_name = request_data.material_name
        elif isinstance(request_data, dict):
            material_name = request_data.get('material_name', 'unknown')
        else:
            material_name = 'unknown'
            
        yield f"Mock streaming response from {self.provider_name} for {material_name}"

    def check_status(self) -> bool:
        """Mock status check"""
        return True

# Simple factory function 
def get_mock_client(provider_name: str = "mock") -> SimpleMockAPIClient:
    """Get a simple mock client"""
    return SimpleMockAPIClient(provider_name)

# Backward compatibility alias
MockAPIClient = SimpleMockAPIClient
