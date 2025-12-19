"""
Configuration Loader Utilities

Utilities for loading and validating domain configuration files.
Part of Export System Consolidation (Phase 1).

Domain configs define exporter behavior without code changes:
- Source/output paths
- Field mappings
- Enrichment pipeline
- Content generation pipeline

Configuration files live in export/config/{domain}.yaml

Example config file (export/config/materials.yaml):
    domain: materials
    source_file: data/materials/Materials.yaml
    output_path: frontmatter/materials
    items_key: materials
    enrichments:
      - type: compound_linkage
        field: produces_compounds
        source: data/compounds/Compounds.yaml
        defaults: [concentration_range, hazard_class]

Usage:
    from export.config.loader import load_domain_config
    
    config = load_domain_config('materials')
    # Returns dict with validated configuration
"""

import logging
from pathlib import Path
from typing import Any, Dict, Optional

import yaml

logger = logging.getLogger(__name__)

# Default config directory
CONFIG_DIR = Path(__file__).parent


def load_domain_config(domain: str, config_dir: Optional[Path] = None) -> Dict[str, Any]:
    """
    Load domain configuration from YAML file.
    
    Args:
        domain: Domain name (e.g., 'materials', 'contaminants')
        config_dir: Optional config directory (default: export/config/)
    
    Returns:
        Validated configuration dict
    
    Raises:
        FileNotFoundError: If config file doesn't exist
        ValueError: If config invalid
        yaml.YAMLError: If YAML parsing fails
    
    Example:
        config = load_domain_config('materials')
        print(config['source_file'])  # 'data/materials/Materials.yaml'
    """
    if config_dir is None:
        config_dir = CONFIG_DIR
    
    config_file = config_dir / f"{domain}.yaml"
    
    if not config_file.exists():
        raise FileNotFoundError(
            f"Domain config not found: {config_file}\n"
            f"Expected location: export/config/{domain}.yaml"
        )
    
    logger.debug(f"Loading domain config: {config_file}")
    
    with open(config_file, 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)
    
    # Validate configuration
    validate_config(config, domain)
    
    logger.info(f"Loaded config for domain: {domain}")
    return config


def validate_config(config: Dict[str, Any], domain: str) -> None:
    """
    Validate domain configuration.
    
    Args:
        config: Configuration dict
        domain: Domain name (for error messages)
    
    Raises:
        ValueError: If configuration invalid
    """
    # Check required keys
    required_keys = ['domain', 'source_file', 'output_path']
    missing_keys = [key for key in required_keys if key not in config]
    
    if missing_keys:
        raise ValueError(
            f"Invalid config for domain '{domain}': "
            f"missing required keys: {', '.join(missing_keys)}\n"
            f"Required keys: {', '.join(required_keys)}"
        )
    
    # Validate domain name matches
    if config['domain'] != domain:
        raise ValueError(
            f"Domain mismatch: config file is '{domain}.yaml' but "
            f"'domain' field is '{config['domain']}'"
        )
    
    # Validate source file exists
    source_file = Path(config['source_file'])
    if not source_file.exists():
        raise ValueError(
            f"Source file not found: {source_file}\n"
            f"Specified in config for domain: {domain}"
        )
    
    # Validate enrichment configs
    if 'enrichments' in config:
        for idx, enrichment in enumerate(config['enrichments']):
            validate_enrichment_config(enrichment, domain, idx)
    
    # Validate generator configs
    if 'generators' in config:
        for idx, generator in enumerate(config['generators']):
            validate_generator_config(generator, domain, idx)
    
    logger.debug(f"Config validation passed for domain: {domain}")


def validate_enrichment_config(
    enrichment: Dict[str, Any],
    domain: str,
    index: int
) -> None:
    """
    Validate enrichment configuration.
    
    Args:
        enrichment: Enrichment config dict
        domain: Domain name (for error messages)
        index: Enrichment index in config list
    
    Raises:
        ValueError: If enrichment config invalid
    """
    if 'type' not in enrichment:
        raise ValueError(
            f"Enrichment #{index} in domain '{domain}' missing 'type' field"
        )
    
    enrichment_type = enrichment['type']
    
    # Validate linkage enrichers
    if enrichment_type.endswith('_linkage'):
        required = ['field', 'source', 'defaults']
        missing = [k for k in required if k not in enrichment]
        
        if missing:
            raise ValueError(
                f"Enrichment #{index} (type: {enrichment_type}) in domain '{domain}' "
                f"missing required keys: {', '.join(missing)}\n"
                f"Required for linkage enrichers: {', '.join(required)}"
            )
        
        # Validate source file exists
        source_file = Path(enrichment['source'])
        if not source_file.exists():
            raise ValueError(
                f"Enrichment #{index} source file not found: {source_file}\n"
                f"Domain: {domain}, type: {enrichment_type}"
            )
    
    # Validate timestamp enricher
    elif enrichment_type == 'timestamp':
        if 'fields' not in enrichment:
            logger.warning(
                f"Timestamp enrichment #{index} in domain '{domain}' "
                f"missing 'fields' - using defaults"
            )


