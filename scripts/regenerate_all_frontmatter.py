#!/usr/bin/env python3
"""
Batch regenerate all frontmatter files with categorized structure
"""
import sys
sys.path.insert(0, '.')

from api.client_factory import create_api_client
from components.frontmatter.core.streamlined_generator import StreamlinedFrontmatterGenerator
import yaml
import os
from pathlib import Path

def main():
    print('�� Frontmatter Batch Regeneration - CATEGORIZED STRUCTURE')
    print('=' * 80)
    
    # Get list of materials
    frontmatter_dir = Path('content/components/frontmatter')
    materials = []
    
    for filepath in frontmatter_dir.glob('*.yaml'):
        try:
            with open(filepath, 'r') as f:
                data = yaml.safe_load(f)
                if 'name' in data:
                    materials.append(data['name'])
        except Exception as e:
            print(f'⚠️  Could not read {filepath.name}: {e}')
    
    materials.sort()
    print(f'📋 Found {len(materials)} materials to regenerate\n')
    
    # Initialize generator
    print('🔧 Initializing generator with API client...')
    api_client = create_api_client('deepseek')
    generator = StreamlinedFrontmatterGenerator(api_client=api_client)
    print('✅ Generator ready\n')
    
    # Regenerate all
    success_count = 0
    categorized_count = 0
    failed = []
    
    for i, material in enumerate(materials, 1):
        print(f'[{i}/{len(materials)}] {material}', end='... ')
        
        try:
            result = generator.generate(material)
            
            if result.success:
                # Check structure
                content = yaml.safe_load(result.content)
                is_categorized = False
                
                if 'materialProperties' in content:
                    props = content['materialProperties']
                    if isinstance(props, dict):
                        first_key = next(iter(props.keys()), None)
                        if first_key and isinstance(props[first_key], dict):
                            if 'label' in props[first_key] and 'properties' in props[first_key]:
                                is_categorized = True
                                categorized_count += 1
                                print('✅ CATEGORIZED')
                            else:
                                print('⚠️  FLAT')
                        else:
                            print('⚠️  FLAT')
                else:
                    print('⚠️  No materialProperties')
                    
                success_count += 1
            else:
                print(f'❌ {result.error_message[:50]}')
                failed.append((material, result.error_message))
        except Exception as e:
            print(f'❌ {str(e)[:50]}')
            failed.append((material, str(e)))
    
    # Summary
    print('\n' + '=' * 80)
    print('📊 REGENERATION COMPLETE')
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
    
    print('\n✨ All frontmatter files have been regenerated with categorized structure!')

if __name__ == '__main__':
    main()
