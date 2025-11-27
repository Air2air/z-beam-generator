#!/usr/bin/env python3
"""
Phase 1A Quick Wins Implementation

Executes all quick win improvements for contamination accuracy:
1. Add 7 missing materials to Materials.yaml
2. Remove/replace contextual terms in Contaminants.yaml  
3. Apply known mappings for generic terms
4. Re-sync material contamination cache

Usage:
    python3 scripts/tools/phase1_quick_wins.py --dry-run
    python3 scripts/tools/phase1_quick_wins.py

Author: AI Assistant
Date: November 26, 2025
"""

import argparse
import sys
import yaml
from pathlib import Path
from datetime import datetime
from collections import defaultdict

project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))


# Materials to add to Materials.yaml
MATERIALS_TO_ADD = {
    'Carbon Steel': {
        'category': 'metal',
        'subcategory': 'ferrous',
        'description': 'Iron-carbon alloy with 0.05-2.0% carbon content, commonly used in structural and mechanical applications'
    },
    'Wrought Iron': {
        'category': 'metal', 
        'subcategory': 'ferrous',
        'description': 'Nearly pure iron with fibrous slag inclusions, known for malleability and corrosion resistance'
    },
    'PVC': {
        'category': 'plastic',
        'subcategory': 'thermoplastic',
        'description': 'Polyvinyl chloride polymer used in pipes, window frames, and electrical cable insulation'
    },
    'Tile': {
        'category': 'ceramic',
        'subcategory': 'glazed',
        'description': 'Thin ceramic or porcelain slab used for floors, walls, and decorative surfaces'
    },
    'PCB': {
        'category': 'composite',
        'subcategory': 'electronic',
        'description': 'Printed circuit board - laminated composite of copper traces on insulating substrate'
    },
    'Chrome-Plated Steel': {
        'category': 'metal',
        'subcategory': 'coated',
        'description': 'Steel with electroplated chromium layer for corrosion resistance and decorative finish'
    },
    'Galvanized Steel': {
        'category': 'metal',
        'subcategory': 'coated',
        'description': 'Steel coated with protective zinc layer through hot-dip galvanizing process'
    }
}

# Contextual terms to remove from valid_materials/prohibited_materials
CONTEXTUAL_TERMS_TO_REMOVE = {
    'Medical Equipment', 'Thin Metals', 'Soft Metals', 'Thin Substrates',
    'Porous Materials', 'Food Surfaces', 'Fabrics', 'Optics',
    'Soft Plastics', 'Open Environments', 'Uncontained Areas',
    'Painted Surfaces', 'Organic Materials', 'Non-Porous Surfaces',
    'Alloy Steel'
}

# Mappings: replace generic term with specific materials
TERM_MAPPINGS = {
    'Aluminum Alloys': 'Aluminum',
    'Textile': ['Cotton', 'Polyester', 'Nylon'],
    'Textiles': ['Cotton', 'Polyester', 'Nylon'],
    'Optical Glass': ['Crown Glass', 'Float Glass'],
    'Composite': ['Carbon Fiber Reinforced Polymer', 'Fiberglass']
}


def add_materials_to_yaml(materials_data, dry_run=False):
    """Add missing materials to Materials.yaml."""
    print('\n📝 STEP 1: Adding Missing Materials to Materials.yaml')
    print('=' * 80)
    
    material_index = materials_data.get('material_index', {})
    materials = materials_data.get('materials', {})
    
    added_count = 0
    skipped_count = 0
    
    for mat_name, mat_info in MATERIALS_TO_ADD.items():
        if mat_name in material_index:
            print(f'  ⏭️  Skipped: {mat_name} (already exists)')
            skipped_count += 1
            continue
        
        if dry_run:
            print(f'  🔍 Would add: {mat_name} → {mat_info["category"]}')
        else:
            # Add to material_index
            material_index[mat_name] = mat_info['category']
            
            # Add minimal material entry
            materials[mat_name] = {
                'name': mat_name,
                'category': mat_info['category'],
                'subcategory': mat_info['subcategory'],
                'title': f'{mat_name} Laser Cleaning',
                'material_metadata': {
                    'last_updated': datetime.now().isoformat() + 'Z',
                    'structure_version': '2.0',
                    'phase1_added': True
                }
            }
            print(f'  ✅ Added: {mat_name} → {mat_info["category"]}')
        added_count += 1
    
    # Sort material_index alphabetically
    if not dry_run:
        materials_data['material_index'] = dict(sorted(material_index.items()))
    
    print(f'\n📊 Summary: {added_count} materials added, {skipped_count} skipped')
    return added_count


def remove_contextual_terms(contam_data, dry_run=False):
    """Remove contextual terms from Contaminants.yaml."""
    print('\n🧹 STEP 2: Removing Contextual Terms from Contaminants.yaml')
    print('=' * 80)
    
    patterns = contam_data.get('contamination_patterns', {})
    removed_count = defaultdict(int)
    
    for pattern_id, pattern_data in patterns.items():
        for field in ['valid_materials', 'prohibited_materials']:
            if field not in pattern_data:
                continue
                
            original_list = pattern_data[field]
            filtered_list = [m for m in original_list if m not in CONTEXTUAL_TERMS_TO_REMOVE]
            
            if len(filtered_list) != len(original_list):
                removed_terms = set(original_list) - set(filtered_list)
                for term in removed_terms:
                    removed_count[term] += 1
                    if dry_run:
                        print(f'  🔍 Would remove "{term}" from {pattern_id}.{field}')
                    else:
                        print(f'  ✅ Removed "{term}" from {pattern_id}.{field}')
                
                if not dry_run:
                    pattern_data[field] = filtered_list
    
    print(f'\n📊 Summary: Removed {len(removed_count)} unique contextual terms')
    for term, count in sorted(removed_count.items(), key=lambda x: x[1], reverse=True):
        print(f'     {count:3}× {term}')
    
    return len(removed_count)


