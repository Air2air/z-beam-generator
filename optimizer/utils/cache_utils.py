#!/usr/bin/env python3
"""
Cache Utilities for Z-Beam Optimizer

Caching utilities for performance optimization.
"""

import hashlib
import logging
import time
from dataclasses import dataclass
from typing import Any, Dict, Optional

logger = logging.getLogger(__name__)


@dataclass
class CacheEntry:
    """Entry in the cache with metadata."""
    key: str
    value: Any
    timestamp: float
    ttl: Optional[float] = None
    access_count: int = 0
    last_accessed: Optional[float] = None

    @property
    def is_expired(self) -> bool:
        """Check if the entry has expired."""
        if self.ttl is None:
            return False
        return time.time() - self.timestamp > self.ttl

    @property
    def age(self) -> float:
        """Get the age of the entry in seconds."""
        return time.time() - self.timestamp

    def access(self) -> None:
        """Mark the entry as accessed."""
        self.access_count += 1
        self.last_accessed = time.time()


class LRUCache:
    """
    Least Recently Used (LRU) cache implementation.

    Provides efficient caching with automatic cleanup of expired entries.
    """

    def __init__(self, max_size: int = 1000, default_ttl: Optional[float] = None):
        self.max_size = max_size
        self.default_ttl = default_ttl
        self.cache: Dict[str, CacheEntry] = {}
        self.access_order: list = []  # For LRU tracking
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")

    def _generate_key(self, key: Any) -> str:
        """Generate a cache key from any hashable object."""
        if isinstance(key, str):
            return key
        elif isinstance(key, (int, float, bool)):
            return str(key)
        else:
            # For complex objects, create a hash
            key_str = str(key)
            return hashlib.md5(key_str.encode()).hexdigest()

    def get(self, key: Any, default: Any = None) -> Any:
        """Get a value from the cache."""
        cache_key = self._generate_key(key)

        if cache_key not in self.cache:
            return default

        entry = self.cache[cache_key]

        if entry.is_expired:
            self._remove_entry(cache_key)
            return default

        entry.access()
        self._update_access_order(cache_key)
        return entry.value

    def put(self, key: Any, value: Any, ttl: Optional[float] = None) -> None:
        """Put a value in the cache."""
        cache_key = self._generate_key(key)
        ttl = ttl or self.default_ttl

        # Remove existing entry if it exists
        if cache_key in self.cache:
            self._remove_entry(cache_key)

        # Create new entry
        entry = CacheEntry(
            key=cache_key,
            value=value,
            timestamp=time.time(),
            ttl=ttl
        )

        self.cache[cache_key] = entry
        self.access_order.append(cache_key)

        # Enforce size limit
        if len(self.cache) > self.max_size:
            self._evict_lru()

    def delete(self, key: Any) -> bool:
        """Delete a key from the cache."""
        cache_key = self._generate_key(key)
        if cache_key in self.cache:
            self._remove_entry(cache_key)
            return True
        return False

    def clear(self) -> None:
        """Clear all entries from the cache."""
        self.cache.clear()
        self.access_order.clear()

    def cleanup_expired(self) -> int:
        """Remove all expired entries."""
        expired_keys = [
            key for key, entry in self.cache.items()
            if entry.is_expired
        ]

        for key in expired_keys:
            self._remove_entry(key)

        if expired_keys:
            self.logger.info(f"Cleaned up {len(expired_keys)} expired cache entries")

        return len(expired_keys)

    def _remove_entry(self, key: str) -> None:
        """Remove an entry from the cache."""
        if key in self.cache:
            del self.cache[key]
        if key in self.access_order:
            self.access_order.remove(key)

    def _update_access_order(self, key: str) -> None:
        """Update the access order for LRU."""
        if key in self.access_order:
            self.access_order.remove(key)
        self.access_order.append(key)

    def _evict_lru(self) -> None:
        """Evict the least recently used entry."""
        if self.access_order:
            lru_key = self.access_order.pop(0)
            if lru_key in self.cache:
                del self.cache[lru_key]
                self.logger.debug(f"Evicted LRU cache entry: {lru_key}")

    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        total_accesses = sum(entry.access_count for entry in self.cache.values())
        avg_age = sum(entry.age for entry in self.cache.values()) / len(self.cache) if self.cache else 0

        return {
            'size': len(self.cache),
            'max_size': self.max_size,
            'total_accesses': total_accesses,
            'hit_rate': total_accesses / max(1, sum(len(self.access_order) for _ in range(len(self.cache)))),
            'average_age': avg_age,
            'expired_entries': len([e for e in self.cache.values() if e.is_expired])
        }

    def __len__(self) -> int:
        """Get the number of entries in the cache."""
        return len(self.cache)

    def __contains__(self, key: Any) -> bool:
        """Check if a key exists in the cache."""
        cache_key = self._generate_key(key)
        return cache_key in self.cache and not self.cache[cache_key].is_expired


class CacheManager:
    """Manager for multiple named caches."""

    def __init__(self):
        self.caches: Dict[str, LRUCache] = {}
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")

    def get_cache(self, name: str, **kwargs) -> LRUCache:
        """Get or create a named cache."""
        if name not in self.caches:
            self.caches[name] = LRUCache(**kwargs)
            self.logger.info(f"Created cache: {name}")
        return self.caches[name]

    def cleanup_all(self) -> Dict[str, int]:
        """Clean up expired entries in all caches."""
        results = {}
        for name, cache in self.caches.items():
            cleaned = cache.cleanup_expired()
            if cleaned > 0:
                results[name] = cleaned
        return results

    def get_all_stats(self) -> Dict[str, Dict[str, Any]]:
        """Get statistics for all caches."""
        return {name: cache.get_stats() for name, cache in self.caches.items()}


# Global cache manager instance
_cache_manager: Optional[CacheManager] = None


def get_cache_manager() -> CacheManager:
    """Get the global cache manager instance."""
    global _cache_manager
    if _cache_manager is None:
        _cache_manager = CacheManager()
    return _cache_manager
