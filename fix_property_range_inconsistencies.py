#!/usr/bin/env python3
"""
Fix material property range inconsistencies by analyzing actual values 
and adjusting min/max ranges or correcting obviously wrong values.
"""

import yaml
from pathlib import Path
from collections import defaultdict
import statistics

def analyze_and_fix_property_ranges():
    """Analyze property values across all materials and fix inconsistencies"""
    
    print("🔧 MATERIAL PROPERTY RANGE CORRECTION")
    print("=" * 60)
    
    # Collect all property values by category and property
    property_stats = defaultdict(lambda: defaultdict(list))
    files_to_fix = {}
    
    frontmatter_dir = Path('content/components/frontmatter')
    
    # First pass: collect all values
    for yaml_file in frontmatter_dir.glob('*.yaml'):
        try:
            with open(yaml_file, 'r') as f:
                data = yaml.safe_load(f)
            
            material_name = yaml_file.stem.replace('-laser-cleaning', '')
            category = data.get('category', '').lower()
            
            material_props = data.get('materialProperties', {})
            
            for prop_name, prop_data in material_props.items():
                if isinstance(prop_data, dict) and 'value' in prop_data:
                    prop_value = prop_data['value']
                    
                    try:
                        # Only process numeric values
                        numeric_val = float(prop_value)
                        property_stats[category][prop_name].append({
                            'value': numeric_val,
                            'material': material_name,
                            'file': yaml_file,
                            'current_min': prop_data.get('min'),
                            'current_max': prop_data.get('max')
                        })
                    except (ValueError, TypeError):
                        # Handle ranges like "2.2-2.8"
                        if isinstance(prop_value, str) and '-' in prop_value and not prop_value.startswith('-'):
                            try:
                                parts = prop_value.split('-')
                                if len(parts) == 2:
                                    low_val = float(parts[0])
                                    high_val = float(parts[1])
                                    property_stats[category][prop_name].append({
                                        'value': (low_val + high_val) / 2,  # Use midpoint
                                        'material': material_name,
                                        'file': yaml_file,
                                        'current_min': prop_data.get('min'),
                                        'current_max': prop_data.get('max'),
                                        'is_range': True,
                                        'range_low': low_val,
                                        'range_high': high_val
                                    })
                            except:
                                pass
        
        except Exception as e:
            print(f"⚠️  Error processing {yaml_file}: {e}")
            continue
    
    # Analyze statistics and determine corrections
    corrections = {}
    
    print("📊 ANALYZING PROPERTY STATISTICS BY CATEGORY:")
    print()
    
    for category, properties in property_stats.items():
        print(f"📋 CATEGORY: {category.upper()}")
        
        for prop_name, value_list in properties.items():
            if len(value_list) < 2:
                continue
            
            values = [item['value'] for item in value_list]
            
            # Calculate statistics
            min_actual = min(values)
            max_actual = max(values)
            mean_val = statistics.mean(values)
            median_val = statistics.median(values)
            
            # Calculate reasonable range with some buffer
            range_span = max_actual - min_actual
            buffer = max(range_span * 0.1, (max_actual - min_actual) * 0.05)  # 10% buffer or 5% of span
            suggested_min = max(0, min_actual - buffer)  # Don't go below 0 for most properties
            suggested_max = max_actual + buffer
            
            print(f"   {prop_name}:")
            print(f"     Actual range: {min_actual:.3f} - {max_actual:.3f}")
            print(f"     Suggested range: {suggested_min:.3f} - {suggested_max:.3f}")
            print(f"     Count: {len(value_list)} materials")
            
            # Check for values outside their own ranges
            out_of_range_count = 0
            for item in value_list:
                current_min = item['current_min']
                current_max = item['current_max']
                value = item['value']
                
                if current_min is not None and current_max is not None:
                    try:
                        if value < float(current_min) or value > float(current_max):
                            out_of_range_count += 1
                    except:
                        pass
            
            if out_of_range_count > 0:
                print(f"     ❌ {out_of_range_count} values outside their own ranges")
                
                # Store correction
                corrections[f"{category}_{prop_name}"] = {
                    'category': category,
                    'property': prop_name,
                    'suggested_min': suggested_min,
                    'suggested_max': suggested_max,
                    'actual_min': min_actual,
                    'actual_max': max_actual,
                    'materials': value_list,
                    'out_of_range_count': out_of_range_count
                }
            else:
                print(f"     ✅ All values in range")
        
        print()
    
    # Apply corrections
    if corrections:
        print(f"🔧 APPLYING CORRECTIONS TO {len(corrections)} PROPERTY RANGES:")
        print()
        
        correction_count = 0
        
        for correction_key, correction_data in corrections.items():
            category = correction_data['category']
            prop_name = correction_data['property']
            suggested_min = correction_data['suggested_min']
            suggested_max = correction_data['suggested_max']
            materials = correction_data['materials']
            
            print(f"   {category.upper()} - {prop_name}")
            print(f"     New range: {suggested_min:.3f} - {suggested_max:.3f}")
            
            # Update all files for this category/property combination
            files_updated = 0
            for item in materials:
                yaml_file = item['file']
                
                try:
                    with open(yaml_file, 'r') as f:
                        data = yaml.safe_load(f)
                    
                    # Update the min/max for this property
                    material_props = data.get('materialProperties', {})
                    if prop_name in material_props and isinstance(material_props[prop_name], dict):
                        # Round to appropriate decimal places
                        if suggested_min >= 1:
                            min_rounded = round(suggested_min, 1)
                            max_rounded = round(suggested_max, 1)
                        else:
                            min_rounded = round(suggested_min, 3)
                            max_rounded = round(suggested_max, 3)
                        
                        material_props[prop_name]['min'] = min_rounded
                        material_props[prop_name]['max'] = max_rounded
                        
                        # Save the file
                        with open(yaml_file, 'w') as f:
                            yaml.dump(data, f, default_flow_style=False, sort_keys=False, allow_unicode=True)
                        
                        files_updated += 1
                
                except Exception as e:
                    print(f"     ⚠️  Error updating {yaml_file}: {e}")
            
            print(f"     Updated {files_updated} files")
            correction_count += files_updated
        
        print(f"\n✅ CORRECTIONS COMPLETE!")
        print(f"   • Fixed ranges for {len(corrections)} property types")
        print(f"   • Updated {correction_count} files")
        
    else:
        print("✅ NO CORRECTIONS NEEDED!")
        print("   All property ranges are consistent with actual values.")
    
    return corrections

if __name__ == "__main__":
    corrections = analyze_and_fix_property_ranges()
    
    if corrections:
        print(f"\n🔍 RECOMMENDED NEXT STEPS:")
        print("   1. Review the applied corrections")
        print("   2. Run consistency check again to verify fixes")
        print("   3. Consider updating Categories.yaml ranges if needed")
        print("   4. Re-deploy updated content")