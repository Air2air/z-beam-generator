#!/usr/bin/env python3
"""
Phase 2: Generic Term Expansion for Contamination Accuracy

Expands generic category terms (Metal, Plastics, Glass, etc.) to specific materials
based on contamination chemistry, material properties, and laser interaction characteristics.

Target: 59.8% → 85%+ accuracy by expanding 173 generic references

Usage:
    python3 scripts/tools/contamination_accuracy_phase2.py --analyze
    python3 scripts/tools/contamination_accuracy_phase2.py --expand --dry-run
    python3 scripts/tools/contamination_accuracy_phase2.py --expand
"""

import yaml
import argparse
from pathlib import Path
from typing import Dict, Set
from datetime import datetime

# Material expansion mappings based on domain knowledge
MATERIAL_EXPANSIONS = {
    'Metal': [
        'Aluminum', 'Steel', 'Stainless Steel', 'Cast Iron', 'Copper', 'Bronze', 
        'Brass', 'Titanium', 'Zinc', 'Nickel', 'Lead', 'Tin', 'Cobalt', 'Chromium'
    ],
    'Metals': [
        'Aluminum', 'Steel', 'Stainless Steel', 'Cast Iron', 'Copper', 'Bronze', 
        'Brass', 'Titanium', 'Zinc', 'Nickel', 'Lead', 'Tin', 'Cobalt', 'Chromium'
    ],
    'Plastics': [
        'ABS', 'Acrylic (PMMA)', 'Polycarbonate', 'HDPE', 'LDPE', 'PET', 
        'Polypropylene', 'PVC', 'Nylon', 'Polyester', 'PTFE'
    ],
    'Glass': [
        'Crown Glass', 'Float Glass', 'Borosilicate Glass', 'Aluminosilicate Glass',
        'Fused Silica', 'Gorilla Glass', 'Tempered Glass'
    ],
    'Ceramic': [
        'Alumina', 'Silicon Carbide', 'Zirconia', 'Aluminum Nitride', 
        'Boron Carbide', 'Boron Nitride', 'Silicon Nitride'
    ],
    'Ceramics': [
        'Alumina', 'Silicon Carbide', 'Zirconia', 'Aluminum Nitride', 
        'Boron Carbide', 'Boron Nitride', 'Silicon Nitride'
    ],
    'Wood': [
        'Oak', 'Maple', 'Cherry', 'Walnut', 'Pine', 'Cedar', 'Ash', 'Birch',
        'Mahogany', 'Teak', 'Bamboo', 'Fir'
    ],
    'Stone': [
        'Granite', 'Marble', 'Limestone', 'Sandstone', 'Basalt', 'Slate',
        'Quartzite', 'Travertine', 'Bluestone', 'Soapstone'
    ],
    'Electronics': [
        'PCB', 'Silicon Wafer', 'Gallium Arsenide', 'Gallium Nitride',
        'Germanium', 'Indium Phosphide'
    ]
}

# Contamination-specific material compatibility rules
# These override default expansions based on contamination chemistry
CONTAMINATION_SPECIFIC_MATERIALS = {
    'rust-oxidation': {
        'Metal': ['Steel', 'Cast Iron', 'Carbon Steel', 'Wrought Iron'],  # Only ferrous metals
        'Metals': ['Steel', 'Cast Iron', 'Carbon Steel', 'Wrought Iron']
    },
    'aluminum-oxidation': {
        'Metal': ['Aluminum', 'Aluminum Bronze'],  # Aluminum-specific
        'Metals': ['Aluminum', 'Aluminum Bronze']
    },
    'copper-patina': {
        'Metal': ['Copper', 'Bronze', 'Brass'],  # Copper alloys only
        'Metals': ['Copper', 'Bronze', 'Brass']
    },
    'galvanize-corrosion': {
        'Metal': ['Galvanized Steel', 'Zinc'],  # Zinc-coated only
        'Metals': ['Galvanized Steel', 'Zinc']
    },
    'chrome-pitting': {
        'Metal': ['Chrome-Plated Steel', 'Chromium', 'Stainless Steel'],
        'Metals': ['Chrome-Plated Steel', 'Chromium', 'Stainless Steel']
    },
    'solder-flux': {
        'Electronics': ['PCB'],  # PCB-specific
        'Metal': ['Copper', 'Tin', 'Lead']  # Solderable metals
    }
}

