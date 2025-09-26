#!/usr/bin/env python3
"""
API Client Cache Adapter

Provides a unified interface for API client caching, automatically using
the persistent cache by default for optimal performance.
"""

import logging
import os
from typing import Dict, List, Optional, Tuple, Any

logger = logging.getLogger(__name__)

# Check if persistent cache should be disabled
USE_PERSISTENT_CACHE = os.environ.get("Z_BEAM_NO_PERSISTENT_CACHE", "").lower() != "true"

# Import the appropriate cache implementation
if USE_PERSISTENT_CACHE:
    try:
        logger.info("🚀 Using persistent API client cache for optimal performance")
        from .persistent_cache import (
            PersistentAPIClientCache as CacheImplementation,
            get_cached_api_client,
            get_cached_client_for_component,
        )
    except ImportError as e:
        logger.warning(f"⚠️ Failed to import persistent cache: {e}, falling back to in-memory cache")
        from .client_cache import (
            APIClientCache as CacheImplementation,
            get_cached_api_client,
            get_cached_client_for_component,
        )
else:
    logger.info("⚠️ Using in-memory API client cache (persistent cache disabled)")
    from .client_cache import (
        APIClientCache as CacheImplementation,
        get_cached_api_client,
        get_cached_client_for_component,
    )


class APIClientCache:
    """
    API client cache adapter that automatically uses the optimal caching strategy.
    
    This adapter provides a unified interface to either the persistent or in-memory
    cache implementation, making it easy to switch between them as needed.
    """
    
    @classmethod
    def get_client(cls, provider: str, **kwargs) -> Any:
        """Get cached API client or create new one if not cached"""
        return get_cached_api_client(provider, **kwargs)
    
    @classmethod
    def get_client_for_component(cls, component_type: str, **kwargs) -> Any:
        """Get cached API client optimized for a specific component type"""
        return get_cached_client_for_component(component_type, **kwargs)
    
    @classmethod
    def clear_cache(cls) -> None:
        """Clear all cached clients"""
        return CacheImplementation.clear_cache()
    
    @classmethod
    def get_cache_stats(cls) -> Dict[str, int]:
        """Get cache performance statistics"""
        stats = CacheImplementation.get_cache_stats()
        
        # Add information about which cache is in use
        if hasattr(stats, "update"):
            stats.update({
                "cache_type": "persistent" if USE_PERSISTENT_CACHE else "in-memory",
                "persistence_enabled": USE_PERSISTENT_CACHE,
            })
        
        return stats
    
    @classmethod
    def preload_clients(cls, providers: List[str]) -> Dict:
        """Preload clients for common providers"""
        return CacheImplementation.preload_clients(providers)
    
    @classmethod
    def is_persistent(cls) -> bool:
        """Check if persistent caching is enabled"""
        return USE_PERSISTENT_CACHE
    
    @classmethod
    def cache_info(cls) -> Dict:
        """Get detailed information about cached clients"""
        if hasattr(CacheImplementation, "cache_info"):
            return CacheImplementation.cache_info()
        else:
            # No fallbacks allowed
            raise RuntimeError("CONFIGURATION ERROR: Cache implementation must support cache_info method - no fallbacks allowed in fail-fast architecture")
