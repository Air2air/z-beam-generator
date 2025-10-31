#!/usr/bin/env python3
"""
Zero Null Value Validator

Comprehensive null value detection across the entire system per ZERO_NULL_POLICY.md.
Identifies all null values in Categories.yaml, materials.yaml, and frontmatter files.

Usage:
    python3 scripts/validation/validate_zero_nulls.py --audit
    python3 scripts/validation/validate_zero_nulls.py --categories
    python3 scripts/validation/validate_zero_nulls.py --materials
    python3 scripts/validation/validate_zero_nulls.py --frontmatter
"""

import yaml
import argparse
from pathlib import Path
from typing import Dict, List, Any, Tuple
from collections import defaultdict


def load_yaml(file_path: Path) -> Dict:
    """Load YAML file safely"""
    with open(file_path, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)


def find_nulls_recursive(data: Any, path: str = "") -> List[str]:
    """Recursively find all null values in nested data structure"""
    nulls = []
    
    if isinstance(data, dict):
        for key, value in data.items():
            current_path = f"{path}.{key}" if path else key
            if value is None:
                nulls.append(current_path)
            elif isinstance(value, (dict, list)):
                nulls.extend(find_nulls_recursive(value, current_path))
    
    elif isinstance(data, list):
        for idx, item in enumerate(data):
            current_path = f"{path}[{idx}]"
            if item is None:
                nulls.append(current_path)
            elif isinstance(item, (dict, list)):
                nulls.extend(find_nulls_recursive(item, current_path))
    
    return nulls


def validate_categories_yaml() -> Tuple[List[str], Dict[str, List[str]]]:
    """Validate Categories.yaml for null values"""
    categories_path = Path('data/Categories.yaml')
    if not categories_path.exists():
        return [f"ERROR: {categories_path} not found"], {}
    
    data = load_yaml(categories_path)
    nulls_found = []
    missing_ranges = defaultdict(list)
    
    # Check category ranges for nulls
    for category_name, category_data in data.get('categories', {}).items():
        category_ranges = category_data.get('category_ranges', {})
        
        for prop_name, prop_data in category_ranges.items():
            if not isinstance(prop_data, dict):
                continue
                
            # Check for null min
            if 'min' in prop_data and prop_data['min'] is None:
                null_path = f"categories.{category_name}.category_ranges.{prop_name}.min"
                nulls_found.append(null_path)
                missing_ranges[category_name].append(f"{prop_name}.min")
            
            # Check for null max
            if 'max' in prop_data and prop_data['max'] is None:
                null_path = f"categories.{category_name}.category_ranges.{prop_name}.max"
                nulls_found.append(null_path)
                missing_ranges[category_name].append(f"{prop_name}.max")
    
    return nulls_found, dict(missing_ranges)


def validate_materials_yaml() -> Tuple[List[str], Dict[str, List[str]]]:
    """Validate materials.yaml for null values"""
    materials_path = Path('data/materials.yaml')
    if not materials_path.exists():
        return [f"ERROR: {materials_path} not found"], {}
    
    data = load_yaml(materials_path)
    nulls_found = []
    missing_values = defaultdict(list)
    
    # Check material properties for nulls
    for material_name, material_data in data.get('materials', {}).items():
        properties = material_data.get('properties', {})
        
        for prop_name, prop_data in properties.items():
            if not isinstance(prop_data, dict):
                continue
            
            # Check for null value
            if 'value' in prop_data and prop_data['value'] is None:
                null_path = f"materials.{material_name}.properties.{prop_name}.value"
                nulls_found.append(null_path)
                missing_values[material_name].append(prop_name)
            
            # Materials.yaml should NEVER have min/max (that's in Categories.yaml)
            if 'min' in prop_data or 'max' in prop_data:
                null_path = f"materials.{material_name}.properties.{prop_name} has min/max (VIOLATION)"
                nulls_found.append(null_path)
    
    return nulls_found, dict(missing_values)


