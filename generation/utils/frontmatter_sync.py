#!/usr/bin/env python3
"""
Frontmatter Partial Field Sync Utility

PURPOSE: Update individual fields in frontmatter files when source YAML changes.
DESIGN: Partial field updates only - preserves all other frontmatter fields.

POLICY: Dual-Write Architecture (Nov 22, 2025)
- Materials.yaml/Settings.yaml: Full write (source of truth)
- Frontmatter: Partial field update only (immediate sync)

Routes fields to correct frontmatter directory:
- Settings fields → frontmatter/settings/{slug}-settings.yaml
- Material fields → frontmatter/materials/{slug}-laser-cleaning.yaml

Usage:
    from generation.utils.frontmatter_sync import sync_field_to_frontmatter
    
    # After saving to Materials.yaml
    sync_field_to_frontmatter('Aluminum', 'caption', new_content)
    
    # After saving to Settings.yaml  
    sync_field_to_frontmatter('Aluminum', 'settings_description', new_content)
"""

import logging
import yaml
import tempfile
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)

# Fields that belong in settings frontmatter (frontmatter/settings/)
SETTINGS_FIELDS = {'settings_description', 'component_summaries'}

# Fields that belong in materials frontmatter (frontmatter/materials/)
MATERIALS_FIELDS = {'caption', 'material_description', 'faq'}


def get_frontmatter_path(material_name: str, field_name: str = None) -> Path:
    """
    Get frontmatter file path for material based on field type.
    
    Args:
        material_name: Name of material (e.g., "Aluminum")
        field_name: Field being updated (determines settings vs materials path)
        
    Returns:
        Path to frontmatter file
    """
    # Convert material name to slug
    slug = material_name.lower().replace(' ', '-').replace('_', '-')
    
    # Route to correct directory based on field type
    if field_name and field_name in SETTINGS_FIELDS:
        frontmatter_dir = Path("frontmatter/settings")
        return frontmatter_dir / f"{slug}-settings.yaml"
    else:
        frontmatter_dir = Path("frontmatter/materials")
        return frontmatter_dir / f"{slug}-laser-cleaning.yaml"


def sync_field_to_frontmatter(material_name: str, field_name: str, field_value: Any):
    """
    Update a single field in frontmatter file (partial update).
    
    Preserves all other fields - only updates the specified field.
    Creates frontmatter file if it doesn't exist (initializes with minimal structure).
    Routes to correct frontmatter directory based on field type.
    
    Args:
        material_name: Name of material
        field_name: Field to update (e.g., 'settings_description', 'material_description', 'caption')
        field_value: New value for field
        
    Policy Compliance:
    - Frontmatter receives immediate field-level updates
    - Never read frontmatter for data persistence
    - Only updated field written, others preserved
    - Settings fields → frontmatter/settings/
    - Material fields → frontmatter/materials/
    """
    # Get correct path based on field type
    frontmatter_path = get_frontmatter_path(material_name, field_name)
    is_settings = field_name in SETTINGS_FIELDS
    
    try:
        # Read existing frontmatter (or create minimal structure)
        if frontmatter_path.exists():
            with open(frontmatter_path, 'r', encoding='utf-8') as f:
                frontmatter_data = yaml.safe_load(f) or {}
        else:
            # Initialize minimal frontmatter structure based on type
            if is_settings:
                frontmatter_data = {
                    'name': material_name,
                    'slug': material_name.lower().replace(' ', '-').replace('_', '-'),
                    'title': f"{material_name} Laser Cleaning Settings"
                }
            else:
                frontmatter_data = {
                    'title': f"{material_name} Laser Cleaning",
                    'name': material_name
                }
            logger.info(f"   📝 Creating new frontmatter file: {frontmatter_path}")
        
        # Update the field at root level
        frontmatter_data[field_name] = field_value
        dest_type = "settings" if is_settings else "materials"
        logger.info(f"   ✅ Updated {dest_type} frontmatter {field_name} for {material_name}")
        
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
