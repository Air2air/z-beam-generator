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

import yaml

# Add project root to path
sys.path.insert(0, str(Path.cwd()))

from export.config.loader import load_domain_config
from export.core.frontmatter_exporter import FrontmatterExporter


def _load_exported_yaml(output_dir: Path, item_id: str) -> dict:
    filepath = output_dir / f'{item_id}.yaml'
    with open(filepath, 'r', encoding='utf-8') as handle:
        return yaml.safe_load(handle)


def run_contaminants_export():
    """Test contaminant frontmatter export"""
    print('\n' + '=' * 80)
    print('TESTING CONTAMINANTS EXPORT')
    print('=' * 80)
    
    test_contaminants = [
        'scale-buildup-contamination',
        'aluminum-oxidation-contamination',
        'adhesive-residue-contamination',
        'copper-patina-contamination',
    ]

    config = load_domain_config('contaminants')
    exporter = FrontmatterExporter(config)
    output_dir = Path(config['output_path'])
    
    results = []
    for contaminant in test_contaminants:
        print(f'\n📋 Exporting: {contaminant}')
        print('-' * 80)
        
        try:
            data = exporter._load_domain_data()[exporter.items_key][contaminant]
            success = exporter.export_single(contaminant, data, force=True)

            if success:
                filepath = output_dir / f'{contaminant}.yaml'
                print(f'✅ SUCCESS - Saved to: {filepath.name}')

                exported = _load_exported_yaml(output_dir, contaminant)
                sections = list(exported.keys())
                print(f'   Sections ({len(sections)}): {", ".join(sections[:10])}{"..." if len(sections) > 10 else ""}')

                has_page_description = 'pageDescription' in exported
                has_relationships = 'relationships' in exported
                has_author = 'author' in exported
                has_category = 'category' in exported
                has_subcategory = 'subcategory' in exported

                print(f'   ✓ pageDescription: {has_page_description}')
                print(f'   ✓ relationships: {has_relationships}')
                print(f'   ✓ author: {has_author}')
                print(f'   ✓ category: {has_category}')
                print(f'   ✓ subcategory: {has_subcategory}')

                if has_category and has_subcategory:
                    category = exported['category']
                    subcategory = exported['subcategory']
                    print(f'   📊 Categorization: {category}/{subcategory}')

                results.append((contaminant, True, len(sections)))
            else:
                print('❌ FAILED: exporter skipped or returned False')
                results.append((contaminant, False, 0))
                
        except Exception as e:
            print(f'❌ EXCEPTION: {e}')
            results.append((contaminant, False, 0))
    
    return results


def run_settings_export():
    """Test settings frontmatter export"""
    print('\n' + '=' * 80)
    print('TESTING SETTINGS EXPORT')
    print('=' * 80)
    
    test_settings = [
        'aluminum-settings',
        'steel-settings',
        'copper-settings',
        'titanium-settings',
    ]

    config = load_domain_config('settings')
    exporter = FrontmatterExporter(config)
    output_dir = Path(config['output_path'])
    
    results = []
    for setting_id in test_settings:
        print(f'\n⚙️  Exporting: {setting_id}')
        print('-' * 80)
        
        try:
            data = exporter._load_domain_data()[exporter.items_key][setting_id]
            success = exporter.export_single(setting_id, data, force=True)

            if success:
                filepath = output_dir / f'{setting_id}.yaml'
                print(f'✅ SUCCESS - Saved to: {filepath.name}')

                exported = _load_exported_yaml(output_dir, setting_id)
                sections = list(exported.keys())
                print(f'   Sections ({len(sections)}): {", ".join(sections[:10])}{"..." if len(sections) > 10 else ""}')

                has_machine_settings = 'machineSettings' in exported
                has_common_challenges = 'relationships' in exported and 'operational' in exported['relationships']
                has_page_description = 'pageDescription' in exported

                print(f'   ✓ machineSettings: {has_machine_settings}')
                print(f'   ✓ operational relationships: {has_common_challenges}')
                print(f'   ✓ pageDescription: {has_page_description}')

                results.append((setting_id, True, len(sections)))
            else:
                print('❌ FAILED: exporter skipped or returned False')
                results.append((setting_id, False, 0))
                
        except Exception as e:
            print(f'❌ EXCEPTION: {e}')
            results.append((setting_id, False, 0))
    
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
        contaminant_results = run_contaminants_export()
        
        # Test settings
        settings_results = run_settings_export()
        
        # Print summary
        print_summary(contaminant_results, settings_results)
        
    except Exception as e:
        print(f'\n❌ Test failed with exception: {e}')
        import traceback
        traceback.print_exc()
        sys.exit(1)
