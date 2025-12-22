"""
Cache Utilities - Centralized cache management operations

Consolidates 23+ cache clearing patterns across the codebase into
standardized, reusable functions.

Created: December 21, 2025
Purpose: Code consolidation and DRY compliance

Note: This provides utility functions for common cache operations.
Each domain/module should still implement domain-specific cache logic
but can use these utilities for common patterns.
"""

from functools import lru_cache, wraps
from typing import Any, Callable, Dict, Optional, Tuple
import logging

logger = logging.getLogger(__name__)


def clear_lru_cache(func: Callable) -> None:
    """
    Clear LRU cache for a decorated function.
    
    Args:
        func: Function decorated with @lru_cache
    
    Example:
        >>> @lru_cache(maxsize=128)
        ... def expensive_operation(key):
        ...     return compute(key)
        >>> 
        >>> # Clear cache when data changes
        >>> clear_lru_cache(expensive_operation)
    """
    if hasattr(func, 'cache_clear'):
        func.cache_clear()
    else:
        logger.warning(f"Function {func.__name__} does not have cache_clear method")


def get_cache_stats(func: Callable) -> Optional[Tuple[int, int, int, int]]:
    """
    Get cache statistics for LRU cached function.
    
    Args:
        func: Function decorated with @lru_cache
    
    Returns:
        Tuple of (hits, misses, maxsize, currsize) or None if not cached
    
    Example:
        >>> @lru_cache(maxsize=128)
        ... def fetch_data(key):
        ...     return database.get(key)
        >>> 
        >>> stats = get_cache_stats(fetch_data)
        >>> if stats:
        ...     hits, misses, maxsize, currsize = stats
        ...     print(f"Hit rate: {hits / (hits + misses):.1%}")
    """
    if hasattr(func, 'cache_info'):
        info = func.cache_info()
        return (info.hits, info.misses, info.maxsize, info.currsize)
    return None


def cache_with_logging(maxsize: int = 128, typed: bool = False):
    """
    LRU cache decorator with automatic logging.
    
    Args:
        maxsize: Maximum cache size
        typed: If True, different argument types are cached separately
    
    Returns:
        Decorator function
    
    Example:
        >>> @cache_with_logging(maxsize=256)
        ... def load_config(config_name: str):
        ...     logger.info(f"Loading {config_name} from disk")
        ...     return yaml.load(f"{config_name}.yaml")
    """
    def decorator(func: Callable) -> Callable:
        cached_func = lru_cache(maxsize=maxsize, typed=typed)(func)
        
        @wraps(func)
        def wrapper(*args, **kwargs):
            result = cached_func(*args, **kwargs)
            
            # Log cache stats periodically
            if hasattr(cached_func, 'cache_info'):
                info = cached_func.cache_info()
                if (info.hits + info.misses) % 100 == 0:  # Log every 100 calls
                    hit_rate = info.hits / (info.hits + info.misses) if (info.hits + info.misses) > 0 else 0
                    logger.debug(
                        f"{func.__name__} cache: {info.hits} hits, {info.misses} misses "
                        f"({hit_rate:.1%} hit rate), {info.currsize}/{info.maxsize} size"
                    )
            
            return result
        
        # Preserve cache methods
        wrapper.cache_clear = cached_func.cache_clear
        wrapper.cache_info = cached_func.cache_info
        
        return wrapper
    
    return decorator


