"""API client for multiple AI providers - SCHEMA-DRIVEN ONLY."""

import os
import logging
import requests
import json
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)

class APIClient:
    """Unified API client for multiple AI providers."""
    
    def __init__(self, provider: str):
        self.provider = provider.lower()
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
            "deepseek": "deepseek-chat"  # Keeping as you confirmed
        }
        
        # Get API key
        self.api_key = self._get_api_key()
        if not self.api_key:
            logger.error(f"No API key found for {provider}")
            raise ValueError(f"Missing API key for {provider}")
        
        logger.info(f"API Client initialized for {provider} with model {self.models[self.provider]}")
    
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
        try:
            if self.provider == "gemini":
                return self._generate_gemini(prompt, max_tokens)
            else:
                return self._generate_openai_format(prompt, max_tokens)
        except Exception as e:
            logger.error(f"Generation failed: {e}")
            return None
    
    def _generate_openai_format(self, prompt: str, max_tokens: int) -> Optional[str]:
        """Generate using OpenAI-compatible format (OpenAI, XAI, DeepSeek)."""
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        # Base data structure
        data = {
            "model": self.models[self.provider],
            "messages": [
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "temperature": 0.7
        }
        
        # Provider-specific adjustments
        if self.provider == "deepseek":
            # DeepSeek specific parameters - they're picky about format
            data["max_tokens"] = min(max_tokens, 4000)  # Conservative limit
            data["stream"] = False
            data["stop"] = None
            # DeepSeek doesn't like certain OpenAI parameters
            
        elif self.provider == "openai":
            data["max_tokens"] = max_tokens
            
        elif self.provider == "xai":
            data["max_tokens"] = max_tokens
            
        else:
            # Default OpenAI format
            data["max_tokens"] = max_tokens
        
        url = self.base_urls[self.provider]
        
        # Retry logic with better error handling
        for attempt in range(3):
            try:
                logger.info(f"Attempt {attempt + 1}: Sending request to {self.provider}")
                
                response = requests.post(
                    url, 
                    headers=headers, 
                    json=data, 
                    timeout=60
                )
                
                # Log request details for debugging
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
                        
                elif response.status_code == 422:
                    # Unprocessable Entity - usually parameter issues
                    logger.error(f"DeepSeek 422 Error - Invalid parameters")
                    logger.error(f"Request data: {json.dumps(data, indent=2)}")
                    logger.error(f"Response: {response.text}")
                    
                    # For DeepSeek, try with minimal parameters
                    if self.provider == "deepseek" and attempt == 0:
                        logger.info("Trying with minimal DeepSeek parameters...")
                        data = {
                            "model": "deepseek-chat",
                            "messages": [
                                {
                                    "role": "user",
                                    "content": prompt
                                }
                            ]
                        }
                        continue
                    
                else:
                    logger.error(f"{self.provider.title()} API request failed: {response.status_code} {response.reason}")
                    logger.error(f"Response: {response.text}")
                    
                    if attempt < 2:  # Don't sleep on last attempt
                        import time
                        time.sleep(2)
                    
            except requests.exceptions.RequestException as e:
                logger.error(f"Request error on attempt {attempt + 1}: {e}")
                if attempt < 2:
                    import time
                    time.sleep(2)
        
        logger.error(f"All 3 attempts failed for {self.provider}")
        return None
    
    def _generate_gemini(self, prompt: str, max_tokens: int) -> Optional[str]:
        """Generate using Gemini format."""
        headers = {
            "Content-Type": "application/json"
        }
        
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
                "maxOutputTokens": max_tokens,
                "temperature": 0.7
            }
        }
        
        url = f"{self.base_urls[self.provider]}?key={self.api_key}"
        
        # Retry logic
        for attempt in range(3):
            try:
                response = requests.post(url, headers=headers, json=data, timeout=60)
                
                if response.status_code == 200:
                    result = response.json()
                    
                    if "candidates" in result and len(result["candidates"]) > 0:
                        content = result["candidates"][0]["content"]["parts"][0]["text"]
                        logger.info(f"Successfully generated content with {self.provider}")
                        return content
                    else:
                        logger.error(f"No candidates in response: {result}")
                        return None
                else:
                    logger.error(f"Gemini API request failed: {response.status_code} {response.reason}")
                    logger.error(f"Response: {response.text}")
                    
                    if attempt < 2:
                        import time
                        time.sleep(2)
                    
            except requests.exceptions.RequestException as e:
                logger.error(f"Request error on attempt {attempt + 1}: {e}")
                if attempt < 2:
                    import time
                    time.sleep(2)
        
        logger.error(f"All 3 attempts failed for {self.provider}")
        return None