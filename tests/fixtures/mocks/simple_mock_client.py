#!/usr/bin/env python3
"""
Simple Mock API Client for Testing

Provides a lightweight mock implementation for testing without real API calls.
This is ONLY for test code - never used in production.
"""

from typing import Optional, Dict, Any
from dataclasses import dataclass


@dataclass
class MockAPIResponse:
    """Mock API response object"""
    content: str
    provider: str
    model: str
    tokens_used: int = 100
    success: bool = True


class MockAPIClient:
    """
    Mock API client for testing purposes only.
    
    This mock is ONLY used in test code to avoid real API calls.
    Production code must use real API clients with fail-fast validation.
    """

    def __init__(self, provider: str = "mock"):
        self.provider = provider
        self.model = "mock-model"
        self.call_count = 0
        self.response_delay = 0.0
        self.should_fail = False
        self.failure_count = 0
        self.custom_responses: Dict[str, str] = {}

    def generate(
        self,
        prompt: str,
        max_tokens: Optional[int] = None,
        temperature: float = 0.7,
        **kwargs
    ) -> MockAPIResponse:
        """
        Generate mock response.
        
        For testing only - simulates API response without network calls.
        """
        import time
        
        self.call_count += 1

        if self.response_delay > 0:
            time.sleep(self.response_delay)

        if self.should_fail:
            self.failure_count += 1
            raise Exception("Mock API failure (simulated for testing)")

        # Check for custom responses
        for key, response in self.custom_responses.items():
            if key.lower() in prompt.lower():
                return MockAPIResponse(
                    content=response,
                    provider=self.provider,
                    model=self.model,
                    tokens_used=len(response.split())
                )

        # Generate appropriate mock content based on prompt keywords
        content = self._generate_mock_content(prompt)

        return MockAPIResponse(
            content=content,
            provider=self.provider,
            model=self.model,
            tokens_used=len(content.split())
        )

    def _generate_mock_content(self, prompt: str) -> str:
        """Generate contextually appropriate mock content"""
        prompt_lower = prompt.lower()

        if "frontmatter" in prompt_lower or "yaml" in prompt_lower:
            return self._mock_frontmatter()
        elif "metatag" in prompt_lower:
            return self._mock_metatags()
        elif "json-ld" in prompt_lower or "jsonld" in prompt_lower:
            return self._mock_jsonld()
        elif "micro" in prompt_lower:
            return "Mock micro for laser cleaning process."
        elif "table" in prompt_lower:
            return self._mock_table()
        else:
            return "Mock AI-generated content for testing purposes."

    def _mock_frontmatter(self) -> str:
        """Generate mock frontmatter YAML"""
        return """---
title: "Mock Material for Testing"
category: "Metal"
density: 4.5
hardness: 6.0
---"""

    def _mock_metatags(self) -> str:
        """Generate mock meta tags"""
        return """<meta name="description" content="Mock description">
<meta name="keywords" content="laser, cleaning, mock">"""

    def _mock_jsonld(self) -> str:
        """Generate mock JSON-LD"""
        return """{
  "@context": "https://schema.org",
  "@type": "Article",
  "name": "Mock Article"
}"""

    def _mock_table(self) -> str:
        """Generate mock properties table"""
        return """| Property | Value | Unit |
|----------|-------|------|
| Density  | 4.5   | g/cm³|
| Hardness | 6.0   | Mohs |"""

    def set_custom_response(self, keyword: str, response: str):
        """Set a custom response for prompts containing a keyword"""
        self.custom_responses[keyword] = response

    def reset(self):
        """Reset mock state"""
        self.call_count = 0
        self.failure_count = 0
        self.should_fail = False
        self.custom_responses = {}

    def configure_failure(self, should_fail: bool = True):
        """Configure mock to simulate failures"""
        self.should_fail = should_fail

    def get_stats(self) -> Dict[str, Any]:
        """Get mock client statistics"""
        return {
            "call_count": self.call_count,
            "failure_count": self.failure_count,
            "provider": self.provider,
            "model": self.model
        }
