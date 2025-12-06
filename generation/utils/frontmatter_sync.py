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
    sync_field_to_frontmatter('Aluminum', 'caption', new_content, domain='materials')
    sync_field_to_frontmatter('Aluminum', 'settings_description', new_content, domain='settings')
"""

import logging
import yaml
import tempfile
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)


def get_frontmatter_path(item_name: str, field_name: str, domain: str) -> Path:
    """
    Get frontmatter file path using domain config (domain-agnostic).
    
    Args:
        item_name: Name of item (e.g., "Aluminum")
        field_name: Field being updated (for logging)
        domain: Domain name (e.g., 'materials', 'settings')
        
    Returns:
        Path to frontmatter file
    """
    # Use DomainAdapter to get frontmatter config
    from generation.core.adapters.domain_adapter import DomainAdapter
    
    try:
        adapter = DomainAdapter(domain)
        config = adapter.config
        
        # Get frontmatter directory from config
        frontmatter_dir = config.get('frontmatter_directory', f'frontmatter/{domain}')
        
        # Get filename pattern from config (e.g., "{slug}-laser-cleaning.yaml")
        pattern = config.get('frontmatter_filename_pattern', '{slug}.yaml')
        
        # Convert item name to slug
        slug = item_name.lower().replace(' ', '-').replace('_', '-')
        filename = pattern.format(slug=slug)
        
        return Path(frontmatter_dir) / filename
        
    except Exception as e:
        # Fallback to legacy behavior if config not found
        logger.warning(f"Could not load domain config for {domain}, using fallback: {e}")
        slug = item_name.lower().replace(' ', '-').replace('_', '-')
        return Path(f"frontmatter/{domain}") / f"{slug}.yaml"


def sync_field_to_frontmatter(item_name: str, field_name: str, field_value: Any, domain: str):
    """
    Update a single field in frontmatter file (partial update).
    
    Preserves all other fields - only updates the specified field.
    Creates frontmatter file if it doesn't exist (initializes with minimal structure).
    Uses domain config to determine frontmatter path (domain-agnostic).
    
    Args:
        item_name: Name of item
        field_name: Field to update (e.g., 'settings_description', 'material_description', 'caption')
        field_value: New value for field
        domain: Domain name (e.g., 'materials', 'settings')
        
    Policy Compliance:
    - Frontmatter receives immediate field-level updates
    - Never read frontmatter for data persistence
    - Only updated field written, others preserved
    - Paths determined by domain config (domain-agnostic)
    """
    # Get correct path from domain config
    frontmatter_path = get_frontmatter_path(item_name, field_name, domain)
    
    try:
        # Read existing frontmatter (or create minimal structure)
        if frontmatter_path.exists():
            with open(frontmatter_path, 'r', encoding='utf-8') as f:
                frontmatter_data = yaml.safe_load(f) or {}
        else:
            # Initialize minimal frontmatter structure
            frontmatter_data = {
                'name': item_name,
                'slug': item_name.lower().replace(' ', '-').replace('_', '-'),
                'title': f"{item_name}"
            }
            logger.info(f"   📝 Creating new frontmatter file: {frontmatter_path}")
        
        # Update the field at root level
        frontmatter_data[field_name] = field_value
        print(f"   ✅ Updated {domain} frontmatter {field_name} for {item_name}")
        logger.info(f"   ✅ Updated {domain} frontmatter {field_name} for {item_name}")
        
        # Atomic write: temp file → rename
        frontmatter_path.parent.mkdir(parents=True, exist_ok=True)
        
        with tempfile.NamedTemporaryFile(
            mode='w',
            encoding='utf-8',
            dir=frontmatter_path.parent,
            delete=False,
            suffix='.yaml'
        ) as temp_f:
            yaml.safe_dump(frontmatter_data, temp_f, default_flow_style=False, allow_unicode=True, sort_keys=False)
            temp_path = temp_f.name
        
        # Atomic rename
        Path(temp_path).replace(frontmatter_path)
        
        print(f"   💾 Frontmatter synced: {frontmatter_path}")
        logger.info(f"   💾 Frontmatter synced: {frontmatter_path}")
        
    except Exception as e:
        logger.warning(f"   ⚠️  Failed to sync frontmatter for {item_name}: {e}")
        logger.warning(f"   Data YAML is still updated correctly (source of truth)")
        # Don't raise - frontmatter sync failure shouldn't break generation
