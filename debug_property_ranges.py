#!/usr/bin/env python3
"""
Debug analysis for material property ranges - detailed logging version.
"""

import yaml
import json
import os
from pathlib import Path

def debug_range_analysis():
    """Debug version with detailed logging"""
    
    # Load data
    with open('data/Materials.yaml', 'r') as f:
        materials_data = yaml.safe_load(f)
    
    with open('data/Categories.yaml', 'r') as f:
        categories_data = yaml.safe_load(f)
    
    print("🔍 DEBUG: MATERIAL PROPERTY RANGE ANALYSIS")
    print("=" * 60)
    
    # Check one specific file - aluminum
    aluminum_file = Path('content/components/frontmatter/aluminum-laser-cleaning.yaml')
    
    if aluminum_file.exists():
        with open(aluminum_file, 'r') as f:
            aluminum_data = yaml.safe_load(f)
        
        print("📋 DEBUG: Checking aluminum material properties")
        
        material_props = aluminum_data.get('materialProperties', {})
        print(f"Found {len(material_props)} properties in aluminum")
        
        categories_section = categories_data.get('categories', {})
        print(f"Found {len(categories_section)} categories in Categories.yaml")
        
        # Check metal category
        if 'metal' in categories_section:
            metal_info = categories_section['metal']
            category_ranges = metal_info.get('category_ranges', {})
            print(f"Found {len(category_ranges)} property ranges for metal category")
            
            # Check specific properties
            for prop_name, prop_data in material_props.items():
                if isinstance(prop_data, dict) and 'value' in prop_data:
                    prop_value = prop_data['value']
                    
                    print(f"\n🔧 Property: {prop_name}")
                    print(f"   Value: {prop_value}")
                    
                    if prop_name in category_ranges:
                        range_info = category_ranges[prop_name]
                        min_val = range_info.get('min')
                        max_val = range_info.get('max')
                        print(f"   Range: {min_val} - {max_val}")
                        
                        if min_val is not None and max_val is not None:
                            try:
                                numeric_val = float(prop_value)
                                if numeric_val < min_val or numeric_val > max_val:
                                    print(f"   ❌ OUT OF RANGE! {numeric_val} not in [{min_val}, {max_val}]")
                                else:
                                    print(f"   ✅ In range")
                            except (ValueError, TypeError):
                                print(f"   ⚠️  Could not convert {prop_value} to number")
                    else:
                        print(f"   ⚠️  No range defined for {prop_name}")
        else:
            print("❌ No metal category found!")
    
    # Now check a few more materials for out-of-range issues
    print(f"\n🔍 CHECKING ALL MATERIALS FOR OUT-OF-RANGE ISSUES:")
    print("=" * 60)
    
    out_of_range_count = 0
    frontmatter_dir = Path('content/components/frontmatter')
    
    for yaml_file in list(frontmatter_dir.glob('*.yaml'))[:5]:  # Check first 5 files
        try:
            with open(yaml_file, 'r') as f:
                data = yaml.safe_load(f)
            
            material_name = yaml_file.stem.replace('-laser-cleaning', '')
            category = data.get('category', '').lower()
            
            print(f"\n📄 {material_name} ({category})")
            
            if category in categories_section:
                category_info = categories_section[category]
                category_ranges = category_info.get('category_ranges', {})
                
                material_props = data.get('materialProperties', {})
                for prop_name, prop_data in material_props.items():
                    if isinstance(prop_data, dict) and 'value' in prop_data:
                        prop_value = prop_data['value']
                        
                        if prop_name in category_ranges:
                            range_info = category_ranges[prop_name]
                            min_val = range_info.get('min')
                            max_val = range_info.get('max')
                            
                            if min_val is not None and max_val is not None:
                                try:
                                    numeric_val = float(prop_value)
                                    if numeric_val < min_val or numeric_val > max_val:
                                        print(f"   ❌ {prop_name}: {numeric_val} outside [{min_val}, {max_val}]")
                                        out_of_range_count += 1
                                except (ValueError, TypeError):
                                    pass
        except Exception as e:
            print(f"⚠️  Error processing {yaml_file}: {e}")
    
    print(f"\n📊 SUMMARY: Found {out_of_range_count} out-of-range issues in first 5 files")

if __name__ == "__main__":
    debug_range_analysis()