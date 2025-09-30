#!/usr/bin/env python3
"""
Analyze material properties for out-of-range values and suggest corrections.
"""

import yaml
from pathlib import Path
from collections import defaultdict

def load_data():
    """Load Materials.yaml and Categories.yaml"""
    with open('data/Materials.yaml', 'r') as f:
        materials_data = yaml.safe_load(f)
    
    with open('data/Categories.yaml', 'r') as f:
        categories_data = yaml.safe_load(f)
    
    return materials_data, categories_data

def analyze_frontmatter_properties():
    """Analyze all frontmatter files for material property values"""
    
    materials_data, categories_data = load_data()
    
    # Get property descriptions with ranges from Categories.yaml
    property_descriptions = categories_data.get('materialPropertyDescriptions', {})
    
    print("🔍 MATERIAL PROPERTY RANGE ANALYSIS")
    print("=" * 60)
    
    # Track all property values by category
    property_values = defaultdict(lambda: defaultdict(list))
    out_of_range_issues = []
    
    frontmatter_dir = Path('content/components/frontmatter')
    
    for yaml_file in frontmatter_dir.glob('*.yaml'):
        try:
            with open(yaml_file, 'r') as f:
                data = yaml.safe_load(f)
            
            material_name = yaml_file.stem.replace('-laser-cleaning', '')
            
            # Get material category
            material_index = materials_data.get('material_index', {})
            category = None
            for mat, cat in material_index.items():
                if mat.replace(' ', '-').replace('_', '-').lower() == material_name.lower():
                    category = cat
                    break
            
            if not category:
                continue
            
            # Check materialProperties
            material_props = data.get('materialProperties', {})
            
            for prop_name, prop_value in material_props.items():
                if prop_value is None or prop_value == 'N/A':
                    continue
                
                # Store value for analysis
                property_values[category][prop_name].append({
                    'material': material_name,
                    'value': prop_value,
                    'file': yaml_file.name
                })
                
                # Check against defined ranges in Categories.yaml
                # First check category-specific ranges in categories section
                categories_section = categories_data.get('categories', {})
                min_val = None
                max_val = None
                
                if category in categories_section:
                    category_info = categories_section[category]
                    category_ranges = category_info.get('category_ranges', {})
                    if prop_name in category_ranges:
                        range_info = category_ranges[prop_name]
                        min_val = range_info.get('min')
                        max_val = range_info.get('max')
                
                # Also check property descriptions for general ranges
                if min_val is None and prop_name in property_descriptions:
                    prop_desc = property_descriptions[prop_name]
                    typical_ranges = prop_desc.get('typical_ranges', {})
                    if category in typical_ranges:
                        range_parts = typical_ranges[category].split('-')
                        if len(range_parts) == 2:
                            try:
                                min_val = float(range_parts[0])
                                max_val = float(range_parts[1])
                            except:
                                pass
                        
                        if min_val is not None and max_val is not None:
                            try:
                                # Extract numeric value
                                if isinstance(prop_value, str):
                                    # Handle ranges like "2.2-2.8"
                                    if '-' in prop_value and not prop_value.startswith('-'):
                                        value_parts = prop_value.split('-')
                                        if len(value_parts) == 2:
                                            low_val = float(value_parts[0])
                                            high_val = float(value_parts[1])
                                            if low_val < min_val or high_val > max_val:
                                                out_of_range_issues.append({
                                                    'material': material_name,
                                                    'category': category,
                                                    'property': prop_name,
                                                    'value': prop_value,
                                                    'expected_range': f"{min_val}-{max_val}",
                                                    'file': yaml_file.name,
                                                    'issue': f"Range {prop_value} outside bounds [{min_val}, {max_val}]"
                                                })
                                    else:
                                        numeric_val = float(prop_value)
                                        if numeric_val < min_val or numeric_val > max_val:
                                            out_of_range_issues.append({
                                                'material': material_name,
                                                'category': category,
                                                'property': prop_name,
                                                'value': prop_value,
                                                'expected_range': f"{min_val}-{max_val}",
                                                'file': yaml_file.name,
                                                'issue': f"Value {numeric_val} outside bounds [{min_val}, {max_val}]"
                                            })
                                else:
                                    numeric_val = float(prop_value)
                                    if numeric_val < min_val or numeric_val > max_val:
                                        out_of_range_issues.append({
                                            'material': material_name,
                                            'category': category,
                                            'property': prop_name,
                                            'value': prop_value,
                                            'expected_range': f"{min_val}-{max_val}",
                                            'file': yaml_file.name,
                                            'issue': f"Value {numeric_val} outside bounds [{min_val}, {max_val}]"
                                        })
                            except (ValueError, TypeError):
                                continue
        
        except Exception as e:
            print(f"⚠️  Error processing {yaml_file}: {e}")
            continue
    
    # Report out-of-range issues
    if out_of_range_issues:
        print(f"❌ FOUND {len(out_of_range_issues)} OUT-OF-RANGE ISSUES:")
        print()
        
        # Group by property
        issues_by_property = defaultdict(list)
        for issue in out_of_range_issues:
            issues_by_property[issue['property']].append(issue)
        
        for prop_name, issues in issues_by_property.items():
            print(f"🔧 PROPERTY: {prop_name}")
            print(f"   Issues found: {len(issues)}")
            
            # Analyze if we should adjust ranges or values
            all_values = []
            categories_affected = set()
            
            for issue in issues:
                categories_affected.add(issue['category'])
                try:
                    if isinstance(issue['value'], str) and '-' in issue['value']:
                        # Handle ranges
                        parts = issue['value'].split('-')
                        if len(parts) == 2:
                            all_values.extend([float(parts[0]), float(parts[1])])
                    else:
                        all_values.append(float(issue['value']))
                except:
                    pass
            
            if all_values:
                min_actual = min(all_values)
                max_actual = max(all_values)
                
                print(f"   Categories affected: {', '.join(sorted(categories_affected))}")
                print(f"   Actual value range: {min_actual:.2f} - {max_actual:.2f}")
                
                # Get current defined range
                if prop_name in property_descriptions:
                    prop_desc = property_descriptions[prop_name]
                    for category in categories_affected:
                        if category in prop_desc.get('categoryRanges', {}):
                            range_info = prop_desc['categoryRanges'][category]
                            current_min = range_info.get('min')
                            current_max = range_info.get('max')
                            print(f"   Current {category} range: {current_min} - {current_max}")
                
                print("   Specific issues:")
                for issue in issues[:5]:  # Show first 5 issues
                    print(f"     • {issue['material']} ({issue['category']}): {issue['value']} - {issue['issue']}")
                if len(issues) > 5:
                    print(f"     ... and {len(issues) - 5} more")
                print()
    
    else:
        print("✅ NO OUT-OF-RANGE ISSUES FOUND!")
        print("   All material property values are within defined ranges.")
    
    # Analyze actual value distributions for recommendations
    print("\n📊 VALUE DISTRIBUTION ANALYSIS:")
    print("=" * 50)
    
    recommendation_count = 0
    
    for category, properties in property_values.items():
        print(f"\n📋 CATEGORY: {category}")
        
        for prop_name, value_list in properties.items():
            if len(value_list) < 2:
                continue
            
            # Extract numeric values
            numeric_values = []
            for item in value_list:
                try:
                    value = item['value']
                    if isinstance(value, str) and '-' in value:
                        parts = value.split('-')
                        if len(parts) == 2:
                            numeric_values.extend([float(parts[0]), float(parts[1])])
                    else:
                        numeric_values.append(float(value))
                except:
                    continue
            
            if len(numeric_values) >= 2:
                min_val = min(numeric_values)
                max_val = max(numeric_values)
                
                # Check current defined range
                current_range = None
                if prop_name in property_descriptions:
                    prop_desc = property_descriptions[prop_name]
                    category_ranges = prop_desc.get('categoryRanges', {})
                    if category in category_ranges:
                        range_info = category_ranges[category]
                        current_min = range_info.get('min')
                        current_max = range_info.get('max')
                        current_range = f"{current_min}-{current_max}"
                
                print(f"   {prop_name}: {min_val:.2f} - {max_val:.2f} (n={len(value_list)})")
                if current_range:
                    print(f"      Current range: {current_range}")
                    
                    # Check if range needs adjustment
                    range_parts = current_range.split('-')
                    if len(range_parts) == 2:
                        try:
                            defined_min = float(range_parts[0])
                            defined_max = float(range_parts[1])
                            
                            if min_val < defined_min or max_val > defined_max:
                                print(f"      🔧 RECOMMENDATION: Adjust range to {min_val:.1f}-{max_val:.1f}")
                                recommendation_count += 1
                        except:
                            pass
    
    print(f"\n📋 SUMMARY:")
    print(f"   • Out-of-range issues: {len(out_of_range_issues)}")
    print(f"   • Range adjustment recommendations: {recommendation_count}")
    
    if out_of_range_issues:
        print(f"\n🔧 NEXT STEPS:")
        print("   1. Review each out-of-range issue")
        print("   2. Determine if the range should be expanded or value corrected")
        print("   3. Apply corrections to either Categories.yaml ranges or frontmatter values")
        print("   4. Re-run analysis to verify fixes")
    
    return out_of_range_issues, property_values

if __name__ == "__main__":
    issues, values = analyze_frontmatter_properties()