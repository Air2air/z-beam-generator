#!/usr/bin/env python3
"""
Redistribute author_id values across all materials for approximately equal distribution.
Target: 121 materials across 4 authors = 30, 30, 30, 31 materials per author.
"""

import yaml
from collections import Counter, OrderedDict
import random

def redistribute_author_ids():
    print('🔄 Redistributing author_id values for equal distribution')
    print('=' * 60)
    
    # Load Materials.yaml
    with open('data/Materials.yaml', 'r', encoding='utf-8') as f:
        data = yaml.safe_load(f)
    
    materials = data.get('materials', {})
    
    # Collect all materials with their current author_ids
    all_materials = []
    for category, category_data in materials.items():
        items = category_data.get('items', [])
        for i, item in enumerate(items):
            all_materials.append({
                'category': category,
                'index': i,
                'current_author_id': item.get('author_id'),
                'name': item.get('name', 'unnamed')
            })
    
    total_materials = len(all_materials)
    num_authors = 4
    base_per_author = total_materials // num_authors  # 30
    remainder = total_materials % num_authors  # 1
    
    print(f'📊 Total materials: {total_materials}')
    print(f'📝 Authors: {num_authors}')
    print(f'🎯 Target distribution:')
    print(f'   • {num_authors - remainder} authors with {base_per_author} materials each')
    print(f'   • {remainder} author(s) with {base_per_author + 1} materials each')
    
    # Calculate target counts for each author
    target_counts = {}
    for author_id in range(1, num_authors + 1):
        if author_id <= remainder:
            target_counts[author_id] = base_per_author + 1  # 31
        else:
            target_counts[author_id] = base_per_author  # 30
    
    print(f'📋 Specific targets:')
    for author_id, count in target_counts.items():
        print(f'   • author_id {author_id}: {count} materials')
    
    # Shuffle materials for random distribution
    random.shuffle(all_materials)
    
    # Assign new author_ids
    author_assignments = {1: [], 2: [], 3: [], 4: []}
    
    # Distribute materials to authors based on target counts
    for material in all_materials:
        # Find author with fewest assignments that hasn't reached target
        available_authors = [
            author_id for author_id in range(1, num_authors + 1)
            if len(author_assignments[author_id]) < target_counts[author_id]
        ]
        
        if available_authors:
            # Assign to author with fewest current assignments
            chosen_author = min(available_authors, 
                              key=lambda x: len(author_assignments[x]))
            author_assignments[chosen_author].append(material)
        else:
            print(f'⚠️  Warning: Could not assign {material["name"]}')
    
    # Update the Materials.yaml data structure
    changes_made = 0
    for author_id, assigned_materials in author_assignments.items():
        for material in assigned_materials:
            category = material['category']
            index = material['index']
            old_author_id = materials[category]['items'][index].get('author_id')
            
            if old_author_id != author_id:
                materials[category]['items'][index]['author_id'] = author_id
                changes_made += 1
    
    # Save the updated Materials.yaml
    if changes_made > 0:
        with open('data/Materials.yaml', 'w', encoding='utf-8') as f:
            yaml.dump(data, f, default_flow_style=False, allow_unicode=True, 
                     width=1000, sort_keys=False)
        
        print(f'\n✅ Successfully updated {changes_made} material author_id assignments')
    else:
        print(f'\n✅ No changes needed - distribution was already optimal')
    
    # Verify new distribution
    print(f'\n📊 New distribution:')
    for author_id, assigned_materials in author_assignments.items():
        count = len(assigned_materials)
        percentage = (count / total_materials) * 100
        print(f'   • author_id {author_id}: {count:2d} materials ({percentage:5.1f}%)')
    
    # Check if distribution is now balanced
    counts = [len(assigned_materials) for assigned_materials in author_assignments.values()]
    max_count = max(counts)
    min_count = min(counts)
    range_diff = max_count - min_count
    
    print(f'\n📈 Distribution quality:')
    print(f'   • Range: {range_diff} (perfect = 0-1)')
    print(f'   • Status: {"✅ EXCELLENT" if range_diff <= 1 else "❌ NEEDS IMPROVEMENT"}')
    
    return changes_made > 0

if __name__ == '__main__':
    # Set random seed for reproducible results
    random.seed(42)
    
    try:
        success = redistribute_author_ids()
        if success:
            print('\n🎉 Author ID redistribution completed successfully!')
        else:
            print('\n✅ Distribution was already optimal!')
    except Exception as e:
        print(f'\n❌ Error during redistribution: {e}')
        import traceback
        traceback.print_exc()