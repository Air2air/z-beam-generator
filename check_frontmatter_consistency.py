#!/usr/bin/env python3
"""
Check for inconsistencies between frontmatter property values and their own min/max ranges.
"""

import yaml
from pathlib import Path

def check_frontmatter_property_consistency():
    """Check if property values are within their own defined min/max ranges"""
    
    print("🔍 FRONTMATTER PROPERTY CONSISTENCY ANALYSIS")
    print("=" * 60)
    
    inconsistencies = []
    frontmatter_dir = Path('content/components/frontmatter')
    
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
                    min_val = prop_data.get('min')
                    max_val = prop_data.get('max')
                    
                    # Check if value is within its own min/max
                    if min_val is not None and max_val is not None:
                        try:
                            numeric_val = float(prop_value)
                            numeric_min = float(min_val)
                            numeric_max = float(max_val)
                            
                            if numeric_val < numeric_min or numeric_val > numeric_max:
                                inconsistencies.append({
                                    'material': material_name,
                                    'category': category,
                                    'property': prop_name,
                                    'value': numeric_val,
                                    'min': numeric_min,
                                    'max': numeric_max,
                                    'file': yaml_file.name
                                })
                        except (ValueError, TypeError):
                            # Handle non-numeric values
                            if isinstance(prop_value, str) and '-' not in prop_value:
                                inconsistencies.append({
                                    'material': material_name,
                                    'category': category,
                                    'property': prop_name,
                                    'value': prop_value,
                                    'min': min_val,
                                    'max': max_val,
                                    'file': yaml_file.name,
                                    'issue': 'Non-numeric value with numeric range'
                                })
                    
                    # Check for null min/max when they might be needed
                    elif prop_value is not None and prop_value != 'N/A':
                        if min_val is None or max_val is None:
                            try:
                                float(prop_value)  # Only flag if value is numeric
                                inconsistencies.append({
                                    'material': material_name,
                                    'category': category,
                                    'property': prop_name,
                                    'value': prop_value,
                                    'min': min_val,
                                    'max': max_val,
                                    'file': yaml_file.name,
                                    'issue': 'Missing min/max range for numeric value'
                                })
                            except (ValueError, TypeError):
                                pass
        
        except Exception as e:
            print(f"⚠️  Error processing {yaml_file}: {e}")
            continue
    
    # Report results
    if inconsistencies:
        print(f"❌ FOUND {len(inconsistencies)} INCONSISTENCIES:")
        print()
        
        # Group by issue type
        value_outside_range = []
        missing_ranges = []
        non_numeric_issues = []
        
        for issue in inconsistencies:
            if 'issue' in issue:
                if 'Non-numeric' in issue['issue']:
                    non_numeric_issues.append(issue)
                elif 'Missing' in issue['issue']:
                    missing_ranges.append(issue)
            else:
                value_outside_range.append(issue)
        
        if value_outside_range:
            print(f"🔧 VALUES OUTSIDE THEIR OWN MIN/MAX RANGES ({len(value_outside_range)}):")
            for issue in value_outside_range[:10]:  # Show first 10
                print(f"   • {issue['material']} ({issue['category']}) - {issue['property']}")
                print(f"     Value: {issue['value']}, Range: [{issue['min']}, {issue['max']}]")
                print(f"     File: {issue['file']}")
                print()
            if len(value_outside_range) > 10:
                print(f"   ... and {len(value_outside_range) - 10} more")
            print()
        
        if missing_ranges:
            print(f"⚠️  MISSING MIN/MAX RANGES ({len(missing_ranges)}):")
            # Group by property
            by_property = {}
            for issue in missing_ranges:
                prop = issue['property']
                if prop not in by_property:
                    by_property[prop] = []
                by_property[prop].append(issue)
            
            for prop_name, issues in by_property.items():
                print(f"   • {prop_name}: {len(issues)} materials missing ranges")
            print()
        
        if non_numeric_issues:
            print(f"🔤 NON-NUMERIC VALUES WITH NUMERIC RANGES ({len(non_numeric_issues)}):")
            for issue in non_numeric_issues[:5]:  # Show first 5
                print(f"   • {issue['material']} - {issue['property']}: '{issue['value']}'")
            print()
    
    else:
        print("✅ NO INCONSISTENCIES FOUND!")
        print("   All property values are within their defined min/max ranges.")
    
    return inconsistencies

if __name__ == "__main__":
    issues = check_frontmatter_property_consistency()
    
    if issues:
        print(f"📋 SUMMARY:")
        print(f"   • Total inconsistencies: {len(issues)}")
        print(f"\n🔧 RECOMMENDED ACTIONS:")
        print("   1. Review values that are outside their own ranges")
        print("   2. Either adjust the value or expand the min/max range")
        print("   3. Add missing min/max ranges for numeric properties")
        print("   4. Consider data validation during content generation")