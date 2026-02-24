#!/usr/bin/env python3
"""
Remove stored intensity fields from source data.

Purpose: Reverse migration to eliminate data redundancy now that intensity
         is dynamically derived during export via IntensityEnricher.

Architecture: Source data should only contain legacy fields (severity, frequency,
              effectiveness, hazard_level). Intensity is calculated on-demand during
              export, ensuring zero redundancy and always-consistent values.

Usage:
    python3 scripts/tools/remove_intensity_field.py
"""

import os
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

import yaml
from typing import Dict, Any


def remove_intensity_from_relationships(data: Dict[str, Any], domain_name: str) -> tuple[int, int]:
    """
    Remove intensity field from all relationship items.
    
    Args:
        data: YAML data structure
        domain_name: Name of domain (for reporting)
        
    Returns:
        Tuple of (items_with_intensity, total_relationship_items)
    """
    removed_count = 0
    total_items = 0
    
    # Navigate to items based on domain structure
    if domain_name == 'compounds':
        items = data.get('compounds', {})
    elif domain_name == 'settings':
        items = data.get('settings', {})
    else:
        print(f"⚠️  Unknown domain: {domain_name}")
        return removed_count, total_items
    
    # Process each item
    for item_id, item_data in items.items():
        if not isinstance(item_data, dict):
            continue
            
        relationships = item_data.get('relationships', {})
        if not isinstance(relationships, dict):
            continue
            
        # Process each relationship type
        for rel_type, rel_items in relationships.items():
            if not isinstance(rel_items, list):
                continue
                
            # Process each relationship item
            for rel_item in rel_items:
                if not isinstance(rel_item, dict):
                    continue
                    
                total_items += 1
                
                # Remove intensity field if present
                if 'intensity' in rel_item:
                    del rel_item['intensity']
                    removed_count += 1
    
    return removed_count, total_items


def main():
    """Remove stored intensity fields from Compounds.yaml and Settings.yaml."""
    
    print("=" * 80)
    print("INTENSITY FIELD REMOVAL (REVERSE MIGRATION)")
    print("=" * 80)
    print()
    print("Purpose: Remove stored intensity fields now that IntensityEnricher")
    print("         dynamically derives intensity during export.")
    print()
    
    # File paths
    compounds_path = project_root / 'data' / 'compounds' / 'Compounds.yaml'
    settings_path = project_root / 'data' / 'settings' / 'Settings.yaml'
    
    total_removed = 0
    total_items = 0
    
    # Process Compounds.yaml
    print("📄 Processing Compounds.yaml...")
    with open(compounds_path, 'r') as f:
        compounds_data = yaml.safe_load(f)
    
    removed, items = remove_intensity_from_relationships(compounds_data, 'compounds')
    print(f"   ✅ Removed intensity from {removed}/{items} relationship items")
    total_removed += removed
    total_items += items
    
    # Write updated Compounds.yaml
    with open(compounds_path, 'w') as f:
        yaml.dump(compounds_data, f, default_flow_style=False, allow_unicode=True, sort_keys=False)
    print(f"   💾 Saved updated Compounds.yaml")
    print()
    
    # Process Settings.yaml
    print("📄 Processing Settings.yaml...")
    with open(settings_path, 'r') as f:
        settings_data = yaml.safe_load(f)
    
    removed, items = remove_intensity_from_relationships(settings_data, 'settings')
    print(f"   ✅ Removed intensity from {removed}/{items} relationship items")
    total_removed += removed
    total_items += items
    
    # Write updated Settings.yaml
    with open(settings_path, 'w') as f:
        yaml.dump(settings_data, f, default_flow_style=False, allow_unicode=True, sort_keys=False)
    print(f"   💾 Saved updated Settings.yaml")
    print()
    
    # Summary
    print("=" * 80)
    print("SUMMARY")
    print("=" * 80)
    print(f"✅ Removed {total_removed} stored intensity fields")
    print(f"📊 Processed {total_items} total relationship items")
    print(f"🎯 Data redundancy eliminated: {total_removed} fewer stored fields")
    print()
    print("Next steps:")
    print("  1. Test export: python3 run.py --export-all --dry-run")
    print("  2. Verify frontmatter contains intensity field (dynamically generated)")
    print("  3. Commit changes: git add . && git commit -m 'Remove stored intensity fields'")
    print()


if __name__ == '__main__':
    main()
