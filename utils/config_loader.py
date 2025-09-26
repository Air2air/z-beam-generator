#!/usr/bin/env python3
"""
Centralized Configuration Loader

Consolidates 20+ duplicate YAML loading implementations across components
into a single, fail-fast, cached configuration loading system.

This utility follows GROK_INSTRUCTIONS principles:
- Fail-fast architecture (no defaults, no silent failures)
- Centralized functionality to reduce bloat
- Caching for performance optimization
- Comprehensive error handling
"""

import logging
import os
import time
import yaml
from pathlib import Path
from typing import Any, Dict, Optional

logger = logging.getLogger(__name__)


class ConfigurationError(Exception):
    """Raised when configuration loading fails"""
    pass


class ConfigLoader:
    """
    Centralized YAML configuration loader with caching and fail-fast behavior.
    
    Replaces 20+ duplicate implementations across components with a single,
    optimized, cached loading system.
    """
    
    # Cache for loaded configurations
    _config_cache: Dict[str, Dict[str, Any]] = {}
    _cache_timestamps: Dict[str, float] = {}
    _cache_ttl: int = 3600  # 1 hour cache TTL
    
    @classmethod
    def load_yaml_config(
        cls,
        config_path: str,
        component_name: Optional[str] = None,
        cache_enabled: bool = True,
        encoding: str = 'utf-8'
    ) -> Dict[str, Any]:
        """
        Load YAML configuration with caching and fail-fast behavior.
        
        Args:
            config_path: Path to YAML configuration file
            component_name: Component name for error context (optional)
            cache_enabled: Whether to use configuration caching
            encoding: File encoding (default: utf-8)
            
        Returns:
            Loaded configuration dictionary
            
        Raises:
            ConfigurationError: If file not found or invalid YAML
        """
        # Normalize path
        config_path = str(Path(config_path).resolve())
        
        # Check cache first (if enabled)
        if cache_enabled and cls._is_cached_valid(config_path):
            logger.debug(f"📋 [CONFIG] Cache HIT for {config_path}")
            return cls._config_cache[config_path].copy()
        
        # Load from file
        logger.debug(f"📂 [CONFIG] Loading YAML config: {config_path}")
        
        try:
            # Validate file exists
            if not os.path.exists(config_path):
                error_msg = f"Configuration file not found: {config_path}"
                if component_name:
                    error_msg += f" (required for {component_name} component)"
                raise ConfigurationError(error_msg)
            
            # Load YAML content
            with open(config_path, 'r', encoding=encoding) as f:
                config_data = yaml.safe_load(f)
            
            # Validate loaded data
            if config_data is None:
                config_data = {}
                logger.warning(f"⚠️  [CONFIG] Empty configuration loaded from {config_path}")
            
            if not isinstance(config_data, dict):
                raise ConfigurationError(
                    f"Configuration must be a dictionary, got {type(config_data).__name__}: {config_path}"
                )
            
            # Cache the result (if enabled)
            if cache_enabled:
                cls._config_cache[config_path] = config_data.copy()
                cls._cache_timestamps[config_path] = time.time()
                logger.debug(f"💾 [CONFIG] Cached configuration for {config_path}")
            
            logger.info(f"✅ [CONFIG] Loaded configuration: {config_path}")
            return config_data
            
        except yaml.YAMLError as e:
            error_msg = f"Invalid YAML in configuration file {config_path}: {e}"
            if component_name:
                error_msg += f" (required for {component_name} component)"
            raise ConfigurationError(error_msg)
        except IOError as e:
            error_msg = f"Cannot read configuration file {config_path}: {e}"
            if component_name:
                error_msg += f" (required for {component_name} component)"
            raise ConfigurationError(error_msg)
    
    @classmethod
    def load_component_config(
        cls,
        component_name: str,
        config_filename: str = "prompt.yaml",
        cache_enabled: bool = True
    ) -> Dict[str, Any]:
        """
        Load configuration for a specific component.
        
        Args:
            component_name: Name of the component (e.g., 'frontmatter', 'text')
            config_filename: Name of configuration file (default: prompt.yaml)
            cache_enabled: Whether to use caching
            
        Returns:
            Component configuration dictionary
            
        Raises:
            ConfigurationError: If component config not found or invalid
        """
        config_path = f"components/{component_name}/{config_filename}"
        return cls.load_yaml_config(
            config_path=config_path,
            component_name=component_name,
            cache_enabled=cache_enabled
        )
    
    @classmethod
    def _is_cached_valid(cls, config_path: str) -> bool:
        """Check if cached configuration is still valid"""
        if config_path not in cls._config_cache:
            return False
        
        # Check cache TTL
        cache_time = cls._cache_timestamps.get(config_path, 0)
        if time.time() - cache_time > cls._cache_ttl:
            # Cache expired
            cls._invalidate_cache(config_path)
            return False
        
        return True
    
    @classmethod
    def _invalidate_cache(cls, config_path: str) -> None:
        """Invalidate specific cache entry"""
        cls._config_cache.pop(config_path, None)
        cls._cache_timestamps.pop(config_path, None)
    
    @classmethod
    def clear_cache(cls) -> None:
        """Clear all cached configurations"""
        cls._config_cache.clear()
        cls._cache_timestamps.clear()
        logger.info("🗑️  [CONFIG] Configuration cache cleared")
    
    @classmethod
    def get_cache_stats(cls) -> Dict[str, Any]:
        """Get configuration cache statistics"""
        return {
            "cached_configs": len(cls._config_cache),
            "cache_size_bytes": sum(
                len(str(config)) for config in cls._config_cache.values()
            ),
            "oldest_cache_age": time.time() - min(cls._cache_timestamps.values()) 
                               if cls._cache_timestamps else 0,
            "cache_ttl": cls._cache_ttl
        }