def validate_frontmatter_files() -> Tuple[List[str], Dict[str, int]]:
    """Validate all frontmatter files for null values"""
    frontmatter_dir = Path('frontmatter')
    if not frontmatter_dir.exists():
        return [f"ERROR: {frontmatter_dir} not found"], {}
    
    nulls_by_file = {}
    all_nulls = []
    
    for yaml_file in sorted(frontmatter_dir.glob('*.yaml')):
        data = load_yaml(yaml_file)
        nulls = find_nulls_recursive(data)
        
        if nulls:
            nulls_by_file[yaml_file.name] = len(nulls)
            for null_path in nulls:
                all_nulls.append(f"{yaml_file.name}: {null_path}")
    
    return all_nulls, nulls_by_file


def print_report(title: str, nulls: List[str], details: Dict = None):
    """Print formatted validation report"""
    print(f"\n{'=' * 80}")
    print(f"{title}")
    print(f"{'=' * 80}")
    
    if not nulls:
        print("✅ NO NULL VALUES FOUND")
        return True
    
    print(f"❌ FOUND {len(nulls)} NULL VALUES\n")
    
    # Print first 50 nulls
    for null in nulls[:50]:
        print(f"  • {null}")
    
    if len(nulls) > 50:
        print(f"\n  ... and {len(nulls) - 50} more")
    
    # Print details if provided
    if details:
        print(f"\n{'-' * 80}")
        print("SUMMARY BY CATEGORY/MATERIAL:")
        for key, value in sorted(details.items()):
            if isinstance(value, list):
                print(f"  • {key}: {len(value)} nulls")
            else:
                print(f"  • {key}: {value} nulls")
    
    return False


def main():
    parser = argparse.ArgumentParser(
        description='Validate zero null values across the system'
    )
    parser.add_argument(
        '--audit',
        action='store_true',
        help='Run full audit of all data sources'
    )
    parser.add_argument(
        '--categories',
        action='store_true',
        help='Check Categories.yaml only'
    )
    parser.add_argument(
        '--materials',
        action='store_true',
        help='Check materials.yaml only'
    )
    parser.add_argument(
        '--frontmatter',
        action='store_true',
        help='Check frontmatter files only'
    )
    
    args = parser.parse_args()
    
    # Default to audit if no specific check requested
    if not any([args.audit, args.categories, args.materials, args.frontmatter]):
        args.audit = True
    
    all_passed = True
    
    # Validate Categories.yaml
    if args.audit or args.categories:
        cat_nulls, cat_details = validate_categories_yaml()
        passed = print_report("CATEGORIES.YAML VALIDATION", cat_nulls, cat_details)
        all_passed = all_passed and passed
    
    # Validate materials.yaml
    if args.audit or args.materials:
        mat_nulls, mat_details = validate_materials_yaml()
        passed = print_report("MATERIALS.YAML VALIDATION", mat_nulls, mat_details)
        all_passed = all_passed and passed
    
    # Validate frontmatter files
    if args.audit or args.frontmatter:
        front_nulls, front_details = validate_frontmatter_files()
        passed = print_report("FRONTMATTER FILES VALIDATION", front_nulls, front_details)
        all_passed = all_passed and passed
    
    # Final summary
    print(f"\n{'=' * 80}")
    if all_passed:
        print("✅ ZERO NULL VALIDATION PASSED - System is complete")
    else:
        print("❌ ZERO NULL VALIDATION FAILED - Null values detected")
        print("\nRECOMMENDED ACTIONS:")
        print("1. Add missing category ranges to data/Categories.yaml")
        print("2. Research missing material property values")
        print("3. Regenerate frontmatter files with complete data")
        print("\nSee docs/ZERO_NULL_POLICY.md for detailed guidance")
    print(f"{'=' * 80}\n")
    
    return 0 if all_passed else 1


if __name__ == '__main__':
    exit(main())
