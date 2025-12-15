#!/usr/bin/env python3
"""
Test normalized export methods across all domains

Tests:
- Contaminants: 4 test contaminants
- Settings: 4 test materials
- Materials: (existing, not tested here)

Verifies:
- All generators registered
- All modules working
- Complete frontmatter export
- Data correctly extracted
"""

import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path.cwd()))

from export.core.orchestrator import FrontmatterOrchestrator
from shared.api.client_factory import create_api_client
import yaml


def test_contaminants_export():
    """Test contaminant frontmatter export"""
    print('\n' + '=' * 80)
    print('TESTING CONTAMINANTS EXPORT')
    print('=' * 80)
    
    test_contaminants = ['scale-buildup', 'aluminum-oxidation', 'adhesive-residue', 'copper-patina']
    
    api_client = create_api_client('grok')
    orchestrator = FrontmatterOrchestrator(api_client=api_client)
    
    results = []
    for contaminant in test_contaminants:
        print(f'\n📋 Exporting: {contaminant}')
        print('-' * 80)
        
        try:
            result = orchestrator.generate(
                content_type='contaminant',
                identifier=contaminant
            )
            
            if result.success:
                # result.content is the file path - read the file
                filepath = Path(result.content)
                print(f'✅ SUCCESS - Saved to: {filepath.name}')
                
                # Read and parse the generated file
                with open(filepath, 'r') as f:
                    data = yaml.safe_load(f)
                
                sections = list(data.keys())
                print(f'   Sections ({len(sections)}): {", ".join(sections[:10])}{"..." if len(sections) > 10 else ""}')
                
                # Check for key fields
                has_description = 'description' in data
                has_micro = 'micro' in data
                has_laser = 'laser_properties' in data
                has_eeat = 'eeat' in data
                has_category = 'category' in data
                has_subcategory = 'subcategory' in data
                
                print(f'   ✓ description: {has_description}')
                print(f'   ✓ micro: {has_micro}')
                print(f'   ✓ laser_properties: {has_laser}')
                print(f'   ✓ eeat: {has_eeat}')
                print(f'   ✓ category: {has_category}')
                print(f'   ✓ subcategory: {has_subcategory}')
                
                # Validate category/subcategory if present
                if has_category and has_subcategory:
                    category = data['category']
                    subcategory = data['subcategory']
                    print(f'   📊 Categorization: {category}/{subcategory}')
                
                results.append((contaminant, True, len(sections)))
            else:
                print(f'❌ FAILED: {result.error_message}')
                results.append((contaminant, False, 0))
                
        except Exception as e:
            print(f'❌ EXCEPTION: {e}')
            results.append((contaminant, False, 0))
    
    return results


def test_settings_export():
    """Test settings frontmatter export"""
    print('\n' + '=' * 80)
    print('TESTING SETTINGS EXPORT')
    print('=' * 80)
    
    test_materials = ['Aluminum', 'Steel', 'Copper', 'Titanium']
    
    api_client = create_api_client('grok')
    orchestrator = FrontmatterOrchestrator(api_client=api_client)
    
    results = []
    for material in test_materials:
        print(f'\n⚙️  Exporting: {material}')
        print('-' * 80)
        
        try:
            result = orchestrator.generate(
                content_type='settings',
                identifier=material
            )
            
            if result.success:
                # result.content is the file path - read the file
                filepath = Path(result.content)
                print(f'✅ SUCCESS - Saved to: {filepath.name}')
                
                # Read and parse the generated file
                with open(filepath, 'r') as f:
                    data = yaml.safe_load(f)
                
                sections = list(data.keys())
                print(f'   Sections ({len(sections)}): {", ".join(sections[:10])}{"..." if len(sections) > 10 else ""}')
                
                # Check for key fields
                has_settings = 'machineSettings' in data
                has_challenges = 'material_challenges' in data
                has_description = 'settings_description' in data
                
                print(f'   ✓ machineSettings: {has_settings}')
                print(f'   ✓ material_challenges: {has_challenges}')
                print(f'   ✓ settings_description: {has_description}')
                
                results.append((material, True, len(sections)))
            else:
                print(f'❌ FAILED: {result.error_message}')
                results.append((material, False, 0))
                
        except Exception as e:
            print(f'❌ EXCEPTION: {e}')
            results.append((material, False, 0))
    
    return results


def print_summary(contaminant_results, settings_results):
    """Print test summary"""
    print('\n' + '=' * 80)
    print('TEST SUMMARY')
    print('=' * 80)
    
    # Contaminants
    print('\nContaminants Export:')
    success_count = sum(1 for _, success, _ in contaminant_results if success)
    total_count = len(contaminant_results)
    print(f'  Success: {success_count}/{total_count}')
    
    for name, success, sections in contaminant_results:
        status = '✅' if success else '❌'
        print(f'    {status} {name}: {sections} sections')
    
    # Settings
    print('\nSettings Export:')
    success_count = sum(1 for _, success, _ in settings_results if success)
    total_count = len(settings_results)
    print(f'  Success: {success_count}/{total_count}')
    
    for name, success, sections in settings_results:
        status = '✅' if success else '❌'
        print(f'    {status} {name}: {sections} sections')
    
    # Overall
    total_success = sum(1 for _, success, _ in contaminant_results + settings_results if success)
    total_tests = len(contaminant_results) + len(settings_results)
    
    print(f'\nOverall: {total_success}/{total_tests} exports successful')
    print('=' * 80)


if __name__ == '__main__':
    try:
        # Test contaminants
        contaminant_results = test_contaminants_export()
        
        # Test settings
        settings_results = test_settings_export()
        
        # Print summary
        print_summary(contaminant_results, settings_results)
        
    except Exception as e:
        print(f'\n❌ Test failed with exception: {e}')
        import traceback
        traceback.print_exc()
        sys.exit(1)
