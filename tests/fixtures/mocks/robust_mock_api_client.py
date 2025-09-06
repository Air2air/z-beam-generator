#!/usr/bin/env python3
"""
Robust Mock API Client

Provides a reliable mock implementation for testing that eliminates brittleness
and provides consistent, predictable behavior.
"""

import json
import logging
import random
import time
from typing import Any, Dict, List, Optional, Union
from unittest.mock import MagicMock

logger = logging.getLogger(__name__)


class RobustMockAPIClient:
    """
    Robust mock API client that provides consistent, predictable responses.

    Eliminates brittleness by providing reliable mock behavior with proper
    error handling and response validation.
    """

    def __init__(self, provider: str = "grok", **kwargs):
        """
        Initialize the mock client.

        Args:
            provider: The API provider to mock (grok, deepseek, etc.)
            **kwargs: Additional configuration options
        """
        self.provider = provider
        self.response_delay = kwargs.get("response_delay", 0.1)
        self.error_rate = kwargs.get("error_rate", 0.0)
        self.max_retries = kwargs.get("max_retries", 3)

        # Response templates for different providers
        self.response_templates = self._load_response_templates()

        # Track request history for debugging
        self.request_history = []
        self.response_history = []

    def _load_response_templates(self) -> Dict[str, Dict[str, Any]]:
        """Load response templates for different providers."""
        return {
            "grok": {
                "success": {
                    "content": "This is a mock response from Grok API for {component_type} generation about {material}. The content is generated using advanced AI technology to provide comprehensive information about laser cleaning processes.",
                    "usage": {"tokens": 150, "cost": 0.002},
                    "model": "grok-1",
                },
                "error": {
                    "error": "Mock API error from Grok",
                    "code": "MOCK_ERROR",
                    "message": "Simulated API error for testing",
                },
            },
            "deepseek": {
                "success": {
                    "content": "DeepSeek AI generated content for {component_type} component regarding {material} laser cleaning. This response demonstrates the capabilities of advanced language models in technical content generation.",
                    "usage": {"tokens": 120, "cost": 0.0015},
                    "model": "deepseek-chat",
                },
                "error": {
                    "error": "Mock API error from DeepSeek",
                    "code": "DEEPSEEK_ERROR",
                    "message": "Simulated DeepSeek API error",
                },
            },
            "openai": {
                "success": {
                    "content": "OpenAI GPT-generated content for {component_type} about {material}. This mock response simulates the quality and structure of OpenAI's language models.",
                    "usage": {"tokens": 130, "cost": 0.0025},
                    "model": "gpt-4",
                },
                "error": {
                    "error": "Mock API error from OpenAI",
                    "code": "OPENAI_ERROR",
                    "message": "Simulated OpenAI API error",
                },
            },
        }

    def generate_content(
        self, prompt: str, component_type: str, material: str, **kwargs
    ) -> Dict[str, Any]:
        """
        Generate mock content for a component.

        Args:
            prompt: The generation prompt
            component_type: Type of component to generate
            material: Material being processed
            **kwargs: Additional parameters

        Returns:
            Dict containing the generated content and metadata
        """
        # Simulate API delay
        if self.response_delay > 0:
            time.sleep(self.response_delay)

        # Track request
        request_info = {
            "prompt": prompt[:100] + "..." if len(prompt) > 100 else prompt,
            "component_type": component_type,
            "material": material,
            "timestamp": time.time(),
        }
        self.request_history.append(request_info)

        # Simulate random errors if configured
        if random.random() < self.error_rate:
            error_response = self._generate_error_response()
            self.response_history.append({"type": "error", "response": error_response})
            raise Exception(error_response["error"]["message"])

        # Generate successful response
        response = self._generate_success_response(component_type, material, **kwargs)
        self.response_history.append({"type": "success", "response": response})

        return response

    def generate_simple(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        max_tokens: int = None,
        temperature: float = None,
    ):
        """
        Simplified generation method for backward compatibility.

        Matches the existing MockAPIClient interface.
        """
        from api.client import APIResponse, GenerationRequest

        # Create a GenerationRequest
        request = GenerationRequest(
            prompt=prompt,
            system_prompt=system_prompt,
            max_tokens=max_tokens or 4000,
            temperature=temperature or 0.7,
        )

        # Use the generate method
        return self.generate(request)

    def generate(self, request):
        """
        Generate content using the GenerationRequest object.

        Matches the existing MockAPIClient interface.
        """
        from api.client import APIResponse

        # Simulate API delay
        if self.response_delay > 0:
            time.sleep(self.response_delay)

        # Track request
        request_info = {
            "prompt": request.prompt[:100] + "..."
            if len(request.prompt) > 100
            else request.prompt,
            "timestamp": time.time(),
        }
        self.request_history.append(request_info)

        # Simulate random errors if configured
        if random.random() < self.error_rate:
            error_response = self._generate_error_response()
            self.response_history.append({"type": "error", "response": error_response})
            raise Exception(error_response["error"]["message"])

        # Generate content based on prompt
        content = self._generate_content_from_prompt(request.prompt)

        # Create APIResponse
        response = APIResponse(
            success=True,
            content=content,
            response_time=self.response_delay,
            token_count=len(content.split()),
            prompt_tokens=len(request.prompt.split()),
            completion_tokens=len(content.split()),
            model_used=self.provider,
            request_id=f"robust-mock-{len(self.request_history)}-{int(time.time())}",
        )

        self.response_history.append({"type": "success", "response": response})
        return response

    def _generate_content_from_prompt(self, prompt: str) -> str:
        """Generate mock response based on prompt content."""
        prompt_lower = prompt.lower()

        # Component-specific content
        if "frontmatter" in prompt_lower or "yaml" in prompt_lower:
            return self._generate_frontmatter_content()
        elif "table" in prompt_lower:
            return self._generate_table_content()
        elif "json" in prompt_lower:
            return self._generate_jsonld_content()
        elif "bullet" in prompt_lower:
            return self._generate_bullets_content()

        # Material-specific content
        materials = {
            "steel": ["steel", "iron"],
            "aluminum": ["aluminum", "aluminium"],
            "copper": ["copper"],
            "titanium": ["titanium"],
        }

        for material, keywords in materials.items():
            if any(keyword in prompt_lower for keyword in keywords):
                return getattr(self, f"_generate_{material}_content")()

        # Default content
        return self._generate_generic_content()

    def _generate_frontmatter_content(self) -> str:
        """Generate mock YAML frontmatter."""
        return """---
title: "Laser Cleaning Technology"
description: "Advanced laser cleaning for industrial applications"
date: "2024-01-15"
author: "AI Assistant"
category: "Technology"
tags: ["laser", "cleaning", "industrial"]
---"""

    def _generate_table_content(self) -> str:
        """Generate mock markdown table."""
        return """| Property | Value | Unit |
|----------|-------|------|
| Wavelength | 1064 | nm |
| Power | 100 | W |
| Speed | 500 | mm/s |"""

    def _generate_jsonld_content(self) -> str:
        """Generate mock JSON-LD."""
        return '{"@context": "https://schema.org", "@type": "Article", "title": "Laser Cleaning"}'

    def _generate_bullets_content(self) -> str:
        """Generate mock bullet points."""
        return "- High precision cleaning\n- No chemical residues\n- Environmentally friendly"

    def _generate_steel_content(self) -> str:
        """Generate mock steel-related content."""
        return "Steel laser cleaning involves removing contaminants using focused laser energy."

    def _generate_aluminum_content(self) -> str:
        """Generate mock aluminum-related content."""
        return "Aluminum laser cleaning provides precise surface preparation for various applications."

    def _generate_copper_content(self) -> str:
        """Generate mock copper-related content."""
        return "Copper laser cleaning effectively removes oxides and contaminants from surfaces."

    def _generate_titanium_content(self) -> str:
        """Generate mock titanium-related content."""
        return "Titanium laser cleaning maintains material integrity while removing surface contaminants."

    def _generate_generic_content(self) -> str:
        """Generate generic mock content."""
        return "This is mock content generated for testing purposes. It simulates AI-generated technical content."

    def _generate_success_response(
        self, component_type: str, material: str, **kwargs
    ) -> Dict[str, Any]:
        """Generate a successful response."""
        template = self.response_templates.get(self.provider, {}).get("success", {})

        # Customize content based on component type
        content = self._customize_content(template["content"], component_type, material)

        response = {
            "content": content,
            "usage": template.get("usage", {}),
            "model": template.get("model", "mock-model"),
            "provider": self.provider,
            "timestamp": time.time(),
        }

        return response

    def _customize_content(
        self, template: str, component_type: str, material: str
    ) -> str:
        """Customize the content template for specific component and material."""
        content = template.format(component_type=component_type, material=material)

        # Add component-specific content
        if component_type == "frontmatter":
            content += "\n---\ntitle: Laser Cleaning of {material}\nauthor: AI Assistant\ndate: 2024-01-01\n---"
        elif component_type == "text":
            content += "\n\n## Introduction\n{material} is commonly used in various industrial applications and can be effectively cleaned using laser technology.\n\n## Process\nThe laser cleaning process involves..."
        elif component_type == "table":
            content += "\n\n| Property | Value | Unit |\n|----------|-------|------|\n| Material | {material} | - |\n| Process | Laser Cleaning | - |"
        elif component_type == "bullets":
            content += "\n\n- High precision cleaning\n- No chemical residues\n- Environmentally friendly\n- Cost effective for {material}"

        return content.format(material=material)

    def _generate_error_response(self) -> Dict[str, Any]:
        """Generate an error response."""
        template = self.response_templates.get(self.provider, {}).get("error", {})
        return {"error": template, "provider": self.provider, "timestamp": time.time()}

    def get_request_history(self) -> List[Dict[str, Any]]:
        """Get the history of requests made to this client."""
        return self.request_history.copy()

    def get_response_history(self) -> List[Dict[str, Any]]:
        """Get the history of responses from this client."""
        return self.response_history.copy()

    def reset_history(self):
        """Reset the request and response history."""
        self.request_history.clear()
        self.response_history.clear()

    def set_error_rate(self, rate: float):
        """Set the error rate for this client (0.0 to 1.0)."""
        self.error_rate = max(0.0, min(1.0, rate))

    def set_response_delay(self, delay: float):
        """Set the response delay in seconds."""
        self.response_delay = max(0.0, delay)


