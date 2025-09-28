#!/usr/bin/env python3
"""
Materials.yaml Data Completeness Analysis
Analyzes the Materials.yaml file for data completeness and structural integrity.
"""

import yaml
import sys
from collections import defaultdict, Counter
from typing import Dict, List, Set, Any

def load_materials(file_path: str) -> Dict[str, Any]:
    """Load the Materials.yaml file."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)
    except Exception as e:
        print(f"Error loading Materials.yaml: {e}")
        sys.exit(1)

def analyze_material_index(data: Dict[str, Any]) -> Dict[str, Any]:
    """Analyze the material_index section."""
    index_data = data.get('material_index', {})
    
    analysis = {
        'total_indexed_materials': len(index_data),
        'categories': Counter(),
        'subcategories': Counter(),
        'author_distribution': Counter(),
        'complexity_distribution': Counter(),
        'missing_fields': defaultdict(list),
        'duplicate_indices': defaultdict(list)
    }
    
    # Track index usage per category
    index_per_category = defaultdict(list)
    
    for material_name, material_info in index_data.items():
        # Count categories and subcategories
        category = material_info.get('category', 'MISSING')
        subcategory = material_info.get('subcategory', 'MISSING')
        author_id = material_info.get('author_id', 'MISSING')
        complexity = material_info.get('complexity', 'MISSING')
        index = material_info.get('index', 'MISSING')
        
        analysis['categories'][category] += 1
        analysis['subcategories'][subcategory] += 1
        analysis['author_distribution'][author_id] += 1
        analysis['complexity_distribution'][complexity] += 1
        
        # Check for missing required fields
        required_fields = ['category', 'subcategory', 'author_id', 'complexity', 'index']
        for field in required_fields:
            if field not in material_info:
                analysis['missing_fields'][field].append(material_name)
        
        # Track index duplicates within categories
        if category != 'MISSING' and index != 'MISSING':
            index_per_category[category].append((index, material_name))
    
    # Find duplicate indices within categories
    for category, indices in index_per_category.items():
        index_counts = defaultdict(list)
        for index, material_name in indices:
            index_counts[index].append(material_name)
        
        for index, materials in index_counts.items():
            if len(materials) > 1:
                analysis['duplicate_indices'][f"{category}:{index}"] = materials
    
    return analysis

def analyze_materials_section(data: Dict[str, Any]) -> Dict[str, Any]:
    """Analyze the materials section for completeness."""
    materials_data = data.get('materials', {})
    
    analysis = {
        'categories_with_materials': list(materials_data.keys()),
        'total_material_entries': 0,
        'materials_per_category': {},
        'missing_machine_settings': [],
        'missing_required_fields': defaultdict(list),
        'field_presence': defaultdict(int),
        'all_material_names': set()
    }
    
    # Required fields for each material entry
    required_fields = [
        'name', 'category', 'author_id', 'complexity', 'applications',
        'compatibility', 'industryTags', 'regulatoryStandards', 'machineSettings'
    ]
    
    # Common optional fields we want to track
    optional_fields = [
        'formula', 'symbol', 'density', 'melting_point', 'hardness',
        'thermalConductivity', 'thermalExpansion', 'tensileStrength',
        'yield_strength', 'youngsModulus', 'difficulty_score'
    ]
    
    for category, category_data in materials_data.items():
        if 'items' not in category_data:
            continue
            
        materials_list = category_data['items']
        analysis['materials_per_category'][category] = len(materials_list)
        analysis['total_material_entries'] += len(materials_list)
        
        for material in materials_list:
            material_name = material.get('name', 'UNNAMED')
            analysis['all_material_names'].add(material_name)
            
            # Check required fields
            for field in required_fields:
                if field in material:
                    analysis['field_presence'][field] += 1
                else:
                    analysis['missing_required_fields'][field].append(f"{category}:{material_name}")
            
            # Check optional fields
            for field in optional_fields:
                if field in material:
                    analysis['field_presence'][field] += 1
            
            # Check machine settings completeness
            if 'machineSettings' not in material:
                analysis['missing_machine_settings'].append(f"{category}:{material_name}")
            else:
                machine_settings = material['machineSettings']
                required_machine_fields = [
                    'ablationThreshold', 'fluenceThreshold', 'laserType',
                    'powerRange', 'processingSpeed', 'pulseDuration',
                    'repetitionRate', 'spotSize', 'surfaceRoughnessChange',
                    'thermalDamageThreshold', 'wavelengthOptimal'
                ]
                
                missing_machine_fields = []
                for field in required_machine_fields:
                    if field not in machine_settings:
                        missing_machine_fields.append(field)
                
                if missing_machine_fields:
                    analysis['missing_required_fields'][f'machineSettings_incomplete'].append(
                        f"{category}:{material_name} (missing: {', '.join(missing_machine_fields)})"
                    )
    
    return analysis

def check_index_material_consistency(data: Dict[str, Any]) -> Dict[str, Any]:
    """Check consistency between material_index and materials sections."""
    index_materials = set(data.get('material_index', {}).keys())
    
    # Extract all material names from materials section
    materials_section = data.get('materials', {})
    actual_materials = set()
    
    for category, category_data in materials_section.items():
        if 'items' in category_data:
            for material in category_data['items']:
                if 'name' in material:
                    actual_materials.add(material['name'])
    
    analysis = {
        'indexed_materials': len(index_materials),
        'actual_materials': len(actual_materials),
        'materials_in_index_not_in_data': index_materials - actual_materials,
        'materials_in_data_not_in_index': actual_materials - index_materials,
        'consistent': index_materials == actual_materials
    }
    
    return analysis

def main():
    """Main analysis function."""
    file_path = "/Users/todddunning/Desktop/Z-Beam/z-beam-generator/data/Materials.yaml"
    
    print("=" * 80)
    print("MATERIALS.YAML DATA COMPLETENESS ANALYSIS")
    print("=" * 80)
    
    # Load data
    data = load_materials(file_path)
    
    # Analyze material index
    print("\n1. MATERIAL INDEX ANALYSIS")
    print("-" * 40)
    index_analysis = analyze_material_index(data)
    
    print(f"Total indexed materials: {index_analysis['total_indexed_materials']}")
    print(f"Categories: {dict(index_analysis['categories'])}")
    print(f"Author distribution: {dict(index_analysis['author_distribution'])}")
    print(f"Complexity distribution: {dict(index_analysis['complexity_distribution'])}")
    
    if index_analysis['missing_fields']:
        print("\nMissing fields in material_index:")
        for field, materials in index_analysis['missing_fields'].items():
            print(f"  {field}: {len(materials)} materials")
            if materials:
                print(f"    Examples: {materials[:5]}")
    
    if index_analysis['duplicate_indices']:
        print("\nDuplicate indices found:")
        for index_key, materials in index_analysis['duplicate_indices'].items():
            print(f"  {index_key}: {materials}")
    
    # Analyze materials section
    print("\n2. MATERIALS SECTION ANALYSIS")
    print("-" * 40)
    materials_analysis = analyze_materials_section(data)
    
    print(f"Total material entries: {materials_analysis['total_material_entries']}")
    print(f"Categories with materials: {materials_analysis['categories_with_materials']}")
    print(f"Materials per category: {materials_analysis['materials_per_category']}")
    
    print("\nField presence statistics:")
    for field, count in sorted(materials_analysis['field_presence'].items()):
        percentage = (count / materials_analysis['total_material_entries']) * 100
        print(f"  {field}: {count}/{materials_analysis['total_material_entries']} ({percentage:.1f}%)")
    
    if materials_analysis['missing_required_fields']:
        print("\nMissing required fields:")
        for field, materials in materials_analysis['missing_required_fields'].items():
            print(f"  {field}: {len(materials)} materials")
            if len(materials) <= 10:
                for material in materials:
                    print(f"    - {material}")
            else:
                print(f"    - First 10: {materials[:10]}")
                print(f"    - ... and {len(materials) - 10} more")
    
    # Check consistency
    print("\n3. CONSISTENCY ANALYSIS")
    print("-" * 40)
    consistency_analysis = check_index_material_consistency(data)
    
    print(f"Materials in index: {consistency_analysis['indexed_materials']}")
    print(f"Materials in data: {consistency_analysis['actual_materials']}")
    print(f"Consistent: {consistency_analysis['consistent']}")
    
    if consistency_analysis['materials_in_index_not_in_data']:
        print("\nMaterials in index but not in data:")
        for material in sorted(consistency_analysis['materials_in_index_not_in_data']):
            print(f"  - {material}")
    
    if consistency_analysis['materials_in_data_not_in_index']:
        print("\nMaterials in data but not in index:")
        for material in sorted(consistency_analysis['materials_in_data_not_in_index']):
            print(f"  - {material}")
    
    # Check ranges
    print("\n4. RANGES ANALYSIS")
    print("-" * 40)
    
    if 'category_ranges' in data:
        category_ranges = data['category_ranges']
        print(f"Category ranges defined for: {list(category_ranges.keys())}")
        
        # Check if all material categories have ranges
        material_categories = set(materials_analysis['categories_with_materials'])
        range_categories = set(category_ranges.keys())
        
        missing_ranges = material_categories - range_categories
        extra_ranges = range_categories - material_categories
        
        if missing_ranges:
            print(f"Categories missing ranges: {missing_ranges}")
        if extra_ranges:
            print(f"Extra range categories: {extra_ranges}")
    
    if 'machineSettingsRanges' in data:
        machine_ranges = data['machineSettingsRanges']
        print(f"Machine settings ranges: {list(machine_ranges.keys())}")
    
    # Summary
    print("\n5. SUMMARY")
    print("-" * 40)
    
    issues = []
    
    if not consistency_analysis['consistent']:
        issues.append(f"Index-data inconsistency: {len(consistency_analysis['materials_in_index_not_in_data'])} orphaned index entries, {len(consistency_analysis['materials_in_data_not_in_index'])} unindexed materials")
    
    if index_analysis['duplicate_indices']:
        issues.append(f"Duplicate indices: {len(index_analysis['duplicate_indices'])} cases")
    
    if materials_analysis['missing_required_fields']:
        total_missing = sum(len(materials) for materials in materials_analysis['missing_required_fields'].values())
        issues.append(f"Missing required fields: {total_missing} field-material combinations")
    
    if issues:
        print("ISSUES FOUND:")
        for i, issue in enumerate(issues, 1):
            print(f"  {i}. {issue}")
        
        print(f"\nData completeness: NEEDS ATTENTION")
    else:
        print("No major issues found!")
        print("Data completeness: GOOD")
    
    print("\n" + "=" * 80)

if __name__ == "__main__":
    main()