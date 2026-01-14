"""
Unified Configuration Loading

Central entry point for all configuration loading operations.
Consolidates multiple load_config() implementations into single interface.

Usage:
    from shared.config import load_config
    
    # Load any config
    config = load_config('materials', 'domain')
    config = load_config('generation', 'system')
    config = load_config('export', 'materials')

Replaces:
    - generation/config/config_loader.py: _load_config()
    - export/utils/data_loader.py: load_config()
    - shared/text/utils/component_specs.py: _load_config()
    - shared/validation/layer_validator.py: _load_config()
    - Multiple ConfigManager instances
"""

from pathlib import Path
from typing import Dict, Any, Optional
import yaml
from shared.config.manager import ConfigManager

# Singleton instance
_config_manager: Optional[ConfigManager] = None


def get_config_manager() -> ConfigManager:
    """Get or create singleton ConfigManager instance."""
    global _config_manager
    if _config_manager is None:
        _config_manager = ConfigManager()
    return _config_manager


def load_config(domain: str, config_type: str = 'domain') -> Dict[str, Any]:
    """
    Load configuration for any domain or system component.
    
    Args:
        domain: Domain name (materials, contaminants, settings, compounds)
               or system area (generation, export)
        config_type: Type of config ('domain', 'system', 'export')
        
    Returns:
        Loaded configuration dictionary
        
    Raises:
        FileNotFoundError: If config file doesn't exist
        ValueError: If config is invalid
        
    Examples:
        >>> config = load_config('materials', 'domain')
        >>> config = load_config('generation', 'system')
        >>> config = load_config('export', 'materials')
    """
    manager = get_config_manager()
    
    # Determine config path based on type
    if config_type == 'domain':
        config_path = Path(f'domains/{domain}/config.yaml')
    elif config_type == 'export':
        config_path = Path(f'export/config/{domain}.yaml')
    elif config_type == 'system':
        config_path = Path(f'{domain}/config.yaml')
    else:
        raise ValueError(f"Unknown config_type: {config_type}")
    
    if not config_path.exists():
        raise FileNotFoundError(f"Config not found: {config_path}")
    
    with open(config_path, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)


def load_domain_config(domain: str) -> Dict[str, Any]:
    """Load domain configuration (domains/*/config.yaml)."""
    return load_config(domain, 'domain')


def load_export_config(domain: str) -> Dict[str, Any]:
    """Load export configuration (export/config/*.yaml)."""
    return load_config(domain, 'export')


def load_system_config(system: str) -> Dict[str, Any]:
    """Load system configuration (generation/config.yaml, etc)."""
    return load_config(system, 'system')


__all__ = [
    'load_config',
    'load_domain_config',
    'load_export_config',
    'load_system_config',
    'get_config_manager',
]
