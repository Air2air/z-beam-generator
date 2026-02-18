"""
Export Configuration Validator

Validates export domain configurations to catch errors early.
Part of the export system health check infrastructure.

Usage:
    from export.config.validator import validate_config, validate_all_configs
    
    # Validate single config
    errors = validate_config(config)
    if errors:
        raise ConfigurationError("\\n".join(errors))
    
    # Validate all domains
    validate_all_configs()  # Raises ConfigurationError if any issues

Created: Dec 20, 2025
"""

import logging
from pathlib import Path
from typing import Dict, List, Any

logger = logging.getLogger(__name__)


class ConfigurationError(Exception):
    """Raised when export configuration is invalid"""
    pass


def validate_config(config: Dict[str, Any], config_dir: Path = None) -> List[str]:
    """
    Validate a domain configuration dictionary.
    
    Args:
        config: Domain configuration dict
        config_dir: Config directory path (for resolving relative paths)
    
    Returns:
        List of error messages (empty if valid)
    """
    errors = []
    
    # Check required keys
    required_keys = ['domain', 'source_file', 'output_path', 'items_key']
    for key in required_keys:
        if key not in config:
            errors.append(f"Missing required key: {key}")
    
    if errors:
        return errors  # Can't continue validation without required keys
    
    # Get base directory for path resolution
    if config_dir is None:
        config_dir = Path(__file__).parent
    project_root = config_dir.parent.parent
    
    # Validate source_file exists
    source_file = project_root / config['source_file']
    if not source_file.exists():
        errors.append(f"Source file not found: {config['source_file']} (resolved: {source_file})")
    
    # Validate source_file is not absolute path
    if config['source_file'].startswith('/'):
        errors.append(f"Source file should use relative path, not absolute: {config['source_file']}")
    
    # Validate output_path is not absolute
    if config['output_path'].startswith('/'):
        errors.append(f"Output path should use relative path, not absolute: {config['output_path']}")
    
    # Validate output_path parent directory exists (or can be created)
    try:
        if config['output_path'].startswith('../'):
            # Relative to project root parent
            output_path = project_root.parent / config['output_path'].lstrip('../')
        else:
            output_path = project_root / config['output_path']
        
        if not output_path.parent.exists():
            errors.append(f"Output directory parent doesn't exist and may not be creatable: {output_path.parent}")
    except Exception as e:
        errors.append(f"Cannot validate output path: {e}")
    
    # Validate enrichments if present
    if 'enrichments' in config:
        if not isinstance(config['enrichments'], list):
            errors.append("'enrichments' must be a list")
        else:
            for i, enrichment in enumerate(config['enrichments']):
                if not isinstance(enrichment, dict):
                    errors.append(f"Enrichment {i} must be a dict")
                elif 'type' not in enrichment:
                    errors.append(f"Enrichment {i} missing required 'type' key")
    
    # Validate generators if present
    if 'generators' in config:
        if not isinstance(config['generators'], list):
            errors.append("'generators' must be a list")
        else:
            for i, generator in enumerate(config['generators']):
                if not isinstance(generator, dict):
                    errors.append(f"Generator {i} must be a dict")
                elif 'type' not in generator:
                    errors.append(f"Generator {i} missing required 'type' key")
    
    return errors


def validate_all_configs() -> None:
    """
    Validate all domain configurations.
    
    Raises:
        ConfigurationError: If any configuration is invalid
    """
    from export.config.loader import load_domain_config
    
    all_errors = []
    domains = ['materials', 'contaminants', 'compounds', 'settings', 'applications']
    
    for domain in domains:
        try:
            config = load_domain_config(domain)
            errors = validate_config(config)
            
            if errors:
                all_errors.append(f"\n{domain.upper()} CONFIG ERRORS:")
                all_errors.extend(f"  - {error}" for error in errors)
                
        except Exception as e:
            all_errors.append(f"\n{domain.upper()} CONFIG LOAD ERROR:")
            all_errors.append(f"  - {e}")
    
    if all_errors:
        raise ConfigurationError("\n".join(all_errors))
    
    logger.info(f"✅ All {len(domains)} domain configs validated successfully")


def check_config_health() -> Dict[str, Any]:
    """
    Check configuration health and return detailed status.
    
    Returns:
        Dict with status information:
        {
            'valid': bool,
            'errors': List[str],
            'warnings': List[str],
            'domains_checked': int
        }
    """
    from export.config.loader import load_domain_config
    
    result = {
        'valid': True,
        'errors': [],
        'warnings': [],
        'domains_checked': 0
    }
    
    domains = ['materials', 'contaminants', 'compounds', 'settings', 'applications']
    
    for domain in domains:
        try:
            config = load_domain_config(domain)
            errors = validate_config(config)
            
            if errors:
                result['valid'] = False
                result['errors'].extend([f"{domain}: {error}" for error in errors])
            
            result['domains_checked'] += 1
            
        except Exception as e:
            result['valid'] = False
            result['errors'].append(f"{domain}: Failed to load config - {e}")
    
    return result


if __name__ == '__main__':
    # Quick validation script
    try:
        validate_all_configs()
        print("✅ All configurations valid")
    except ConfigurationError as e:
        print(f"❌ Configuration errors found:\n{e}")
        exit(1)
