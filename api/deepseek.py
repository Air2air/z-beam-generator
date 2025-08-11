"""
DeepSeek API provider implementation.

API MODULE DIRECTIVES FOR AI ASSISTANTS:
1. INTERFACE COMPLIANCE: All methods must match BaseProvider exactly
2. ERROR HANDLING: Convert all DeepSeek errors to standard ApiError classes
3. NO BLOAT: Don't add methods not in BaseProvider interface
4. TIMEOUT ENFORCEMENT: All API calls must include timeouts
"""

import json
import logging
import os
import time
from typing import Dict, Any

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

logger = logging.getLogger(__name__)

class DeepseekClient:
    """Client for the DeepSeek API with improved robustness and performance."""
    
    def __init__(self, options: Dict[str, Any] = None):
        """Initialize the DeepSeek client.
        
        Args:
            options: Options for the client
        """
        self.api_key = os.environ["DEEPSEEK_API_KEY"]  # No fallback - must exist
        if options is None:
            raise ValueError("options parameter must be provided")
        self.options = options
        self.model = self.options["model"]  # No fallback - must be provided
        self.api_base = "https://api.deepseek.com/v1"
        
        # Create a session with retry strategy for better reliability
        self.session = self._create_robust_session()
    
    def _create_robust_session(self) -> requests.Session:
        """Create a requests session with retry strategy and connection pooling."""
        session = requests.Session()
        
        # Configure retry strategy
        retry_strategy = Retry(
            total=3,  # Total number of retries
            backoff_factor=1,  # Wait time between retries (1, 2, 4 seconds)
            status_forcelist=[429, 500, 502, 503, 504],  # HTTP status codes to retry
            allowed_methods=["POST"]  # Only retry POST requests
        )
        
        # Mount adapter with retry strategy
        adapter = HTTPAdapter(
            max_retries=retry_strategy,
            pool_connections=10,  # Connection pool size
            pool_maxsize=20,      # Max connections in pool
            pool_block=False      # Don't block when pool is full
        )
        
        session.mount("https://", adapter)
        session.mount("http://", adapter)
        
        return session
    
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
            "Authorization": f"Bearer {self.api_key}",
            "User-Agent": "Z-Beam-Generator/1.0"
        }
        
        # Calculate optimal max_tokens based on prompt length if not specified
        max_tokens = self.options.get("max_tokens", 4000)
        if max_tokens is None or max_tokens <= 0:
            # Estimate tokens (rough approximation: 1 token ≈ 4 characters)
            prompt_tokens = len(prompt) // 4
            max_tokens = min(4000, max(1000, 8000 - prompt_tokens))
        
        payload = {
            "model": self.model,
            "messages": [
                {
                    "role": "system", 
                    "content": "You are a technical expert providing precise factual data. Output only raw technical information without any formatting, structure, or markdown. Python utilities will handle all formatting."
                },
                {
                    "role": "user", 
                    "content": prompt
                }
            ],
            "temperature": self.options.get("temperature", 0.7),
            "max_tokens": max_tokens,
            "stream": False,  # Explicitly disable streaming for reliability
            "presence_penalty": 0.1,  # Encourage diverse content
            "frequency_penalty": 0.1   # Reduce repetition
        }
        
        start_time = time.time()
        
        try:
            response = self.session.post(
                f"{self.api_base}/chat/completions",
                headers=headers,
                json=payload,
                timeout=(10, 90)  # (connection timeout, read timeout)
            )
            
            elapsed_time = time.time() - start_time
            logger.debug(f"DeepSeek API response received in {elapsed_time:.2f}s")
            
            response.raise_for_status()
            data = response.json()
            
            # Extract content from response - no fallbacks, data must be valid
            if "choices" not in data or not data["choices"]:
                raise ValueError("Invalid API response: no choices returned")
            
            choice = data["choices"][0]
            if "message" not in choice or "content" not in choice["message"]:
                raise ValueError("Invalid API response: no message content")
            
            content = choice["message"]["content"]
            
            if not content or not content.strip():
                logger.warning("Empty response from DeepSeek API")
                raise ValueError("Empty response from DeepSeek API")
            
            # Log usage info if available
            if "usage" in data:
                usage = data["usage"]
                logger.debug(f"DeepSeek API usage - prompt_tokens: {usage.get('prompt_tokens', 'N/A')}, "
                           f"completion_tokens: {usage.get('completion_tokens', 'N/A')}, "
                           f"total_tokens: {usage.get('total_tokens', 'N/A')}")
            
            return content.strip()
            
        except requests.exceptions.Timeout as e:
            logger.error(f"DeepSeek API timeout error: {e}")
            raise TimeoutError(f"DeepSeek API request timed out: {e}")
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 429:
                # Rate limiting
                retry_after = e.response.headers.get('Retry-After', '60')
                logger.error(f"DeepSeek API rate limit exceeded. Retry after {retry_after}s")
                raise ValueError(f"DeepSeek API rate limit exceeded. Retry after {retry_after} seconds")
            elif e.response.status_code == 422:
                logger.error(f"DeepSeek API validation error: {e.response.text}")
                raise ValueError(f"DeepSeek API validation error: {e.response.text}")
            elif e.response.status_code == 401:
                logger.error("DeepSeek API authentication failed - check API key")
                raise ValueError("DeepSeek API authentication failed - check API key")
            elif e.response.status_code == 404:
                logger.error(f"DeepSeek API endpoint not found - check model: {self.model}")
                raise ValueError(f"DeepSeek API endpoint not found - check model: {self.model}")
            else:
                logger.error(f"DeepSeek API HTTP error {e.response.status_code}: {e.response.text}")
                raise ValueError(f"DeepSeek API HTTP error {e.response.status_code}: {e.response.text}")
        except requests.exceptions.ConnectionError as e:
            logger.error(f"DeepSeek API connection error: {e}")
            raise ConnectionError(f"Failed to connect to DeepSeek API: {e}")
        except requests.exceptions.RequestException as e:
            logger.error(f"DeepSeek API request error: {e}")
            raise ValueError(f"DeepSeek API request failed: {e}")
        except json.JSONDecodeError as e:
            logger.error(f"DeepSeek API response parsing error: {e}")
            raise ValueError(f"Invalid JSON response from DeepSeek API: {e}")
        except Exception as e:
            logger.error(f"DeepSeek API unexpected error: {e}")
            raise ValueError(f"Unexpected error calling DeepSeek API: {e}")
    
    def __del__(self):
        """Cleanup session when client is destroyed."""
        if hasattr(self, 'session'):
            self.session.close()