def load_data():
    """Load Materials.yaml and Contaminants.yaml"""
    materials_path = Path('data/materials/Materials.yaml')
    contaminants_path = Path('data/contaminants/Contaminants.yaml')
    
    with open(materials_path, 'r') as f:
        materials = yaml.safe_load(f)
    
    with open(contaminants_path, 'r') as f:
        contaminants = yaml.safe_load(f)
    
    return materials, contaminants

def get_available_materials(materials_data: Dict) -> Set[str]:
    """Get set of all available material names"""
    return set(materials_data['material_index'].keys())

def analyze_generic_terms(contaminants: Dict, available_materials: Set[str]) -> Dict:
    """Analyze which patterns use generic terms and need expansion"""
    
    generic_terms = set(MATERIAL_EXPANSIONS.keys())
    patterns_to_expand = {}
    
    for pattern_id, pattern_data in contaminants['contamination_patterns'].items():
        valid_materials = pattern_data.get('valid_materials', [])
        
        # Find generic terms in valid_materials
        generic_in_valid = [m for m in valid_materials if m in generic_terms]
        
        if generic_in_valid:
            # Get expansion for each generic term
            expansions = {}
            for generic_term in generic_in_valid:
                # Check if contamination-specific expansion exists
                if pattern_id in CONTAMINATION_SPECIFIC_MATERIALS:
                    if generic_term in CONTAMINATION_SPECIFIC_MATERIALS[pattern_id]:
                        expansion = CONTAMINATION_SPECIFIC_MATERIALS[pattern_id][generic_term]
                    else:
                        expansion = MATERIAL_EXPANSIONS[generic_term]
                else:
                    expansion = MATERIAL_EXPANSIONS[generic_term]
                
                # Filter to only include materials that exist in Materials.yaml
                expansion = [m for m in expansion if m in available_materials]
                expansions[generic_term] = expansion
            
            patterns_to_expand[pattern_id] = {
                'name': pattern_data.get('name', pattern_id),
                'generic_terms': generic_in_valid,
                'expansions': expansions,
                'other_materials': [m for m in valid_materials if m not in generic_terms]
            }
    
    return patterns_to_expand

def print_analysis(patterns_to_expand: Dict):
    """Print analysis of patterns that need expansion"""
    
    print("\n" + "=" * 80)
    print("📊 PHASE 2: GENERIC TERM EXPANSION ANALYSIS")
    print("=" * 80)
    
    total_patterns = len(patterns_to_expand)
    total_expansions = sum(
        sum(len(exp) for exp in p['expansions'].values()) 
        for p in patterns_to_expand.values()
    )
    
    print(f"\n📋 Patterns requiring expansion: {total_patterns}")
    print(f"📈 Total new material references: {total_expansions}")
    print("🎯 Expected accuracy improvement: 59.8% → 85%+\n")
    
    # Group by generic term
    term_stats = {}
    for pattern_data in patterns_to_expand.values():
        for term in pattern_data['generic_terms']:
            if term not in term_stats:
                term_stats[term] = {'patterns': 0, 'expansions': 0}
            term_stats[term]['patterns'] += 1
            term_stats[term]['expansions'] += len(pattern_data['expansions'][term])
    
    print("📊 EXPANSION BY GENERIC TERM:\n")
    for term in sorted(term_stats.keys(), key=lambda x: term_stats[x]['expansions'], reverse=True):
        stats = term_stats[term]
        print(f"   {term:20s} → {stats['patterns']:3d} patterns, {stats['expansions']:4d} new references")
    
    # Show examples
    print("\n" + "=" * 80)
    print("📋 EXPANSION EXAMPLES (first 5 patterns):\n")
    
    for i, (pattern_id, data) in enumerate(list(patterns_to_expand.items())[:5]):
        print(f"{i+1}. {data['name']} ({pattern_id})")
        for generic_term in data['generic_terms']:
            expansion = data['expansions'][generic_term]
            print(f"   ❌ Current: {generic_term}")
            print(f"   ✅ Expand to: {', '.join(expansion[:5])}", end='')
            if len(expansion) > 5:
                print(f" ... (+{len(expansion) - 5} more)")
            else:
                print()
        print()