def validate_generator_config(
    generator: Dict[str, Any],
    domain: str,
    index: int
) -> None:
    """
    Validate generator configuration.
    
    Args:
        generator: Generator config dict
        domain: Domain name (for error messages)
        index: Generator index in config list
    
    Raises:
        ValueError: If generator config invalid
    """
    if 'type' not in generator:
        raise ValueError(
            f"Generator #{index} in domain '{domain}' missing 'type' field"
        )
    
    generator_type = generator['type']
    
    # Validate SEO description generator
    if generator_type == 'seo_description':
        required = ['source_field', 'output_field']
        missing = [k for k in required if k not in generator]
        
        if missing:
            raise ValueError(
                f"Generator #{index} (type: seo_description) in domain '{domain}' "
                f"missing required keys: {', '.join(missing)}"
            )
    
    # Validate breadcrumb generator
    elif generator_type == 'breadcrumb':
        if 'template' not in generator:
            raise ValueError(
                f"Generator #{index} (type: breadcrumb) in domain '{domain}' "
                f"missing required 'template' field"
            )
    
    # Validate excerpt generator
    elif generator_type == 'excerpt':
        required = ['source_field', 'output_field']
        missing = [k for k in required if k not in generator]
        
        if missing:
            raise ValueError(
                f"Generator #{index} (type: excerpt) in domain '{domain}' "
                f"missing required keys: {', '.join(missing)}"
            )
    
    # Validate slug generator
    elif generator_type == 'slug':
        if 'source_field' not in generator:
            raise ValueError(
                f"Generator #{index} (type: slug) in domain '{domain}' "
                f"missing required 'source_field'"
            )


def list_available_domains(config_dir: Optional[Path] = None) -> list[str]:
    """
    List all available domain configurations.
    
    Args:
        config_dir: Optional config directory (default: export/config/)
    
    Returns:
        List of domain names (without .yaml extension)
    
    Example:
        domains = list_available_domains()
        # ['materials', 'contaminants', 'compounds', 'settings']
    """
    if config_dir is None:
        config_dir = CONFIG_DIR
    
    domains = []
    for config_file in config_dir.glob('*.yaml'):
        if config_file.stem not in ['example', 'template']:
            domains.append(config_file.stem)
    
    return sorted(domains)


def get_config_path(domain: str, config_dir: Optional[Path] = None) -> Path:
    """
    Get path to domain configuration file.
    
    Args:
        domain: Domain name
        config_dir: Optional config directory (default: export/config/)
    
    Returns:
        Path to config file
    
    Example:
        path = get_config_path('materials')
        # Path('export/config/materials.yaml')
    """
    if config_dir is None:
        config_dir = CONFIG_DIR
    
    return config_dir / f"{domain}.yaml"


def create_default_config(domain: str) -> Dict[str, Any]:
    """
    Create default configuration template for domain.
    
    Useful for initializing new domain configs.
    
    Args:
        domain: Domain name
    
    Returns:
        Default configuration dict
    
    Example:
        config = create_default_config('industries')
        config['source_file'] = 'data/industries/Industries.yaml'
        # ... customize config ...
    """
    return {
        'domain': domain,
        'source_file': f'data/{domain}/{domain.capitalize()}.yaml',
        'output_path': f'frontmatter/{domain}',
        'items_key': domain,
        'id_field': 'id',
        'slug_field': 'slug',
        'enrichments': [
            {
                'type': 'timestamp',
                'fields': ['datePublished', 'dateModified']
            }
        ],
        'generators': [
            {
                'type': 'seo_description',
                'source_field': f'{domain}_description',
                'output_field': 'seo_description',
                'max_length': 160
            }
        ]
    }
