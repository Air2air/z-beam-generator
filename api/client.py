"""
API client for interacting with AI providers.

MODULE DIRECTIVES FOR AI ASSISTANTS:
1. NO CACHING: Client must not cache any API responses
2. FRESH API CALLS: Always make fresh API calls for each request
3. ERROR HANDLING: Provide clear error messages for API failures
4. CONSISTENT INTERFACE: Use generate_content as the primary method name
5. PROVIDER SUPPORT: Support multiple AI providers (deepseek, openai, etc.)
6. API KEY MANAGEMENT: Get API keys from environment variables
7. NO MOCKS: Never add mock responses or fallbacks
8. FAIL FAST: Always fail explicitly rather than degrading silently
9. CLEAR ERRORS: Error messages must identify the exact failure point
10. STRICT API: No modifications to provider API parameters
11. PURE INTEGRATION: This is an integration layer, not a simulation layer
12. VERSION TRACKING: Track API versions in logs for debugging
"""

import os
import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)

class ApiClient:
    """Client for interacting with AI APIs."""
    
    def __init__(self, ai_provider=None, provider=None, options=None, article_context=None):
        """Initialize API client with provider and options."""
        # Use either parameter name with ai_provider taking precedence
        self.ai_provider = ai_provider or provider or "deepseek"
        self.options = options or {}
        self.article_context = article_context or {}
        
        # Load API keys from environment variables
        self.api_keys = {
            "deepseek": os.environ.get("DEEPSEEK_API_KEY"),
            "openai": os.environ.get("OPENAI_API_KEY"),
            "gemini": os.environ.get("GEMINI_API_KEY"),
            "xai": os.environ.get("XAI_API_KEY")
        }
        
        # Set the API key for the current provider
        self.api_key = self.api_keys.get(self.ai_provider)
        
        logger.debug(f"Initialized ApiClient with provider={self.ai_provider}")
    
    def complete(self, prompt: str) -> str:
        """Complete a prompt using the configured provider."""
        try:
            # Get provider-specific API client
            if self.ai_provider == "deepseek":
                from api.providers.deepseek import DeepseekClient
                client = DeepseekClient(self.options)
            elif self.ai_provider == "openai":
                from api.providers.openai import OpenAIClient
                client = OpenAIClient(self.options)
            # Add other providers as needed
            else:
                raise ValueError(f"Unsupported AI provider: {self.ai_provider}")
            
            # Call provider's completion method
            return client.complete(prompt)
        except Exception as e:
            logger.error(f"API completion error with provider {self.ai_provider}: {str(e)}")
            raise
    
    # Alias for backward compatibility
    generate_content = complete