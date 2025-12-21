#!/usr/bin/env python3
"""
Analyze Invalid Material References with Fuzzy Matching

Identifies materials referenced in Contaminants.yaml and DomainAssociations.yaml
that don't exist in Materials.yaml, using fuzzy matching to suggest corrections.
"""

import sys
from pathlib import Path
from difflib import get_close_matches

# Add project root to path
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from shared.utils.yaml_utils import load_yaml

# Known exceptions (category names, generic terms, equipment)
KNOWN_EXCEPTIONS = {
    'ALL',  # Special value
    # Category names
    'Plastics', 'Metals', 'Woods', 'Stones', 'Ceramics', 'Composites',
    'Glass', 'Wood', 'Metal',  # Singular category names
    'Painted Metal', 'Thin Sheet Metal', 'Galvanized Metal',
    'Porous Stone', 'Soft Stone', 'Hard Stone',
    'Synthetic Materials', 'Natural Materials',
    'Thin Plastics', 'Soft Materials', 'Porous Surfaces',
    'Soft Substrates', 'Delicate Substrates', 'Flexible Substrates',
    # Abbreviations
    'HSS', 'PCB', 'ABS', 'PVC',
    # Generic terms
    'Tile', 'Drywall', 'Teflon', 'Cardboard', 'Paper', 'Asphalt', 'Grout',
    'Carbide', 'Quartz',  # Generic material terms
    # Equipment/non-materials
    'Boilers', 'Machinery', 'Transformer Housings', 'Turbine Blades',
    'Electronics', 'Optical Components', 'Steel Pipes', 'Silicon Wafers',
    # Application contexts
    'Food Areas', 'Heated Surfaces', 'Unsealed Areas',
    'Uncontrolled Environments',
    # Composite terms
    'Plastics (ABS)', 'Porous Wood',
    # Material variants/coatings
    'Chrome-Plated Steel', 'Galvanized Steel', 'Nickel-Plated Surfaces',
    'Zinc-Coated Metal', 'Zinc Alloy', 'Wrought Iron', 'Copper-Beryllium Alloy',
    'Carbon Steel',
    # Plastic types
    'PET', 'PTFE',
}


def main():
    print("=" * 80)
    print("INVALID MATERIAL REFERENCE ANALYSIS (WITH FUZZY MATCHING)")
    print("=" * 80)
    
    # Load data
    materials_path = PROJECT_ROOT / 'data' / 'materials' / 'Materials.yaml'
    contaminants_path = PROJECT_ROOT / 'data' / 'contaminants' / 'Contaminants.yaml'
    associations_path = PROJECT_ROOT / 'data' / 'associations' / 'DomainAssociations.yaml'
    
    materials_data = load_yaml(materials_path)
    contaminants_data = load_yaml(contaminants_path)
    associations_data = load_yaml(associations_path)
    
    # Get valid material names
    material_full_slugs = set(materials_data['materials'].keys())
    material_base_slugs = {m.replace('-laser-cleaning', '') for m in material_full_slugs}
    material_display_names = {
        ' '.join(word.capitalize() for word in slug.split('-'))
        for slug in material_base_slugs
    }
    
    print(f"\n📊 Materials.yaml: {len(material_full_slugs)} materials")
    
    # Analyze Contaminants.yaml
    print(f"\n🔍 Analyzing Contaminants.yaml (with fuzzy matching)...")
    invalid_contam = {}
    
    for pattern_id, pattern in contaminants_data['contamination_patterns'].items():
        if 'valid_materials' in pattern:
            for mat in pattern['valid_materials']:
                if mat not in material_display_names and mat not in KNOWN_EXCEPTIONS:
                    matches = get_close_matches(mat, material_display_names, n=1, cutoff=0.6)
                    if mat not in invalid_contam:
                        invalid_contam[mat] = {'patterns': [], 'fuzzy_match': matches[0] if matches else None}
                    invalid_contam[mat]['patterns'].append(pattern_id)
    
    truly_invalid = {k: v for k, v in invalid_contam.items() if not v['fuzzy_match']}
    fuzzy_fixable = {k: v for k, v in invalid_contam.items() if v['fuzzy_match']}
    
    print(f"   ✅ Found {len(fuzzy_fixable)} references with fuzzy matches")
    print(f"   ❌ Found {len(truly_invalid)} truly invalid references")
    
    if fuzzy_fixable:
        print(f"\n   🔧 FUZZY MATCH FIXES:")
        for mat in sorted(fuzzy_fixable.keys()):
            fuzzy = fuzzy_fixable[mat]['fuzzy_match']
            count = len(fuzzy_fixable[mat]['patterns'])
            print(f"      • '{mat}' → '{fuzzy}' ({count} patterns)")
    
    if truly_invalid:
        print(f"\n   ❌ NO MATCH:")
        for mat in sorted(truly_invalid.keys()):
            count = len(truly_invalid[mat]['patterns'])
            print(f"      • '{mat}' ({count} patterns)")
    
    # Analyze DomainAssociations.yaml
    print(f"\n🔍 Analyzing DomainAssociations.yaml (with fuzzy matching)...")
    invalid_assoc = {}
    
    for assoc in associations_data['associations']:
        mat_id = assoc.get('material_id', '')
        if mat_id and mat_id not in material_base_slugs:
            matches = get_close_matches(mat_id, material_base_slugs, n=1, cutoff=0.6)
            if mat_id not in invalid_assoc:
                invalid_assoc[mat_id] = {'count': 0, 'fuzzy_match': matches[0] if matches else None}
            invalid_assoc[mat_id]['count'] += 1
    
    assoc_truly_invalid = {k: v for k, v in invalid_assoc.items() if not v['fuzzy_match']}
    assoc_fuzzy_fixable = {k: v for k, v in invalid_assoc.items() if v['fuzzy_match']}
    
    print(f"   ✅ Found {len(assoc_fuzzy_fixable)} material_ids with fuzzy matches")
    print(f"   ❌ Found {len(assoc_truly_invalid)} truly invalid material_ids")
    
    if assoc_fuzzy_fixable:
        print(f"\n   🔧 FUZZY MATCH FIXES:")
        for mat_id in sorted(assoc_fuzzy_fixable.keys()):
            fuzzy = assoc_fuzzy_fixable[mat_id]['fuzzy_match']
            count = assoc_fuzzy_fixable[mat_id]['count']
            print(f"      • '{mat_id}' → '{fuzzy}' ({count} associations)")
    
    if assoc_truly_invalid:
        print(f"\n   ❌ NO MATCH:")
        for mat_id in sorted(assoc_truly_invalid.keys()):
            count = assoc_truly_invalid[mat_id]['count']
            print(f"      • '{mat_id}' ({count} associations)")
    
    # Summary
    total_fuzzy = len(fuzzy_fixable) + len(assoc_fuzzy_fixable)
    total_invalid = len(truly_invalid) + len(assoc_truly_invalid)
    
    print(f"\n" + "=" * 80)
    print(f"SUMMARY")
    print(f"=" * 80)
    print(f"🔧 TOTAL FIXABLE: {total_fuzzy}")
    print(f"❌ TOTAL TRULY INVALID: {total_invalid}")
    print("=" * 80)
    
    return 0 if (len(invalid_contam) + len(invalid_assoc)) == 0 else 1


if __name__ == '__main__':
    sys.exit(main())
