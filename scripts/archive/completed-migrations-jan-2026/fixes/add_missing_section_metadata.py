#!/usr/bin/env python3
"""
Add missing _section metadata to relationship fields in frontmatter files.
Adds titles, descriptions, icons, order, and variant to improve UI presentation.
"""

import yaml
from pathlib import Path
from typing import Dict, Any

# Define _section metadata for each field type
SECTION_METADATA = {
    'safety.regulatory_standards': {
        'title': 'Regulatory Standards',
        'description': 'OSHA, ANSI, ISO, and industry safety standards',
        'icon': 'shield-check',
        'order': 1,
        'variant': 'default'
    },
    'technical.removes_contaminants': {
        'title': 'Removes Contaminants',
        'description': 'Contaminants effectively removed by these settings',
        'icon': 'droplet',
        'order': 2,
        'variant': 'default'
    },
    'technical.works_on_materials': {
        'title': 'Works On Materials',
        'description': 'Materials compatible with these laser settings',
        'icon': 'box',
        'order': 1,
        'variant': 'default'
    },
    'materials': {
        'title': 'Found On Materials',
        'description': 'Materials where this contaminant is commonly found',
        'icon': 'box',
        'order': 10,
        'variant': 'default'
    },
    'technical.affects_materials': {
        'title': 'Affects Materials',
        'description': 'Materials impacted by this contaminant',
        'icon': 'box',
        'order': 1,
        'variant': 'default'
    },
    'technical.produces_compounds': {
        'title': 'Produces Compounds',
        'description': 'Hazardous compounds generated during laser removal',
        'icon': 'flask',
        'order': 3,
        'variant': 'warning'
    },
    'operational.health_effects': {
        'title': 'Health Effects',
        'description': 'Potential health impacts from exposure',
        'icon': 'activity',
        'order': 1,
        'variant': 'warning'
    }
}

def add_section_metadata(filepath: Path) -> bool:
    """Add missing _section metadata to a single file."""
    
    with open(filepath, 'r', encoding='utf-8') as f:
        data = yaml.safe_load(f)
    
    if 'relationships' not in data:
        return False
    
    relationships = data['relationships']
    modified = False
    
    # Helper to add _section to a field
    def add_section_to_field(field_data: Dict, field_path: str) -> bool:
        """Add _section if missing and field has items."""
        if not isinstance(field_data, dict):
            return False
        
        if 'items' not in field_data:
            return False
        
        if '_section' in field_data:
            return False  # Already has _section
        
        if field_path in SECTION_METADATA:
            field_data['_section'] = SECTION_METADATA[field_path].copy()
            return True
        
        return False
    
    # Check flat structure fields
    for field_name in ['materials']:
        if field_name in relationships:
            if add_section_to_field(relationships[field_name], field_name):
                modified = True
    
    # Check hierarchical structure (technical, safety, operational)
    for group_name in ['technical', 'safety', 'operational']:
        if group_name not in relationships:
            continue
        
        group = relationships[group_name]
        if not isinstance(group, dict):
            continue
        
        for field_name, field_data in group.items():
            if field_name == '_section':  # Skip group _section
                continue
            
            field_path = f"{group_name}.{field_name}"
            if add_section_to_field(field_data, field_path):
                modified = True
    
    # Save if modified
    if modified:
        with open(filepath, 'w', encoding='utf-8') as f:
            yaml.dump(data, f, default_flow_style=False, allow_unicode=True, sort_keys=False)
        return True
    
    return False

def main():
    """Process all frontmatter files."""
    
    # Use absolute path to z-beam directory
    base_dir = Path(__file__).parent.parent.parent.parent / 'z-beam'
    
    directories = [
        base_dir / 'frontmatter/materials',
        base_dir / 'frontmatter/contaminants',
        base_dir / 'frontmatter/compounds',
        base_dir / 'frontmatter/settings'
    ]
    
    total_files = 0
    modified_files = 0
    
    print("=" * 80)
    print("ADDING MISSING _section METADATA")
    print("=" * 80)
    
    for directory in directories:
        if not directory.exists():
            print(f"⚠️  Directory not found: {directory}")
            continue
        
        dir_modified = 0
        for filepath in sorted(directory.glob('*.yaml')):
            total_files += 1
            if add_section_metadata(filepath):
                modified_files += 1
                dir_modified += 1
        
        print(f"✅ {directory.name}: {dir_modified} files modified")
    
    print("\n" + "=" * 80)
    print(f"COMPLETE: Modified {modified_files}/{total_files} files")
    print("=" * 80)

if __name__ == '__main__':
    main()
