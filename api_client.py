#!/usr/bin/env python3
"""
API Client - Handles all API communication
"""
import os
import requests
import logging

logger = logging.getLogger(__name__)

class APIClient:
    """Simple API client for OpenAI calls"""
    
    def __init__(self, config):
        self.config = config
        self.api_key = os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("Environment variable OPENAI_API_KEY not set")
    
    def call(self, prompt, call_type):
        """Make API call - FAIL FAST on errors"""
        logger.info(f"🌐 API CALL [{call_type}]")
        logger.info(f"🌐 Model: {self.config['model']} | Temp: {self.config['temperature']} | Tokens: {self.config['max_tokens']}")
        
        # Use metadata_temperature for metadata calls
        temperature = self.config.get('metadata_temperature', self.config['temperature']) if call_type == 'metadata' else self.config['temperature']
        
        payload = {
            "model": self.config["model"],
            "messages": [{"role": "user", "content": prompt}],
            "temperature": temperature,
            "max_tokens": self.config["max_tokens"]
        }
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        api_url = "https://api.openai.com/v1/chat/completions"
        
        try:
            response = requests.post(api_url, headers=headers, json=payload, timeout=60)
            response.raise_for_status()
            
            result = response.json()
            content = result["choices"][0]["message"]["content"]
            
            logger.info(f"✅ API call successful [{call_type}] - Response: {len(content)} chars")
            return content
            
        except requests.exceptions.RequestException as e:
            logger.error(f"❌ API call failed [{call_type}]: {e}")
            raise