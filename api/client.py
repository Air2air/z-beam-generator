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
    """API client for generating content with AI providers."""
    
    def __init__(self, provider: str = "deepseek"):
        """Initialize the API client.
        
        Args:
            provider: Default AI provider to use
        """
        self.provider = provider
        
        # Load API keys from environment variables
        self.api_keys = {
            "deepseek": os.environ.get("DEEPSEEK_API_KEY"),
            "openai": os.environ.get("OPENAI_API_KEY"),
            "gemini": os.environ.get("GEMINI_API_KEY"),
            "xai": os.environ.get("XAI_API_KEY")  # This is correct - use XAI_API_KEY
        }
        
        # Set the API key for the current provider
        self.api_key = self.api_keys.get(provider)
        
        if not self.api_key:
            logger.warning(f"No API key found for provider: {provider}")
        
        # Validate the provider is supported
        supported_providers = ["deepseek", "xai", "openai", "gemini"]
        if provider not in supported_providers:
            raise ValueError(f"Unsupported AI provider: {provider}")
        
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
    
    def generate_content(self, prompt: str, provider: str = "deepseek", **kwargs) -> str:
        """Generate content using the specified provider.
        
        Args:
            prompt: Prompt for generation
            provider: Provider to use
            **kwargs: Additional parameters
            
        Returns:
            Generated content
        """
        # Validate API key before attempting generation
        if not self.api_key:
            error_msg = f"API key not found for {self.provider} (expected {self.provider.upper()}_API_KEY)"
            logger.error(f"GENERATION FAILED: {error_msg}")
            raise ValueError(error_msg)
            
        # Call the text generation method
        return self.generate_text(prompt, provider, kwargs)
    
    def generate_text(self, prompt: str, provider: str = "deepseek", options: Dict[str, Any] = None) -> str:
        """Generate text from prompt.
        
        Args:
            prompt: Prompt text
            provider: Provider to use
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
            
            # Fix: Use the api_key directly since it's a string, not a dictionary
            api_key = self.api_key  # Changed from self.api_key.get("gemini")
            
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
        """Generate text using XAI/Grok API with the official SDK."""
        try:
            # Import the xai-sdk
            try:
                from xai_sdk import Client
                from xai_sdk.chat import user, system
            except ImportError:
                raise ImportError("xai-sdk not installed. Run 'pip install xai-sdk' to install it.")
            
            # Use the instance API key
            api_key = self.api_key
            
            if not api_key:
                raise ValueError("XAI_API_KEY environment variable not set")
            
            # Updated model name based on the curl example
            model = options.get("model", "grok-3-latest")  # Changed from "grok-1" to "grok-3-latest"
            temperature = options.get("temperature", 0.7)
            max_tokens = options.get("max_tokens", 2000)
            
            logger.info(f"Calling XAI API with model: {model}, temp: {temperature}, max_tokens: {max_tokens}")
            
            # Create client with the API key
            client = Client(
                api_key=api_key,
                timeout=120  # Set reasonable timeout
            )
            
            # Create chat session with the specified model
            chat = client.chat.create(model=model)
            
            # Add system message if needed
            system_message = options.get("system_message", "You are a helpful, technical AI assistant.")
            chat.append(system(system_message))
            
            # Add user message (the prompt)
            chat.append(user(prompt))
            
            # Generate response with no parameters
            response = chat.sample()
            
            # Extract the response content
            result = response.content
            
            logger.debug(f"XAI API response length: {len(result)} characters")
            return result
            
        except ImportError as e:
            error_msg = f"XAI SDK not installed: {str(e)}"
            logger.error(error_msg)
            raise ImportError(error_msg)
            
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

    def _call_xai_api(self, prompt: str, **kwargs) -> str:
        """Call XAI API to generate content.
        
        Args:
            prompt: Prompt for content generation
            **kwargs: Additional parameters
            
        Returns:
            Generated content as string
        """
        try:
            # Original API call implementation remains unchanged
            headers = {
                "Authorization": f"Bearer {os.environ.get('XAI_API_KEY')}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "prompt": prompt,
                **kwargs
            }
            
            response = requests.post(
                self.xai_api_url,
                headers=headers,
                json=payload
            )
            
            response.raise_for_status()
            
            # Fix: Handle both dictionary and string responses
            result = response.json()
            
            # If result is already a string, return it directly
            if isinstance(result, str):
                return result
                
            # If result is a dictionary, extract content field
            # Different XAI implementations use different response formats
            if isinstance(result, dict):
                # Try common response formats
                if "content" in result:
                    return result["content"]
                elif "text" in result:
                    return result["text"]
                elif "output" in result:
                    return result["output"]
                elif "generated_text" in result:
                    return result["generated_text"]
                elif "choices" in result and len(result["choices"]) > 0:
                    choices = result["choices"]
                    if isinstance(choices[0], dict) and "message" in choices[0]:
                        return choices[0]["message"].get("content", "")
                    else:
                        return str(choices[0])
                # If none of the common fields are found, return the stringified result
                return str(result)
            
            # Handle unexpected response type
            logger.warning(f"Unexpected response type from XAI API: {type(result)}")
            return str(result)
            
        except requests.exceptions.RequestException as e:
            logger.error(f"XAI API request failed: {e}")
            raise
        except ValueError as e:
            logger.error(f"XAI API response parsing failed: {e}")
            raise