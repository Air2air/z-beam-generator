#!/usr/bin/env python3
"""
Optimized Configuration Manager
Provides efficient caching and loading of persona configurations.
"""

import yaml
import time
import logging
from pathlib import Path
from typing import Dict, Optional, Any
from functools import lru_cache

logger = logging.getLogger(__name__)

class ConfigurationManager:
    """Optimized configuration manager with caching and fallback handling."""
    
    def __init__(self):
        self._cache = {}
        self._cache_timestamps = {}
        self._cache_ttl = 300  # 5 minutes cache TTL
    
    @lru_cache(maxsize=32)
    def load_persona_config(self, author_id: int) -> Dict[str, Any]:
        """Load persona configuration with caching."""
        cache_key = f"persona_{author_id}"
        
        # Check cache validity
        if self._is_cache_valid(cache_key):
            return self._cache[cache_key]
        
        # Load fresh configuration
        config = self._load_persona_from_files(author_id)
        
        # Cache the result
        self._cache[cache_key] = config
        self._cache_timestamps[cache_key] = time.time()
        
        return config
    
    def _is_cache_valid(self, cache_key: str) -> bool:
        """Check if cached configuration is still valid."""
        if cache_key not in self._cache:
            return False
        
        cache_age = time.time() - self._cache_timestamps.get(cache_key, 0)
        return cache_age < self._cache_ttl
    
    def _load_persona_from_files(self, author_id: int) -> Dict[str, Any]:
        """Load persona configuration from available files."""
        # File priority: complete > enhanced > original
        file_patterns = [
            f"components/content/prompts/personas/*_complete.yaml",
            f"components/content/prompts/personas/*_enhanced.yaml", 
            f"components/content/prompts/personas/*_persona.yaml"
        ]
        
        country_map = {1: "taiwan", 2: "italy", 3: "indonesia", 4: "usa"}
        country = country_map.get(author_id, "international")
        
        # Try loading files in priority order
        for pattern in file_patterns:
            file_path = pattern.replace("*", country)
            if Path(file_path).exists() and Path(file_path).stat().st_size > 0:
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        config = yaml.safe_load(f)
                        if config:
                            logger.info(f"Loaded persona config from {file_path}")
                            return self._normalize_config(config)
                except Exception as e:
                    logger.warning(f"Failed to load {file_path}: {e}")
                    continue
        
        # Fallback configuration
        logger.warning(f"No valid persona config found for author_id {author_id}, using fallback")
        return self._get_fallback_config(author_id, country)
    
    def _normalize_config(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Normalize configuration structure for consistency."""
        normalized = config.copy()
        
        # Ensure required sections exist
        required_sections = ['writing_style', 'language_patterns', 'content_structure']
        for section in required_sections:
            if section not in normalized:
                normalized[section] = {}
        
        # Add formatting section if available
        if 'formatting' in config:
            normalized['enhanced_formatting'] = config['formatting']
        
        return normalized
    
    def _get_fallback_config(self, author_id: int, country: str) -> Dict[str, Any]:
        """Provide fallback configuration when files are missing."""
        author_names = {1: "Yi-Chun Lin", 2: "Alessandro Moretti", 3: "Ikmanda Roswati", 4: "Todd Dunning"}
        countries = {1: "Taiwan", 2: "Italy", 3: "Indonesia", 4: "United States"}
        
        return {
            'author_id': author_id,
            'name': author_names.get(author_id, "Expert"),
            'country': countries.get(author_id, "International"),
            'writing_style': {
                'approach': 'professional',
                'sentence_structure': 'medium sentences with natural flow',
                'organization': 'logical progression'
            },
            'language_patterns': {
                'signature_phrases': ['technical analysis shows', 'systematic approach enables']
            },
            'content_structure': {
                'title_pattern': 'Laser Cleaning of {material}: Technical Analysis',
                'byline': f"**{author_names.get(author_id, 'Expert')}, Ph.D. - {countries.get(author_id, 'International')}**"
            }
        }
    
    def clear_cache(self):
        """Clear configuration cache."""
        self._cache.clear()
        self._cache_timestamps.clear()
        # Clear LRU cache
        self.load_persona_config.cache_clear()
    
    def preload_all_personas(self):
        """Preload all persona configurations for better performance."""
        for author_id in [1, 2, 3, 4]:
            self.load_persona_config(author_id)
        logger.info("Preloaded all persona configurations")

# Global instance for efficient access
_config_manager = ConfigurationManager()

def get_optimized_persona_config(author_id: int) -> Dict[str, Any]:
    """Get optimized persona configuration with caching."""
    return _config_manager.load_persona_config(author_id)

def clear_persona_cache():
    """Clear persona configuration cache."""
    _config_manager.clear_cache()

def preload_persona_configs():
    """Preload all persona configurations."""
    _config_manager.preload_all_personas()