def expand_generic_terms(contaminants: Dict, patterns_to_expand: Dict, dry_run: bool = True) -> Dict:
    """Expand generic terms to specific materials"""
    
    if dry_run:
        print("\n🔍 DRY RUN MODE - No changes will be saved\n")
    
    modified_patterns = {}
    
    for pattern_id, data in patterns_to_expand.items():
        pattern = contaminants['contamination_patterns'][pattern_id]
        
        # Get current valid_materials
        valid_materials = pattern.get('valid_materials', [])
        
        # Build new valid_materials list
        new_valid_materials = []
        
        # Add all non-generic materials first
        new_valid_materials.extend(data['other_materials'])
        
        # Add expansions for each generic term
        for generic_term in data['generic_terms']:
            new_valid_materials.extend(data['expansions'][generic_term])
        
        # Remove duplicates while preserving order
        seen = set()
        unique_valid_materials = []
        for m in new_valid_materials:
            if m not in seen:
                seen.add(m)
                unique_valid_materials.append(m)
        
        # Store modification
        modified_patterns[pattern_id] = {
            'name': data['name'],
            'old_count': len(valid_materials),
            'new_count': len(unique_valid_materials),
            'removed_generic': data['generic_terms'],
            'added_specific': sum(len(exp) for exp in data['expansions'].values())
        }
        
        if not dry_run:
            # Apply the change
            contaminants['contamination_patterns'][pattern_id]['valid_materials'] = unique_valid_materials
    
    return modified_patterns

def print_expansion_results(modified_patterns: Dict):
    """Print results of expansion"""
    
    print("\n" + "=" * 80)
    print("✅ EXPANSION RESULTS")
    print("=" * 80)
    
    total_patterns = len(modified_patterns)
    total_removed = sum(len(p['removed_generic']) for p in modified_patterns.values())
    total_added = sum(p['added_specific'] for p in modified_patterns.values())
    
    print("\n📊 Summary:")
    print(f"   • Patterns modified: {total_patterns}")
    print(f"   • Generic terms removed: {total_removed}")
    print(f"   • Specific materials added: {total_added}")
    print(f"   • Net change: +{total_added - total_removed} material references\n")
    
    print("📋 Modified patterns (first 10):\n")
    for i, (pattern_id, data) in enumerate(list(modified_patterns.items())[:10]):
        print(f"{i+1}. {data['name']}")
        print(f"   Materials: {data['old_count']} → {data['new_count']} (+{data['new_count'] - data['old_count']})")
        print(f"   Removed: {', '.join(data['removed_generic'])}")
        print(f"   Added: {data['added_specific']} specific materials\n")
    
    if len(modified_patterns) > 10:
        print(f"   ... and {len(modified_patterns) - 10} more patterns\n")

def save_contaminants(contaminants: Dict, backup: bool = True):
    """Save modified Contaminants.yaml"""
    
    contaminants_path = Path('data/contaminants/Contaminants.yaml')
    
    if backup:
        backup_path = contaminants_path.with_suffix(f'.backup.{datetime.now().strftime("%Y%m%d_%H%M%S")}.yaml')
        with open(contaminants_path, 'r') as f:
            backup_content = f.read()
        with open(backup_path, 'w') as f:
            f.write(backup_content)
        print(f"💾 Backup saved: {backup_path}")
    
    with open(contaminants_path, 'w') as f:
        yaml.dump(contaminants, f, default_flow_style=False, sort_keys=False, allow_unicode=True)
    
    print(f"💾 Saved: {contaminants_path}")

def main():
    parser = argparse.ArgumentParser(description='Phase 2: Expand generic terms to specific materials')
    parser.add_argument('--analyze', action='store_true', help='Analyze patterns requiring expansion')
    parser.add_argument('--expand', action='store_true', help='Expand generic terms')
    parser.add_argument('--dry-run', action='store_true', help='Preview changes without saving')
    
    args = parser.parse_args()
    
    # Load data
    print("📂 Loading data...")
    materials, contaminants = load_data()
    available_materials = get_available_materials(materials)
    print(f"   ✅ Loaded {len(available_materials)} materials")
    print(f"   ✅ Loaded {len(contaminants['contamination_patterns'])} patterns")
    
    # Analyze patterns
    patterns_to_expand = analyze_generic_terms(contaminants, available_materials)
    
    if args.analyze:
        print_analysis(patterns_to_expand)
    
    if args.expand:
        modified_patterns = expand_generic_terms(contaminants, patterns_to_expand, dry_run=args.dry_run)
        print_expansion_results(modified_patterns)
        
        if not args.dry_run:
            save_contaminants(contaminants, backup=True)
            print("\n✅ Expansion complete! Run populate_material_contaminants.py to update cache.")
    
    if not args.analyze and not args.expand:
        parser.print_help()

if __name__ == '__main__':
    main()