# Convenience functions for backward compatibility with existing patterns
def load_yaml_config(config_path: str, component_name: Optional[str] = None) -> Dict[str, Any]:
    """
    Convenience function for loading YAML configuration.
    
    Replaces common pattern:
        with open(config_file, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f)
    
    With:
        data = load_yaml_config(config_file, component_name)
    """
    return ConfigLoader.load_yaml_config(config_path, component_name)


def load_component_config(component_name: str, config_filename: str = "prompt.yaml") -> Dict[str, Any]:
    """
    Convenience function for loading component configuration.
    
    Args:
        component_name: Component name (e.g., 'frontmatter', 'text')
        config_filename: Configuration file name (default: prompt.yaml)
        
    Returns:
        Component configuration dictionary
    """
    return ConfigLoader.load_component_config(component_name, config_filename)


# Factory function for easy instantiation
def create_config_loader() -> ConfigLoader:
    """Create a new ConfigLoader instance"""
    return ConfigLoader()


# ===== STANDARDIZED YAML UTILITIES =====
# These functions replace common YAML processing patterns throughout the codebase

def dump_yaml_with_defaults(data: Dict[str, Any], **kwargs) -> str:
    """
    Dump YAML with standardized default arguments.
    
    Replaces common pattern:
        yaml.dump(data, default_flow_style=False, sort_keys=False, allow_unicode=True)
    
    With:
        dump_yaml_with_defaults(data)
    """
    default_args = {
        'default_flow_style': False,
        'sort_keys': False,
        'allow_unicode': True,
        'width': 1000,  # Prevent excessive line wrapping
    }
    default_args.update(kwargs)
    return yaml.dump(data, **default_args)


def parse_yaml_frontmatter(content: str) -> Optional[Dict[str, Any]]:
    """
    Parse YAML frontmatter from content with standard delimiters.
    
    Handles both:
    - Standard frontmatter: --- YAML ---
    - Code block format: ```yaml YAML ```
    """
    content = content.strip()
    
    # Standard frontmatter format
    if content.startswith("---"):
        end_marker = content.find("---", 3)
        if end_marker != -1:
            yaml_content = content[3:end_marker].strip()
            try:
                return yaml.safe_load(yaml_content)
            except yaml.YAMLError as e:
                logger.error(f"YAML parsing error in frontmatter: {e}")
                return None
    
    # Code block format
    elif content.startswith("```yaml"):
        end_marker = content.find("```", 7)
        if end_marker != -1:
            yaml_content = content[7:end_marker].strip()
            try:
                return yaml.safe_load(yaml_content)
            except yaml.YAMLError as e:
                logger.error(f"YAML parsing error in code block: {e}")
                return None
    
    # Fail-fast: YAML content must be parseable - no fallback
    logger.error("No valid YAML content found in response")
    raise ValueError("YAML content parsing failed - no valid YAML found")


def safe_yaml_load(file_path: str) -> Optional[Dict[str, Any]]:
    """
    Safely load YAML file with error handling.
    
    Replaces common pattern:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = yaml.safe_load(f)
        except Exception as e:
            # handle error
    
    With:
        data = safe_yaml_load(file_path)
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)
    except Exception as e:
        logger.error(f"Error loading YAML file {file_path}: {e}")
        return None


# Global instance for easy access
config_loader = ConfigLoader()
