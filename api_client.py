"""API client for multiple AI providers - SCHEMA-DRIVEN ONLY."""

import os
import logging
import requests
import json
import time
from typing import Dict, Any, Optional, List, Tuple

logger = logging.getLogger(__name__)

class APIClient:
    """Unified API client for multiple AI providers."""
    
    def __init__(self, provider_name: str):
        self.provider = provider_name.lower()
        self.base_urls = {
            "openai": "https://api.openai.com/v1/chat/completions",
            "xai": "https://api.x.ai/v1/chat/completions",
            "gemini": "https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash-latest:generateContent",
            "deepseek": "https://api.deepseek.com/v1/chat/completions"
        }
        
        self.models = {
            "openai": "gpt-4o-mini",
            "xai": "grok-beta",
            "gemini": "gemini-1.5-flash-latest",
            "deepseek": "deepseek-chat"
        }
        
        # Get configuration for this provider
        self.config = self.get_provider_config()
        
        # Get API key
        self.api_key = self._get_api_key()
        
        if not self.api_key:
            logger.warning(f"No API key found for {provider_name}, using mock mode")
            self.mock_mode = True
        else:
            self.mock_mode = False
        
        logger.info(f"Initialized API client for {provider_name} (mock_mode={self.mock_mode})")
    
    def _get_api_key(self) -> Optional[str]:
        """Get API key for the current provider."""
        key_map = {
            "openai": "OPENAI_API_KEY",
            "xai": "XAI_API_KEY", 
            "gemini": "GEMINI_API_KEY",
            "deepseek": "DEEPSEEK_API_KEY"
        }
        
        return os.getenv(key_map.get(self.provider))
    
    def generate(self, prompt: str, max_tokens: int = 2000) -> Optional[str]:
        """Generate content using the configured provider."""
        if self.mock_mode:
            return self._generate_mock_response(prompt)
        
        try:
            if self.provider == "gemini":
                return self._generate_gemini(prompt, max_tokens)
            else:
                return self._generate_openai_format(prompt, max_tokens)
        except Exception as e:
            logger.error(f"Generation failed: {e}", exc_info=True)
            return None
    
    def _generate_openai_format(self, prompt: str, max_tokens: int) -> Optional[str]:
        """Generate using OpenAI-compatible format (OpenAI, XAI, DeepSeek)."""
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        # Adjust max tokens based on provider limits
        adjusted_max_tokens = min(max_tokens, self.config["max_tokens_limit"])
        
        # Base data structure
        data = {
            "model": self.models[self.provider],
            "messages": [
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "temperature": 0.7,
            "max_tokens": adjusted_max_tokens
        }
        
        # Provider-specific adjustments
        if self.provider == "deepseek":
            if self.config.get("minimal_request", False):
                # Use minimal parameters for DeepSeek
                data = {
                    "model": self.models[self.provider],
                    "messages": data["messages"],
                    "temperature": 0.7,
                    "max_tokens": adjusted_max_tokens
                }
        
        url = self.base_urls[self.provider]
        timeout = self.config["timeout"]
        
        # Retry logic with better error handling
        for attempt in range(3):
            try:
                # Apply exponential backoff for retries
                if attempt > 0:
                    backoff_time = self.config["retry_delay"] * (2 ** (attempt - 1))
                    logger.info(f"Retry {attempt} after {backoff_time}s delay")
                    time.sleep(backoff_time)
                
                logger.info(f"Attempt {attempt + 1}: Sending request to {self.provider}")
                
                # Increase timeout for subsequent attempts
                current_timeout = timeout * (1 + attempt * 0.5)  # Increase by 50% each retry
                
                response = requests.post(
                    url, 
                    headers=headers, 
                    json=data, 
                    timeout=current_timeout
                )
                
                # Log request details for debugging (headers sanitized in logging filter)
                logger.debug(f"Request URL: {url}")
                logger.debug(f"Request headers: {headers}")
                logger.debug(f"Request data: {json.dumps(data, indent=2)}")
                
                if response.status_code == 200:
                    result = response.json()
                    
                    if "choices" in result and len(result["choices"]) > 0:
                        content = result["choices"][0]["message"]["content"]
                        logger.info(f"Successfully generated content with {self.provider}")
                        return content
                    else:
                        logger.error(f"No choices in response: {result}")
                        return None
                else:
                    # Handle specific error codes
                    special_handling = self.handle_provider_error(response, attempt)
                    if special_handling is True:
                        # Continue to next retry without counting this attempt
                        continue
                    elif isinstance(special_handling, (int, float)):
                        # Update timeout and retry
                        timeout = special_handling
                        continue
                    
                    # Log the error with appropriate detail
                    logger.error(f"{self.provider.title()} API error: {response.status_code} {response.reason}")
                    try:
                        error_detail = response.json()
                        logger.error(f"Error details: {error_detail}")
                    except:
                        logger.error(f"Error response: {response.text[:500]}")
                    
                    # For 422 errors, try with simplified parameters
                    if response.status_code == 422 and self.provider == "deepseek" and attempt == 0:
                        logger.info("Trying with minimal DeepSeek parameters...")
                        data = {
                            "model": self.models[self.provider],
                            "messages": [
                                {
                                    "role": "user",
                                    "content": prompt
                                }
                            ],
                            "max_tokens": adjusted_max_tokens
                        }
                        continue
                    
            except requests.exceptions.Timeout:
                logger.error(f"Request timeout on attempt {attempt + 1} after {current_timeout}s")
                # Automatically increase timeout for next attempt
                timeout = timeout * 1.5
                
            except requests.exceptions.RequestException as e:
                logger.error(f"Request error on attempt {attempt + 1}: {e}")
        
        logger.error(f"All 3 attempts failed for {self.provider}")
        return None
    
    def _generate_gemini(self, prompt: str, max_tokens: int) -> Optional[str]:
        """Generate using Gemini format."""
        headers = {
            "Content-Type": "application/json"
        }
        
        # Adjust max tokens based on provider limits
        adjusted_max_tokens = min(max_tokens, self.config["max_tokens_limit"])
        
        data = {
            "contents": [
                {
                    "parts": [
                        {
                            "text": prompt
                        }
                    ]
                }
            ],
            "generationConfig": {
                "maxOutputTokens": adjusted_max_tokens,
                "temperature": 0.7
            }
        }
        
        url = f"{self.base_urls[self.provider]}?key={self.api_key}"
        timeout = self.config["timeout"]
        
        # Retry logic
        for attempt in range(3):
            try:
                # Apply exponential backoff for retries
                if attempt > 0:
                    backoff_time = self.config["retry_delay"] * (2 ** (attempt - 1))
                    logger.info(f"Retry {attempt} after {backoff_time}s delay")
                    time.sleep(backoff_time)
                
                logger.info(f"Attempt {attempt + 1}: Sending request to {self.provider}")
                
                # Increase timeout for subsequent attempts
                current_timeout = timeout * (1 + attempt * 0.5)  # Increase by 50% each retry
                
                response = requests.post(url, headers=headers, json=data, timeout=current_timeout)
                
                if response.status_code == 200:
                    result = response.json()
                    
                    if "candidates" in result and len(result["candidates"]) > 0 and "content" in result["candidates"][0]:
                        # Extract text content safely with error handling
                        try:
                            content = result["candidates"][0]["content"]["parts"][0]["text"]
                            logger.info(f"Successfully generated content with {self.provider}")
                            return content
                        except (KeyError, IndexError) as e:
                            logger.error(f"Unexpected response structure: {e}")
                            logger.debug(f"Response structure: {json.dumps(result, indent=2)[:500]}")
                            return None
                    else:
                        logger.error(f"No valid candidates in response")
                        logger.debug(f"Response: {json.dumps(result, indent=2)[:500]}")
                        return None
                else:
                    # Log the error with appropriate detail
                    logger.error(f"{self.provider.title()} API error: {response.status_code} {response.reason}")
                    try:
                        error_detail = response.json()
                        logger.error(f"Error details: {json.dumps(error_detail, indent=2)}")
                    except:
                        logger.error(f"Error response: {response.text[:500]}")
                    
            except requests.exceptions.Timeout:
                logger.error(f"Request timeout on attempt {attempt + 1} after {current_timeout}s")
                # Automatically increase timeout for next attempt
                timeout = timeout * 1.5
                
            except requests.exceptions.RequestException as e:
                logger.error(f"Request error on attempt {attempt + 1}: {e}")
        
        logger.error(f"All 3 attempts failed for {self.provider}")
        return None
    
    def handle_provider_error(self, response, attempt):
        """Handle provider-specific error responses."""
        # Timeout errors
        if response.status_code == 408:
            logger.warning(f"{self.provider} timeout on attempt {attempt + 1}, increasing timeout")
            return self.config["timeout"] * 2  # Double the timeout
            
        # Rate limiting
        if response.status_code == 429:
            retry_after = response.headers.get("Retry-After")
            if retry_after:
                try:
                    wait_time = int(retry_after)
                except ValueError:
                    # If Retry-After is not a simple integer, default to provider's retry delay
                    wait_time = self.config["retry_delay"] * 2
            else:
                wait_time = self.config["retry_delay"] * 2
                
            logger.warning(f"Rate limited by {self.provider}, waiting {wait_time} seconds")
            time.sleep(wait_time)
            return True  # Retry
            
        # Authentication errors
        if response.status_code == 401:
            logger.error(f"Authentication failed for {self.provider}. Check API key.")
            return False  # Don't retry auth failures
            
        # Provider specific errors
        if self.provider == "deepseek" and response.status_code == 422:
            if attempt == 0:
                logger.warning("DeepSeek parameter error, will retry with minimal parameters")
                return True
                
        return False  # No special handling
    
    def get_provider_config(self):
        """Get provider-specific configuration."""
        configs = {
            "openai": {
                "timeout": 60,
                "max_tokens_limit": 8192,
                "retry_delay": 2,
                "backoff_factor": 1.5
            },
            "deepseek": {
                "timeout": 180,  # Increased from 60s to 180s
                "max_tokens_limit": 4000,  # DeepSeek's documented limit
                "retry_delay": 5,  # Longer retry delay for DeepSeek
                "minimal_request": True,  # Flag to use minimal parameters if first attempt fails
                "backoff_factor": 2.0  # More aggressive backoff for DeepSeek
            },
            "xai": {
                "timeout": 60,
                "max_tokens_limit": 4096,
                "retry_delay": 2,
                "backoff_factor": 1.5
            },
            "gemini": {
                "timeout": 60,
                "max_tokens_limit": 8192,
                "retry_delay": 2,
                "backoff_factor": 1.5
            }
        }
        
        return configs.get(self.provider, configs["openai"])  # Default to OpenAI config
    
    @classmethod
    def get_available_providers(cls) -> List[str]:
        """Detect which providers have valid API keys configured."""
        available = []
        key_map = {
            "openai": "OPENAI_API_KEY",
            "xai": "XAI_API_KEY", 
            "gemini": "GEMINI_API_KEY",
            "deepseek": "DEEPSEEK_API_KEY"
        }
        
        for provider, env_var in key_map.items():
            if os.getenv(env_var):
                available.append(provider)
        
        return available
    
    @staticmethod
    def format_error_message(response) -> str:
        """Format error message from response for consistent logging."""
        try:
            error_json = response.json()
            if isinstance(error_json, dict):
                if "error" in error_json:
                    if isinstance(error_json["error"], dict):
                        return f"{error_json['error'].get('message', 'Unknown error')}"
                    else:
                        return f"{error_json['error']}"
            return f"Status {response.status_code}: {response.reason}"
        except:
            return f"Status {response.status_code}: {response.text[:100]}"
    
    def _generate_mock_response(self, prompt):
        """Generate a mock response for testing."""
        logger.warning("Using mock response (no API key available)")
        
        # Different mock responses based on prompt content
        if "metadata" in prompt.lower():
            return "---\nname: Mock Response\ndescription: This is a mock response.\n---"
        elif "jsonld" in prompt.lower():
            return '{"@context": "https://schema.org", "@type": "TechnicalArticle", "headline": "Mock Article"}'
        elif "tags" in prompt.lower():
            return "tag1, tag2, tag3, mock-tag, test-tag"
        else:
            return "Mock response for: " + prompt[:50] + "..."


def generate_with_fallback(prompt: str, max_tokens: int = 2000, preferred_provider: Optional[str] = None) -> Optional[str]:
    """Generate content with automatic fallback to available providers."""
    available_providers = APIClient.get_available_providers()
    
    if not available_providers:
        logger.error("No API providers configured with valid keys")
        return None
    
    # Start with preferred provider if specified and available
    if preferred_provider and preferred_provider in available_providers:
        providers_to_try = [preferred_provider] + [p for p in available_providers if p != preferred_provider]
    else:
        # Default provider order (prioritizing more capable models)
        provider_priority = ["openai", "deepseek", "gemini", "xai"]
        providers_to_try = [p for p in provider_priority if p in available_providers]
    
    last_error = None
    for provider in providers_to_try:
        try:
            logger.info(f"Attempting generation with {provider}")
            client = APIClient(provider)
            result = client.generate(prompt, max_tokens)
            
            if result:
                if provider != preferred_provider and preferred_provider:
                    logger.warning(f"Successfully generated with fallback provider {provider}")
                return result
        except Exception as e:
            logger.warning(f"Provider {provider} failed: {str(e)}")
            last_error = e
    
    logger.error(f"All providers failed. Last error: {last_error}")
    return None


def test_all_providers() -> Dict[str, Dict[str, Any]]:
    """Test connectivity and basic functionality of all providers."""
    results = {}
    test_prompt = "Generate a single word response: hello"
    
    for provider in ["openai", "deepseek", "xai", "gemini"]:
        try:
            key_map = {
                "openai": "OPENAI_API_KEY",
                "xai": "XAI_API_KEY", 
                "gemini": "GEMINI_API_KEY",
                "deepseek": "DEEPSEEK_API_KEY"
            }
            
            if not os.getenv(key_map.get(provider)):
                results[provider] = {
                    "status": "MISSING_KEY",
                    "message": f"No API key found in environment ({key_map.get(provider)})"
                }
                continue
                
            # Test connectivity and basic functionality
            start_time = time.time()
            
            client = APIClient(provider)
            response = client.generate(test_prompt, 50)
            
            elapsed = time.time() - start_time
            
            if response:
                results[provider] = {
                    "status": "OK",
                    "latency": f"{elapsed:.2f}s",
                    "model": client.models[provider],
                    "response": response[:50] + ("..." if len(response) > 50 else "")
                }
            else:
                results[provider] = {
                    "status": "ERROR",
                    "message": "Empty response received"
                }
                
        except Exception as e:
            results[provider] = {
                "status": "ERROR",
                "message": str(e)
            }
    
    return results


def print_provider_status():
    """Print status of all providers in a readable format."""
    results = test_all_providers()
    
    print("\n=== API Provider Status ===")
    print(f"{'Provider':<10} | {'Status':<8} | {'Latency':<10} | {'Model':<20} | {'Response'}")
    print("-" * 80)
    
    for provider, result in results.items():
        status = result["status"]
        if status == "OK":
            latency = result["latency"]
            model = result["model"]
            response = result["response"]
            print(f"{provider:<10} | {status:<8} | {latency:<10} | {model:<20} | {response}")
        else:
            message = result.get("message", "Unknown error")
            print(f"{provider:<10} | {status:<8} | {'N/A':<10} | {'N/A':<20} | {message}")
    
    print("\n")