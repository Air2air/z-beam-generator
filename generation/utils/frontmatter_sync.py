#!/usr/bin/env python3
"""
Frontmatter Partial Field Sync Utility

PURPOSE: Update individual fields in frontmatter files when source YAML changes.
DESIGN: Partial field updates only - preserves all other frontmatter fields.

POLICY: Dual-Write Architecture (Nov 22, 2025)
- Data YAMLs (Materials.yaml/Settings.yaml): Full write (source of truth)
- Frontmatter: Partial field update only (immediate sync)

Routes fields using domain config (domain-agnostic):
- Reads frontmatter_directory from domains/*/config.yaml
- Reads frontmatter_filename_pattern from domains/*/config.yaml
- Uses component_fields mapping to determine which fields sync to frontmatter

Usage:
    from generation.utils.frontmatter_sync import sync_field_to_frontmatter
    
    # After saving to any domain YAML
    sync_field_to_frontmatter('Aluminum', 'micro', new_content, domain='materials')
    sync_field_to_frontmatter('Aluminum', 'description', new_content, domain='settings')
"""

import logging
from pathlib import Path
from typing import Any

from shared.utils.yaml_utils import load_yaml, save_yaml

logger = logging.getLogger(__name__)


def _load_domain_config(domain: str) -> dict:
    """Load and validate domain config for frontmatter routing."""
    domain_config_path = Path("domains") / domain / "config.yaml"
    if not domain_config_path.exists():
        raise FileNotFoundError(f"Domain config not found: {domain_config_path}")

    config = load_yaml(domain_config_path)
    if not isinstance(config, dict):
        raise ValueError(f"Invalid domain config format (expected dict): {domain_config_path}")
    return config


def get_frontmatter_path(item_name: str, field_name: str, domain: str) -> Path:
    """
    Get frontmatter file path using domain config (domain-agnostic).
    
    Checks for existing files with legacy naming (parentheses removed) before
    creating new files. This prevents duplicate files when material names contain
    parentheses (e.g., "Acrylic (PMMA)" has legacy file "acrylic-pmma-..." not "acrylic-(pmma)-...").
    
    Args:
        item_name: Name of item (e.g., "Aluminum", "Acrylic (PMMA)")
        field_name: Field being updated (for logging)
        domain: Domain name (e.g., 'materials', 'settings')
        
    Returns:
        Path to frontmatter file (existing legacy file or new normalized path)
    """
    config = _load_domain_config(domain)

    # Get frontmatter directory from config (support both old flat and new nested structure)
    if 'frontmatter' in config:
        # New nested structure
        frontmatter_cfg = config['frontmatter']
        if not isinstance(frontmatter_cfg, dict):
            raise ValueError(f"Invalid frontmatter config for domain '{domain}': expected dict")
        frontmatter_dir = frontmatter_cfg.get('directory')
        pattern = frontmatter_cfg.get('filename_pattern')
    else:
        # Old flat structure (legacy explicit config)
        frontmatter_dir = config.get('frontmatter_directory')
        pattern = config.get('frontmatter_filename_pattern')

    # Require explicit domain config values (fail-fast)
    if not frontmatter_dir or not pattern:
        raise ValueError(
            f"Domain '{domain}' missing required frontmatter configuration: "
            f"frontmatter directory and filename pattern must be defined"
        )
        
    # NEW: Legacy slug (parentheses REMOVED - old behavior)
    # Example: "Acrylic (PMMA)" → "acrylic-pmma"
    slug_legacy = item_name.lower().replace(' ', '-').replace('_', '-').replace('(', '').replace(')', '')
    # Remove consecutive hyphens that result from removing parentheses
    while '--' in slug_legacy:
        slug_legacy = slug_legacy.replace('--', '-')
    slug_legacy = slug_legacy.strip('-')

    filename_legacy = pattern.format(slug=slug_legacy)
    path_legacy = Path(frontmatter_dir) / filename_legacy

    # If legacy file exists, use it (preserve existing complete files)
    if path_legacy.exists():
        logger.info(f"   📂 Using existing file: {path_legacy.name}")
        return path_legacy

    # Otherwise create new file with same normalization
    return path_legacy


def sync_field_to_frontmatter(item_name: str, field_name: str, field_value: Any, domain: str) -> None:
    """
    Update a single field in frontmatter file (partial update).
    
    Preserves all other fields - only updates the specified field.
    Creates frontmatter file if it doesn't exist (initializes with minimal structure).
    Uses domain config to determine frontmatter path (domain-agnostic).
    
    Args:
        item_name: Name of item
        field_name: Field to update (e.g., 'description', 'micro')
        field_value: New value for field
        domain: Domain name (e.g., 'materials', 'settings')
        
    Policy Compliance:
    - Frontmatter receives immediate field-level updates
    - Never read frontmatter for data persistence
    - Only updated field written, others preserved
    - Paths determined by domain config (domain-agnostic)
    - Author field is NEVER updated (immutability policy)
    """
    # Get correct path from domain config
    frontmatter_path = get_frontmatter_path(item_name, field_name, domain)
    
    try:
        # Read existing frontmatter (or create minimal structure)
        if frontmatter_path.exists():
            frontmatter_data = load_yaml(frontmatter_path)
            if frontmatter_data is None:
                raise ValueError(f"Corrupted YAML file: {frontmatter_path}")
        else:
            # Initialize minimal frontmatter structure
            # Note: 'title' field deprecated (Dec 29, 2025) - use 'page_title' instead
            frontmatter_data = {
                'name': item_name,
                'slug': item_name.lower().replace(' ', '-').replace('_', '-'),
                'page_title': f"{item_name}"
            }
            logger.info(f"   📝 Creating new frontmatter file: {frontmatter_path}")
        
        # Update ONLY the specified field (NEVER update author - immutability policy)
        # Normalize description aliases to canonical frontmatter field name
        persisted_field = (
            'page_description'
            if field_name in ('pageDescription', 'description', 'page_description')
            else field_name
        )

        frontmatter_data[persisted_field] = field_value
        if persisted_field == 'page_description':
            logger.info(f"   ✨ Saved description component to page_description field")
        
        print(f"   ✅ Updated {domain} frontmatter {field_name} for {item_name}")
        logger.info(f"   ✅ Updated {domain} frontmatter {field_name} for {item_name}")
        
        # Atomic write using save_yaml (path first, data second)
        frontmatter_path.parent.mkdir(parents=True, exist_ok=True)
        save_yaml(frontmatter_path, frontmatter_data)

        # Verify persistence (fail-fast)
        persisted = load_yaml(frontmatter_path)
        if persisted is None or persisted.get(persisted_field) != frontmatter_data.get(persisted_field):
            raise RuntimeError(
                f"Frontmatter persistence verification failed for {frontmatter_path} ({persisted_field})"
            )
        
        print(f"   💾 Frontmatter synced: {frontmatter_path}")
        logger.info(f"   💾 Frontmatter synced: {frontmatter_path}")
        
    except Exception as e:
        raise RuntimeError(f"Failed to sync frontmatter for {item_name}.{field_name}: {e}") from e
