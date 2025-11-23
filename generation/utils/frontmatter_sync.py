#!/usr/bin/env python3
"""
Frontmatter Partial Field Sync Utility

PURPOSE: Update individual fields in frontmatter files when Materials.yaml changes.
DESIGN: Partial field updates only - preserves all other frontmatter fields.

POLICY: Dual-Write Architecture (Nov 22, 2025)
- Materials.yaml: Full write (source of truth)
- Frontmatter: Partial field update only (immediate sync)

Usage:
    from generation.utils.frontmatter_sync import sync_field_to_frontmatter
    
    # After saving to Materials.yaml
    sync_field_to_frontmatter('Aluminum', 'description', new_content)
"""

import logging
import yaml
import tempfile
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)


def get_frontmatter_path(material_name: str) -> Path:
    """
    Get frontmatter file path for material.
    
    Args:
        material_name: Name of material (e.g., "Aluminum")
        
    Returns:
        Path to frontmatter file
    """
    # Convert material name to slug
    slug = material_name.lower().replace(' ', '-').replace('_', '-')
    frontmatter_dir = Path("frontmatter/materials")
    
    # Standard naming: {slug}-laser-cleaning.yaml
    return frontmatter_dir / f"{slug}-laser-cleaning.yaml"


def sync_field_to_frontmatter(material_name: str, field_name: str, field_value: Any):
    """
    Update a single field in frontmatter file (partial update).
    
    Preserves all other fields - only updates the specified field.
    Creates frontmatter file if it doesn't exist (initializes with minimal structure).
    
    Args:
        material_name: Name of material
        field_name: Field to update (e.g., 'settings_description', 'material_description', 'caption')
        field_value: New value for field
        
    Policy Compliance:
    - Frontmatter receives immediate field-level updates
    - Never read frontmatter for data persistence
    - Only updated field written, others preserved
    """
    frontmatter_path = get_frontmatter_path(material_name)
    
    try:
        # Read existing frontmatter (or create minimal structure)
        if frontmatter_path.exists():
            with open(frontmatter_path, 'r', encoding='utf-8') as f:
                frontmatter_data = yaml.safe_load(f) or {}
        else:
            # Initialize minimal frontmatter structure
            frontmatter_data = {
                'title': f"{material_name} Laser Cleaning",
                'name': material_name
            }
            logger.info(f"   📝 Creating new frontmatter file: {frontmatter_path}")
        
        # Handle component fields - all stored at root level in frontmatter
        if field_name in ['caption', 'material_description', 'settings_description', 'faq']:
            # All text component fields at root level
            frontmatter_data[field_name] = field_value
            logger.info(f"   ✅ Updated frontmatter {field_name} for {material_name}")
        else:
            # Generic field update at root
            frontmatter_data[field_name] = field_value
            logger.info(f"   ✅ Updated frontmatter {field_name} for {material_name}")
        
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
        
        logger.info(f"   💾 Frontmatter synced: {frontmatter_path}")
        
    except Exception as e:
        logger.warning(f"   ⚠️  Failed to sync frontmatter for {material_name}: {e}")
        logger.warning("   Materials.yaml is still updated correctly (source of truth)")
        # Don't raise - frontmatter sync failure shouldn't break generation
