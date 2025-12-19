#!/usr/bin/env python3
"""
Persistent API Client Cache

Provides persistent client instance caching to improve performance by reusing
API clients across multiple program runs.
"""

import json
import logging
import os
import pickle
import tempfile
import time
from pathlib import Path
from typing import Dict, List, Optional, Tuple

from .client_factory import APIClientFactory

logger = logging.getLogger(__name__)

# Cache directory for persisting API client state
CACHE_DIR = os.path.join(tempfile.gettempdir(), "z-beam-cache")
CACHE_INFO_FILE = os.path.join(CACHE_DIR, "cache_info.json")


class PersistentAPIClientCache:
    """
    Persistent cache for API client instances to improve performance across program runs.
    
    Saves client state to disk and restores it on program startup to avoid
    the overhead of recreating connections and authentication.
    """
    
    _instances: Dict[str, any] = {}
    _cache_hits = 0
    _cache_misses = 0
    _loaded_from_disk = False
    
    @classmethod
    def initialize(cls) -> None:
        """Initialize the persistent cache by loading state from disk"""
        # Create cache directory if it doesn't exist
        os.makedirs(CACHE_DIR, exist_ok=True)
        
        # Load cache info if it exists
        cls._load_cache_info()
        
        logger.info(f"🚀 [PERSISTENT CACHE] Initialized cache directory: {CACHE_DIR}")
    
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
        # Ensure cache is initialized
        if not cls._loaded_from_disk:
            cls.initialize()
        
        # Create cache key from provider and relevant kwargs
        cache_key = cls._create_cache_key(provider, **kwargs)
        
        if cache_key in cls._instances:
            cls._cache_hits += 1
            logger.debug(f"📋 [PERSISTENT CACHE] Cache HIT for {provider} (hits: {cls._cache_hits})")
            return cls._instances[cache_key]
        
        # Try to load from disk cache
        client = cls._load_client_from_disk(cache_key)
        if client:
            cls._instances[cache_key] = client
            cls._cache_hits += 1
            logger.info(f"📂 [PERSISTENT CACHE] Loaded {provider} client from disk cache")
            return client
        
        # Cache miss - create new client
        cls._cache_misses += 1
        logger.info(f"🏭 [PERSISTENT CACHE] Cache MISS for {provider} - creating new client (misses: {cls._cache_misses})")
        
        client = APIClientFactory.create_client(provider, **kwargs)
        cls._instances[cache_key] = client
        
        # Save to disk cache
        cls._save_client_to_disk(cache_key, client)
        
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
    def _get_client_cache_path(cls, cache_key: str) -> str:
        """Get file path for cached client"""
        # Create a filename-safe version of the cache key
        safe_key = cache_key.replace("|", "_").replace("=", "-").replace("/", "_")
        return os.path.join(CACHE_DIR, f"{safe_key}.cache")
    
    @classmethod
    def _save_client_to_disk(cls, cache_key: str, client: any) -> bool:
        """
        Save client to disk cache
        
        Returns:
            True if saved successfully, False otherwise
        """
        try:
            cache_path = cls._get_client_cache_path(cache_key)
            
            # Serialize client to file
            with open(cache_path, 'wb') as f:
                pickle.dump(client, f)
            
            # Update cache info
            cls._update_cache_info(cache_key, cache_path)
            
            logger.info(f"💾 [PERSISTENT CACHE] Saved client to disk: {cache_path}")
            return True
            
        except Exception as e:
            logger.warning(f"⚠️ [PERSISTENT CACHE] Failed to save client to disk: {e}")
            return False
    
    @classmethod
    def _load_client_from_disk(cls, cache_key: str) -> Optional[any]:
        """
        Load client from disk cache
        
        Returns:
            Client instance if loaded successfully, None otherwise
        """
        try:
            cache_path = cls._get_client_cache_path(cache_key)
            
            # Check if cache file exists
            if not os.path.exists(cache_path):
                return None
            
            # Deserialize client from file
            with open(cache_path, 'rb') as f:
                client = pickle.load(f)
            
            logger.info(f"📂 [PERSISTENT CACHE] Loaded client from disk: {cache_path}")
            return client
            
        except Exception as e:
            logger.warning(f"⚠️ [PERSISTENT CACHE] Failed to load client from disk: {e}")
            return None
    
    @classmethod
    def _load_cache_info(cls) -> dict:
        """
        Load cache info from disk
        
        Returns:
            Cache info dictionary
        """
        try:
            if os.path.exists(CACHE_INFO_FILE):
                with open(CACHE_INFO_FILE, 'r') as f:
                    cache_info = json.load(f)
                
                logger.info(f"📂 [PERSISTENT CACHE] Loaded cache info: {len(cache_info['clients'])} clients")
                cls._loaded_from_disk = True
                return cache_info
        except Exception as e:
            logger.warning(f"⚠️ [PERSISTENT CACHE] Failed to load cache info: {e}")
        
        # Return empty cache info if loading failed
        return {"clients": {}}
    
    @classmethod
    def _update_cache_info(cls, cache_key: str, cache_path: str) -> None:
        """Update cache info with new client"""
        try:
            cache_info = cls._load_cache_info()
            
            # Add or update client info
            cache_info["clients"][cache_key] = {
                "path": cache_path,
                "timestamp": str(Path(cache_path).stat().st_mtime),
                "size": str(Path(cache_path).stat().st_size),
            }
            
            # Save updated cache info
            with open(CACHE_INFO_FILE, 'w') as f:
                json.dump(cache_info, f, indent=2)
            
            logger.debug(f"📝 [PERSISTENT CACHE] Updated cache info for {cache_key}")
            
        except Exception as e:
            logger.warning(f"⚠️ [PERSISTENT CACHE] Failed to update cache info: {e}")
    
    @classmethod
    def clear_cache(cls) -> Tuple[int, List[str]]:
        """
        Clear all cached clients from memory and disk
        
        Returns:
            Tuple of (cleared_count, error_list)
        """
        cleared_count = len(cls._instances)
        errors = []
        
        # Clear in-memory cache
        cls._instances.clear()
        cls._cache_hits = 0
        cls._cache_misses = 0
        
        # Clear disk cache
        try:
            cache_info = cls._load_cache_info()
            
            for cache_key, info in cache_info["clients"].items():
                try:
                    cache_path = info["path"]
                    if os.path.exists(cache_path):
                        os.remove(cache_path)
                except Exception as e:
                    errors.append(f"Failed to remove {cache_key}: {e}")
            
            # Reset cache info
            with open(CACHE_INFO_FILE, 'w') as f:
                json.dump({"clients": {}}, f)
                
            logger.info(f"🧹 [PERSISTENT CACHE] Cleared {cleared_count} cached clients from disk")
            
        except Exception as e:
            errors.append(f"Failed to clear cache info: {e}")
        
        return cleared_count, errors
    
    @classmethod
    def get_cache_stats(cls) -> Dict[str, int]:
        """Get cache performance statistics"""
        # Ensure cache is initialized
        if not cls._loaded_from_disk:
            cls.initialize()
            
        total_requests = cls._cache_hits + cls._cache_misses
        hit_rate = (cls._cache_hits / total_requests * 100) if total_requests > 0 else 0
        
        # Count cached instances on disk
        try:
            cache_info = cls._load_cache_info()
            disk_instances = len(cache_info["clients"])
        except Exception as e:
            # Fail-fast: Cache info loading must succeed for accurate statistics
            raise RuntimeError(f"Failed to load cache statistics: {e}")
        
        return {
            "cache_hits": cls._cache_hits,
            "cache_misses": cls._cache_misses,
            "total_requests": total_requests,
            "hit_rate_percent": round(hit_rate, 1),
            "cached_instances": len(cls._instances),
            "disk_cached_instances": disk_instances,
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
        # Ensure cache is initialized
        if not cls._loaded_from_disk:
            cls.initialize()
            
        logger.info(f"🚀 [PERSISTENT CACHE] Preloading clients for: {', '.join(providers)}")
        results = {"success": [], "failed": []}
        
        for provider in providers:
            try:
                client = cls.get_client(provider)
                logger.info(f"✅ [PERSISTENT CACHE] Preloaded {provider} client")
                results["success"].append(provider)
            except Exception as e:
                logger.warning(f"⚠️ [PERSISTENT CACHE] Failed to preload {provider}: {e}")
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
                        logger.info(f"✅ [PERSISTENT CACHE] Preloaded component provider: {provider}")
                        results["success"].append(provider)
                    except Exception as e:
                        logger.warning(f"⚠️ [PERSISTENT CACHE] Failed to preload component provider {provider}: {e}")
                        results["failed"].append({"provider": provider, "error": str(e)})
        
        except ImportError:
            logger.info("⚠️ [PERSISTENT CACHE] COMPONENT_CONFIG not available, skipping component-specific preloading")
        
        return results
        
    @classmethod
    def cache_info(cls) -> dict:
        """Get detailed information about cached clients"""
        # Ensure cache is initialized
        if not cls._loaded_from_disk:
            cls.initialize()
            
        try:
            cache_info = cls._load_cache_info()
            
            # Enhance with additional metadata
            for cache_key, info in cache_info["clients"].items():
                cache_path = info["path"]
                if os.path.exists(cache_path):
                    # Add file age in seconds
                    mtime = os.path.getmtime(cache_path)
                    age = int(time.time() - mtime)
                    info["age_seconds"] = age
                    info["age_formatted"] = f"{age // 86400}d {(age % 86400) // 3600}h {(age % 3600) // 60}m"
                    
                    # Add whether it's loaded in memory
                    info["in_memory"] = cache_key in cls._instances
                else:
                    # Mark as missing
                    info["missing"] = True
            
            return {
                "clients": cache_info["clients"],
                "stats": cls.get_cache_stats(),
                "cache_dir": CACHE_DIR,
                "cache_info_file": CACHE_INFO_FILE,
            }
            
        except Exception as e:
            logger.warning(f"⚠️ [PERSISTENT CACHE] Failed to get cache info: {e}")
            return {"error": str(e)}


# Convenience functions for drop-in replacement
def get_cached_api_client(provider: str = "deepseek", **kwargs):
    """Get cached API client (convenience function)"""
    return PersistentAPIClientCache.get_client(provider, **kwargs)


def get_cached_client_for_component(component_type: str, **kwargs):
    """Get cached API client for component (convenience function)"""
    return PersistentAPIClientCache.get_client_for_component(component_type, **kwargs)


# Initialize cache on module import
PersistentAPIClientCache.initialize()
