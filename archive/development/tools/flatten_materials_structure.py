#!/usr/bin/env python3
"""
Flatten materials.yaml structure for easier AI navigation.

BEFORE (Nested - requires two-step lookup):
  material_index:
    Aluminum: metal
  materials:
    metal:
      items:
        - name: Aluminum
          properties: {...}

AFTER (Flat - direct lookup):
  materials:
    Aluminum:
      category: metal
      properties: {...}
  
  # Metadata sections preserved at top level
"""

import yaml
import sys
from pathlib import Path
from datetime import datetime

def flatten_materials_yaml(input_path: str, output_path: str = None, backup: bool = True):
    """
    Flatten materials.yaml from nested category structure to flat material lookup.
    
    Args:
        input_path: Path to original materials.yaml
        output_path: Path for new file (default: overwrites original)
        backup: Whether to create backup before overwriting (default: True)
    """
    # Load current structure
    print("📖 Reading materials.yaml...")
    with open(input_path, 'r') as f:
        data = yaml.safe_load(f)
    
    # Create backup if overwriting
    if backup and (output_path is None or output_path == input_path):
        backup_path = f"{input_path}.backup.{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        print(f"💾 Creating backup: {backup_path}")
        with open(backup_path, 'w') as f:
            yaml.dump(data, f, default_flow_style=False, allow_unicode=True, sort_keys=False)
    
    # Extract materials from nested structure
    print("🔄 Flattening structure...")
    flat_materials = {}
    material_count = 0
    
    for category, category_data in data['materials'].items():
        if 'items' not in category_data:
            print(f"⚠️  Warning: Category '{category}' has no 'items' key, skipping")
            continue
        
        for material_data in category_data['items']:
            material_name = material_data.get('name')
            if not material_name:
                print(f"⚠️  Warning: Material in '{category}' has no 'name', skipping")
                continue
            
            # Ensure category is embedded in material data
            if 'category' not in material_data:
                material_data['category'] = category
            
            flat_materials[material_name] = material_data
            material_count += 1
    
    print(f"✅ Flattened {material_count} materials from {len(data['materials'])} categories")
    
    # Build new structure (preserve order for readability)
    new_structure = {
        'metadata': data.get('metadata', {}),
        'category_metadata': data.get('category_metadata', {}),
        'machineSettingsRanges': data.get('machineSettingsRanges', {}),
        'property_groups': data.get('property_groups', {}),
        'materials': flat_materials,
        # Keep material_index for backward compatibility (now just for quick category lookup)
        'material_index': data.get('material_index', {}),
    }
    
    # Write flattened structure
    output_file = output_path or input_path
    print(f"💾 Writing flattened structure to: {output_file}")
    
    with open(output_file, 'w') as f:
        yaml.dump(new_structure, f, default_flow_style=False, allow_unicode=True, sort_keys=False)
    
    # Validation
    print("\n🔍 Validating flattened structure...")
    validation_errors = []
    
    # Check all materials exist
    for mat_name in data['material_index'].keys():
        if mat_name not in flat_materials:
            validation_errors.append(f"Material '{mat_name}' in index but not in flattened materials")
    
    # Check all materials have category
    for mat_name, mat_data in flat_materials.items():
        if 'category' not in mat_data:
            validation_errors.append(f"Material '{mat_name}' missing category field")
    
    if validation_errors:
        print("❌ Validation errors found:")
        for error in validation_errors:
            print(f"  - {error}")
        return False
    
    print(f"✅ Validation passed: All {material_count} materials properly flattened")
    
    # Show usage examples
    print("\n📚 New usage pattern:")
    print("   OLD: materials[material_index['Aluminum']]['items'][?]['name'=='Aluminum']")
    print("   NEW: materials['Aluminum']")
    print("\n   To get category: materials['Aluminum']['category']")
    
    return True

def show_comparison():
    """Show before/after structure comparison."""
    print("\n" + "="*70)
    print("STRUCTURE COMPARISON")
    print("="*70)
    print("\nBEFORE (Nested - Two-step lookup):")
    print("""
    material_index:
      Aluminum: metal           # Step 1: Look up category
      Copper: metal
      
    materials:
      metal:
        items:                  # Step 2: Find in category's items array
          - name: Aluminum
            properties: {...}
          - name: Copper
            properties: {...}
    """)
    
    print("\nAFTER (Flat - Direct lookup):")
    print("""
    materials:
      Aluminum:                 # Direct access
        category: metal         # Category embedded
        properties: {...}
      Copper:
        category: metal
        properties: {...}
    
    material_index:             # Kept for backward compatibility
      Aluminum: metal
      Copper: metal
    """)
    print("="*70 + "\n")

if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Flatten materials.yaml structure for easier AI navigation',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument(
        'input',
        nargs='?',
        default='data/materials.yaml',
        help='Input materials.yaml file (default: data/materials.yaml)'
    )
    parser.add_argument(
        '-o', '--output',
        help='Output file path (default: overwrites input with backup)'
    )
    parser.add_argument(
        '--no-backup',
        action='store_true',
        help='Skip creating backup file'
    )
    parser.add_argument(
        '--show-comparison',
        action='store_true',
        help='Show before/after structure comparison'
    )
    
    args = parser.parse_args()
    
    if args.show_comparison:
        show_comparison()
        sys.exit(0)
    
    try:
        success = flatten_materials_yaml(
            args.input,
            args.output,
            backup=not args.no_backup
        )
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"❌ Error: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        sys.exit(1)
