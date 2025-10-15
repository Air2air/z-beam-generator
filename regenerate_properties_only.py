#!/usr/bin/env python3
"""
Regenerate ONLY materialProperties section with categorized structure.
Preserves all other frontmatter sections (caption, tags, machineSettings, etc.)
"""
import sys
sys.path.insert(0, '.')

from api.client_factory import create_api_client
from components.frontmatter.core.streamlined_generator import StreamlinedFrontmatterGenerator
import yaml
import os
from pathlib import Path

def main():
    print('🔄 Regenerate Material Properties ONLY - CATEGORIZED STRUCTURE')
    print('=' * 80)
    print('📝 Preserving: caption, tags, machineSettings, images, author, etc.')
    print('🔧 Updating: materialProperties → categorized structure')
    print('=' * 80)
    
    # Get list of materials
    frontmatter_dir = Path('content/components/frontmatter')
    materials = []
    
    for filepath in frontmatter_dir.glob('*.yaml'):
        try:
            with open(filepath, 'r') as f:
                data = yaml.safe_load(f)
                if 'name' in data:
                    materials.append((data['name'], filepath))
        except Exception as e:
            print(f'⚠️  Could not read {filepath.name}: {e}')
    
    materials.sort(key=lambda x: x[0])
    print(f'📋 Found {len(materials)} materials to update\n')
    
    # Initialize generator
    print('🔧 Initializing generator with API client...')
    api_client = create_api_client('deepseek')
    generator = StreamlinedFrontmatterGenerator(api_client=api_client)
    print('✅ Generator ready\n')
    
    # Update all
    success_count = 0
    categorized_count = 0
    failed = []
    
    for i, (material_name, filepath) in enumerate(materials, 1):
        print(f'[{i}/{len(materials)}] {material_name}', end='... ')
        
        try:
            # Load existing frontmatter
            with open(filepath, 'r') as f:
                existing = yaml.safe_load(f)
            
            # Generate ONLY material properties
            from data.materials import get_material_by_name_cached
            material_data = get_material_by_name_cached(material_name)
            
            if not material_data:
                print('❌ Material data not found')
                failed.append((material_name, 'Material data not found in Materials.yaml'))
                continue
            
            # Get unified properties and generate categorized structure
            unified_properties = generator._get_unified_material_properties(material_name, material_data)
            material_data_with_unified = material_data.copy()
            for prop_type, props in unified_properties.items():
                material_data_with_unified[prop_type] = props
            
            # Generate categorized properties
            categorized_properties = generator._generate_properties_with_ranges(
                material_data_with_unified, 
                material_name
            )
            
            # Check if categorized
            is_categorized = False
            if isinstance(categorized_properties, dict):
                first_key = next(iter(categorized_properties.keys()), None)
                if first_key and isinstance(categorized_properties[first_key], dict):
                    if 'label' in categorized_properties[first_key] and 'properties' in categorized_properties[first_key]:
                        is_categorized = True
                        categorized_count += 1
            
            # Replace ONLY materialProperties in existing frontmatter
            existing['materialProperties'] = categorized_properties
            
            # Save back to file
            with open(filepath, 'w') as f:
                yaml.dump(existing, f, default_flow_style=False, allow_unicode=True, sort_keys=False, indent=2)
            
            if is_categorized:
                print('✅ CATEGORIZED')
            else:
                print('⚠️  FLAT')
            
            success_count += 1
            
        except Exception as e:
            print(f'❌ {str(e)[:50]}')
            failed.append((material_name, str(e)))
    
    # Summary
    print('\n' + '=' * 80)
    print('📊 PROPERTY REGENERATION COMPLETE')
    print('=' * 80)
    print(f'✅ Successful: {success_count}/{len(materials)}')
    print(f'🏷️  Categorized: {categorized_count}/{len(materials)}')
    print(f'❌ Failed: {len(failed)}/{len(materials)}')
    
    if failed:
        print('\n❌ Failed Materials:')
        for material, error in failed[:10]:
            print(f'   - {material}: {error[:80]}')
        if len(failed) > 10:
            print(f'   ... and {len(failed) - 10} more')
    
    print('\n✨ Material properties updated with categorized structure!')
    print('📝 All other sections (caption, tags, etc.) preserved unchanged')

if __name__ == '__main__':
    main()
