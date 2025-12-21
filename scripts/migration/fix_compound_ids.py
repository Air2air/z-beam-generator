#!/usr/bin/env python3
"""
Fix compound IDs in Contaminants.yaml to match frontmatter naming

Updates all compound references to include -compound suffix
Example: water-vapor → water-vapor-compound
"""

import yaml
from pathlib import Path
from datetime import datetime
import shutil

def fix_compound_ids():
    """Fix compound IDs to match frontmatter naming convention."""
    
    contaminants_path = Path("data/contaminants/Contaminants.yaml")
    
    # Create backup
    backup_path = contaminants_path.with_suffix(f'.yaml.backup_{datetime.now().strftime("%Y%m%d_%H%M%S")}')
    shutil.copy2(contaminants_path, backup_path)
    print(f"✅ Backup created: {backup_path}")
    
    # Load data
    with open(contaminants_path, 'r', encoding='utf-8') as f:
        data = yaml.safe_load(f)
    
    patterns = data['contamination_patterns']
    updates_made = 0
    
    for pattern_id, pattern_data in patterns.items():
        # Fix produces_compounds IDs
        relationships = pattern_data.get('relationships', {})
        produces = relationships.get('produces_compounds', [])
        
        for compound_ref in produces:
            compound_id = compound_ref.get('id', '')
            if compound_id and not compound_id.endswith('-compound'):
                compound_ref['id'] = f"{compound_id}-compound"
                updates_made += 1
    
    # Save
    with open(contaminants_path, 'w', encoding='utf-8') as f:
        yaml.dump(data, f, default_flow_style=False, allow_unicode=True, sort_keys=False, width=1000)
    
    print(f"\n✅ Fixed {updates_made} compound ID references")
    print(f"✅ Added -compound suffix to all compound IDs")
    
    # Verify
    with open(contaminants_path, 'r', encoding='utf-8') as f:
        verify_data = yaml.safe_load(f)
    
    verify_count = 0
    for pattern_data in verify_data['contamination_patterns'].values():
        rel = pattern_data.get('relationships', {})
        for compound_ref in rel.get('produces_compounds', []):
            if compound_ref.get('id', '').endswith('-compound'):
                verify_count += 1
    
    print(f"🔍 Verification: {verify_count} compound IDs now have -compound suffix")

if __name__ == "__main__":
    fix_compound_ids()
