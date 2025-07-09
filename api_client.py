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

logger = logging.getLogger(__name__)

class APIClient:
    """Universal API client supporting multiple providers"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.provider = config["provider"]
        self.model = config["model"]
        self.temperature = config.get("temperature", 0.7)
        self.max_tokens = config.get("max_tokens", 4000)
        
        # Get provider config
        provider_config = config["providers"][self.provider]
        self.api_key = os.getenv(provider_config["api_key_env"])
        self.base_url = provider_config["base_url"]
        
        if not self.api_key:
            raise ValueError(f"Missing API key for {self.provider}")
        
        logger.info(f"🔧 APIClient initialized - {self.provider}/{self.model}")
    
    def call(self, prompt: str, call_type: str = "general") -> str:
        """Make API call to configured provider"""
        logger.info(f"🌐 API CALL [{call_type}]")
        logger.info(f"🌐 Model: {self.model} | Temp: {self.temperature} | Tokens: {self.max_tokens}")
        
        try:
            if self.provider == "OPENAI":
                return self._call_openai(prompt)
            elif self.provider == "XAI":
                return self._call_xai(prompt)
            elif self.provider == "GEMINI":
                return self._call_gemini(prompt)
            elif self.provider == "DEEPSEEK":
                return self._call_deepseek(prompt)
            else:
                raise ValueError(f"Unsupported provider: {self.provider}")
                
        except Exception as e:
            logger.error(f"❌ API call failed [{call_type}]: {e}")
            raise
    
    def _call_openai(self, prompt: str) -> str:
        """OpenAI API call"""
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        data = {
            "model": self.model,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": self.temperature,
            "max_tokens": self.max_tokens
        }
        
        response = requests.post(
            f"{self.base_url}/chat/completions",
            headers=headers,
            json=data,
            timeout=120
        )
        
        response.raise_for_status()
        result = response.json()
        content = result["choices"][0]["message"]["content"]
        
        logger.info(f"✅ API call successful - Response: {len(content)} chars")
        return content
    
    def _call_xai(self, prompt: str) -> str:
        """XAI (Grok) API call"""
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        data = {
            "model": self.model,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": self.temperature,
            "max_tokens": self.max_tokens
        }
        
        response = requests.post(
            f"{self.base_url}/chat/completions",
            headers=headers,
            json=data,
            timeout=120
        )
        
        response.raise_for_status()
        result = response.json()
        content = result["choices"][0]["message"]["content"]
        
        logger.info(f"✅ API call successful - Response: {len(content)} chars")
        return content
    
    def _call_gemini(self, prompt: str) -> str:
        """Google Gemini API call with rate limiting"""
        time.sleep(1)  # Wait 1 second between requests
        
        url = f"{self.base_url}/models/{self.model}:generateContent"
        
        headers = {
            "Content-Type": "application/json"
        }
        
        params = {
            "key": self.api_key
        }
        
        data = {
            "contents": [{
                "parts": [{"text": prompt}]
            }],
            "generationConfig": {
                "temperature": self.temperature,
                "maxOutputTokens": self.max_tokens
            }
        }
        
        try:
            response = requests.post(
                url,
                headers=headers,
                params=params,
                json=data,
                timeout=120
            )
            
            response.raise_for_status()
            result = response.json()
            content = result["candidates"][0]["content"]["parts"][0]["text"]
            
            logger.info(f"✅ API call successful - Response: {len(content)} chars")
            return content
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 429:
                logger.warning("⏳ Rate limit hit, waiting 5 seconds...")
                time.sleep(5)
                # Retry once
                response = requests.post(
                    url,
                    headers=headers,
                    params=params,
                    json=data,
                    timeout=120
                )
                response.raise_for_status()
                result = response.json()
                content = result["candidates"][0]["content"]["parts"][0]["text"]
                
                logger.info(f"✅ API call successful - Response: {len(content)} chars")
                return content
            else:
                raise
    
    def _call_deepseek(self, prompt: str) -> str:
        """DeepSeek API call"""
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        data = {
            "model": self.model,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": self.temperature,
            "max_tokens": self.max_tokens
        }
        
        response = requests.post(
            f"{self.base_url}/chat/completions",
            headers=headers,
            json=data,
            timeout=120
        )
        
        response.raise_for_status()
        result = response.json()
        content = result["choices"][0]["message"]["content"]
        
        logger.info(f"✅ API call successful - Response: {len(content)} chars")
        return content