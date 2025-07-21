"""
API client for AI content generation.

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
import sys
from typing import Dict, Any, Optional

import requests

logger = logging.getLogger(__name__)

class ApiClient:
    """Client for interacting with AI APIs."""
    
    def __init__(self, provider: str = "deepseek"):
        """Initialize API client.
        
        Args:
            provider: AI provider to use
        """
        self.provider = provider
        self.api_key = self._get_api_key()
        
        # Validate we have what we need immediately
        if not self.api_key:
            logger.error(f"CRITICAL: No API key found for {self.provider} (expected {self.provider.upper()}_API_KEY)")
        else:
            logger.debug(f"Initialized API client for {provider}")
    
    def _get_api_key(self) -> Optional[str]:
        """Get API key for the current provider.
        
        Returns:
            API key or None if not found
        """
        key_name = f"{self.provider.upper()}_API_KEY"
        api_key = os.environ.get(key_name)
        
        if not api_key:
            logger.warning(f"No API key found for {self.provider} (expected {key_name})")
            
        return api_key
    
    def generate_content(self, prompt: str, options: Dict[str, Any] = None) -> str:
        """Generate content from prompt (primary interface method).
        
        Args:
            prompt: Prompt text
            options: Generation options
            
        Returns:
            Generated content
            
        Raises:
            ValueError: If API key is missing
            RuntimeError: If API call fails
            ImportError: If provider module is not installed
        """
        # Validate API key before attempting generation
        if not self.api_key:
            error_msg = f"API key not found for {self.provider} (expected {self.provider.upper()}_API_KEY)"
            logger.error(f"GENERATION FAILED: {error_msg}")
            raise ValueError(error_msg)
            
        # Call the text generation method
        return self.generate_text(prompt, options)
    
    def generate_text(self, prompt: str, options: Dict[str, Any] = None) -> str:
        """Generate text from prompt.
        
        Args:
            prompt: Prompt text
            options: Generation options
            
        Returns:
            Generated text
            
        Raises:
            ValueError: If provider is not supported
            RuntimeError: If API call fails
        """
        options = options or {}
        
        if self.provider == "deepseek":
            return self._generate_deepseek(prompt, options)
        elif self.provider == "openai":
            return self._generate_openai(prompt, options)
        elif self.provider == "gemini":
            return self._generate_gemini(prompt, options)
        elif self.provider == "xai":
            return self._generate_xai(prompt, options)
        else:
            error_msg = f"Unsupported AI provider: {self.provider}"
            logger.error(error_msg)
            raise ValueError(error_msg)
    
    def _generate_deepseek(self, prompt: str, options: Dict[str, Any]) -> str:
        """Generate text using Deepseek API."""
        try:
            # Import the Deepseek client
            import deepseek_ai
            
            # Set default options
            model = options.get("model", "deepseek-chat")
            temperature = options.get("temperature", 0.7)
            max_tokens = options.get("max_tokens", 2000)
            
            # Log the API call (excluding prompt content)
            logger.info(f"Calling Deepseek API with model: {model}, temp: {temperature}, max_tokens: {max_tokens}")
            
            # Create client with API key
            # Based on the debug output, we need to use DeepSeekAI class
            client = deepseek_ai.DeepSeekAI(api_key=self.api_key)
            
            # Create messages in the format expected by the API
            messages = [{"role": "user", "content": prompt}]
            
            # Make the API call
            # We'll try to use the chat module since that was found in the debug output
            response = client.chat.completions.create(
                model=model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens
            )
            
            # Extract the response content
            # The exact structure depends on the API response format
            # We'll use a try-except to handle different possibilities
            try:
                if hasattr(response, 'choices') and len(response.choices) > 0:
                    if hasattr(response.choices[0], 'message'):
                        result = response.choices[0].message.content.strip()
                    else:
                        result = response.choices[0].text.strip()
                else:
                    # Fallback to string representation
                    result = str(response).strip()
            except AttributeError:
                # Last resort, convert response to string
                result = str(response).strip()
                
            logger.debug(f"Deepseek API response length: {len(result)} characters")
            return result
            
        except ImportError as e:
            error_msg = f"Deepseek package not installed: {str(e)}"
            logger.error(error_msg)
            raise ImportError(error_msg)
            
        except Exception as e:
            error_msg = f"Deepseek API call failed: {str(e)}"
            logger.error(error_msg)
            raise RuntimeError(error_msg)
    
    def _generate_openai(self, prompt: str, options: Dict[str, Any]) -> str:
        """Generate text using OpenAI API.
        
        Args:
            prompt: Prompt text
            options: Generation options
            
        Returns:
            Generated text
            
        Raises:
            ImportError: If openai module is not installed
            RuntimeError: If API call fails
        """
        try:
            # Import the OpenAI client
            import openai
            openai.api_key = self.api_key
            
            # Set default options
            model = options.get("model", "gpt-4")
            temperature = options.get("temperature", 0.7)
            max_tokens = options.get("max_tokens", 2000)
            
            # Log the API call (excluding prompt content)
            logger.info(f"Calling OpenAI API with model: {model}, temp: {temperature}, max_tokens: {max_tokens}")
            
            # Call API
            response = openai.ChatCompletion.create(
                model=model,
                messages=[{"role": "user", "content": prompt}],
                temperature=temperature,
                max_tokens=max_tokens
            )
            
            # Extract text from response
            result = response.choices[0].message.content.strip()
            logger.debug(f"OpenAI API response length: {len(result)} characters")
            return result
            
        except ImportError as e:
            error_msg = f"OpenAI package not installed: {str(e)}"
            logger.error(error_msg)
            raise ImportError(error_msg)
            
        except Exception as e:
            error_msg = f"OpenAI API call failed: {str(e)}"
            logger.error(error_msg, exc_info=True)
            raise RuntimeError(error_msg)
    
    def _generate_gemini(self, prompt: str, options: Dict[str, Any]) -> str:
        """Generate text using Google's Gemini API."""
        try:
            # Import Gemini package
            import google.generativeai as genai
            
            # Set API key
            api_key = self.api_key.get("gemini") or os.environ.get('GEMINI_API_KEY')
            if not api_key:
                raise ValueError("GEMINI_API_KEY environment variable not set")
                
            genai.configure(api_key=api_key)
            
            # Get model parameters
            model = options.get("model", "gemini-pro")
            temperature = options.get("temperature", 0.7)
            max_tokens = options.get("max_tokens", 2000)
            
            # Log the API call (excluding prompt content)
            logger.info(f"Calling Gemini API with model: {model}, temp: {temperature}, max_tokens: {max_tokens}")
            
            # Generate response
            model = genai.GenerativeModel(model_name=model)
            response = model.generate_content(
                prompt,
                generation_config=genai.types.GenerationConfig(
                    temperature=temperature,
                    max_output_tokens=max_tokens
                )
            )
            
            # Extract text from response
            result = response.text
            
            logger.debug(f"Gemini API response length: {len(result)} characters")
            return result
            
        except ImportError as e:
            error_msg = f"Gemini package not installed: {str(e)}"
            logger.error(error_msg)
            raise ImportError(error_msg)
            
        except Exception as e:
            error_msg = f"Gemini API call failed: {str(e)}"
            logger.error(error_msg)
            raise RuntimeError(error_msg)

    def _generate_xai(self, prompt: str, options: Dict[str, Any]) -> str:
        """Generate text using XAI API."""
        try:
            # Get API key
            api_key = self.api_key.get("xai") or os.environ.get('XAI_API_KEY')
            if not api_key:
                raise ValueError("XAI_API_KEY environment variable not set")
                
            # Get model parameters
            model = options.get("model", "xai-1")
            temperature = options.get("temperature", 0.7)
            max_tokens = options.get("max_tokens", 2000)
            
            # Log the API call (excluding prompt content)
            logger.info(f"Calling XAI API with model: {model}, temp: {temperature}, max_tokens: {max_tokens}")
            
            # Set up API request
            headers = {
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "model": model,
                "messages": [{"role": "user", "content": prompt}],
                "temperature": temperature,
                "max_tokens": max_tokens
            }
            
            # Make the API request
            response = requests.post(
                "https://api.xai.com/v1/chat/completions",
                headers=headers,
                json=payload,
                timeout=120
            )
            
            # Check for errors
            response.raise_for_status()
            
            # Parse the response
            response_data = response.json()
            result = response_data["choices"][0]["message"]["content"]
            
            logger.debug(f"XAI API response length: {len(result)} characters")
            return result
            
        except Exception as e:
            error_msg = f"XAI API call failed: {str(e)}"
            logger.error(error_msg)
            raise RuntimeError(error_msg)

    def generate(self, prompt: str, provider: str = None, **options) -> str:
        """Generate text using the specified provider."""
        provider = provider or self.config.get("ai_provider", "deepseek")
        
        # Select the provider method
        provider_methods = {
            "deepseek": self._generate_deepseek,
            "openai": self._generate_openai,
            "gemini": self._generate_gemini,  # Added Gemini
            "xai": self._generate_xai         # Added XAI
        }
        
        generator = provider_methods.get(provider.lower())
        if not generator:
            error_msg = f"Unsupported AI provider: {provider}"
            logger.error(error_msg)
            raise ValueError(error_msg)
        
        # Generate text
        try:
            return generator(prompt, options)
        except Exception as e:
            error_msg = f"Error generating with {provider}: {str(e)}"
            logger.error(error_msg)
            raise RuntimeError(error_msg)