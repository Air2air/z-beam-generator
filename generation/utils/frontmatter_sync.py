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
import tempfile
from pathlib import Path
from typing import Any

from shared.utils.yaml_utils import load_yaml, save_yaml

logger = logging.getLogger(__name__)


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
    # Use DomainAdapter to get frontmatter config
    from generation.core.adapters.domain_adapter import DomainAdapter
    
    try:
        adapter = DomainAdapter(domain)
        config = adapter.config
        
        # Get frontmatter directory from config (support both old flat and new nested structure)
        if 'frontmatter' in config:
            # New nested structure
            frontmatter_dir = config['frontmatter'].get('directory', f'frontmatter/{domain}')
            pattern = config['frontmatter'].get('filename_pattern', '{slug}.yaml')
        else:
            # Old flat structure (backward compatibility)
            frontmatter_dir = config.get('frontmatter_directory') or \
                             config.get('export', {}).get('frontmatter_directory', f'frontmatter/{domain}')
            pattern = config.get('frontmatter_filename_pattern') or \
                     config.get('export', {}).get('filename_pattern', '{slug}.yaml')
        
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
        
    except Exception as e:
        # Fallback to legacy behavior if config not found
        logger.warning(f"Could not load domain config for {domain}, using fallback: {e}")
        slug = item_name.lower().replace(' ', '-').replace('_', '-').replace('(', '').replace(')', '')
        while '--' in slug:
            slug = slug.replace('--', '-')
        slug = slug.strip('-')
        return Path(f"frontmatter/{domain}") / f"{slug}.yaml"


def sync_field_to_frontmatter(item_name: str, field_name: str, field_value: Any, domain: str):
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
            frontmatter_data = load_yaml(frontmatter_path) or {}
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
        # DEPRECATED: 'description' field at root level is deprecated in favor of 'page_description'
        # All new content goes to 'page_description' field. Legacy 'description' preserved if it exists.
        if field_name == 'description':
            # ALL description content goes to page_description (new standard)
            frontmatter_data['page_description'] = field_value
            # Legacy description preserved if it exists (don't overwrite)
            if 'description' in frontmatter_data:
                logger.info(f"   🔄 Using page_description (legacy description preserved)")
            else:
                logger.info(f"   ✨ Using page_description (new standard field)")
        else:
            # Normal field update
            frontmatter_data[field_name] = field_value
        
        print(f"   ✅ Updated {domain} frontmatter {field_name} for {item_name}")
        logger.info(f"   ✅ Updated {domain} frontmatter {field_name} for {item_name}")
        
        # Atomic write using save_yaml (path first, data second)
        frontmatter_path.parent.mkdir(parents=True, exist_ok=True)
        save_yaml(frontmatter_path, frontmatter_data)
        
        print(f"   💾 Frontmatter synced: {frontmatter_path}")
        logger.info(f"   💾 Frontmatter synced: {frontmatter_path}")
        
    except Exception as e:
        logger.warning(f"   ⚠️  Failed to sync frontmatter for {item_name}: {e}")
        logger.warning(f"   Data YAML is still updated correctly (source of truth)")
        # Don't raise - frontmatter sync failure shouldn't break generation
