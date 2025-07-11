#!/usr/bin/env python3
"""
API Client - Handles all API communication
"""
import os
import json
import logging
import requests
import time
from typing import Dict, Any
from pathlib import Path

class APIClient:
    """API client for external LLM services"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.logger = logging.getLogger(__name__)  # Add this line to create a logger instance
        
        # Load environment variables from .env file
        self._load_env_file()
        
        # Get provider from config
        self.provider = config.get("provider", "DEEPSEEK").upper()
        
        # Provider-specific configurations
        provider_configs = {
            "DEEPSEEK": {
                "base_url": "https://api.deepseek.com/v1",
                "model": "deepseek-chat"
            },
            "OPENAI": {
                "base_url": "https://api.openai.com/v1",
                "model": "gpt-4"
            },
            "XAI": {
                "base_url": "https://api.x.ai/v1",
                "model": "grok-beta"
            },
            "GEMINI": {
                "base_url": "https://generativelanguage.googleapis.com/v1beta",
                "model": "gemini-1.5-flash"
            }
        }
        
        # Get provider config or use defaults
        provider_config = provider_configs.get(self.provider, provider_configs["DEEPSEEK"])
        
        # Set configuration
        self.base_url = config.get("base_url", provider_config["base_url"])
        self.model = config.get("model", provider_config["model"])
        
        # Try config first, then environment variable
        self.api_key = config.get("api_key") or os.getenv(f"{self.provider}_API_KEY") or ""
        
        self.max_tokens = config.get("max_tokens", 4000)
        self.temperature = config.get("temperature", 0.7)
        self.timeout = config.get("timeout", 30)
        self.max_retries = config.get("max_retries", 3)
        
        # Validate configuration
        if not self.api_key:
            self.logger.error(f"❌ No API key found for provider: {self.provider}")
            self.logger.error(f"💡 Set {self.provider}_API_KEY in .env file")
            raise ValueError(f"API key not configured for provider: {self.provider}")
    
        # Mask API key in logs
        masked_key = f"{self.api_key[:8]}...{self.api_key[-4:]}" if len(self.api_key) > 12 else "***"
        self.logger.info(f"🔧 API Client initialized: {self.provider} ({self.model}) - Key: {masked_key}")
    
    def _load_env_file(self):
        """Load environment variables from .env file"""
        env_file = Path(".env")
        if env_file.exists():
            try:
                with open(env_file, 'r') as f:
                    for line in f:
                        line = line.strip()
                        if line and not line.startswith('#') and not line.startswith('//'):
                            if '=' in line:
                                key, value = line.split('=', 1)
                                os.environ[key.strip()] = value.strip()
                self.logger.info("🔧 Environment variables loaded from .env file")
            except Exception as e:
                self.logger.warning(f"⚠️ Could not load .env file: {e}")
    
    def call(self, prompt: str, operation: str = "generation") -> str:
        """Call the API client with proper error handling"""
        if not prompt:
            self.logger.warning(f"Empty prompt for {operation}")
            raise ValueError(f"Cannot process empty prompt for {operation}")
        
        self.logger.info(f"📡 API call: {operation} ({len(prompt)} chars)")
        
        try:
            response = self.call_api(prompt)
            
            if not response:
                self.logger.error(f"❌ API returned empty response for {operation}")
                raise ValueError(f"Empty API response for {operation}")
                
            self.logger.info(f"✅ API call successful: {len(response)} chars returned")
            return response
            
        except requests.exceptions.RequestException as e:
            self.logger.error(f"❌ API call failed: {e}")
            raise RuntimeError(f"API call failed for {operation}: {e}")
        except KeyError as e:
            self.logger.error(f"❌ Invalid API response format: {e}")
            raise RuntimeError(f"Invalid API response for {operation}: {e}")
        except Exception as e:
            self.logger.error(f"❌ Unexpected error in API call: {str(e)}")
            raise RuntimeError(f"Error in API call for {operation}: {str(e)}")
    
    def call_api(self, prompt, max_tokens=None, temperature=None, retries=2, timeout=30):
        """
        Call the API with retry handling for timeouts
        """
        attempt = 0
        while attempt <= retries:
            try:
                return self._make_api_request(prompt, max_tokens, temperature, timeout)
            except requests.exceptions.Timeout:
                attempt += 1
                if attempt <= retries:
                    self.logger.warning(f"Request timed out, retrying ({attempt}/{retries})...")
                else:
                    self.logger.error(f"Request failed after {retries} retries")
                    raise
            except Exception as e:
                self.logger.error(f"API request failed: {e}")
                raise

    def _make_api_request(self, prompt, max_tokens=None, temperature=None, timeout=30):
        """
        Make actual API request to the provider
        """
        # Set default values if not provided
        max_tokens = max_tokens or self.max_tokens
        temperature = temperature or self.temperature
        
        # Format the request based on provider
        if self.provider == "OPENAI":
            url = f"{self.base_url}/chat/completions"
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.api_key}"
            }
            data = {
                "model": self.model,
                "messages": [
                    {"role": "system", "content": "You are a helpful technical assistant."},
                    {"role": "user", "content": prompt}
                ],
                "max_tokens": max_tokens,
                "temperature": temperature
            }
        else:
            # Generic fallback for other providers
            url = f"{self.base_url}/chat/completions"
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.api_key}"
            }
            data = {
                "model": self.model,
                "messages": [
                    {"role": "system", "content": "You are a helpful technical assistant."},
                    {"role": "user", "content": prompt}
                ],
                "max_tokens": max_tokens,
                "temperature": temperature
            }
        
        # Make the request
        response = requests.post(url, headers=headers, json=data, timeout=timeout)
        response.raise_for_status()  # Raise an exception for HTTP errors
        
        # Parse the response
        result = response.json()
        
        # Extract the content based on provider
        if self.provider == "OPENAI":
            content = result["choices"][0]["message"]["content"]
        else:
            # Generic fallback for other providers
            content = result["choices"][0]["message"]["content"]
        
        return content