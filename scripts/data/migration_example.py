#!/usr/bin/env python3
"""
Example: Migrating from direct YAML loading to CategoryDataLoader

This script demonstrates updating existing code to use the new loader.
"""

from pathlib import Path
import sys

project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))


def example_old_way():
    """❌ OLD WAY: Direct YAML file loading (DON'T USE)"""
    import yaml
    
    # Load entire 121KB file just to get machine settings
    with open(project_root / 'data' / 'Categories.yaml', 'r') as f:
        categories = yaml.safe_load(f)
    
    machine_settings = categories['machineSettingsRanges']
    safety_templates = categories['safetyTemplates']
    
    return machine_settings, safety_templates


def example_new_way():
    """✅ NEW WAY: Use CategoryDataLoader (RECOMMENDED)"""
    from materials.category_loader import CategoryDataLoader
    
    loader = CategoryDataLoader()
    
    # Load only what you need - faster and cleaner
    settings_data = loader.get_machine_settings()
    machine_settings = settings_data['machineSettingsRanges']
    
    safety_data = loader.get_safety_regulatory()
    safety_templates = safety_data['safetyTemplates']
    
    return machine_settings, safety_templates


def example_convenience():
    """✅ ALTERNATIVE: Use convenience function"""
    from materials.category_loader import load_category_data
    
    # Quick access for specific data
    settings = load_category_data('machine_settings')
    safety = load_category_data('safety_regulatory')
    
    return settings['machineSettingsRanges'], safety['safetyTemplates']


def example_specific_category():
    """✅ BEST: Use specific helper for category ranges"""
    from materials.category_loader import CategoryDataLoader
    
    loader = CategoryDataLoader()
    
    # Get property ranges for a specific category
    metal_ranges = loader.get_category_ranges('metal')
    ceramic_ranges = loader.get_category_ranges('ceramic')
    
    print(f"Metal properties: {len(metal_ranges)}")
    print(f"Ceramic properties: {len(ceramic_ranges)}")
    
    return metal_ranges, ceramic_ranges


if __name__ == '__main__':
    print("🔄 Migration Examples\n")
    
    # Show old way
    print("❌ OLD WAY (Direct YAML):")
    settings1, safety1 = example_old_way()
    print(f"   Loaded {len(settings1)} settings, {len(safety1)} safety templates\n")
    
    # Show new way
    print("✅ NEW WAY (CategoryDataLoader):")
    settings2, safety2 = example_new_way()
    print(f"   Loaded {len(settings2)} settings, {len(safety2)} safety templates\n")
    
    # Show convenience
    print("✅ CONVENIENCE (load_category_data):")
    settings3, safety3 = example_convenience()
    print(f"   Loaded {len(settings3)} settings, {len(safety3)} safety templates\n")
    
    # Show specific category
    print("✅ SPECIFIC CATEGORY (get_category_ranges):")
    example_specific_category()
    
    print("\n✨ All methods work! Use the new way for better performance.")
