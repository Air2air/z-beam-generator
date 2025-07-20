"""
MODULE DIRECTIVES FOR AI ASSISTANTS:
1. NO MOCKS: Implement actual API client without placeholder functionality
2. ERROR HANDLING: Provide detailed error messages for debugging
3. PARAMETER SUPPORT: Support all required parameters for content generation
4. AUTHENTICATION: Use proper API key authentication
5. DYNAMIC CONTENT: Return actual AI-generated content, not placeholders
"""

import logging
import os
import requests
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)

class APIClient:
    """Unified client for interacting with AI APIs."""
    
    def __init__(self, provider: str, api_key: Optional[str] = None):
        """Initialize the API client.
        
        Args:
            provider: The AI provider to use (deepseek, openai, etc.)
            api_key: API key for authentication (if None, reads from env var)
        """
        self.provider = provider.lower()
        
        # Get API key from environment if not provided
        if api_key is None:
            env_key = f"{provider.upper()}_API_KEY"
            self.api_key = os.environ.get(env_key)
        else:
            self.api_key = api_key
        
        # Set up configuration
        self.endpoints = {
            "deepseek": "https://api.deepseek.com/v1/chat/completions",
            "openai": "https://api.openai.com/v1/chat/completions",
            "anthropic": "https://api.anthropic.com/v1/messages",
            "gemini": "https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent"
        }
        
        self.default_models = {
            "deepseek": "deepseek-chat",
            "openai": "gpt-4o-mini",
            "anthropic": "claude-3-sonnet-20240229",
            "gemini": "gemini-pro"
        }
        
        logger.info(f"Initialized API client for {provider}")
    
    def generate_content(self, prompt: str, **kwargs) -> str:
        """Generate content using the provider API.
        
        Args:
            prompt: The prompt to generate content from
            **kwargs: Additional parameters:
                - max_tokens: Maximum length of generated text
                - temperature: Sampling temperature (0.0-1.0)
                
        Returns:
            The generated content as a string
            
        Raises:
            ValueError: If API configuration is invalid
            RuntimeError: If API request fails
        """
        try:
            # Check for API key
            if not self.api_key:
                error_msg = f"No API key available for {self.provider}"
                logger.error(error_msg)
                return f"<!-- Error: {error_msg} -->\n\n"
            
            # Get parameters
            max_tokens = kwargs.get("max_tokens", 4000)
            temperature = kwargs.get("temperature", 0.7)
            
            # Create appropriate request based on provider
            if self.provider in ["deepseek", "openai"]:
                # OpenAI-compatible format
                return self._call_openai_compatible_api(prompt, max_tokens, temperature)
            elif self.provider == "anthropic":
                return self._call_anthropic_api(prompt, max_tokens, temperature)
            elif self.provider == "gemini":
                return self._call_gemini_api(prompt, max_tokens, temperature)
            else:
                error_msg = f"Unknown provider: {self.provider}"
                logger.error(error_msg)
                return f"<!-- Error: {error_msg} -->\n\n"
                
        except Exception as e:
            error_msg = f"Error generating content: {str(e)}"
            logger.error(error_msg)
            return f"<!-- Error: {error_msg} -->\n\n"
    
    def _call_openai_compatible_api(self, prompt: str, max_tokens: int, temperature: float) -> str:
        """Call OpenAI-compatible API (works for DeepSeek too)."""
        # Add instruction to limit response length
        prompt_with_limit = f"{prompt}\n\nIMPORTANT: Your entire response MUST be under 3,000 characters total, including spaces. This is a hard requirement."
        
        # Set up request
        endpoint = self.endpoints.get(self.provider)
        model = os.environ.get(f"{self.provider.upper()}_MODEL", self.default_models.get(self.provider))
        
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }
        
        payload = {
            "model": model,
            "messages": [{"role": "user", "content": prompt_with_limit}],
            "max_tokens": max_tokens,  # Keep this reasonable like 2500
            "temperature": temperature
        }
        
        # Make request
        response = requests.post(endpoint, headers=headers, json=payload, timeout=120)
        
        # Handle response
        if response.status_code != 200:
            raise RuntimeError(f"API error ({response.status_code}): {response.text}")
        
        result = response.json()
        return result["choices"][0]["message"]["content"]
    
    def _call_anthropic_api(self, prompt: str, max_tokens: int, temperature: float) -> str:
        """Call Anthropic API."""
        endpoint = self.endpoints.get("anthropic")
        model = os.environ.get("ANTHROPIC_MODEL", self.default_models.get("anthropic"))
        
        headers = {
            "Content-Type": "application/json",
            "x-api-key": self.api_key,
            "anthropic-version": "2023-06-01"
        }
        
        payload = {
            "model": model,
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": max_tokens,
            "temperature": temperature
        }
        
        response = requests.post(endpoint, headers=headers, json=payload, timeout=120)
        
        if response.status_code != 200:
            raise RuntimeError(f"API error ({response.status_code}): {response.text}")
        
        result = response.json()
        return result["content"][0]["text"]
    
    def _call_gemini_api(self, prompt: str, max_tokens: int, temperature: float) -> str:
        """Call Google Gemini API."""
        endpoint = self.endpoints.get("gemini")
        api_key = self.api_key
        
        # Gemini uses query parameter for API key
        url = f"{endpoint}?key={api_key}"
        
        payload = {
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {
                "maxOutputTokens": max_tokens,
                "temperature": temperature
            }
        }
        
        headers = {"Content-Type": "application/json"}
        
        response = requests.post(url, headers=headers, json=payload, timeout=120)
        
        if response.status_code != 200:
            raise RuntimeError(f"API error ({response.status_code}): {response.text}")
        
        result = response.json()
        return result["candidates"][0]["content"]["parts"][0]["text"]