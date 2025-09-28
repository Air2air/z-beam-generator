#!/usr/bin/env python3
"""
Detailed Materials.yaml Issues Analysis
Focuses on the specific data quality issues found in the initial analysis.
"""

import yaml
from collections import defaultdict

def load_materials(file_path: str):
    """Load the Materials.yaml file."""
    with open(file_path, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)

def analyze_duplicate_indices(data):
    """Detailed analysis of duplicate index issues."""
    print("=" * 60)
    print("DUPLICATE INDEX ANALYSIS")
    print("=" * 60)
    
    index_data = data.get('material_index', {})
    
    # Group by category and index
    category_indices = defaultdict(lambda: defaultdict(list))
    
    for material_name, material_info in index_data.items():
        category = material_info.get('category', 'UNKNOWN')
        index = material_info.get('index', 'UNKNOWN')
        category_indices[category][index].append(material_name)
    
    # Find and report duplicates
    duplicates_found = False
    for category, indices in category_indices.items():
        category_duplicates = []
        for index, materials in indices.items():
            if len(materials) > 1:
                category_duplicates.append((index, materials))
                duplicates_found = True
        
        if category_duplicates:
            print(f"\n{category.upper()} category:")
            for index, materials in category_duplicates:
                print(f"  Index {index} used by: {', '.join(materials)}")
                print(f"    IMPACT: These materials will conflict in the indexing system")
    
    if not duplicates_found:
        print("No duplicate indices found.")
    
    return duplicates_found

def analyze_field_completeness(data):
    """Analyze field completeness and identify patterns."""
    print("\n" + "=" * 60)
    print("FIELD COMPLETENESS ANALYSIS")
    print("=" * 60)
    
    materials_data = data.get('materials', {})
    
    # Track field presence by category
    field_by_category = defaultdict(lambda: defaultdict(int))
    category_totals = defaultdict(int)
    missing_fields_details = defaultdict(list)
    
    for category, category_data in materials_data.items():
        if 'items' not in category_data:
            continue
            
        materials_list = category_data['items']
        category_totals[category] = len(materials_list)
        
        # Key fields to analyze
        important_fields = {
            'formula': 'Chemical formula',
            'symbol': 'Chemical symbol', 
            'melting_point': 'Melting point',
            'hardness': 'Hardness rating',
            'tensileStrength': 'Tensile strength',
            'thermalConductivity': 'Thermal conductivity',
            'thermalExpansion': 'Thermal expansion',
            'yield_strength': 'Yield strength',
            'youngsModulus': 'Young\'s modulus',
            'density': 'Material density'
        }
        
        for material in materials_list:
            material_name = material.get('name', 'UNNAMED')
            
            for field, description in important_fields.items():
                if field in material:
                    field_by_category[category][field] += 1
                else:
                    missing_fields_details[field].append(f"{category}:{material_name}")
    
    # Report field completeness by category
    print("\nField completeness by category:")
    for field, description in important_fields.items():
        print(f"\n{field} ({description}):")
        total_present = 0
        total_materials = 0
        
        for category in sorted(category_totals.keys()):
            present = field_by_category[category][field]
            total = category_totals[category]
            percentage = (present / total * 100) if total > 0 else 0
            
            print(f"  {category}: {present}/{total} ({percentage:.1f}%)")
            total_present += present
            total_materials += total
        
        overall_percentage = (total_present / total_materials * 100) if total_materials > 0 else 0
        print(f"  OVERALL: {total_present}/{total_materials} ({overall_percentage:.1f}%)")
        
        if overall_percentage < 80:  # Report if less than 80% complete
            print(f"  ⚠️  LOW COMPLETENESS - Missing from {len(missing_fields_details[field])} materials")

