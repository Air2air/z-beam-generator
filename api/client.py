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
        # Use either parameter name with ai_provider taking precedence - no fallbacks
        if ai_provider:
            self.ai_provider = ai_provider
        elif provider:
            self.ai_provider = provider
        else:
            raise ValueError("Either ai_provider or provider must be specified")
        
        if options is None:
            raise ValueError("options parameter must be provided")
        self.options = options
        
        if article_context is None:
            raise ValueError("article_context parameter must be provided")
        self.article_context = article_context
        
        # Load only the required API key for the current provider - no fallbacks
        api_key_map = {
            "deepseek": "DEEPSEEK_API_KEY",
            "openai": "OPENAI_API_KEY", 
            "gemini": "GEMINI_API_KEY",
            "xai": "XAI_API_KEY"
        }
        
        if self.ai_provider not in api_key_map:
            raise ValueError(f"Unsupported AI provider: {self.ai_provider}")
        
        # Get the specific API key for this provider
        api_key_name = api_key_map[self.ai_provider]
        if api_key_name not in os.environ:
            raise ValueError(f"Missing environment variable: {api_key_name}")
        
        self.api_key = os.environ[api_key_name]
        
        logger.debug(f"Initialized ApiClient with provider={self.ai_provider}")
    
    def complete(self, prompt: str) -> str:
        """Complete a prompt using the configured provider."""
        try:
            # Get provider-specific API client
            if self.ai_provider == "deepseek":
                from api.deepseek import DeepseekClient
                client = DeepseekClient(self.options)
            elif self.ai_provider == "openai":
                # Import OpenAI client when implemented
                raise ValueError("OpenAI provider not yet implemented")
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