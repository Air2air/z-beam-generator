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

logger = logging.getLogger(__name__)

class APIClient:
    """API client for external LLM services"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        
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
            logger.error(f"❌ No API key found for provider: {self.provider}")
            logger.error(f"💡 Set {self.provider}_API_KEY in .env file")
            raise ValueError(f"API key not configured for provider: {self.provider}")
        
        # Mask API key in logs
        masked_key = f"{self.api_key[:8]}...{self.api_key[-4:]}" if len(self.api_key) > 12 else "***"
        logger.info(f"🔧 API Client initialized: {self.provider} ({self.model}) - Key: {masked_key}")
    
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
                logger.info("🔧 Environment variables loaded from .env file")
            except Exception as e:
                logger.warning(f"⚠️ Could not load .env file: {e}")
    
    def call(self, prompt: str, operation: str = "generation") -> str:
        """Make API call to the configured provider"""
        logger.info(f"📡 API call: {operation} ({len(prompt)} chars)")
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        # Standard OpenAI-compatible payload
        payload = {
            "model": self.model,
            "messages": [
                {"role": "user", "content": prompt}
            ],
            "max_tokens": self.max_tokens,
            "temperature": self.temperature
        }
        
        try:
            response = requests.post(
                f"{self.base_url}/chat/completions",
                headers=headers,
                json=payload,
                timeout=self.timeout
            )
            
            response.raise_for_status()
            
            result = response.json()
            content = result["choices"][0]["message"]["content"]
            
            logger.info(f"✅ API call successful: {len(content)} chars returned")
            return content
            
        except requests.exceptions.RequestException as e:
            logger.error(f"❌ API call failed: {e}")
            raise RuntimeError(f"API call failed for {operation}: {e}")
        except KeyError as e:
            logger.error(f"❌ Invalid API response format: {e}")
            raise RuntimeError(f"Invalid API response for {operation}: {e}")