class SimpleCache:
    """
    Simple dict-based cache with optional size limit.
    
    Use when you need more control than @lru_cache provides.
    
    Example:
        >>> cache = SimpleCache(maxsize=100)
        >>> 
        >>> # Store data
        >>> cache.set('user_123', {'name': 'Alice', 'role': 'admin'})
        >>> 
        >>> # Retrieve data
        >>> user = cache.get('user_123')
        >>> if user:
        ...     print(f"Found: {user['name']}")
        >>> 
        >>> # Clear cache
        >>> cache.clear()
    """
    
    def __init__(self, maxsize: Optional[int] = None):
        """
        Initialize cache.
        
        Args:
            maxsize: Maximum number of items (None = unlimited)
        """
        self._cache: Dict[Any, Any] = {}
        self._maxsize = maxsize
        self._hits = 0
        self._misses = 0
    
    def get(self, key: Any, default: Any = None) -> Any:
        """
        Get value from cache.
        
        Args:
            key: Cache key
            default: Default value if key not found
        
        Returns:
            Cached value or default
        """
        if key in self._cache:
            self._hits += 1
            return self._cache[key]
        else:
            self._misses += 1
            return default
    
    def set(self, key: Any, value: Any) -> None:
        """
        Store value in cache.
        
        Args:
            key: Cache key
            value: Value to cache
        """
        # Enforce size limit (simple FIFO eviction)
        if self._maxsize and len(self._cache) >= self._maxsize:
            # Remove oldest item (first inserted)
            first_key = next(iter(self._cache))
            del self._cache[first_key]
        
        self._cache[key] = value
    
    def clear(self, key: Optional[Any] = None) -> None:
        """
        Clear cache.
        
        Args:
            key: Specific key to clear (None = clear all)
        """
        if key is None:
            self._cache.clear()
            self._hits = 0
            self._misses = 0
        elif key in self._cache:
            del self._cache[key]
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Get cache statistics.
        
        Returns:
            Dict with hits, misses, size, hit_rate
        """
        total = self._hits + self._misses
        hit_rate = self._hits / total if total > 0 else 0
        
        return {
            'hits': self._hits,
            'misses': self._misses,
            'size': len(self._cache),
            'maxsize': self._maxsize,
            'hit_rate': hit_rate
        }
    
    def __len__(self) -> int:
        """Return number of cached items."""
        return len(self._cache)
    
    def __contains__(self, key: Any) -> bool:
        """Check if key exists in cache."""
        return key in self._cache


def timed_cache(seconds: int):
    """
    Cache decorator with time-based expiration.
    
    Args:
        seconds: Cache lifetime in seconds
    
    Returns:
        Decorator function
    
    Example:
        >>> from time import time
        >>> 
        >>> @timed_cache(seconds=300)  # Cache for 5 minutes
        ... def fetch_external_data(api_key):
        ...     return requests.get(f"https://api.example.com/data?key={api_key}").json()
    """
    import time
    
    def decorator(func: Callable) -> Callable:
        cache: Dict[Tuple, Tuple[float, Any]] = {}
        
        @wraps(func)
        def wrapper(*args, **kwargs):
            key = (args, tuple(sorted(kwargs.items())))
            current_time = time.time()
            
            if key in cache:
                timestamp, value = cache[key]
                if current_time - timestamp < seconds:
                    return value
            
            # Cache expired or not found, compute new value
            value = func(*args, **kwargs)
            cache[key] = (current_time, value)
            
            return value
        
        def cache_clear():
            cache.clear()
        
        wrapper.cache_clear = cache_clear
        return wrapper
    
    return decorator


# Global registry of cacheable functions for batch clearing
_CACHE_REGISTRY: Dict[str, Callable] = {}


def register_cache(name: str, func: Callable) -> None:
    """
    Register a cached function for centralized cache management.
    
    Args:
        name: Unique name for this cache
        func: Cached function
    
    Example:
        >>> @lru_cache(maxsize=128)
        ... def load_materials():
        ...     return yaml.load('Materials.yaml')
        >>> 
        >>> register_cache('materials_loader', load_materials)
    """
    _CACHE_REGISTRY[name] = func


def clear_all_registered_caches() -> int:
    """
    Clear all registered caches.
    
    Returns:
        Number of caches cleared
    
    Example:
        >>> # After data update, clear all caches
        >>> cleared = clear_all_registered_caches()
        >>> print(f"Cleared {cleared} caches")
    """
    count = 0
    for name, func in _CACHE_REGISTRY.items():
        try:
            clear_lru_cache(func)
            count += 1
            logger.debug(f"Cleared cache: {name}")
        except Exception as e:
            logger.warning(f"Failed to clear cache {name}: {e}")
    
    return count


def get_all_cache_stats() -> Dict[str, Any]:
    """
    Get statistics for all registered caches.
    
    Returns:
        Dict mapping cache name to stats
    
    Example:
        >>> stats = get_all_cache_stats()
        >>> for name, cache_stats in stats.items():
        ...     if cache_stats:
        ...         print(f"{name}: {cache_stats[0]} hits, {cache_stats[1]} misses")
    """
    return {
        name: get_cache_stats(func)
        for name, func in _CACHE_REGISTRY.items()
    }
