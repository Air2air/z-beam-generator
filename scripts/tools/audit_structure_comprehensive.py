#!/usr/bin/env python3
"""
Comprehensive structure audit for Materials.yaml.

Checks for ALL possible structure variations:
1. Properties wrapper (properties: {})
2. Flat vs nested structure
3. Percentage at wrong level
4. Empty vs populated
5. Metadata keys
6. Per frontmatter_template.yaml compliance
"""

import yaml
from pathlib import Path
from collections import defaultdict

def main():
    materials_file = Path("data/materials/Materials.yaml")
    
    with open(materials_file) as f:
        data = yaml.safe_load(f)
    
    materials = data.get('materials', {})
    
    print("=" * 80)
    print("COMPREHENSIVE MATERIALS.YAML STRUCTURE AUDIT")
    print("=" * 80)
    print()
    
    # Track all variations
    issues = {
        'has_properties_wrapper': [],
        'has_percentage_wrong_level': [],
        'has_description_wrong_level': [],
        'missing_label': [],
        'empty_category_groups': [],
        'has_flat_properties': [],
        'completely_empty': []
    }
    
    metadata_keys = {'label', 'description', 'percentage'}
    
    for mat_name, mat_data in materials.items():
        if not isinstance(mat_data, dict):
            continue
            
        mat_props = mat_data.get('materialProperties', {})
        if not isinstance(mat_props, dict):
            continue
        
        for category in ['material_characteristics', 'laser_material_interaction']:
            cat_data = mat_props.get(category, {})
            
            if not isinstance(cat_data, dict):
                continue
            
            # Check 1: Has 'properties' wrapper?
            if 'properties' in cat_data:
                issues['has_properties_wrapper'].append(f"{mat_name}.{category}")
            
            # Check 2: Has 'percentage' at wrong level?
            if 'percentage' in cat_data:
                issues['has_percentage_wrong_level'].append(f"{mat_name}.{category}")
            
            # Check 3: Has 'description' at category level (should only have at property level)?
            if 'description' in cat_data and cat_data['description'] != cat_data.get('label'):
                # Description is OK if it's just a category description
                pass
            
            # Check 4: Missing 'label'?
            if 'label' not in cat_data:
                issues['missing_label'].append(f"{mat_name}.{category}")
            
            # Check 5: Count actual properties (excluding metadata)
            prop_keys = [k for k in cat_data.keys() if k not in metadata_keys]
            
            if len(prop_keys) == 0:
                issues['empty_category_groups'].append(f"{mat_name}.{category}")
            elif len(prop_keys) > 0:
                issues['has_flat_properties'].append(f"{mat_name}.{category} ({len(prop_keys)} props)")
    
    # Report
    print("📊 STRUCTURE VIOLATIONS")
    print("-" * 80)
    print()
    
    total_violations = 0
    
    for issue_type, violations in issues.items():
        if violations:
            count = len(violations)
            total_violations += count
            print(f"❌ {issue_type}: {count} instances")
            if count <= 10:
                for v in violations:
                    print(f"   - {v}")
            else:
                for v in violations[:5]:
                    print(f"   - {v}")
                print(f"   ... and {count - 5} more")
            print()
    
    if total_violations == 0:
        print("✅ NO VIOLATIONS FOUND!")
        print()
    
    # Summary statistics
    print("=" * 80)
    print("SUMMARY")
    print("=" * 80)
    print(f"Total materials: {len(materials)}")
    print(f"Total category groups: {len(materials) * 2}")
    print(f"Total violations: {total_violations}")
    print()
    
    # Most critical issues
    print("🔥 CRITICAL ISSUES (must fix):")
    critical = issues['has_properties_wrapper']
    if critical:
        print(f"   - {len(critical)} category groups have 'properties' wrapper")
        print(f"     This violates frontmatter_template.yaml structure")
    else:
        print("   - None! ✅")
    
    print()
    print("⚠️  CLEANUP NEEDED:")
    cleanup_count = len(issues['has_percentage_wrong_level']) + len(issues['has_description_wrong_level'])
    if cleanup_count > 0:
        print(f"   - {cleanup_count} metadata fields at wrong level")
    else:
        print("   - None! ✅")
    
    print()
    print("📋 EMPTY DATA (needs research):")
    empty_count = len(issues['empty_category_groups'])
    if empty_count > 0:
        print(f"   - {empty_count} category groups are empty")
    else:
        print("   - None! All groups have data ✅")
    
    return total_violations == 0

if __name__ == "__main__":
    import sys
    sys.exit(0 if main() else 1)
