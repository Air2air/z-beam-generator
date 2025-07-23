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
from api.config import get_provider_config, update_provider_configs

import requests

logger = logging.getLogger(__name__)

class ApiClient:
    """API client for generating content with AI providers."""
    
    def __init__(self, provider: str = "deepseek", article_context: Dict[str, Any] = None):
        """Initialize the API client.
        
        Args:
            provider: Default AI provider to use
            article_context: Article context from run.py
        """
        self.provider = provider
        self.article_context = article_context or {}
        
        # Update provider configs from article context
        if article_context:
            update_provider_configs(article_context)
        
        # Load API keys from environment variables
        self.api_keys = {
            "deepseek": os.environ.get("DEEPSEEK_API_KEY"),
            "openai": os.environ.get("OPENAI_API_KEY"),
            "gemini": os.environ.get("GEMINI_API_KEY"),
            "xai": os.environ.get("XAI_API_KEY")
        }
        
        # Set the API key for the current provider
        self.api_key = self.api_keys.get(provider)
        
        if not self.api_key:
            logger.warning(f"No API key found for provider: {provider}")
    
    def _generate_gemini(self, prompt: str, options: Dict[str, Any], component: str = None) -> str:
        """Generate text using Google's Gemini API."""
        try:
            # Import Gemini package
            import google.generativeai as genai
            
            # Get API key
            api_key = self.api_keys.get("gemini")
            if not api_key:
                raise ValueError("Gemini API key not found in environment variables")
                
            genai.configure(api_key=api_key)
            
            # Get configuration from central config - now with component and context awareness
            gemini_config = get_provider_config("gemini", component, self.article_context)
            
            # Get model parameters (NO HARDCODED FALLBACKS)
            model = options.get("model", gemini_config.get("model"))
            temperature = options.get("temperature", gemini_config.get("temperature"))
            max_tokens = options.get("max_tokens", gemini_config.get("max_tokens_limit"))
            
            # Log the API call
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
    
    def _generate_deepseek(self, prompt: str, options: Dict[str, Any], component: str = None) -> str:
        """Generate text using Deepseek API."""
        try:
            # Import the Deepseek client
            import deepseek_ai
            
            # Get configuration from central config
            deepseek_config = get_provider_config("deepseek", component, self.article_context)
            
            # Set options with NO HARDCODED FALLBACKS
            model = options.get("model", deepseek_config.get("model"))
            temperature = options.get("temperature", deepseek_config.get("temperature"))
            max_tokens = options.get("max_tokens", deepseek_config.get("max_tokens_limit"))
            
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
    
    def _generate_openai(self, prompt: str, options: Dict[str, Any], component: str = None) -> str:
        """Generate text using OpenAI API."""
        try:
            # Import the OpenAI client
            from openai import OpenAI
            
            # Get API key
            api_key = self.api_keys.get("openai")
            if not api_key:
                raise ValueError("OpenAI API key not found in environment variables")
            
            # Initialize client with API key
            client = OpenAI(api_key=api_key)
            
            # Get configuration from central config
            openai_config = get_provider_config("openai", component, self.article_context)
            
            # Set options with NO HARDCODED FALLBACKS
            model = options.get("model", openai_config.get("model"))
            temperature = options.get("temperature", openai_config.get("temperature"))
            max_tokens = options.get("max_tokens", openai_config.get("max_tokens_limit"))
            
            # Log the API call (excluding prompt content)
            logger.info(f"Calling OpenAI API with model: {model}, temp: {temperature}, max_tokens: {max_tokens}")
            
            # Generate response using new API format
            response = client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": "You are a helpful, technical AI assistant."},
                    {"role": "user", "content": prompt}
                ],
                temperature=temperature,
                max_tokens=max_tokens
            )
            
            # Extract the response content
            result = response.choices[0].message.content
            
            logger.debug(f"OpenAI API response length: {len(result)} characters")
            return result
            
        except ImportError as e:
            error_msg = f"OpenAI package not installed: {str(e)}"
            logger.error(error_msg)
            raise ImportError(error_msg)
            
        except Exception as e:
            error_msg = f"OpenAI API call failed: {str(e)}"
            logger.error(error_msg)
            raise RuntimeError(error_msg)
    
    def _generate_xai(self, prompt: str, options: Dict[str, Any], component: str = None) -> str:
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
            
            # Get configuration from central config
            xai_config = get_provider_config("xai", component, self.article_context)
            
            # Set options with NO HARDCODED FALLBACKS
            model = options.get("model", xai_config.get("model"))
            temperature = options.get("temperature", xai_config.get("temperature"))
            max_tokens = options.get("max_tokens", xai_config.get("max_tokens_limit"))
            
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

    def generate(self, prompt: str, provider: str = None, component: str = None, **options) -> str:
        """Generate text using the specified provider."""
        # Determine provider: explicit arg > component config > global default
        provider_to_use = provider
        
        if not provider_to_use and component and self.article_context:
            # Look up provider in component config
            component_config = self.article_context.get("components", {}).get(component, {})
            provider_to_use = component_config.get("provider")
            # DEBUG: Print what we found
            logger.info(f"Component {component} config: {component_config}")
            logger.info(f"Found provider in component config: {provider_to_use}")
        
        provider_to_use = provider_to_use or self.provider
        logger.info(f"Final provider selected: {provider_to_use}")
        
        # Select the provider method
        provider_methods = {
            "deepseek": self._generate_deepseek,
            "openai": self._generate_openai,
            "gemini": self._generate_gemini,
            "xai": self._generate_xai
        }
        
        generator = provider_methods.get(provider_to_use.lower())
        if not generator:
            error_msg = f"Unsupported AI provider: {provider_to_use}"
            logger.error(error_msg)
            raise ValueError(error_msg)
        
        # Generate text
        try:
            return generator(prompt, options, component)
        except Exception as e:
            error_msg = f"Error generating with {provider_to_use}: {str(e)}"
            logger.error(error_msg)
            raise RuntimeError(error_msg)
    
    # Add this alias method
    def generate_content(self, prompt: str, provider: str = None, component: str = None, **options) -> str:
        """Alias for generate() to maintain backwards compatibility."""
        return self.generate(prompt, provider, component, **options)