#!/usr/bin/env python3
"""
Cached API Client

Wraps APIClient with response caching to reduce costs and improve performance.
Implements fail-fast architecture with explicit configuration requirements.
"""

import logging
from typing import Any, Dict, Optional

from .client import APIClient, APIResponse, GenerationRequest
from .response_cache import ResponseCache

logger = logging.getLogger(__name__)


class CachedAPIClient(APIClient):
    """
    API client with response caching.
    
    Extends APIClient to add transparent response caching. All requests
    check the cache first; on cache miss, requests are sent to the API
    and responses are cached for future use.
    """
    
    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        model: Optional[str] = None,
        config: Optional[Dict] = None,
        cache_config: Optional[Dict] = None,
    ):
        """
        Initialize cached API client.
        
        Args:
            api_key: API key (or will be loaded from config/env)
            base_url: API base URL
            model: Model name
            config: API client configuration
            cache_config: Response cache configuration (required if caching enabled)
        
        Raises:
            ValueError: If cache_config missing when caching is enabled
        """
        # Initialize base API client
        super().__init__(
            api_key=api_key,
            base_url=base_url,
            model=model,
            config=config
        )
        
        # Initialize response cache
        if cache_config is None:
            raise ValueError(
                "cache_config must be provided explicitly - no defaults allowed in fail-fast architecture. "
                "Set cache_config['enabled'] = False to disable caching."
            )
        
        self.cache = ResponseCache(cache_config)
        
        if self.cache.enabled:
            logger.info("🗄️  [CACHED API CLIENT] Response caching ENABLED")
        else:
            logger.info("🗄️  [CACHED API CLIENT] Response caching DISABLED")
    
    def generate(self, request: GenerationRequest) -> APIResponse:
        """
        Generate content with caching.
        
        Checks cache first; on miss, calls API and caches response.
        
        Args:
            request: Generation request
        
        Returns:
            APIResponse with generated content
        """
        # Prepare request data for caching
        request_data = {
            'prompt': request.prompt,
            'system_prompt': request.system_prompt,
            'model': self.model,
            'temperature': request.temperature,
            'max_tokens': request.max_tokens,
            'top_p': request.top_p,
            'frequency_penalty': request.frequency_penalty,
            'presence_penalty': request.presence_penalty,
        }
        
        # Check cache first
        cached_response = self.cache.get(request_data)
        if cached_response is not None:
            required_cached_keys = [
                'success',
                'content',
                'error',
                'response_time',
                'token_count',
                'prompt_tokens',
                'completion_tokens',
                'model_used',
                'request_id',
                'retry_count',
            ]
            missing_cached_keys = [key for key in required_cached_keys if key not in cached_response]
            if missing_cached_keys:
                raise RuntimeError(
                    f"CACHE DATA ERROR: Cached response is missing required keys: {missing_cached_keys}"
                )

            # Cache hit - return cached response
            return APIResponse(
                success=cached_response['success'],
                content=cached_response['content'],
                error=cached_response['error'],
                response_time=cached_response['response_time'],
                token_count=cached_response['token_count'],
                prompt_tokens=cached_response['prompt_tokens'],
                completion_tokens=cached_response['completion_tokens'],
                model_used=cached_response['model_used'],
                request_id=cached_response['request_id'],
                retry_count=cached_response['retry_count']
            )
        
        # Cache miss - call API
        logger.debug("🗄️  [CACHED API CLIENT] Cache miss, calling API...")
        response = super().generate(request)
        
        # Cache the response (only if successful)
        if response.success:
            response_data = {
                'success': response.success,
                'content': response.content,
                'error': response.error,
                'response_time': response.response_time,
                'token_count': response.token_count,
                'prompt_tokens': response.prompt_tokens,
                'completion_tokens': response.completion_tokens,
                'model_used': response.model_used,
                'request_id': response.request_id,
                'retry_count': response.retry_count
            }
            self.cache.set(request_data, response_data)
        
        return response
    
    def clear_cache(self) -> int:
        """
        Clear all cached responses.
        
        Returns:
            Number of entries cleared
        """
        return self.cache.clear()
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """
        Get cache statistics.
        
        Returns:
            Dictionary with cache statistics
        """
        return self.cache.get_stats()
    
    def check_text(self, text: str) -> Dict[str, Any]:
        """
        Check text for AI detection (Winston API compatibility).
        
        This method is not supported in CachedAPIClient.
        
        Args:
            text: Text to analyze
            
        Raises:
            RuntimeError: Always - Winston detection must use non-cached client
        """
        raise RuntimeError(
            "CachedAPIClient.check_text is not supported. Use non-cached Winston client for AI detection."
        )
