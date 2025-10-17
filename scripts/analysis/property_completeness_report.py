#!/usr/bin/env python3
"""
Property Data Completeness Analysis

Analyzes what percentage of properties have missing data across:
1. Categories.yaml - Category range completeness
2. materials.yaml - Material value completeness
"""

import yaml
from pathlib import Path
from collections import defaultdict

PROJECT_ROOT = Path(__file__).parent.parent.parent

def analyze_completeness():
    """Analyze property data completeness"""
    
    # Load Categories.yaml
    with open(PROJECT_ROOT / 'data' / 'Categories.yaml') as f:
        categories = yaml.safe_load(f)
    
    # Load materials.yaml
    with open(PROJECT_ROOT / 'data' / 'materials.yaml') as f:
        materials = yaml.safe_load(f)
    
    print('='*80)
    print('PROPERTY DATA COMPLETENESS ANALYSIS')
    print('='*80)
    
    # 1. Category Ranges Analysis
    print('\n📊 CATEGORY RANGES (Categories.yaml)')
    print('-'*80)
    
    total_categories = len(categories['categories'])
    properties_by_category = {}
    missing_ranges_by_category = defaultdict(list)
    
    for cat_name, cat_data in categories['categories'].items():
        cat_ranges = cat_data.get('category_ranges', {})
        properties_by_category[cat_name] = set(cat_ranges.keys())
        
        for prop_name, prop_data in cat_ranges.items():
            if not isinstance(prop_data, dict):
                continue
                
            if prop_name == 'thermalDestruction':
                # Nested structure
                point_data = prop_data.get('point', {})
                if isinstance(point_data, dict):
                    if point_data.get('min') is None or point_data.get('max') is None:
                        missing_ranges_by_category[cat_name].append(f'{prop_name}.point')
            else:
                # Flat structure
                if prop_data.get('min') is None or prop_data.get('max') is None:
                    missing_ranges_by_category[cat_name].append(prop_name)
    
    # Get all unique properties across all categories
    all_properties = set()
    for props in properties_by_category.values():
        all_properties.update(props)
    
    total_unique_properties = len(all_properties)
    print(f'Total unique properties across categories: {total_unique_properties}')
    print(f'Total categories: {total_categories}')
    
    # Calculate coverage per category
    print(f'\nCategory Range Coverage:')
    total_props_all_cats = 0
    total_complete_all_cats = 0
    
    for cat_name in sorted(categories['categories'].keys()):
        props = properties_by_category.get(cat_name, set())
        missing = missing_ranges_by_category.get(cat_name, [])
        complete = len(props) - len(missing)
        total = len(props)
        total_props_all_cats += total
        total_complete_all_cats += complete
        pct = (complete/total*100) if total > 0 else 0
        status = '✅' if pct == 100 else '⚠️' if pct >= 90 else '❌'
        print(f'  {status} {cat_name:15s}: {complete:2d}/{total:2d} properties ({pct:5.1f}% complete)')
        if missing:
            for prop in missing[:5]:  # Show first 5
                print(f'       Missing: {prop}')
    
    cat_range_pct = (total_complete_all_cats/total_props_all_cats*100) if total_props_all_cats > 0 else 0
    print(f'\n  Overall Category Ranges: {total_complete_all_cats}/{total_props_all_cats} ({cat_range_pct:.1f}% complete)')
    
    # 2. Material Values Analysis
    print(f'\n📊 MATERIAL VALUES (materials.yaml)')
    print('-'*80)
    
    total_materials = len(materials['materials'])
    materials_by_category = defaultdict(list)
    property_coverage = defaultdict(lambda: {'present': 0, 'missing': 0, 'materials_with': []})
    
    for mat_name, mat_data in materials['materials'].items():
        cat = mat_data.get('category', 'unknown')
        materials_by_category[cat].append(mat_name)
        
        props = mat_data.get('properties', {})
        
        # Track all properties this material should have
        expected_props = properties_by_category.get(cat, set())
        
        for expected_prop in expected_props:
            prop_data = props.get(expected_prop)
            
            if prop_data is None:
                # Property completely missing
                property_coverage[expected_prop]['missing'] += 1
            elif isinstance(prop_data, dict):
                # Check if it has a value
                if expected_prop == 'thermalDestruction':
                    # Nested structure
                    point_data = prop_data.get('point', {})
                    if isinstance(point_data, dict) and point_data.get('value') is not None:
                        property_coverage[expected_prop]['present'] += 1
                        property_coverage[expected_prop]['materials_with'].append(mat_name)
                    else:
                        property_coverage[expected_prop]['missing'] += 1
                else:
                    # Flat structure
                    if prop_data.get('value') is not None:
                        property_coverage[expected_prop]['present'] += 1
                        property_coverage[expected_prop]['materials_with'].append(mat_name)
                    else:
                        property_coverage[expected_prop]['missing'] += 1
            else:
                # Non-dict value (shouldn't happen but handle it)
                property_coverage[expected_prop]['present'] += 1
                property_coverage[expected_prop]['materials_with'].append(mat_name)
    
    print(f'Total materials: {total_materials}')
    print(f'\nMaterials per category:')
    for cat in sorted(materials_by_category.keys()):
        count = len(materials_by_category[cat])
        print(f'  • {cat:15s}: {count:3d} materials')
    
    print(f'\nProperty Coverage Across All Materials:')
    print(f'{"Property":30s} {"Present":>8s} {"Missing":>8s} {"Coverage":>10s}')
    print('-'*60)
    
    sorted_props = sorted(property_coverage.items(), 
                         key=lambda x: x[1]['present']/(x[1]['present']+x[1]['missing']) if (x[1]['present']+x[1]['missing']) > 0 else 0, 
                         reverse=True)
    
    for prop_name, counts in sorted_props:
        present = counts['present']
        missing = counts['missing']
        total = present + missing
        pct = (present/total*100) if total > 0 else 0
        status = '✅' if pct >= 90 else '⚠️' if pct >= 70 else '❌'
        print(f'{status} {prop_name:28s} {present:8d} {missing:8d} {pct:9.1f}%')
    
    # 3. Overall Statistics
    print(f'\n📊 OVERALL STATISTICS')
    print('-'*80)
    
    total_present = sum(c['present'] for c in property_coverage.values())
    total_missing = sum(c['missing'] for c in property_coverage.values())
    total_checked = total_present + total_missing
    
    overall_pct = (total_present / total_checked * 100) if total_checked > 0 else 0
    
    print(f'Total materials: {total_materials:,}')
    print(f'Total unique properties: {total_unique_properties}')
    print(f'Total property slots checked: {total_checked:,}')
    print(f'Properties with values: {total_present:,}')
    print(f'Properties missing values: {total_missing:,}')
    print(f'\n{"Overall Material Data Completeness:":<40s} {overall_pct:>6.1f}%')
    print(f'{"Category Range Completeness:":<40s} {cat_range_pct:>6.1f}%')
    
    # Combined score
    combined_pct = (overall_pct + cat_range_pct) / 2
    print(f'\n{"COMBINED DATA COMPLETENESS:":<40s} {combined_pct:>6.1f}%')
    
    if total_missing > 0:
        print(f'\n⚠️  {total_missing:,} property values need AI research')
        print(f'⚠️  {total_props_all_cats - total_complete_all_cats} category ranges need research')
    else:
        print(f'\n✅ All property values complete!')
    
    # 4. Most Missing Properties (Need Research Priority)
    print(f'\n📋 PROPERTIES NEEDING MOST RESEARCH (Top 10)')
    print('-'*80)
    
    sorted_by_missing = sorted(property_coverage.items(), 
                               key=lambda x: x[1]['missing'], 
                               reverse=True)
    
    print(f'{"Property":30s} {"Missing":>8s} {"Materials Affected":>18s}')
    print('-'*60)
    for prop_name, counts in sorted_by_missing[:10]:
        missing = counts['missing']
        if missing > 0:
            print(f'{prop_name:30s} {missing:8d} {missing:18d}')
    
    print('='*80)

if __name__ == '__main__':
    analyze_completeness()
