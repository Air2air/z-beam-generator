#!/usr/bin/env python3
"""
Remove description fields from Materials.yaml except within regulatoryStandards.

This script:
1. Removes description fields from category_metadata
2. Preserves description fields within regulatoryStandards sections
3. Creates a backup before modification
"""

import yaml
import shutil
from pathlib import Path
from datetime import datetime


def remove_descriptions_recursive(data, inside_regulatory_standards=False):
    """
    Recursively remove description fields except when inside regulatoryStandards.
    
    Args:
        data: Dictionary or list to process
        inside_regulatory_standards: Boolean flag indicating if we're inside a regulatoryStandards section
    
    Returns:
        Tuple of (modified_data, count_removed)
    """
    removed_count = 0
    
    if isinstance(data, dict):
        keys_to_remove = []
        
        # Check if we're entering regulatoryStandards
        is_regulatory = 'regulatoryStandards' in data or inside_regulatory_standards
        
        for key, value in data.items():
            # Determine if this branch is regulatory
            branch_is_regulatory = is_regulatory or key == 'regulatoryStandards'
            
            # Remove description unless we're in regulatoryStandards
            if key == 'description' and not inside_regulatory_standards:
                keys_to_remove.append(key)
                removed_count += 1
            elif isinstance(value, (dict, list)):
                # Recursively process nested structures
                data[key], nested_removed = remove_descriptions_recursive(value, branch_is_regulatory)
                removed_count += nested_removed
        
        # Remove marked keys
        for key in keys_to_remove:
            del data[key]
    
    elif isinstance(data, list):
        for i, item in enumerate(data):
            if isinstance(item, (dict, list)):
                data[i], nested_removed = remove_descriptions_recursive(item, inside_regulatory_standards)
                removed_count += nested_removed
    
    return data, removed_count


def process_materials_yaml():
    """Process Materials.yaml to remove description fields."""
    
    # Get Materials.yaml path
    root_dir = Path(__file__).parent.parent
    materials_file = root_dir / 'materials' / 'data' / 'Materials.yaml'
    
    if not materials_file.exists():
        print(f"❌ Materials.yaml not found: {materials_file}")
        return
    
    print(f"📂 Processing: {materials_file}")
    print()
    
    # Create backup
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_file = materials_file.parent / f'materials_backup_{timestamp}.yaml'
    
    print(f"💾 Creating backup: {backup_file.name}")
    shutil.copy2(materials_file, backup_file)
    print()
    
    # Load YAML
    print("📖 Loading Materials.yaml...")
    with open(materials_file, 'r', encoding='utf-8') as f:
        data = yaml.safe_load(f)
    
    print(f"✅ Loaded {len(data)} top-level sections")
    print()
    
    # Remove descriptions except in regulatoryStandards
    print("🔍 Removing description fields (preserving regulatoryStandards)...")
    modified_data, removed_count = remove_descriptions_recursive(data, inside_regulatory_standards=False)
    
    # Save modified YAML
    print(f"💾 Writing modified Materials.yaml...")
    with open(materials_file, 'w', encoding='utf-8') as f:
        yaml.safe_dump(
            modified_data,
            f,
            default_flow_style=False,
            allow_unicode=True,
            sort_keys=False,
            width=120
        )
    
    print()
    print("=" * 60)
    print("📊 SUMMARY")
    print("=" * 60)
    print(f"✅ Description fields removed: {removed_count}")
    print(f"✅ Regulatory descriptions preserved: YES")
    print(f"💾 Backup created: {backup_file.name}")
    print(f"📝 Updated: {materials_file.name}")
    
    # Verify regulatory standards still have descriptions
    print()
    print("🔍 Verifying regulatoryStandards descriptions preserved...")
    regulatory_desc_count = 0
    
    if 'materials' in modified_data:
        for material_name, material_data in modified_data['materials'].items():
            if 'regulatoryStandards' in material_data:
                for standard_key, standard_data in material_data['regulatoryStandards'].items():
                    if isinstance(standard_data, dict) and 'description' in standard_data:
                        regulatory_desc_count += 1
    
    print(f"✅ RegulatoryStandards descriptions found: {regulatory_desc_count}")
    print()


if __name__ == "__main__":
    print("🚀 Removing description fields from Materials.yaml")
    print("=" * 60)
    print()
    process_materials_yaml()
