"""Unified API client for multiple AI providers."""

import os
import logging
import requests
import json
from typing import Dict, Any, Optional
from time import sleep

logger = logging.getLogger(__name__)

class APIClient:
    """Unified client for XAI, Gemini, DeepSeek, and OpenAI APIs."""
    
    def __init__(self, provider: str = "openai"):
        self.provider = provider.lower()
        self.api_key = self._get_api_key()
        self.base_url = self._get_base_url()
        self.model = self._get_model()
        
        if not self.api_key:
            raise ValueError(f"No API key found for provider: {provider}")
        
        logger.info(f"API Client initialized for {provider} with model {self.model}")
    
    def _get_api_key(self) -> Optional[str]:
        """Get API key for the selected provider."""
        key_mapping = {
            "openai": "OPENAI_API_KEY",
            "xai": "XAI_API_KEY",
            "gemini": "GEMINI_API_KEY",
            "deepseek": "DEEPSEEK_API_KEY"
        }
        return os.getenv(key_mapping.get(self.provider))
    
    def _get_base_url(self) -> str:
        """Get base URL for the selected provider."""
        urls = {
            "openai": "https://api.openai.com/v1",
            "xai": "https://api.x.ai/v1",
            "gemini": "https://generativelanguage.googleapis.com/v1beta",
            "deepseek": "https://api.deepseek.com/v1"
        }
        return urls.get(self.provider, "")
    
    def _get_model(self) -> str:
        """Get model name for the selected provider."""
        models = {
            "openai": "gpt-4",
            "xai": "grok-beta",
            "gemini": "gemini-pro",
            "deepseek": "deepseek-chat"
        }
        return models.get(self.provider, "")
    
    def _make_openai_request(self, prompt: str, max_tokens: int = 1000) -> Optional[str]:
        """Make request to OpenAI API."""
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": self.model,
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": max_tokens,
            "temperature": 0.7
        }
        
        try:
            response = requests.post(
                f"{self.base_url}/chat/completions",
                headers=headers,
                json=payload,
                timeout=30
            )
            response.raise_for_status()
            return response.json()["choices"][0]["message"]["content"]
        except Exception as e:
            logger.error(f"OpenAI API request failed: {e}")
            return None
    
    def _make_xai_request(self, prompt: str, max_tokens: int = 1000) -> Optional[str]:
        """Make request to XAI API."""
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": self.model,
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": max_tokens,
            "temperature": 0.7
        }
        
        try:
            response = requests.post(
                f"{self.base_url}/chat/completions",
                headers=headers,
                json=payload,
                timeout=30
            )
            response.raise_for_status()
            return response.json()["choices"][0]["message"]["content"]
        except Exception as e:
            logger.error(f"XAI API request failed: {e}")
            return None
    
    def _make_gemini_request(self, prompt: str, max_tokens: int = 1000) -> Optional[str]:
        """Make request to Gemini API."""
        url = f"{self.base_url}/models/{self.model}:generateContent?key={self.api_key}"
        
        payload = {
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {
                "maxOutputTokens": max_tokens,
                "temperature": 0.7
            }
        }
        
        try:
            response = requests.post(url, json=payload, timeout=30)
            response.raise_for_status()
            return response.json()["candidates"][0]["content"]["parts"][0]["text"]
        except Exception as e:
            logger.error(f"Gemini API request failed: {e}")
            return None
    
    def _make_deepseek_request(self, prompt: str, max_tokens: int = 1000) -> Optional[str]:
        """Make request to DeepSeek API."""
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": self.model,
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": max_tokens,
            "temperature": 0.7
        }
        
        try:
            response = requests.post(
                f"{self.base_url}/chat/completions",
                headers=headers,
                json=payload,
                timeout=30
            )
            response.raise_for_status()
            return response.json()["choices"][0]["message"]["content"]
        except Exception as e:
            logger.error(f"DeepSeek API request failed: {e}")
            return None
    
    def generate(self, prompt: str, max_tokens: int = 2000, retries: int = 3) -> Optional[str]:
        """Generate content using the selected AI provider."""
        # Validate max_tokens for different providers
        provider_limits = {
            "openai": 4000,
            "xai": 3000, 
            "gemini": 4000,
            "deepseek": 4000
        }
        
        max_allowed = provider_limits.get(self.provider, 2000)
        if max_tokens > max_allowed:
            logger.warning(f"Reducing max_tokens from {max_tokens} to {max_allowed} for {self.provider}")
            max_tokens = max_allowed
        
        for attempt in range(retries):
            try:
                if self.provider == "openai":
                    result = self._make_openai_request(prompt, max_tokens)
                elif self.provider == "xai":
                    result = self._make_xai_request(prompt, max_tokens)
                elif self.provider == "gemini":
                    result = self._make_gemini_request(prompt, max_tokens)
                elif self.provider == "deepseek":
                    result = self._make_deepseek_request(prompt, max_tokens)
                else:
                    logger.error(f"Unknown provider: {self.provider}")
                    return None
                
                if result:
                    logger.info(f"Successfully generated content using {self.provider}")
                    return result
                
            except Exception as e:
                logger.warning(f"Attempt {attempt + 1} failed: {e}")
                if attempt < retries - 1:
                    sleep(2 ** attempt)  # Exponential backoff
        
        logger.error(f"All {retries} attempts failed for {self.provider}")
        return None