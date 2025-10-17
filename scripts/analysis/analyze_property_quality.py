#!/usr/bin/env python3
"""
Detailed analysis of properties with data quality issues.
"""

import yaml
from pathlib import Path
from collections import defaultdict, Counter

ROOT_DIR = Path(__file__).resolve().parents[2]
FRONTMATTER_DIR = ROOT_DIR / "content" / "components" / "frontmatter"

# Properties identified with issues
PROBLEMATIC_PROPERTIES = [
    'chemicalStability',
    'crystallineStructure',
    'hardness',
    'laserAbsorption',
    'oxidationResistance',
    'thermalDiffusivity',
    'thermalExpansion',
    'youngsModulus'
]


def analyze_property(prop_name):
    """Detailed analysis of a specific property."""
    
    data_by_category = defaultdict(lambda: {
        'units': Counter(),
        'values': [],
        'examples': []
    })
    
    for fm_file in FRONTMATTER_DIR.glob('*.yaml'):
        with open(fm_file) as f:
            fm = yaml.safe_load(f)
        
        category = fm.get('category', 'unknown')
        material = fm.get('material', fm_file.stem)
        
        for cat_name, cat_data in fm.get('materialProperties', {}).items():
            if 'properties' not in cat_data:
                continue
            
            if prop_name in cat_data['properties']:
                prop_data = cat_data['properties'][prop_name]
                
                if isinstance(prop_data, dict):
                    unit = prop_data.get('unit')
                    value = prop_data.get('value')
                    
                    data_by_category[category]['units'][unit] += 1
                    
                    if value is not None:
                        data_by_category[category]['values'].append(value)
                    
                    # Store examples
                    if len(data_by_category[category]['examples']) < 3:
                        data_by_category[category]['examples'].append({
                            'material': material,
                            'value': value,
                            'unit': unit,
                            'source': prop_data.get('source', 'N/A')[:60]
                        })
    
    return data_by_category


def main():
    print("=" * 80)
    print("DETAILED PROPERTY DATA QUALITY ANALYSIS")
    print("=" * 80)
    print()
    
    for prop_name in PROBLEMATIC_PROPERTIES:
        print(f"\n{'=' * 80}")
        print(f"PROPERTY: {prop_name}")
        print(f"{'=' * 80}\n")
        
        data = analyze_property(prop_name)
        
        # Overall stats
        total_files = sum(len(d['values']) for d in data.values())
        all_units = Counter()
        for d in data.values():
            all_units.update(d['units'])
        
        print(f"Total files: {total_files}")
        print(f"Unit variations: {len(all_units)}")
        print(f"Units used: {dict(all_units)}")
        print()
        
        # By category
        for category in sorted(data.keys()):
            cat_data = data[category]
            print(f"{category.upper()}:")
            print(f"  Units: {dict(cat_data['units'])}")
            
            if cat_data['values']:
                try:
                    numeric_values = [float(v) for v in cat_data['values'] if v is not None]
                    if numeric_values:
                        print(f"  Value range: {min(numeric_values):.3f} - {max(numeric_values):.3f}")
                except:
                    print(f"  Values: (non-numeric)")
            
            print(f"  Examples:")
            for ex in cat_data['examples']:
                print(f"    {ex['material']}: {ex['value']} {ex['unit']}")
            print()
        
        # Recommendations
        print("RECOMMENDATIONS:")
        
        if prop_name == 'chemicalStability':
            print("  ⚠️  SEVERE: 13 different units - qualitative vs quantitative mix")
            print("  📋 Action: Standardize to rating scale (1-10) OR remove if too inconsistent")
            print("  🔍 Consider: Is this property well-defined enough for laser cleaning?")
        
        elif prop_name == 'crystallineStructure':
            print("  ⚠️  MODERATE: Qualitative property with mixed formats")
            print("  📋 Action: Standardize to 'crystal system' OR remove (non-numeric)")
            print("  🔍 Note: Already flagged for removal")
        
        elif prop_name == 'hardness':
            print("  ⚠️  MODERATE: 13 different units - different hardness scales")
            print("  📋 Action: Keep but note that units vary by material type")
            print("  ✅ This is EXPECTED - Mohs (minerals), Vickers (metals), Shore (plastics)")
        
        elif prop_name == 'laserAbsorption':
            print("  ✅ MINOR: 5 units but 114/122 use '%' (93%)")
            print("  📋 Action: Convert the 8 outliers to '%' format")
            print("  🔍 Low priority - mostly consistent")
        
        elif prop_name == 'oxidationResistance':
            print("  ⚠️  MODERATE: 6 units - °C vs qualitative scales")
            print("  📋 Action: Standardize to °C for consistency")
            print("  🔍 Qualitative values (5 files) should be researched/converted")
        
        elif prop_name == 'thermalDiffusivity':
            print("  ✅ MINOR: Only 2 units (mm²/s vs m²/s)")
            print("  📋 Action: Convert 5 m²/s values to mm²/s")
            print("  🔍 Simple unit conversion fix")
        
        elif prop_name == 'thermalExpansion':
            print("  ⚠️  MODERATE: 11 different unit formats")
            print("  📋 Action: Standardize to single format: 10⁻⁶/K")
            print("  🔍 All represent same quantity, just formatting differences")
        
        elif prop_name == 'youngsModulus':
            print("  ✅ MINOR: GPa vs MPa (easy conversion)")
            print("  📋 Action: Convert 16 MPa values to GPa")
            print("  🔍 Note: Some materials use MPa for very flexible materials")
        
        print()


if __name__ == '__main__':
    main()
