#!/usr/bin/env python3
"""
Standardized DeepSeek API Client for Z-Beam Generator

Simple, clean API integration with:
- Standardized error handling
- Consistent response processing
- Environment-based API key management
- Proper timeout handling
"""

import os
import logging
import time
import requests
from typing import Optional
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class APIResponse:
    """Standardized API response structure."""
    success: bool
    content: str
    error_message: Optional[str] = None
    usage_tokens: Optional[int] = None
    response_time: Optional[float] = None


class DeepSeekAPIError(Exception):
    """Custom exception for DeepSeek API errors."""
    pass


class StandardizedDeepSeekClient:
    """Simplified, standardized DeepSeek API client."""
    
    def __init__(self, model: str = "deepseek-chat", max_tokens: int = 3000, temperature: float = 0.7):
        """Initialize the client with standardized parameters.
        
        Args:
            model: Model to use (default: deepseek-chat)
            max_tokens: Maximum tokens to generate
            temperature: Generation temperature
        """
        # Load API key from environment
        self.api_key = self._load_api_key()
        self.model = model
        self.max_tokens = max_tokens
        self.temperature = temperature
        self.api_url = "https://api.deepseek.com/v1/chat/completions"
        
        logger.info(f"Initialized DeepSeek client: model={model}, max_tokens={max_tokens}")
    
    def _load_api_key(self) -> str:
        """Load API key from environment with proper error handling."""
        api_key = os.environ.get("DEEPSEEK_API_KEY")
        
        if not api_key:
            raise DeepSeekAPIError(
                "DEEPSEEK_API_KEY not found in environment variables. "
                "Please set your API key in the .env file."
            )
        
        if len(api_key) < 20:  # Basic validation
            raise DeepSeekAPIError("DEEPSEEK_API_KEY appears to be invalid (too short)")
        
        logger.info(f"✅ DeepSeek API key loaded (length: {len(api_key)})")
        return api_key
    
    def generate(self, prompt: str, system_prompt: Optional[str] = None) -> APIResponse:
        """Generate content using DeepSeek API.
        
        Args:
            prompt: User prompt for generation
            system_prompt: Optional system prompt
            
        Returns:
            APIResponse with standardized structure
        """
        start_time = time.time()
        
        # Prepare messages
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})
        
        # Prepare request
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "User-Agent": "Z-Beam-Generator-Simple/1.0"
        }
        
        payload = {
            "model": self.model,
            "messages": messages,
            "temperature": self.temperature,
            "max_tokens": self.max_tokens,
            "stream": False
        }
        
        try:
            logger.info(f"📡 Sending request to DeepSeek API (prompt length: {len(prompt)} chars)")
            
            response = requests.post(
                self.api_url,
                headers=headers,
                json=payload,
                timeout=(10, 60)  # 10s connect, 60s read
            )
            
            response_time = time.time() - start_time
            
            # Handle HTTP errors
            if response.status_code != 200:
                error_msg = f"HTTP {response.status_code}: {response.text[:200]}"
                logger.error(f"❌ API request failed: {error_msg}")
                return APIResponse(
                    success=False,
                    content="",
                    error_message=error_msg,
                    response_time=response_time
                )
            
            # Parse response
            data = response.json()
            
            # Extract content
            if "choices" not in data or not data["choices"]:
                error_msg = "No choices in API response"
                logger.error(f"❌ Invalid response: {error_msg}")
                return APIResponse(
                    success=False,
                    content="",
                    error_message=error_msg,
                    response_time=response_time
                )
            
            content = data["choices"][0]["message"]["content"]
            usage_tokens = data.get("usage", {}).get("total_tokens", 0)
            
            logger.info(f"✅ Generated content: {len(content)} chars, {usage_tokens} tokens, {response_time:.2f}s")
            
            return APIResponse(
                success=True,
                content=content.strip(),
                usage_tokens=usage_tokens,
                response_time=response_time
            )
            
        except requests.exceptions.Timeout:
            error_msg = "Request timed out"
            logger.error(f"❌ {error_msg}")
            return APIResponse(
                success=False,
                content="",
                error_message=error_msg,
                response_time=time.time() - start_time
            )
            
        except requests.exceptions.ConnectionError as e:
            error_msg = f"Connection error: {str(e)}"
            logger.error(f"❌ {error_msg}")
            return APIResponse(
                success=False,
                content="",
                error_message=error_msg,
                response_time=time.time() - start_time
            )
            
        except Exception as e:
            error_msg = f"Unexpected error: {str(e)}"
            logger.error(f"❌ {error_msg}")
            return APIResponse(
                success=False,
                content="",
                error_message=error_msg,
                response_time=time.time() - start_time
            )
    
    def test_connection(self) -> APIResponse:
        """Test the API connection with a simple request."""
        test_prompt = "Say 'Hello' in exactly one word."
        system_prompt = "You are a helpful assistant. Respond with exactly one word."
        
        logger.info("🧪 Testing DeepSeek API connection...")
        result = self.generate(test_prompt, system_prompt)
        
        if result.success:
            logger.info("✅ API connection test successful")
        else:
            logger.error(f"❌ API connection test failed: {result.error_message}")
        
        return result


# Convenience function for easy import
def create_deepseek_client(model: str = "deepseek-chat", **kwargs) -> StandardizedDeepSeekClient:
    """Create a standardized DeepSeek client with default settings."""
    return StandardizedDeepSeekClient(model=model, **kwargs)


if __name__ == "__main__":
    # Test the client
    from dotenv import load_dotenv
    load_dotenv()
    
    client = create_deepseek_client()
    result = client.test_connection()
    
    if result.success:
        print(f"✅ Test successful: {result.content}")
    else:
        print(f"❌ Test failed: {result.error_message}")