def apply_term_mappings(contam_data, materials_data, dry_run=False):
    """Apply mappings for generic terms."""
    print('\n🔄 STEP 3: Applying Term Mappings in Contaminants.yaml')
    print('=' * 80)
    
    patterns = contam_data.get('contamination_patterns', {})
    available_materials = set(materials_data.get('material_index', {}).keys())
    mapped_count = defaultdict(int)
    
    for pattern_id, pattern_data in patterns.items():
        for field in ['valid_materials', 'prohibited_materials']:
            if field not in pattern_data:
                continue
            
            material_list = pattern_data[field]
            updated_list = []
            
            for mat in material_list:
                if mat in TERM_MAPPINGS:
                    replacement = TERM_MAPPINGS[mat]
                    
                    # Handle both single string and list replacements
                    replacements = [replacement] if isinstance(replacement, str) else replacement
                    
                    # Only use replacements that exist in Materials.yaml
                    valid_replacements = [r for r in replacements if r in available_materials]
                    
                    if valid_replacements:
                        mapped_count[mat] += 1
                        if dry_run:
                            print(f'  🔍 Would map "{mat}" → {valid_replacements} in {pattern_id}.{field}')
                        else:
                            print(f'  ✅ Mapped "{mat}" → {valid_replacements} in {pattern_id}.{field}')
                            updated_list.extend(valid_replacements)
                    else:
                        # No valid replacements exist, keep original
                        updated_list.append(mat)
                else:
                    updated_list.append(mat)
            
            if not dry_run:
                # Remove duplicates while preserving order
                pattern_data[field] = list(dict.fromkeys(updated_list))
    
    print(f'\n📊 Summary: Mapped {len(mapped_count)} generic terms')
    for term, count in sorted(mapped_count.items(), key=lambda x: x[1], reverse=True):
        print(f'     {count:3}× {term}')
    
    return len(mapped_count)


def save_yaml_files(materials_data, contam_data, dry_run=False):
    """Save updated YAML files."""
    if dry_run:
        print('\n🔍 DRY RUN: No files will be modified')
        return
    
    print('\n💾 STEP 4: Saving Updated Files')
    print('=' * 80)
    
    # Update last_updated timestamps
    materials_data['last_updated'] = datetime.now().strftime('%Y-%m-%d')
    contam_data['last_updated'] = datetime.now().strftime('%Y-%m-%d')
    
    # Save Materials.yaml
    mat_file = project_root / 'data' / 'materials' / 'Materials.yaml'
    with open(mat_file, 'w') as f:
        yaml.dump(materials_data, f, default_flow_style=False, sort_keys=False, allow_unicode=True)
    print(f'  ✅ Saved: {mat_file}')
    
    # Save Contaminants.yaml
    contam_file = project_root / 'data' / 'contaminants' / 'Contaminants.yaml'
    with open(contam_file, 'w') as f:
        yaml.dump(contam_data, f, default_flow_style=False, sort_keys=False, allow_unicode=True)
    print(f'  ✅ Saved: {contam_file}')


def main():
    parser = argparse.ArgumentParser(description='Phase 1A Quick Wins Implementation')
    parser.add_argument('--dry-run', action='store_true', help='Show what would be changed without modifying files')
    args = parser.parse_args()
    
    print('=' * 80)
    print('🚀 PHASE 1A QUICK WINS IMPLEMENTATION')
    print('=' * 80)
    
    if args.dry_run:
        print('🔍 DRY RUN MODE - No files will be modified\n')
    
    # Load data
    print('📂 Loading data files...')
    mat_file = project_root / 'data' / 'materials' / 'Materials.yaml'
    contam_file = project_root / 'data' / 'contaminants' / 'Contaminants.yaml'
    
    with open(mat_file, 'r') as f:
        materials_data = yaml.safe_load(f)
    with open(contam_file, 'r') as f:
        contam_data = yaml.safe_load(f)
    
    print(f'  ✅ Loaded {len(materials_data.get("materials", {}))} materials')
    print(f'  ✅ Loaded {len(contam_data.get("contamination_patterns", {}))} patterns')
    
    # Execute improvements
    materials_added = add_materials_to_yaml(materials_data, args.dry_run)
    terms_removed = remove_contextual_terms(contam_data, args.dry_run)
    terms_mapped = apply_term_mappings(contam_data, materials_data, args.dry_run)
    
    # Save files
    if not args.dry_run:
        save_yaml_files(materials_data, contam_data, args.dry_run)
    
    # Final summary
    print('\n' + '=' * 80)
    print('📊 PHASE 1A COMPLETION SUMMARY')
    print('=' * 80)
    print(f'  Materials added:      {materials_added}')
    print(f'  Contextual terms removed: {terms_removed}')
    print(f'  Generic terms mapped: {terms_mapped}')
    print(f'  Total improvements:   {materials_added + terms_removed + terms_mapped}')
    
    if not args.dry_run:
        print('\n✅ All changes saved successfully!')
        print('\n💡 Next steps:')
        print('  1. Run sync script: python3 scripts/sync/populate_material_contaminants.py')
        print('  2. Verify accuracy improvement with analysis tool')
    else:
        print('\n💡 Run without --dry-run to apply changes')


if __name__ == '__main__':
    main()
