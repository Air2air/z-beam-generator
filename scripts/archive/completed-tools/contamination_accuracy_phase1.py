#!/usr/bin/env python3
"""
Phase 1: Contamination Accuracy Improvements

Implements quick wins for contamination data accuracy:
1. Maps generic/contextual terms to actual materials
2. Identifies truly missing materials that need to be added
3. Suggests pattern-specific fixes

Usage:
    python3 scripts/tools/contamination_accuracy_phase1.py --analyze
    python3 scripts/tools/contamination_accuracy_phase1.py --fix --dry-run
    python3 scripts/tools/contamination_accuracy_phase1.py --fix

Author: AI Assistant
Date: November 26, 2025
"""

import argparse
import sys
import yaml
from pathlib import Path
from collections import Counter, defaultdict

project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))


# Generic/contextual terms that should be mapped or removed
GENERIC_TERMS = {
    'Metal', 'Ceramic', 'Ceramics', 'Plastics', 'Wood', 'Glass', 
    'Stone', 'Electronics', 'ALL', 'Metals'
}

# Contextual terms that aren't materials (should be removed)
CONTEXTUAL_TERMS = {
    'Medical Equipment', 'Thin Metals', 'Soft Metals', 'Thin Substrates',
    'Porous Materials', 'Food Surfaces', 'Fabrics', 'Optics',
    'Soft Plastics', 'Open Environments', 'Uncontained Areas',
    'Painted Surfaces', 'Organic Materials', 'Non-Porous Surfaces',
    'Alloy Steel'  # Too generic - need specific alloy
}

# Materials that truly need to be added
MATERIALS_TO_ADD = {
    'Carbon Steel': 'metal',
    'Wrought Iron': 'metal',
    'PVC': 'plastic',
    'Tile': 'ceramic',
    'PCB': 'composite',
    'Chrome-Plated Steel': 'metal',
    'Galvanized Steel': 'metal',
}

# Mapping suggestions for generic terms
GENERIC_MAPPINGS = {
    'Aluminum Alloys': ['Aluminum'],  # Use base material
    'Textile': ['Cotton', 'Polyester', 'Nylon'],  # Expand if these exist
    'Textiles': ['Cotton', 'Polyester', 'Nylon'],
    'Paper': ['Cardboard', 'Paper Products'],  # If appropriate
    'Composite': ['Carbon Fiber Reinforced Polymer', 'Fiberglass'],  # Existing composites
    'Optical Glass': ['Crown Glass', 'Float Glass'],  # Existing glass types
}


def load_data():
    """Load both YAML files."""
    contam_file = project_root / 'data' / 'contaminants' / 'Contaminants.yaml'
    mat_file = project_root / 'data' / 'materials' / 'Materials.yaml'
    
    with open(contam_file, 'r') as f:
        contam_data = yaml.safe_load(f)
    with open(mat_file, 'r') as f:
        mat_data = yaml.safe_load(f)
    
    return contam_data, mat_data


def analyze_issues(contam_data, mat_data):
    """Analyze all accuracy issues."""
    patterns = contam_data.get('contamination_patterns', {})
    materials = mat_data.get('materials', {})
    
    issues = {
        'generic': Counter(),
        'contextual': Counter(),
        'missing_real': Counter(),
        'missing_mappable': Counter(),
        'by_pattern': defaultdict(lambda: {'generic': [], 'contextual': [], 'missing': []})
    }
    
    for pattern_id, pattern_data in patterns.items():
        all_mats = pattern_data.get('valid_materials', []) + pattern_data.get('prohibited_materials', [])
        
        for mat in all_mats:
            if mat in GENERIC_TERMS:
                issues['generic'][mat] += 1
                issues['by_pattern'][pattern_id]['generic'].append(mat)
            elif mat in CONTEXTUAL_TERMS:
                issues['contextual'][mat] += 1
                issues['by_pattern'][pattern_id]['contextual'].append(mat)
            elif mat not in materials:
                if mat in MATERIALS_TO_ADD:
                    issues['missing_real'][mat] += 1
                    issues['by_pattern'][pattern_id]['missing'].append(mat)
                elif mat in GENERIC_MAPPINGS:
                    issues['missing_mappable'][mat] += 1
                    issues['by_pattern'][pattern_id]['missing'].append(mat)
                else:
                    # Unknown - could be typo or needs investigation
                    issues['missing_real'][mat] += 1
                    issues['by_pattern'][pattern_id]['missing'].append(mat)
    
    return issues


