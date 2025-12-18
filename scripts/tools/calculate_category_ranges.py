#!/usr/bin/env python3
"""
Calculate Category Ranges from Material Data

Analyzes all material property values within each category and calculates
appropriate min/max ranges for MaterialProperties.yaml.
"""

import yaml
from pathlib import Path
from collections import defaultdict
from typing import Dict, List, Any

def load_materials() -> dict:
    """Load Materials.yaml"""
    materials_file = Path('data/materials/Materials.yaml')
    with open(materials_file, 'r') as f:
        return yaml.safe_load(f)

def load_material_properties() -> dict:
    """Load MaterialProperties.yaml"""
    properties_file = Path('data/materials/MaterialProperties.yaml')
    with open(properties_file, 'r') as f:
        return yaml.safe_load(f)

def extract_property_values_by_category():
    """Extract all property values organized by category"""
    materials_data = load_materials()
    materials = materials_data.get('materials', {})
    
    # Structure: {category: {property: [values]}}
    category_properties = defaultdict(lambda: defaultdict(list))
    
    for material_name, material_data in materials.items():
        category = material_data.get('category', 'unknown')
        
        if 'properties' not in material_data:
            continue
        
        mat_props = material_data['properties']
        
        # Check both property groups
        for group_name in ['material_characteristics', 'laser_material_interaction']:
            if group_name not in mat_props:
                continue
            
            group = mat_props[group_name]
            metadata_fields = {'label', 'description', 'percentage'}
            
            for prop_name, prop_value in group.items():
                if prop_name in metadata_fields:
                    continue
                
                if not isinstance(prop_value, dict):
                    continue
                
                value = prop_value.get('value')
                unit = prop_value.get('unit', '')
                
                if value is not None:
                    category_properties[category][prop_name].append({
                        'value': value,
                        'unit': unit,
                        'material': material_name
                    })
    
    return category_properties

def calculate_ranges(category_properties):
    """Calculate min/max ranges for each property in each category"""
    ranges = {}
    
    for category, properties in sorted(category_properties.items()):
        ranges[category] = {}
        
        for prop_name, values in sorted(properties.items()):
            if not values:
                continue
            
            # Extract numeric values
            numeric_values = []
            unit = values[0]['unit']
            
            for item in values:
                try:
                    val = float(item['value'])
                    numeric_values.append(val)
                except (ValueError, TypeError):
                    continue
            
            if not numeric_values:
                continue
            
            min_val = min(numeric_values)
            max_val = max(numeric_values)
            
            # Add some buffer (5%) to ensure all values fit
            range_span = max_val - min_val
            buffer = range_span * 0.05 if range_span > 0 else 0.1
            
            ranges[category][prop_name] = {
                'min': round(min_val - buffer, 6) if min_val > buffer else round(min_val * 0.95, 6),
                'max': round(max_val + buffer, 6),
                'unit': unit,
                'source': 'calculated_from_materials',
                'confidence': 100,
                'notes': f'Calculated from {len(numeric_values)} materials',
                'last_updated': '2025-11-13'
            }
    
    return ranges

def update_material_properties_file(calculated_ranges):
    """Update MaterialProperties.yaml with calculated ranges"""
    properties_data = load_material_properties()
    
    category_ranges = properties_data.get('categoryRanges', {})
    
    updated_count = 0
    added_count = 0
    
    for category, properties in calculated_ranges.items():
        # Handle category name format (e.g., rare-earth)
        category_key = category.lower().replace('_', '-')
        
        if category_key not in category_ranges:
            print(f"⚠️  Category '{category_key}' not found in MaterialProperties.yaml")
            continue
        
        if 'ranges' not in category_ranges[category_key]:
            category_ranges[category_key]['ranges'] = {}
        
        ranges = category_ranges[category_key]['ranges']
        
        for prop_name, prop_range in properties.items():
            if prop_name in ranges:
                # Update existing range if our calculated values are wider
                existing = ranges[prop_name]
                try:
                    existing_min = float(existing.get('min', float('inf')))
                    existing_max = float(existing.get('max', float('-inf')))
                except (ValueError, TypeError):
                    existing_min = float('inf')
                    existing_max = float('-inf')
                
                if prop_range['min'] < existing_min or prop_range['max'] > existing_max:
                    ranges[prop_name].update(prop_range)
                    updated_count += 1
                    print(f"  Updated: {category_key}.{prop_name}")
            else:
                # Add new range
                ranges[prop_name] = prop_range
                added_count += 1
                print(f"  Added: {category_key}.{prop_name}")
    
    # Save updated file
    backup_file = Path('data/materials/MaterialProperties_backup_before_range_update.yaml')
    with open('data/materials/MaterialProperties.yaml', 'r') as f:
        backup_content = f.read()
    with open(backup_file, 'w') as bf:
        bf.write(backup_content)
    
    with open('data/materials/MaterialProperties.yaml', 'w') as f:
        yaml.dump(properties_data, f, default_flow_style=False, sort_keys=False, 
                  allow_unicode=True, width=1000)
    
    print(f"\n💾 Backup created: {backup_file}")
    print(f"💾 Saved to materials/data/MaterialProperties.yaml")
    
    return updated_count, added_count

def main():
    print("=" * 80)
    print("CALCULATE CATEGORY RANGES FROM MATERIAL DATA")
    print("=" * 80)
    print()
    
    # Extract property values by category
    print("📊 Extracting property values from materials...")
    category_properties = extract_property_values_by_category()
    
    total_properties = sum(len(props) for props in category_properties.values())
    print(f"✅ Found {total_properties} properties across {len(category_properties)} categories")
    print()
    
    # Calculate ranges
    print("🔢 Calculating min/max ranges...")
    calculated_ranges = calculate_ranges(category_properties)
    
    # Show what will be added/updated
    print("\nCalculated Ranges:")
    print("-" * 80)
    for category, properties in sorted(calculated_ranges.items()):
        print(f"\n{category.upper()} ({len(properties)} properties)")
        for prop_name in sorted(properties.keys())[:5]:  # Show first 5
            prop_range = properties[prop_name]
            print(f"  {prop_name}: {prop_range['min']} - {prop_range['max']} {prop_range['unit']}")
        if len(properties) > 5:
            print(f"  ... and {len(properties) - 5} more")
    
    print("\n" + "=" * 80)
    print("UPDATING MaterialProperties.yaml")
    print("=" * 80)
    print()
    
    updated_count, added_count = update_material_properties_file(calculated_ranges)
    
    print("\n" + "=" * 80)
    print("COMPLETE")
    print("=" * 80)
    print(f"✅ Ranges added: {added_count}")
    print(f"✅ Ranges updated: {updated_count}")
    print()

if __name__ == '__main__':
    import sys
    main()
    sys.exit(0)