def analyze_machine_settings_completeness(data):
    """Analyze machine settings field completeness."""
    print("\n" + "=" * 60)
    print("MACHINE SETTINGS COMPLETENESS")
    print("=" * 60)
    
    materials_data = data.get('materials', {})
    
    required_machine_fields = {
        'ablationThreshold': 'Ablation threshold',
        'fluenceThreshold': 'Fluence threshold', 
        'laserType': 'Laser type',
        'powerRange': 'Power range',
        'processingSpeed': 'Processing speed',
        'pulseDuration': 'Pulse duration',
        'repetitionRate': 'Repetition rate',
        'spotSize': 'Spot size',
        'surfaceRoughnessChange': 'Surface roughness change',
        'thermalDamageThreshold': 'Thermal damage threshold',
        'wavelengthOptimal': 'Optimal wavelength'
    }
    
    machine_settings_issues = defaultdict(list)
    total_materials = 0
    materials_with_complete_settings = 0
    
    for category, category_data in materials_data.items():
        if 'items' not in category_data:
            continue
            
        for material in category_data['items']:
            material_name = material.get('name', 'UNNAMED')
            total_materials += 1
            
            if 'machineSettings' not in material:
                machine_settings_issues['missing_machineSettings'].append(f"{category}:{material_name}")
                continue
            
            machine_settings = material['machineSettings']
            missing_fields = []
            
            for field in required_machine_fields:
                if field not in machine_settings:
                    missing_fields.append(field)
            
            if missing_fields:
                machine_settings_issues['incomplete_machineSettings'].append(
                    f"{category}:{material_name} (missing: {', '.join(missing_fields)})"
                )
            else:
                materials_with_complete_settings += 1
    
    # Report findings
    print(f"Total materials: {total_materials}")
    print(f"Materials with complete machine settings: {materials_with_complete_settings}")
    print(f"Completeness: {(materials_with_complete_settings/total_materials*100):.1f}%")
    
    if machine_settings_issues:
        print("\nIssues found:")
        for issue_type, materials in machine_settings_issues.items():
            print(f"\n{issue_type.replace('_', ' ').title()}: {len(materials)} materials")
            if len(materials) <= 10:
                for material in materials:
                    print(f"  - {material}")
            else:
                print(f"  - First 10 examples:")
                for material in materials[:10]:
                    print(f"    - {material}")
                print(f"    ... and {len(materials) - 10} more")

def check_data_quality_patterns(data):
    """Look for patterns in data quality issues."""
    print("\n" + "=" * 60)
    print("DATA QUALITY PATTERNS")
    print("=" * 60)
    
    materials_data = data.get('materials', {})
    
    # Check for patterns in missing data
    author_completeness = defaultdict(lambda: {'total': 0, 'complete_formula': 0, 'complete_symbol': 0})
    category_completeness = defaultdict(lambda: {'total': 0, 'missing_physical_props': 0})
    
    for category, category_data in materials_data.items():
        if 'items' not in category_data:
            continue
            
        for material in category_data['items']:
            author_id = material.get('author_id', 'unknown')
            author_completeness[author_id]['total'] += 1
            
            if 'formula' in material:
                author_completeness[author_id]['complete_formula'] += 1
            if 'symbol' in material:
                author_completeness[author_id]['complete_symbol'] += 1
            
            # Check physical properties completeness
            physical_props = ['density', 'hardness', 'thermalConductivity', 'tensileStrength']
            missing_props = sum(1 for prop in physical_props if prop not in material)
            
            category_completeness[category]['total'] += 1
            if missing_props > 2:  # More than 2 missing physical properties
                category_completeness[category]['missing_physical_props'] += 1
    
    print("Data completeness by author:")
    for author_id, stats in author_completeness.items():
        if stats['total'] > 0:
            formula_pct = (stats['complete_formula'] / stats['total']) * 100
            symbol_pct = (stats['complete_symbol'] / stats['total']) * 100
            print(f"  Author {author_id}: {stats['total']} materials")
            print(f"    Formula: {formula_pct:.1f}% | Symbol: {symbol_pct:.1f}%")
    
    print("\nCategories with significant missing physical properties:")
    for category, stats in category_completeness.items():
        if stats['total'] > 0:
            missing_pct = (stats['missing_physical_props'] / stats['total']) * 100
            if missing_pct > 20:  # More than 20% have significant missing props
                print(f"  {category}: {missing_pct:.1f}% materials missing >2 physical properties")

def main():
    """Main analysis function."""
    file_path = "/Users/todddunning/Desktop/Z-Beam/z-beam-generator/data/Materials.yaml"
    
    print("DETAILED MATERIALS.YAML ISSUES ANALYSIS")
    
    # Load data
    data = load_materials(file_path)
    
    # Run specific analyses
    analyze_duplicate_indices(data)
    analyze_field_completeness(data)
    analyze_machine_settings_completeness(data)
    check_data_quality_patterns(data)
    
    print("\n" + "=" * 60)
    print("ANALYSIS COMPLETE")
    print("=" * 60)

if __name__ == "__main__":
    main()