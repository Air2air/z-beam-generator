#!/usr/bin/env python3
"""
API Response Cache

Caches API responses to disk to reduce costs and improve performance.
Implements fail-fast architecture with explicit configuration requirements.
"""

import hashlib
import json
import logging
import os
import time
from pathlib import Path
from typing import Any, Dict, Optional

logger = logging.getLogger(__name__)


class ResponseCache:
    """
    Disk-based cache for API responses with TTL and size limits.
    
    Caches actual API responses to avoid duplicate API calls for identical prompts.
    Follows fail-fast architecture - all configuration must be explicit.
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize response cache with explicit configuration.
        
        Args:
            config: Cache configuration dictionary with required keys:
                - enabled (bool): Whether caching is enabled
                - storage_location (str): Directory path for cache files
                - ttl_seconds (int): Time-to-live for cached responses
                - max_size_mb (int): Maximum cache size in megabytes
                - key_strategy (str): Strategy for generating cache keys
        
        Raises:
            ValueError: If required configuration is missing
        """
        # Fail-fast: Validate required configuration
        required_keys = ['enabled', 'storage_location', 'ttl_seconds', 'max_size_mb', 'key_strategy']
        missing = [key for key in required_keys if key not in config]
        if missing:
            raise ValueError(
                f"Response cache configuration incomplete. Missing required keys: {missing}. "
                f"No defaults allowed in fail-fast architecture."
            )
        
        self.enabled = config['enabled']
        self.storage_location = Path(config['storage_location'])
        self.ttl_seconds = config['ttl_seconds']
        self.max_size_mb = config['max_size_mb']
        self.key_strategy = config['key_strategy']
        
        # Validate configuration values
        if not isinstance(self.enabled, bool):
            raise ValueError(f"cache.enabled must be boolean, got {type(self.enabled)}")
        
        if self.ttl_seconds <= 0:
            raise ValueError(f"cache.ttl_seconds must be positive, got {self.ttl_seconds}")
        
        if self.max_size_mb <= 0:
            raise ValueError(f"cache.max_size_mb must be positive, got {self.max_size_mb}")
        
        if self.key_strategy not in ['prompt_hash', 'prompt_hash_with_model', 'full_request_hash']:
            raise ValueError(
                f"cache.key_strategy must be one of: prompt_hash, prompt_hash_with_model, full_request_hash. "
                f"Got: {self.key_strategy}"
            )
        
        # Initialize cache directory if enabled
        if self.enabled:
            self.storage_location.mkdir(parents=True, exist_ok=True)
            logger.info(f"🗄️  [RESPONSE CACHE] Initialized at {self.storage_location}")
            logger.info(f"🗄️  [RESPONSE CACHE] TTL: {self.ttl_seconds}s, Max size: {self.max_size_mb}MB")
        else:
            logger.info("🗄️  [RESPONSE CACHE] Caching disabled by configuration")
        
        # Statistics
        self.stats = {
            'hits': 0,
            'misses': 0,
            'writes': 0,
            'evictions': 0,
            'errors': 0
        }
    
    def get(self, request_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Get cached response for a request.
        
        Args:
            request_data: Request parameters (prompt, model, temperature, etc.)
        
        Returns:
            Cached response dict or None if not cached/expired
        """
        if not self.enabled:
            return None
        
        try:
            cache_key = self._generate_cache_key(request_data)
            cache_file = self.storage_location / f"{cache_key}.json"
            
            if not cache_file.exists():
                self.stats['misses'] += 1
                return None
            
            # Load cached response
            with open(cache_file, 'r') as f:
                cached_data = json.load(f)

            if not isinstance(cached_data, dict):
                raise RuntimeError("Cached entry must be a dictionary")
            if 'cached_at' not in cached_data:
                raise RuntimeError("Cached entry missing required 'cached_at' field")
            if 'response' not in cached_data:
                raise RuntimeError("Cached entry missing required 'response' field")
            
            # Check if expired
            cached_time = cached_data['cached_at']
            age_seconds = time.time() - cached_time
            
            if age_seconds > self.ttl_seconds:
                logger.debug(f"🗄️  [RESPONSE CACHE] Cache EXPIRED (age: {age_seconds:.1f}s)")
                cache_file.unlink()  # Remove expired cache
                self.stats['misses'] += 1
                return None
            
            # Cache hit!
            self.stats['hits'] += 1
            hit_rate = self.stats['hits'] / (self.stats['hits'] + self.stats['misses']) * 100
            logger.info(
                f"🎯 [RESPONSE CACHE] Cache HIT! Age: {age_seconds:.1f}s, "
                f"Hit rate: {hit_rate:.1f}% ({self.stats['hits']}/{self.stats['hits'] + self.stats['misses']})"
            )
            
            return cached_data['response']
            
        except Exception as e:
            self.stats['errors'] += 1
            logger.warning(f"⚠️  [RESPONSE CACHE] Error reading cache: {e}")
            return None
    
    def set(self, request_data: Dict[str, Any], response: Dict[str, Any]) -> bool:
        """
        Cache a response.
        
        Args:
            request_data: Request parameters
            response: API response to cache
        
        Returns:
            True if cached successfully, False otherwise
        """
        if not self.enabled:
            return False
        
        try:
            cache_key = self._generate_cache_key(request_data)
            cache_file = self.storage_location / f"{cache_key}.json"
            
            # Prepare cache entry
            required_request_keys = ['model', 'temperature', 'max_tokens', 'prompt']
            missing_request_keys = [key for key in required_request_keys if key not in request_data]
            if missing_request_keys:
                raise RuntimeError(
                    f"Request data missing required keys for caching: {missing_request_keys}"
                )

            cache_entry = {
                'cached_at': time.time(),
                'request_data': {
                    'model': request_data['model'],
                    'temperature': request_data['temperature'],
                    'max_tokens': request_data['max_tokens'],
                    'prompt_length': len(str(request_data['prompt']))
                },
                'response': response
            }
            
            # Write to cache
            with open(cache_file, 'w') as f:
                json.dump(cache_entry, f, indent=2)
            
            self.stats['writes'] += 1
            logger.debug(f"💾 [RESPONSE CACHE] Cached response: {cache_key[:16]}...")
            
            # Check cache size and evict if needed
            self._enforce_size_limit()
            
            return True
            
        except Exception as e:
            self.stats['errors'] += 1
            logger.warning(f"⚠️  [RESPONSE CACHE] Error writing cache: {e}")
            return False
    
    def _generate_cache_key(self, request_data: Dict[str, Any]) -> str:
        """
        Generate cache key based on configured strategy.
        
        Args:
            request_data: Request parameters
        
        Returns:
            Cache key string (hash)
        """
        if self.key_strategy == 'prompt_hash':
            # Hash only the prompt
            if 'prompt' not in request_data:
                raise RuntimeError("Request data missing required key 'prompt' for key_strategy 'prompt_hash'")
            key_data = str(request_data['prompt'])
            
        elif self.key_strategy == 'prompt_hash_with_model':
            # Hash prompt + model + temperature
            required_keys = ['model', 'prompt', 'temperature']
            missing_keys = [key for key in required_keys if key not in request_data]
            if missing_keys:
                raise RuntimeError(
                    f"Request data missing required keys for key_strategy 'prompt_hash_with_model': {missing_keys}"
                )
            key_data = f"{request_data['model']}|{request_data['prompt']}|{request_data['temperature']}"
            
        elif self.key_strategy == 'full_request_hash':
            # Hash entire request (most strict)
            key_data = json.dumps(request_data, sort_keys=True)
        
        else:
            # Should never reach here due to validation in __init__
            raise ValueError(f"Unknown key_strategy: {self.key_strategy}")
        
        # Generate SHA256 hash
        return hashlib.sha256(key_data.encode()).hexdigest()
    
    def _enforce_size_limit(self) -> None:
        """
        Enforce maximum cache size by evicting oldest entries.
        """
        try:
            # Calculate current cache size
            total_size_mb = sum(
                f.stat().st_size for f in self.storage_location.glob('*.json')
            ) / (1024 * 1024)
            
            if total_size_mb <= self.max_size_mb:
                return  # Within limits
            
            logger.info(
                f"🗑️  [RESPONSE CACHE] Cache size {total_size_mb:.1f}MB exceeds limit {self.max_size_mb}MB, "
                f"evicting oldest entries..."
            )
            
            # Get all cache files sorted by modification time (oldest first)
            cache_files = sorted(
                self.storage_location.glob('*.json'),
                key=lambda f: f.stat().st_mtime
            )
            
            # Evict oldest files until under limit
            evicted = 0
            for cache_file in cache_files:
                cache_file.unlink()
                evicted += 1
                self.stats['evictions'] += 1
                
                # Recalculate size
                total_size_mb = sum(
                    f.stat().st_size for f in self.storage_location.glob('*.json')
                ) / (1024 * 1024)
                
                if total_size_mb <= self.max_size_mb * 0.8:  # Leave 20% buffer
                    break
            
            logger.info(f"🗑️  [RESPONSE CACHE] Evicted {evicted} entries, new size: {total_size_mb:.1f}MB")
            
        except Exception as e:
            logger.warning(f"⚠️  [RESPONSE CACHE] Error enforcing size limit: {e}")
    
    def clear(self) -> int:
        """
        Clear all cached responses.
        
        Returns:
            Number of entries cleared
        """
        if not self.enabled:
            return 0
        
        try:
            cache_files = list(self.storage_location.glob('*.json'))
            count = len(cache_files)
            
            for cache_file in cache_files:
                cache_file.unlink()
            
            logger.info(f"🧹 [RESPONSE CACHE] Cleared {count} cached responses")
            
            # Reset stats
            self.stats = {
                'hits': 0,
                'misses': 0,
                'writes': 0,
                'evictions': 0,
                'errors': 0
            }
            
            return count
            
        except Exception as e:
            logger.error(f"❌ [RESPONSE CACHE] Error clearing cache: {e}")
            return 0
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Get cache statistics.
        
        Returns:
            Dictionary with cache statistics
        """
        total_requests = self.stats['hits'] + self.stats['misses']
        hit_rate = (self.stats['hits'] / total_requests * 100) if total_requests > 0 else 0
        
        # Calculate current cache size
        try:
            cache_size_mb = sum(
                f.stat().st_size for f in self.storage_location.glob('*.json')
            ) / (1024 * 1024)
            entry_count = len(list(self.storage_location.glob('*.json')))
        except:
            cache_size_mb = 0
            entry_count = 0
        
        return {
            'enabled': self.enabled,
            'hits': self.stats['hits'],
            'misses': self.stats['misses'],
            'writes': self.stats['writes'],
            'evictions': self.stats['evictions'],
            'errors': self.stats['errors'],
            'total_requests': total_requests,
            'hit_rate_percent': round(hit_rate, 1),
            'cache_size_mb': round(cache_size_mb, 2),
            'entry_count': entry_count,
            'ttl_seconds': self.ttl_seconds,
            'max_size_mb': self.max_size_mb
        }