def print_analysis(issues):
    """Print analysis report."""
    print('=' * 80)
    print('📊 CONTAMINATION ACCURACY ANALYSIS')
    print('=' * 80)
    print()
    
    print('🔴 GENERIC TERMS (need expansion to specific materials):')
    print(f'   {sum(issues["generic"].values())} references across {len(issues["generic"])} terms')
    print()
    for term, count in issues['generic'].most_common(10):
        print(f'      {count:3}× {term}')
    print()
    
    print('🟡 CONTEXTUAL TERMS (should be removed/replaced):')
    print(f'   {sum(issues["contextual"].values())} references across {len(issues["contextual"])} terms')
    print()
    for term, count in issues['contextual'].most_common(10):
        print(f'      {count:3}× {term}')
    print()
    
    print('🟢 REAL MISSING MATERIALS (need to be added):')
    print(f'   {sum(issues["missing_real"].values())} references across {len(issues["missing_real"])} materials')
    print()
    for mat, count in issues['missing_real'].most_common(10):
        category = MATERIALS_TO_ADD.get(mat, '?')
        print(f'      {count:3}× {mat:30} → Add to {category}')
    print()
    
    print('🔵 MAPPABLE TERMS (can map to existing materials):')
    print(f'   {sum(issues["missing_mappable"].values())} references across {len(issues["missing_mappable"])} terms')
    print()
    for term, count in issues['missing_mappable'].most_common():
        suggestions = GENERIC_MAPPINGS.get(term, [])
        print(f'      {count:3}× {term:30} → {", ".join(suggestions)}')
    print()
    
    # Calculate accuracy improvement
    total_refs = (sum(issues['generic'].values()) + 
                  sum(issues['contextual'].values()) + 
                  sum(issues['missing_real'].values()) +
                  sum(issues['missing_mappable'].values()))
    
    fixable = (sum(issues['missing_real'].values()) +
               sum(issues['missing_mappable'].values()))
    
    print('=' * 80)
    print('📈 POTENTIAL IMPROVEMENT:')
    print(f'   Total problematic references: {total_refs}')
    print(f'   Quick fixes available: {fixable} ({fixable/total_refs*100:.1f}%)')
    print(f'   Generic terms remaining: {sum(issues["generic"].values())} (need manual expansion)')
    print()


def print_recommendations():
    """Print actionable recommendations."""
    print('=' * 80)
    print('💡 RECOMMENDATIONS:')
    print('=' * 80)
    print()
    
    print('QUICK WINS (30-60 minutes):')
    print()
    print('1. Add Missing Materials to Materials.yaml')
    print(f'   Materials to add: {len(MATERIALS_TO_ADD)}')
    for mat, category in MATERIALS_TO_ADD.items():
        print(f'      • {mat} ({category})')
    print()
    
    print('2. Map/Replace Contextual Terms')
    print('   Remove inappropriate terms from Contaminants.yaml:')
    for term in sorted(CONTEXTUAL_TERMS)[:5]:
        print(f'      • "{term}" → Remove or replace with specific material')
    print(f'   ... and {len(CONTEXTUAL_TERMS) - 5} more')
    print()
    
    print('3. Apply Known Mappings')
    for term, mappings in list(GENERIC_MAPPINGS.items())[:3]:
        print(f'      • "{term}" → {", ".join(mappings)}')
    print()
    
    print('PHASE 2 (2-3 hours):')
    print('   • Expand generic terms (Metal, Plastics, etc.)')
    print('   • Use AI to suggest material lists per pattern')
    print('   • Validate chemical compatibility')
    print()


def main():
    parser = argparse.ArgumentParser(description='Phase 1: Contamination Accuracy Improvements')
    parser.add_argument('--analyze', action='store_true', help='Analyze accuracy issues')
    parser.add_argument('--fix', action='store_true', help='Apply fixes')
    parser.add_argument('--dry-run', action='store_true', help='Show what would be fixed')
    
    args = parser.parse_args()
    
    if not args.analyze and not args.fix:
        parser.print_help()
        return
    
    # Load data
    print('📂 Loading data...')
    contam_data, mat_data = load_data()
    print(f'   ✅ Loaded {len(contam_data["contamination_patterns"])} patterns')
    print(f'   ✅ Loaded {len(mat_data["materials"])} materials')
    print()
    
    # Analyze
    issues = analyze_issues(contam_data, mat_data)
    
    if args.analyze:
        print_analysis(issues)
        print_recommendations()
    
    if args.fix:
        print('🔧 FIX MODE')
        print('   This will be implemented in next step...')
        print('   Requires decision on which materials to add and how')


if __name__ == '__main__':
    main()