class MockAPIClientFactory:
    """
    Factory for creating mock API clients with different configurations.
    """

    @staticmethod
    def create_client(provider: str = "grok", **kwargs) -> RobustMockAPIClient:
        """Create a mock API client."""
        return RobustMockAPIClient(provider, **kwargs)

    @staticmethod
    def create_failing_client(provider: str = "grok") -> RobustMockAPIClient:
        """Create a mock client that always fails."""
        return RobustMockAPIClient(provider, error_rate=1.0)

    @staticmethod
    def create_slow_client(provider: str = "grok") -> RobustMockAPIClient:
        """Create a mock client with slow responses."""
        return RobustMockAPIClient(provider, response_delay=2.0)

    @staticmethod
    def create_unreliable_client(provider: str = "grok") -> RobustMockAPIClient:
        """Create a mock client with occasional failures."""
        return RobustMockAPIClient(provider, error_rate=0.3)


class MockAPIManager:
    """
    Manages multiple mock API clients for testing scenarios.
    """

    def __init__(self):
        self.clients = {}
        self.default_provider = "grok"

    def get_client(self, provider: str = None) -> RobustMockAPIClient:
        """Get a mock client for the specified provider."""
        if provider is None:
            provider = self.default_provider

        if provider not in self.clients:
            self.clients[provider] = RobustMockAPIClient(provider)

        return self.clients[provider]

    def set_client(self, provider: str, client: RobustMockAPIClient):
        """Set a specific client for a provider."""
        self.clients[provider] = client

    def reset_all_clients(self):
        """Reset all clients and their history."""
        for client in self.clients.values():
            client.reset_history()

    def get_all_clients(self) -> Dict[str, RobustMockAPIClient]:
        """Get all managed clients."""
        return self.clients.copy()


# Backward compatibility - create aliases for existing code
MockAPIClient = RobustMockAPIClient


# Convenience functions
def create_mock_client(provider: str = "grok", **kwargs) -> RobustMockAPIClient:
    """Create a mock API client."""
    return RobustMockAPIClient(provider, **kwargs)


def create_test_client_manager() -> MockAPIManager:
    """Create a test API client manager."""
    return MockAPIManager()


# Export key classes and functions
__all__ = [
    "RobustMockAPIClient",
    "MockAPIClientFactory",
    "MockAPIManager",
    "MockAPIClient",  # Backward compatibility
    "create_mock_client",
    "create_test_client_manager",
]
