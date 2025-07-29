"""
API MODULE DIRECTIVES FOR AI ASSISTANTS:
1. INTERFACE COMPLIANCE: All methods must match BaseProvider exactly
2. ERROR HANDLING: Convert all DeepSeek errors to standard ApiError classes
3. NO BLOAT: Don't add methods not in BaseProvider interface
4. TIMEOUT ENFORCEMENT: All API calls must include timeouts
"""

"""DeepSeek API provider implementation."""

import logging
import requests
from typing import Dict, Any
import os
import json

logger = logging.getLogger(__name__)

class DeepseekClient:
    """Client for the DeepSeek API."""
    
    def __init__(self, options: Dict[str, Any] = None):
        """Initialize the DeepSeek client.
        
        Args:
            options: Options for the client
        """
        self.api_key = os.environ["DEEPSEEK_API_KEY"]  # No fallback - must exist
        self.options = options or {}
        self.model = self.options["model"]  # No fallback - must be provided
        self.api_base = "https://api.deepseek.com/v1"
    
    def complete(self, prompt: str) -> str:
        """Complete a prompt using the DeepSeek API.
        
        Args:
            prompt: The prompt to complete
            
        Returns:
            str: The completed text
        """
        logger.debug(f"Sending prompt to DeepSeek API (model: {self.model})")
        
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }
        
        payload = {
            "model": self.model,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": self.options["temperature"],  # No fallback - must be provided
            "max_tokens": self.options["max_tokens"]     # No fallback - must be provided
        }
        
        try:
            response = requests.post(
                f"{self.api_base}/chat/completions",
                headers=headers,
                json=payload
            )
            
            response.raise_for_status()
            data = response.json()
            
            # Extract content from response - no fallbacks, data must be valid
            content = data["choices"][0]["message"]["content"]
            
            if not content:
                logger.warning("Empty response from DeepSeek API")
            
            return content
            
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 422:
                logger.error(f"DeepSeek API validation error: {e.response.text}")
                raise ValueError(f"DeepSeek API validation error: {e.response.text}")
            else:
                logger.error(f"DeepSeek API HTTP error: {e}")
                raise
        except requests.exceptions.RequestException as e:
            logger.error(f"DeepSeek API request error: {e}")
            raise
        except Exception as e:
            logger.error(f"DeepSeek API unexpected error: {e}")
            raise