#!/usr/bin/env python3
"""
Add relationship fields to Contaminants.yaml

Adds:
- produces_compounds: []  # What compounds are produced when removing this contaminant
- found_on_materials: []  # What materials this contaminant is commonly found on

Following the normalized relationship structure (minimal refs with id + optional context).
"""

import yaml
from pathlib import Path
from datetime import datetime
import shutil

def add_contaminant_relationships():
    """Add produces_compounds and found_on_materials to all contaminant entries."""
    
    contaminants_path = Path("data/contaminants/Contaminants.yaml")
    
    # Create backup
    backup_path = contaminants_path.with_suffix(f'.yaml.backup_{datetime.now().strftime("%Y%m%d_%H%M%S")}')
    shutil.copy2(contaminants_path, backup_path)
    print(f"✅ Backup created: {backup_path}")
    
    # Load data
    with open(contaminants_path, 'r', encoding='utf-8') as f:
        data = yaml.safe_load(f)
    
    if 'contamination_patterns' not in data:
        print("❌ No contamination_patterns found in Contaminants.yaml")
        return
    
    patterns = data['contamination_patterns']
    total_patterns = len(patterns)
    updated_count = 0
    
    for pattern_id, pattern_data in patterns.items():
        # Ensure relationships section exists
        if 'relationships' not in pattern_data:
            pattern_data['relationships'] = {}
        
        relationships = pattern_data['relationships']
        
        # Add produces_compounds if not present
        if 'produces_compounds' not in relationships:
            relationships['produces_compounds'] = []
            updated_count += 1
        
        # Add found_on_materials if not present
        if 'found_on_materials' not in relationships:
            relationships['found_on_materials'] = []
            updated_count += 1
    
    # Save updated data
    with open(contaminants_path, 'w', encoding='utf-8') as f:
        yaml.dump(data, f, default_flow_style=False, allow_unicode=True, sort_keys=False, width=1000)
    
    print(f"\n✅ Updated {total_patterns} contamination patterns")
    print(f"✅ Added {updated_count} relationship fields")
    print(f"✅ Backup saved to: {backup_path.name}")
    
    # Verify structure
    print("\n🔍 Verifying updated structure...")
    with open(contaminants_path, 'r', encoding='utf-8') as f:
        verify_data = yaml.safe_load(f)
    
    sample_pattern = next(iter(verify_data['contamination_patterns'].values()))
    if 'relationships' in sample_pattern:
        rel = sample_pattern['relationships']
        has_produces = 'produces_compounds' in rel
        has_found_on = 'found_on_materials' in rel
        
        print(f"  produces_compounds: {'✅' if has_produces else '❌'}")
        print(f"  found_on_materials: {'✅' if has_found_on else '❌'}")
        
        if has_produces and has_found_on:
            print("\n✅ Contaminants domain migration COMPLETE")
        else:
            print("\n⚠️ Some fields missing")
    else:
        print("❌ Relationships section not found")

if __name__ == "__main__":
    add_contaminant_relationships()
