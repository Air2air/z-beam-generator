#!/usr/bin/env python3
"""
API Client Cache

Provides client instance caching to improve performance by reusing
API clients across multiple generations instead of recreating them.
"""

import logging
from functools import lru_cache
from typing import Dict, Optional

from .client_factory import APIClientFactory

logger = logging.getLogger(__name__)


class APIClientCache:
    """
    Cache for API client instances to improve performance.
    
    Reuses API clients across multiple generations to avoid
    the overhead of recreating connections and authentication.
    """
    
    _instances: Dict[str, any] = {}
    _cache_hits = 0
    _cache_misses = 0
    
    @classmethod
    def get_client(cls, provider: str, **kwargs) -> any:
        """
        Get cached API client or create new one if not cached.
        
        Args:
            provider: API provider name (deepseek, grok, winston)
            **kwargs: Additional client configuration
            
        Returns:
            Cached or new APIClient instance
        """
        # Create cache key from provider and relevant kwargs
        cache_key = cls._create_cache_key(provider, **kwargs)
        
        if cache_key in cls._instances:
            cls._cache_hits += 1
            logger.debug(f"📋 [CLIENT CACHE] Cache HIT for {provider} (hits: {cls._cache_hits})")
            return cls._instances[cache_key]
        
        # Cache miss - create new client
        cls._cache_misses += 1
        logger.info(f"🏭 [CLIENT CACHE] Cache MISS for {provider} - creating new client (misses: {cls._cache_misses})")
        
        client = APIClientFactory.create_client(provider, **kwargs)
        cls._instances[cache_key] = client
        
        return client
    
    @classmethod
    def get_client_for_component(cls, component_type: str, **kwargs) -> any:
        """
        Get cached API client optimized for a specific component type.
        
        Args:
            component_type: Component type (frontmatter, text, etc.)
            **kwargs: Additional client configuration
            
        Returns:
            Cached or new APIClient instance
        """
        # Import component config to get provider mapping
        try:
            from run import COMPONENT_CONFIG
            component_config = COMPONENT_CONFIG.get(component_type, {})
            provider = component_config.get("api_provider")
            
            if not provider or provider == "none":
                return None
                
            if provider == "none":
                return None
                
        except ImportError:
            raise ValueError(f"COMPONENT_CONFIG must be available for component '{component_type}' - no defaults allowed in fail-fast architecture")
        
        return cls.get_client(provider, **kwargs)
    
    @classmethod
    def _create_cache_key(cls, provider: str, **kwargs) -> str:
        """Create cache key from provider and configuration"""
        # Include only relevant configuration in cache key
        relevant_params = ['use_mock', 'temperature', 'max_tokens']
        key_parts = [provider]
        
        for param in relevant_params:
            if param in kwargs:
                key_parts.append(f"{param}={kwargs[param]}")
                
        return "|".join(key_parts)
    
    @classmethod
    def clear_cache(cls) -> None:
        """Clear all cached clients"""
        cleared_count = len(cls._instances)
        cls._instances.clear()
        cls._cache_hits = 0
        cls._cache_misses = 0
        logger.info(f"🧹 [CLIENT CACHE] Cleared {cleared_count} cached clients")
    
    @classmethod
    def get_cache_stats(cls) -> Dict[str, int]:
        """Get cache performance statistics"""
        total_requests = cls._cache_hits + cls._cache_misses
        hit_rate = (cls._cache_hits / total_requests * 100) if total_requests > 0 else 0
        
        return {
            "cache_hits": cls._cache_hits,
            "cache_misses": cls._cache_misses,
            "total_requests": total_requests,
            "hit_rate_percent": round(hit_rate, 1),
            "cached_instances": len(cls._instances)
        }
    
    @classmethod
    def preload_clients(cls, providers: list) -> dict:
        """
        Preload clients for common providers and return status
        
        Args:
            providers: List of provider names to preload
            
        Returns:
            Dictionary with preload results
        """
        logger.info(f"🚀 [CLIENT CACHE] Preloading clients for: {', '.join(providers)}")
        results = {"success": [], "failed": []}
        
        for provider in providers:
            try:
                client = cls.get_client(provider)
                logger.info(f"✅ [CLIENT CACHE] Preloaded {provider} client")
                results["success"].append(provider)
            except Exception as e:
                logger.warning(f"⚠️  [CLIENT CACHE] Failed to preload {provider}: {e}")
                results["failed"].append({"provider": provider, "error": str(e)})
        
        # Also preload component-specific clients if COMPONENT_CONFIG is available
        try:
            from run import COMPONENT_CONFIG
            
            # Get unique API providers from component config
            component_providers = set()
            for component, config in COMPONENT_CONFIG.items():
                provider = config.get("api_provider")
                if provider and provider != "none" and provider not in providers:
                    component_providers.add(provider)
            
            # Preload any additional providers found in components
            for provider in component_providers:
                if provider not in providers:  # Skip if already loaded
                    try:
                        client = cls.get_client(provider)
                        logger.info(f"✅ [CLIENT CACHE] Preloaded component provider: {provider}")
                        results["success"].append(provider)
                    except Exception as e:
                        logger.warning(f"⚠️  [CLIENT CACHE] Failed to preload component provider {provider}: {e}")
                        results["failed"].append({"provider": provider, "error": str(e)})
        
        except ImportError:
            logger.info("⚠️  [CLIENT CACHE] COMPONENT_CONFIG not available, skipping component-specific preloading")
        
        return results


# Convenience functions for drop-in replacement
def get_cached_api_client(provider: str = "deepseek", **kwargs):
    """Get cached API client (convenience function)"""
    return APIClientCache.get_client(provider, **kwargs)


def get_cached_client_for_component(component_type: str, **kwargs):
    """Get cached API client for component (convenience function)"""
    return APIClientCache.get_client_for_component(component_type, **kwargs)


# Global cache instance
api_client_cache = APIClientCache()
