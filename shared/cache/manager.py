"""
CacheManager - Domain-keyed in-memory cache with TTL support.

Provides a simple shared cache for all data loaders. Each domain gets its own
namespace so invalidation can be scoped without affecting other domains.

Usage:
    from shared.cache.manager import cache_manager

    # Store
    cache_manager.set('materials', 'main_yaml', data, ttl=3600)

    # Retrieve (returns None if missing or expired)
    data = cache_manager.get('materials', 'main_yaml')

    # Invalidate an entire domain
    cache_manager.invalidate('materials')
"""

import logging
import threading
import time
from typing import Any, Dict, Optional, Tuple

logger = logging.getLogger(__name__)


class CacheManager:
    """
    Thread-safe, domain-keyed in-memory cache with TTL expiry.

    Structure:
        _store[domain][key] = (value, expires_at)
    """

    def __init__(self) -> None:
        self._store: Dict[str, Dict[str, Tuple[Any, float]]] = {}
        self._lock = threading.Lock()

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def get(self, domain: str, key: str) -> Optional[Any]:
        """
        Return cached value for domain/key, or None if absent or expired.

        Args:
            domain: Namespace (e.g. 'materials', 'contaminants')
            key:    Cache key within the domain

        Returns:
            Cached value, or None
        """
        with self._lock:
            entry = self._store.get(domain, {}).get(key)
            if entry is None:
                return None
            value, expires_at = entry
            if expires_at != 0 and time.monotonic() > expires_at:
                # Expired — evict lazily
                del self._store[domain][key]
                logger.debug(f"Cache expired: {domain}/{key}")
                return None
            return value

    def set(self, domain: str, key: str, value: Any, ttl: int = 3600) -> None:
        """
        Store value under domain/key with a TTL.

        Args:
            domain: Namespace
            key:    Cache key
            value:  Value to store
            ttl:    Seconds until expiry. Use 0 for no expiry.
        """
        expires_at = (time.monotonic() + ttl) if ttl > 0 else 0
        with self._lock:
            if domain not in self._store:
                self._store[domain] = {}
            self._store[domain][key] = (value, expires_at)
            logger.debug(f"Cache set: {domain}/{key} (ttl={ttl}s)")

    def invalidate(self, domain: str) -> None:
        """
        Remove all cached entries for a domain.

        Args:
            domain: Namespace to clear
        """
        with self._lock:
            count = len(self._store.pop(domain, {}))
            if count:
                logger.info(f"Cache invalidated: {domain} ({count} entries cleared)")

    def invalidate_key(self, domain: str, key: str) -> None:
        """
        Remove a single cached entry.

        Args:
            domain: Namespace
            key:    Cache key to remove
        """
        with self._lock:
            if domain in self._store and key in self._store[domain]:
                del self._store[domain][key]
                logger.debug(f"Cache key removed: {domain}/{key}")

    def clear_all(self) -> None:
        """Remove all cached data across all domains."""
        with self._lock:
            total = sum(len(v) for v in self._store.values())
            self._store.clear()
            logger.info(f"Cache fully cleared ({total} entries)")

    def stats(self) -> Dict[str, Any]:
        """Return cache statistics for diagnostics."""
        with self._lock:
            return {
                "domains": list(self._store.keys()),
                "total_entries": sum(len(v) for v in self._store.values()),
                "by_domain": {d: len(keys) for d, keys in self._store.items()},
            }


# Singleton — import and use directly
cache_manager = CacheManager()
