#!/usr/bin/env python3
"""
Persistent Research Cache for Category Contamination Data

Provides disk-based caching of category research results to avoid redundant API calls.
Cache entries expire after 30 days to ensure freshness.

Author: AI Assistant
Date: November 25, 2025
"""

import json
import logging
from pathlib import Path
from typing import Dict, Optional, Any
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


class PersistentResearchCache:
    """
    Disk-based cache for category contamination research with TTL support.
    
    CACHING SCOPE:
    - Caches: Category-level contamination patterns (e.g., metals_ferrous research)
    - Does NOT cache: Dynamic prompt assembly, material-specific customization,
      contamination_level, uniformity, environment_wear, or any generation parameters
    
    IMPACT ON CUSTOMIZATION:
    - Cached patterns are TEMPLATES that get dynamically applied
    - Each generation fully customizes: intensity, distribution, aging effects
    - Prompts remain 100% dynamic and unique per generation
    - Cache provides reusable KNOWLEDGE, not fixed prompts
    
    Example: 10 Steel generations with cache:
    - Research metals_ferrous once (patterns: rust, oil, dust)
    - Each generation applies patterns differently based on:
      * contamination_level (1-5): How much contamination
      * uniformity (1-5): How many pattern types
      * environment_wear (1-5): Background aging level
      * Material-specific properties
    - Result: 10 unique prompts from 1 cached research call
    """
    
    def __init__(self, cache_dir: Optional[Path] = None, ttl_days: int = 30):
        """
        Initialize persistent cache.
        
        Args:
            cache_dir: Directory for cache files (default: cache/research/)
            ttl_days: Time-to-live in days for cache entries (default: 30)
        """
        if cache_dir is None:
            # Default to cache/research/ relative to project root
            project_root = Path(__file__).parent.parent.parent.parent
            cache_dir = project_root / "cache" / "research"
        
        self.cache_dir = Path(cache_dir)
        self.ttl_days = ttl_days
        self.ttl_delta = timedelta(days=ttl_days)
        
        # Create cache directory if it doesn't exist
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        
        logger.info(f"✅ Persistent cache initialized at {self.cache_dir} (TTL: {ttl_days} days)")
    
    def _get_cache_path(self, category: str) -> Path:
        """Get cache file path for category."""
        # Sanitize category name for filename
        safe_name = category.replace("/", "_").replace("\\", "_")
        return self.cache_dir / f"{safe_name}.json"
    
    def get(self, category: str) -> Optional[Dict[str, Any]]:
        """
        Get cached research data for category if fresh.
        
        Args:
            category: Material category
            
        Returns:
            Cached data if fresh, None if expired or not found
        """
        cache_path = self._get_cache_path(category)
        
        if not cache_path.exists():
            logger.debug(f"📭 Cache miss: {category}")
            return None
        
        try:
            with open(cache_path, 'r', encoding='utf-8') as f:
                cache_entry = json.load(f)
            
            # Check expiration
            cached_time = datetime.fromisoformat(cache_entry['timestamp'])
            age = datetime.now() - cached_time
            
            if age > self.ttl_delta:
                logger.info(f"⏰ Cache expired for {category} (age: {age.days} days)")
                # Delete expired entry
                cache_path.unlink()
                return None
            
            logger.info(f"📬 Cache hit: {category} (age: {age.days} days)")
            return cache_entry['data']
            
        except (json.JSONDecodeError, KeyError, ValueError) as e:
            logger.warning(f"⚠️  Corrupted cache for {category}: {e}")
            # Delete corrupted entry
            cache_path.unlink(missing_ok=True)
            return None
    
    def set(self, category: str, data: Dict[str, Any]) -> None:
        """
        Store research data in cache.
        
        Args:
            category: Material category
            data: Research data to cache
        """
        cache_path = self._get_cache_path(category)
        
        cache_entry = {
            'timestamp': datetime.now().isoformat(),
            'category': category,
            'data': data
        }
        
        try:
            with open(cache_path, 'w', encoding='utf-8') as f:
                json.dump(cache_entry, f, indent=2, ensure_ascii=False)
            
            logger.info(f"💾 Cached research for {category}")
            
        except Exception as e:
            logger.error(f"❌ Failed to cache {category}: {e}")
    
    def clear_expired(self) -> int:
        """
        Remove all expired cache entries.
        
        Returns:
            Number of entries removed
        """
        removed = 0
        
        for cache_file in self.cache_dir.glob("*.json"):
            try:
                with open(cache_file, 'r', encoding='utf-8') as f:
                    cache_entry = json.load(f)
                
                cached_time = datetime.fromisoformat(cache_entry['timestamp'])
                age = datetime.now() - cached_time
                
                if age > self.ttl_delta:
                    cache_file.unlink()
                    removed += 1
                    logger.debug(f"🗑️  Removed expired cache: {cache_file.name}")
                    
            except Exception as e:
                logger.warning(f"⚠️  Error checking {cache_file.name}: {e}")
                # Remove corrupted files
                cache_file.unlink(missing_ok=True)
                removed += 1
        
        if removed > 0:
            logger.info(f"🗑️  Cleared {removed} expired cache entries")
        
        return removed
    
    def clear_all(self) -> int:
        """
        Remove all cache entries.
        
        Returns:
            Number of entries removed
        """
        removed = 0
        
        for cache_file in self.cache_dir.glob("*.json"):
            cache_file.unlink()
            removed += 1
        
        logger.info(f"🗑️  Cleared all cache ({removed} entries)")
        return removed
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """
        Get cache statistics.
        
        Returns:
            Dictionary with cache stats (count, total_size, oldest, newest)
        """
        entries = list(self.cache_dir.glob("*.json"))
        total_size = sum(f.stat().st_size for f in entries)
        
        timestamps = []
        for cache_file in entries:
            try:
                with open(cache_file, 'r', encoding='utf-8') as f:
                    cache_entry = json.load(f)
                timestamps.append(datetime.fromisoformat(cache_entry['timestamp']))
            except Exception:
                continue
        
        stats = {
            'count': len(entries),
            'total_size_bytes': total_size,
            'total_size_mb': total_size / (1024 * 1024),
            'oldest': min(timestamps).isoformat() if timestamps else None,
            'newest': max(timestamps).isoformat() if timestamps else None,
            'cache_dir': str(self.cache_dir),
            'ttl_days': self.ttl_days
        }
        
        return stats
